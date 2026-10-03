from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import logging
import os
from pathlib import Path
import random
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import requests


app = FastAPI(
    title="Pokemon AI Service",
    version="1.0.0",
)
logger = logging.getLogger("uvicorn.error")

IMAGE_SERVICE_URL = os.getenv("IMAGE_SERVICE_URL", "http://image-model:8000")
BACKGROUND_SERVICE_URL = os.getenv(
    "BACKGROUND_SERVICE_URL",
    "http://background-model:8000",
)
TEXT_SERVICE_URL = os.getenv("TEXT_SERVICE_URL", "http://text-model:8000")
AUDIO_SERVICE_URL = os.getenv("AUDIO_SERVICE_URL", "http://audio-model:8000")
PARALLEL_MODEL_CALLS = os.getenv(
    "AI_PARALLEL_MODEL_CALLS",
    "false",
).lower() == "true"
GENERATED_ASSET_DIR = Path(
    os.getenv("GENERATED_ASSET_DIR", "/app/generated-assets")
)


class GenerateImageRequest(BaseModel):
    type: str


class GenerateAudioRequest(BaseModel):
    description: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(request: Request, body: GenerateImageRequest):
    started = perf_counter()
    random_pokemon = _timed(
        "pokemon_type_lookup",
        get_random_pokemon_by_type,
        body.type,
    )
    pokemon_data, source_image = _timed(
        "pokemon_and_sprite_fetch",
        get_pokemon_and_image,
        random_pokemon["url"],
    )

    front_image = _timed(
        "front_image_and_background_removal",
        generate_front_image,
        source_image,
        random_pokemon["name"],
        body.type,
    )

    if PARALLEL_MODEL_CALLS:
        with ThreadPoolExecutor(max_workers=2) as executor:
            back_future = executor.submit(
                _timed,
                "back_image_and_background_removal",
                generate_back_image,
                front_image,
            )
            text_future = executor.submit(
                _timed,
                "text_generation",
                generate_creature_text,
                front_image,
            )
            name, description = text_future.result()
            audio_future = executor.submit(
                _timed,
                "audio_generation",
                generate_audio,
                description,
            )
            back_image = back_future.result()
            audio = audio_future.result()
    else:
        back_image = _timed(
            "back_image_and_background_removal",
            generate_back_image,
            front_image,
        )
        name, description = _timed(
            "text_generation",
            generate_creature_text,
            front_image,
        )
        audio = _timed("audio_generation", generate_audio, description)

    GENERATED_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    asset_id = uuid4().hex
    front_filename = f"{asset_id}-front.png"
    back_filename = f"{asset_id}-back.png"
    audio_filename = f"{asset_id}-cry.wav"
    (GENERATED_ASSET_DIR / front_filename).write_bytes(front_image)
    (GENERATED_ASSET_DIR / back_filename).write_bytes(back_image)
    (GENERATED_ASSET_DIR / audio_filename).write_bytes(audio)
    logger.info(
        "ai timing stage=generate_total elapsed_seconds=%.2f",
        perf_counter() - started,
    )

    public_base_url = os.getenv(
        "PUBLIC_BASE_URL",
        str(request.base_url).rstrip("/"),
    ).rstrip("/")
    pokemon_data["name"] = name
    pokemon_data["description"] = description
    pokemon_data.setdefault("sprites", {})["front_default"] = (
        f"{public_base_url}/generated/{front_filename}"
    )
    pokemon_data["sprites"]["back_default"] = (
        f"{public_base_url}/generated/{back_filename}"
    )
    pokemon_data.setdefault("cries", {})["latest"] = (
        f"{public_base_url}/generated/{audio_filename}"
    )
    return pokemon_data


@app.get("/generated/{filename}")
def get_generated_asset(filename: str):
    asset_path = (GENERATED_ASSET_DIR / filename).resolve()
    if asset_path.parent != GENERATED_ASSET_DIR.resolve() or not asset_path.is_file():
        raise HTTPException(status_code=404, detail="Generated asset not found")

    media_type = "audio/wav" if asset_path.suffix == ".wav" else "image/png"
    return FileResponse(
        asset_path,
        media_type=media_type,
        filename=asset_path.name,
        content_disposition_type="inline",
    )


