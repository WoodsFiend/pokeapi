from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import random
import torch
import torchaudio
import os
from diffusers import Flux2KleinPipeline
from PIL import Image
from io import BytesIO
import numpy as np
from stable_audio_3 import StableAudioModel
from huggingface_hub import hf_hub_download
import onnxruntime as ort

app = FastAPI(
    title="Pokemon AI Service",
    version="1.0.0",
)

class GenerateImageRequest(BaseModel):
    type: str

class GenerateAudioRequest(BaseModel):
    description: str


device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

IMAGE_GEN_MODEL = os.getenv(
    "HF_MODEL",
    "black-forest-labs/FLUX.2-klein-4B",
)

TOKEN = os.getenv("HF_TOKEN")

# ----------------------------------------
# BiRefNet
# ----------------------------------------

BACKGROUND_REMOVAL_MODEL = (
    "studioludens/birefnet-lite-512"
)

background_model_path = hf_hub_download(
    repo_id=BACKGROUND_REMOVAL_MODEL,
    filename="onnx/model_fp16.onnx",
    token=TOKEN,
)

background_removal_model = ort.InferenceSession(
    background_model_path,
    providers=[
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ],
)

print(
    "Background removal providers:",
    background_removal_model.get_providers(),
)

# ----------------------------------------
# FLUX
# ----------------------------------------

if device == "cuda":

    pipe = Flux2KleinPipeline.from_pretrained(
        IMAGE_GEN_MODEL,
        token=TOKEN,
        dtype=torch.bfloat16,
    )
    pipe.to("cuda")

else:

    pipe = Flux2KleinPipeline.from_pretrained(
        IMAGE_GEN_MODEL,
        token=TOKEN,
        dtype=torch.float32,
    )

    pipe.to("cpu")

torch.set_grad_enabled(False)

# ----------------------------------------
# Stable Audio
# ----------------------------------------

audio_model = StableAudioModel.from_pretrained(
    "small-sfx",
)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.post("/generate")
def generate(request: GenerateImageRequest):
    response = requests.get(
        "http://app/api/v2/type/" + request.type + "/"
    )
    # Handle the response and select a random Pokemon from the type.pokemon array
    if response.status_code != 200:
        return {
            "error": "Failed to fetch Pokemon data from PokeAPI"
        }
    # Handle the response and select a random Pokemon from the type.pokemon array
    data = response.json()
    if "pokemon" not in data or not data["pokemon"]:
        return {
            "error": "No Pokemon found for the specified type"
        }
    
    random_pokemon = random.choice(data["pokemon"])["pokemon"]
    name = random_pokemon["name"]
    pokemon_url = random_pokemon["url"]

    # Get the pokemon from the pokemon url
    pokemon_response = requests.get(pokemon_url)
    if pokemon_response.status_code != 200:
        return {
            "error": "Failed to fetch Pokemon data from PokeAPI"
        }
    imageFrontUrl = pokemon_response.json()["sprites"]["front_default"]

    # Get the image from the imageFrontUrl
    image_response = requests.get(imageFrontUrl)
    if image_response.status_code != 200:
        return {
            "error": "Failed to fetch Pokemon image from PokeAPI"
        }
    
    input_image = Image.open(
        BytesIO(image_response.content)
    ).convert("RGB")

    prompt = (
        f"Create a completely original creature inspired by the visual "
        f"characteristics of {name}. "
        f"The creature should be a {request.type}-type fantasy creature. "
        f"Do not copy the original creature exactly. "
        f"Do not include shadows or reflections. "
        f"Do not include text. "
        f"Use a solid white background. "
        f"High-quality pixel art, crisp pixel edges, limited color palette. "
        f"Create a polished video game creature."
    )

    result = pipe(
        prompt=prompt,
        image=input_image,
        height=512,
        width=512,
        guidance_scale=1.0,
        num_inference_steps=4,
    )

    generated_image = result.images[0].convert("RGBA")
    
    generated_image = remove_background(generated_image)

    image_buffer = BytesIO()
    generated_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )

def remove_background(image: Image.Image) -> Image.Image:
    original_size = image.size

    # Convert to RGB and resize for BiRefNet.
    input_image = image.convert("RGB").resize(
        (512, 512),
        Image.Resampling.LANCZOS,
    )

    image_array = np.asarray(
        input_image,
        dtype=np.float32,
    ) / 255.0

    # HWC -> CHW
    image_array = np.transpose(
        image_array,
        (2, 0, 1),
    )

    # Add batch dimension.
    image_array = np.expand_dims(
        image_array,
        axis=0,
    )

    # ImageNet normalization.
    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32,
    ).reshape(1, 3, 1, 1)

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32,
    ).reshape(1, 3, 1, 1)

    image_array = (
        image_array - mean
    ) / std

    input_name = background_removal_model.get_inputs()[0].name

    outputs = background_removal_model.run(
        None,
        {
            input_name: image_array,
        },
    )

    mask = outputs[0]

    # Remove batch/channel dimensions.
    mask = np.squeeze(mask)

    # Convert logits to probabilities.
    mask = 1.0 / (1.0 + np.exp(-mask))

    # Convert to 0-255.
    mask = (
        np.clip(mask, 0.0, 1.0) * 255
    ).astype(np.uint8)

    mask_image = Image.fromarray(
        mask,
        mode="L",
    )

    # Restore the mask to the generated image's resolution.
    mask_image = mask_image.resize(
        original_size,
        Image.Resampling.BILINEAR,
    )

    # Apply alpha channel.
    result = image.convert("RGBA")
    result.putalpha(mask_image)

    return result

@app.post("/generateCry")
def generate_audio(request: GenerateAudioRequest):
    prompt = (
        f"Create a completely original creature cry sound effect inspired by "
        f"the description: {request.description}. "
        f"Make the sound effect suitable for a video game."
    )

    audio = audio_model.generate(
        prompt=prompt,
        duration=1,
    )

    # Stable Audio returns a torch Tensor.
    # Make sure it has [channels, samples] shape.
    if audio.dim() == 3:
        audio = audio.squeeze(0)

    audio = audio.detach().cpu()
    print("Audio type:", type(audio))
    print("Audio shape:", audio.shape)
    audio_buffer = BytesIO()

    torchaudio.save(
        audio_buffer,
        audio,
        sample_rate=44100,
        format="wav",
    )

    audio_buffer.seek(0)

    return StreamingResponse(
        audio_buffer,
        media_type="audio/wav",
        headers={
            "Content-Disposition": "inline; filename=creature.wav"
        },
    )