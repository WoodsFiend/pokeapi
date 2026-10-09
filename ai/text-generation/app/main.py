import json
import logging
import os
import threading
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
text_processor = None
text_model = None
inference_lock = threading.Lock()


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
            temperature=0.9,
            top_p=0.95,
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


@app.post("/generate")
def generate(body: GenerateTextRequest):
    with inference_lock:
        generated_text = generate_text(body.prompt)

    try:
        json_start = generated_text.index("{")
        generated_data, _ = json.JSONDecoder().raw_decode(
            generated_text[json_start:]
        )
        name = generated_data["name"].strip()
        description = generated_data["description"].strip()
    except (ValueError, KeyError, AttributeError, TypeError) as error:
        raise HTTPException(
            status_code=502,
            detail="Text model returned an invalid name/description response",
        ) from error

    if not name or not description:
        raise HTTPException(
            status_code=502,
            detail="Text model returned an empty name or description",
        )

    return {
        "name": name,
        "description": description,
    }