@app.post("/generateImage")
def generate_image(body: GenerateImageRequest):
    random_pokemon = get_random_pokemon_by_type(body.type)
    _, source_image = get_pokemon_and_image(random_pokemon["url"])
    image = generate_front_image(
        source_image,
        random_pokemon["name"],
        body.type,
    )
    return StreamingResponse(BytesIO(image), media_type="image/png")


@app.post("/generateCry")
def generate_cry(body: GenerateAudioRequest):
    audio = generate_audio(body.description)
    return StreamingResponse(
        BytesIO(audio),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=creature.wav"},
    )


def get_random_pokemon_by_type(pokemon_type: str) -> dict:
    response = requests.get(
        f"https://pokeapi.co/api/v2/type/{pokemon_type}/",
        timeout=30,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch Pokemon type")

    pokemon_entries = response.json().get("pokemon", [])
    if not pokemon_entries:
        raise HTTPException(
            status_code=404,
            detail="No Pokemon found for the specified type",
        )
    return random.choice(pokemon_entries)["pokemon"]


def get_pokemon_and_image(pokemon_url: str) -> tuple[dict, bytes]:
    pokemon_response = requests.get(pokemon_url, timeout=30)
    if pokemon_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch Pokemon data")

    pokemon_data = pokemon_response.json()
    image_url = pokemon_data.get("sprites", {}).get("front_default")
    if not image_url:
        raise HTTPException(status_code=404, detail="Pokemon has no front sprite")

    image_response = requests.get(image_url, timeout=30)
    if image_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch Pokemon sprite")
    return pokemon_data, image_response.content


def _service_response(response: requests.Response, service_name: str) -> bytes:
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"{service_name} service returned HTTP {response.status_code}",
        )
    return response.content


def _timed(stage: str, operation, *args, **kwargs):
    started = perf_counter()
    try:
        return operation(*args, **kwargs)
    finally:
        logger.info(
            "ai timing stage=%s elapsed_seconds=%.2f",
            stage,
            perf_counter() - started,
        )


def generate_front_image(source_image: bytes, name: str, pokemon_type: str) -> bytes:
    try:
        response = _timed(
            "image_front_service",
            requests.post,
            f"{IMAGE_SERVICE_URL}/generate/front",
            data={"name": name, "pokemon_type": pokemon_type},
            files={"image": ("source.png", source_image, "image/png")},
            timeout=1200,
        )
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Image service is unavailable") from error
    generated_image = _service_response(response, "Image")

    return _timed(
        "background_removal_front",
        remove_image_background,
        generated_image,
    )


def generate_back_image(front_image: bytes) -> bytes:
    try:
        response = _timed(
            "image_back_service",
            requests.post,
            f"{IMAGE_SERVICE_URL}/generate/back",
            files={"image": ("front.png", front_image, "image/png")},
            timeout=1200,
        )
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Image service is unavailable") from error
    generated_image = _service_response(response, "Image")

    return _timed(
        "background_removal_back",
        remove_image_background,
        generated_image,
    )


def remove_image_background(image: bytes) -> bytes:
    try:
        response = requests.post(
            f"{BACKGROUND_SERVICE_URL}/remove-background",
            files={"image": ("creature.png", image, "image/png")},
            timeout=120,
        )
    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail="Background removal service is unavailable",
        ) from error
    return _service_response(response, "Background removal")


def generate_creature_text(image: bytes) -> tuple[str, str]:
    try:
        response = requests.post(
            f"{TEXT_SERVICE_URL}/generate",
            files={"image": ("creature.png", image, "image/png")},
            timeout=600,
        )
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Text service is unavailable") from error
    _service_response(response, "Text")
    generated_text = response.json()
    return generated_text["name"], generated_text["description"]


def generate_audio(description: str) -> bytes:
    try:
        response = requests.post(
            f"{AUDIO_SERVICE_URL}/generate",
            json={"description": description},
            timeout=600,
        )
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Audio service is unavailable") from error
    return _service_response(response, "Audio")
