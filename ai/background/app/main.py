from io import BytesIO
import os
import threading

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from huggingface_hub import hf_hub_download
from PIL import Image
import numpy as np
import onnxruntime as ort


app = FastAPI(title="Pokemon Background Removal Service", version="1.0.0")
background_removal_model = None
inference_lock = threading.Lock()


@app.on_event("startup")
def startup():
    global background_removal_model
    model_path = hf_hub_download(
        repo_id=os.getenv(
            "BACKGROUND_REMOVAL_MODEL",
            "studioludens/birefnet-lite-512",
        ),
        filename="onnx/model_fp16.onnx",
        token=os.getenv("HF_TOKEN"),
    )
    background_removal_model = ort.InferenceSession(
        model_path,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
    )
    print("Background removal model ready")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": background_removal_model is not None}


@app.post("/remove-background")
def remove_background(image: UploadFile = File(...)):
    source_image = Image.open(BytesIO(image.file.read())).convert("RGBA")
    with inference_lock:
        result = apply_background_mask(source_image)

    buffer = BytesIO()
    result.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")


def apply_background_mask(image: Image.Image) -> Image.Image:
    original_size = image.size
    input_image = image.convert("RGB").resize(
        (512, 512),
        Image.Resampling.LANCZOS,
    )
    image_array = np.asarray(input_image, dtype=np.float32) / 255.0
    image_array = np.transpose(image_array, (2, 0, 1))
    image_array = np.expand_dims(image_array, axis=0)

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)
    image_array = (image_array - mean) / std

    input_name = background_removal_model.get_inputs()[0].name
    outputs = background_removal_model.run(None, {input_name: image_array})
    mask = np.squeeze(outputs[0])
    mask = 1.0 / (1.0 + np.exp(-mask))
    mask = (np.clip(mask, 0.0, 1.0) * 255).astype(np.uint8)
    mask_image = Image.fromarray(mask, mode="L").resize(
        original_size,
        Image.Resampling.BILINEAR,
    )

    result = image.convert("RGBA")
    result.putalpha(mask_image)
    return result
