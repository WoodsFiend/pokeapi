from io import BytesIO
import logging
import os
import threading
from time import perf_counter

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response
from diffusers import Flux2KleinPipeline
from PIL import Image
from pydantic import BaseModel, Field
import torch


app = FastAPI(title="Pokemon Image Model Service", version="1.0.0")
logger = logging.getLogger("uvicorn.error")
device = "cuda" if torch.cuda.is_available() else "cpu"
image_model = None
inference_lock = threading.Lock()
image_size = int(os.getenv("IMAGE_GENERATION_SIZE", "512"))
inference_steps = int(os.getenv("IMAGE_INFERENCE_STEPS", "4"))


class GenerateFrontRequest(BaseModel):
    prompt: str = Field(min_length=1)


def setup():
    global image_model

    token = os.getenv("HF_TOKEN")
    model_name = os.getenv(
        "IMAGE_MODEL",
        "black-forest-labs/FLUX.2-klein-4B",
    )

    dtype = (
        torch.bfloat16
        if device == "cuda"
        else torch.float32
    )

    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    image_model = Flux2KleinPipeline.from_pretrained(
        model_name,
        token=token,
        torch_dtype=dtype,
    )

    image_model.load_lora_weights(
        "Limbicnation/pixel-art-lora"
    )

    image_model.to(device)

    logger.info(
        "CUDA: %s | GPU: %s",
        torch.cuda.is_available(),
        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
    )

    logger.info(
        "Transformer device=%s dtype=%s",
        next(image_model.transformer.parameters()).device,
        next(image_model.transformer.parameters()).dtype,
    )

    logger.info(
        "VAE device=%s dtype=%s",
        next(image_model.vae.parameters()).device,
        next(image_model.vae.parameters()).dtype,
    )

    adapter = image_model.get_active_adapters()[0]
    image_model.set_adapters(
        adapter,
        adapter_weights=0.05,
    )

    if device == "cuda":
        try:
            image_model.transformer = torch.compile(
                image_model.transformer,
                mode="reduce-overhead",
                fullgraph=False,
            )
            print("Transformer torch.compile enabled")
        except Exception as e:
            logger.warning(
                "Could not compile transformer: %s",
                e,
            )

    torch.set_grad_enabled(False)

    print(f"Image model ready on {device}: {model_name}")
    print(
        "Image generation settings: "
        f"size={image_size}x{image_size}, "
        f"steps={inference_steps}, "
        f"dtype={dtype}"
    )

@app.on_event("startup")
def startup():
    setup()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": image_model is not None}


@app.post("/generate/front")
def generate_front(body: GenerateFrontRequest):
    with inference_lock, torch.inference_mode():
        if device == "cuda":
            torch.cuda.synchronize()
        started = perf_counter()
        result = image_model(
            prompt=body.prompt,
            height=image_size,
            width=image_size,
            guidance_scale=1.0,
            num_inference_steps=inference_steps,
        )
        if device == "cuda":
            torch.cuda.synchronize()
        logger.info(
            "image timing mode=front inference_seconds=%.2f",
            perf_counter() - started,
        )
        generated_image = result.images[0]
        has_transparency = image_has_transparency(generated_image)
        generated_image = generated_image.convert("RGBA")
    return image_response(generated_image, has_transparency)


@app.post("/generate/back")
def generate_back(
    image: UploadFile = File(...),
    prompt: str = Form(..., min_length=1),
):
    front_image = Image.open(BytesIO(image.file.read())).convert("RGBA")
    with inference_lock, torch.inference_mode():
        if device == "cuda":
            torch.cuda.synchronize()
        started = perf_counter()
        result = image_model(
            prompt=prompt,
            image=front_image,
            height=image_size,
            width=image_size,
            guidance_scale=1.0,
            num_inference_steps=inference_steps,
        )
        if device == "cuda":
            torch.cuda.synchronize()
        logger.info(
            "image timing mode=back inference_seconds=%.2f",
            perf_counter() - started,
        )
        generated_image = result.images[0]
        has_transparency = image_has_transparency(generated_image)
        generated_image = generated_image.convert("RGBA")
    return image_response(generated_image, has_transparency)


def image_has_transparency(image: Image.Image) -> bool:
    if "A" not in image.getbands() and "transparency" not in image.info:
        return False
    return image.convert("RGBA").getchannel("A").getextrema()[0] < 255


def image_response(image: Image.Image, has_transparency: bool) -> Response:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={
            "X-Image-Has-Transparency": (
                "true" if has_transparency else "false"
            ),
        },
    )
