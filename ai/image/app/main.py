from io import BytesIO
import logging
import os
import threading
from time import perf_counter

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response
from diffusers import Flux2KleinPipeline
from PIL import Image
import torch


app = FastAPI(title="Pokemon Image Model Service", version="1.0.0")
logger = logging.getLogger("uvicorn.error")
device = "cuda" if torch.cuda.is_available() else "cpu"
image_model = None
inference_lock = threading.Lock()
image_size = int(os.getenv("IMAGE_GENERATION_SIZE", "512"))
inference_steps = int(os.getenv("IMAGE_INFERENCE_STEPS", "4"))


def setup():
    global image_model

    token = os.getenv("HF_TOKEN")
    model_name = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.2-klein-4B")
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    image_model = Flux2KleinPipeline.from_pretrained(
        model_name,
        token=token,
        dtype=dtype,
    )
    image_model.to(device)
    torch.set_grad_enabled(False)
    print(f"Image model ready on {device}: {model_name}")
    print(
        "Image generation settings: "
        f"size={image_size}x{image_size}, steps={inference_steps}"
    )


@app.on_event("startup")
def startup():
    setup()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": image_model is not None}


@app.post("/generate/front")
def generate_front(
    name: str = Form(...),
    pokemon_type: str = Form(...),
    image: UploadFile = File(...),
):
    source_image = Image.open(BytesIO(image.file.read())).convert("RGB")
    prompt = (
        f"Create a completely original creature inspired by the visual "
        f"characteristics of {name}. "
        f"The creature should be a {pokemon_type}-type fantasy creature. "
        "Do not copy the original creature exactly. "
        "Do not include shadows or reflections. "
        "Do not include text. "
        "Use a solid white background. "
        "High-quality pixel art, crisp pixel edges, limited color palette. "
        "Create a polished video game creature."
    )

    with inference_lock, torch.inference_mode():
        started = perf_counter()
        result = image_model(
            prompt=prompt,
            image=source_image,
            height=image_size,
            width=image_size,
            guidance_scale=1.0,
            num_inference_steps=inference_steps,
        )
        logger.info(
            "image timing mode=front inference_seconds=%.2f",
            perf_counter() - started,
        )
        generated_image = result.images[0].convert("RGBA")
    return image_response(generated_image)


@app.post("/generate/back")
def generate_back(image: UploadFile = File(...)):
    front_image = Image.open(BytesIO(image.file.read())).convert("RGBA")
    with inference_lock, torch.inference_mode():
        started = perf_counter()
        result = image_model(
            prompt="Create a view of this creature from the back.",
            image=front_image,
            height=image_size,
            width=image_size,
            guidance_scale=1.0,
            num_inference_steps=inference_steps,
        )
        logger.info(
            "image timing mode=back inference_seconds=%.2f",
            perf_counter() - started,
        )
        generated_image = result.images[0].convert("RGBA")
    return image_response(generated_image)


def image_response(image: Image.Image) -> Response:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")
