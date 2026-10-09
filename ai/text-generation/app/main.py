import json
import logging
import os
import threading
import unicodedata
from time import perf_counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


app = FastAPI(
    title="Pokemon Text Model Service",
    version="1.0.0",
)
logger = logging.getLogger("uvicorn.error")
device = "cuda" if torch.cuda.is_available() else "cpu"
TEXT_GENERATION_TEMPERATURE = float(
    os.getenv("TEXT_GENERATION_TEMPERATURE", "1.0")
)
TEXT_GENERATION_TOP_P = float(os.getenv("TEXT_GENERATION_TOP_P", "0.98"))
text_processor = None
text_model = None
inference_lock = threading.Lock()
MAX_GENERATION_ATTEMPTS = 2

if TEXT_GENERATION_TEMPERATURE <= 0:
    raise ValueError("TEXT_GENERATION_TEMPERATURE must be greater than 0")
if not 0 < TEXT_GENERATION_TOP_P <= 1:
    raise ValueError("TEXT_GENERATION_TOP_P must be greater than 0 and at most 1")


class GenerateTextRequest(BaseModel):
    prompt: str = Field(min_length=1)


def setup():
    global text_processor
    global text_model

    token = os.getenv("HF_TOKEN")
    model_name = os.getenv(
        "TEXT_MODEL",
        "Qwen/Qwen2.5-VL-3B-Instruct",
    )

    print(f"Loading text model: {model_name}")
    print(f"Using device: {device}")

    text_processor = AutoProcessor.from_pretrained(
        model_name,
        token=token,
    )

    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    text_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_name,
        token=token,
        dtype=dtype,
        device_map="auto" if device == "cuda" else None,
        attn_implementation="sdpa",
    )

    if device == "cpu":
        text_model.to("cpu")

    text_model.eval()

    loaded_devices = sorted(
        {
            str(loaded_device)
            for loaded_device in getattr(text_model, "hf_device_map", {}).values()
        }
    )
    if not loaded_devices:
        loaded_devices = [device]
    print(f"Text model ready on {', '.join(loaded_devices)}: {model_name}")
    if "cpu" in loaded_devices or "disk" in loaded_devices:
        print("Text model offload is enabled; CPU or disk offload can slow generation.")


@app.on_event("startup")
def startup():
    setup()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": text_model is not None,
        "device": device,
    }


def generate_text(prompt: str, max_new_tokens: int = 140) -> str:
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ]
    inputs = text_processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    inputs = inputs.to(text_model.device)

    generation_started = perf_counter()
    with torch.inference_mode():
        generated_ids = text_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=TEXT_GENERATION_TEMPERATURE,
            top_p=TEXT_GENERATION_TOP_P,
        )
    logger.info(
        "text timing stage=model_generate elapsed_seconds=%.2f output_tokens=%d",
        perf_counter() - generation_started,
        generated_ids.shape[-1] - inputs["input_ids"].shape[-1],
    )

    input_length = inputs["input_ids"].shape[-1]
    generated_ids = generated_ids[:, input_length:]
    return text_processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()


def normalize_english_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    characters = []
    for character in normalized:
        if character.isascii():
            characters.append(character)
        elif not unicodedata.combining(character):
            characters.append(" ")
    return " ".join("".join(characters).split())


@app.post("/generate")
def generate(body: GenerateTextRequest):
    with inference_lock:
        for attempt in range(MAX_GENERATION_ATTEMPTS):
            prompt = body.prompt
            if attempt > 0:
                prompt += (
                    "\n\nYour previous response was invalid. Return a fresh, valid JSON object "
                    'with non-empty string fields named "name" and "description". '
                    "Write both fields in English using ASCII characters only."
                )

            generated_text = generate_text(prompt)
            try:
                json_start = generated_text.index("{")
                generated_data, _ = json.JSONDecoder().raw_decode(
                    generated_text[json_start:]
                )
                raw_name = generated_data["name"]
                raw_description = generated_data["description"]
                if not isinstance(raw_name, str) or not isinstance(raw_description, str):
                    raise ValueError("name and description must be strings")

                raw_name = raw_name.strip()
                raw_description = raw_description.strip()
                if not raw_name or not raw_description:
                    raise ValueError("name and description must not be empty")

                name = normalize_english_ascii(raw_name)
                description = normalize_english_ascii(raw_description)
                break
            except (ValueError, KeyError, AttributeError, TypeError) as error:
                if attempt + 1 == MAX_GENERATION_ATTEMPTS:
                    raise HTTPException(
                        status_code=502,
                        detail="Text model returned an invalid name/description response after retry",
                    ) from error
                logger.warning(
                    "Text model returned an invalid name/description response; retrying"
                )

    return {
        "name": name,
        "description": description,
    }
