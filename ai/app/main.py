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
import base64

app = FastAPI(
    title="Pokemon AI Service",
    version="1.0.0",
)

image_model = None
background_removal_model = None
audio_model = None

class GenerateImageRequest(BaseModel):
    type: str

class GenerateAudioRequest(BaseModel):
    description: str

def setup():
    global image_model
    global background_removal_model
    global audio_model

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Hugging Face token for private model access
    TOKEN = os.getenv("HF_TOKEN")

    # ----------------------------------------
    # Background Removal Model
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
    # Image Generation Model
    # ----------------------------------------
    IMAGE_GEN_MODEL = os.getenv(
        "HF_MODEL",
        "black-forest-labs/FLUX.2-klein-4B",
    )
    if device == "cuda":

        image_model = Flux2KleinPipeline.from_pretrained(
            IMAGE_GEN_MODEL,
            token=TOKEN,
            dtype=torch.bfloat16,
        )
        image_model.to("cuda")
    else:

        image_model = Flux2KleinPipeline.from_pretrained(
            IMAGE_GEN_MODEL,
            token=TOKEN,
            dtype=torch.float32,
        )

        image_model.to("cpu")

    torch.set_grad_enabled(False)

    # ----------------------------------------
    # Audio Generation Model
    # ----------------------------------------
    audio_model = StableAudioModel.from_pretrained(
        "small-sfx",
    )

@app.on_event("startup")
def startup():
    setup()

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.post("/generate")
def generate(request: GenerateImageRequest):
    random_pokemon = get_random_pokemon_by_type(
        request.type
    )
    image = generate_image_data(random_pokemon, request.type)

    name = generate_name_from_image(
        image,
        request.type,
    )

    description = generate_description_from_image(
        image,
        request.type,
    )

    audio = generate_audio_data(
        GenerateAudioRequest(
            description=description,
        )
    )

    # Convert image to PNG bytes
    image_buffer = BytesIO()
    image.save(
        image_buffer,
        format="PNG",
    )

    image_base64 = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    # Convert audio to WAV bytes
    audio_buffer = BytesIO()

    torchaudio.save(
        audio_buffer,
        audio,
        sample_rate=44100,
        format="wav",
    )

    audio_base64 = base64.b64encode(
        audio_buffer.getvalue()
    ).decode("utf-8")

    return {
        "pokemon": random_pokemon,
        "image": image_base64,
        "name": name,
        "description": description,
        "cry": audio_base64,
    }

@app.post("/generateImage")
def generate_image(request: GenerateImageRequest):
    random_pokemon = get_random_pokemon_by_type(
        request.type
    )
    image = generate_image_data(random_pokemon, request.type)

    image_buffer = BytesIO()

    image.save(
        image_buffer,
        format="PNG",
    )

    image_buffer.seek(0)

    return StreamingResponse(
        image_buffer,
        media_type="image/png",
    )

@app.post("/generateCry")
def generate_audio(request: GenerateAudioRequest):
    audio = generate_audio_data(request)

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

def generate_image_data(random_pokemon: dict, type: str) -> Image.Image:
    name = random_pokemon["name"]
    pokemon_url = random_pokemon["url"]

    input_image = get_pokemon_image(
        pokemon_url
    )

    prompt = (
        f"Create a completely original creature inspired by the visual "
        f"characteristics of {name}. "
        f"The creature should be a {type}-type fantasy creature. "
        f"Do not copy the original creature exactly. "
        f"Do not include shadows or reflections. "
        f"Do not include text. "
        f"Use a solid white background. "
        f"High-quality pixel art, crisp pixel edges, limited color palette. "
        f"Create a polished video game creature."
    )

    result = image_model(
        prompt=prompt,
        image=input_image,
        height=512,
        width=512,
        guidance_scale=1.0,
        num_inference_steps=4,
    )

    generated_image = result.images[0].convert("RGBA")

    return remove_background(generated_image)

def generate_audio_data(
    request: GenerateAudioRequest,
) -> torch.Tensor:

    prompt = (
        f"Create a completely original creature cry sound effect inspired by "
        f"the description: {request.description}. "
        f"Make the sound effect suitable for a video game."
    )

    audio = audio_model.generate(
        prompt=prompt,
        duration=1,
    )

    if audio.dim() == 3:
        audio = audio.squeeze(0)

    return audio.detach().cpu()

def get_random_pokemon_by_type(pokemon_type: str):
    response = requests.get(
        f"https://pokeapi.co/api/v2/type/{pokemon_type}/"
    )
    if response.status_code != 200:
        raise ValueError("Failed to fetch Pokemon data from PokeAPI")
    
    data = response.json()
    if "pokemon" not in data or not data["pokemon"]:
        raise ValueError("No Pokemon found for the specified type")
    
    random_pokemon = random.choice(data["pokemon"])["pokemon"]
    return random_pokemon

def get_pokemon_image(pokemon_url: str):
    response = requests.get(pokemon_url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch Pokemon data from PokeAPI")
    
    data = response.json()
    if "sprites" not in data or "front_default" not in data["sprites"]:
        raise ValueError("No image found for the specified Pokemon")

    image_front_url = data["sprites"]["front_default"]
    # Get the image from the imageFrontUrl
    image_response = requests.get(image_front_url)
    if image_response.status_code != 200:
        return {
            "error": "Failed to fetch Pokemon image from PokeAPI"
        }
    
    image = Image.open(
        BytesIO(image_response.content)
    ).convert("RGB")

    return image

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

def generate_description_from_image(image: Image.Image, type: str) -> str:
    # Placeholder for image captioning logic.
    # In a real implementation, you would use an image captioning model here.
    return f"A unique {type} creature."

def generate_name_from_image(image: Image.Image, type: str) -> str:
    # Placeholder for image naming logic.
    # In a real implementation, you would use an image naming model here.
    return f"{type} Boy"