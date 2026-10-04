from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import logging
import os
from pathlib import Path
import types
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

DESCRIPTION_TONES = [
    "whimsical",
    "mysterious",
    "playful",
    "dramatic",
    "charming",
    "curious",
    "lighthearted",
    "adventurous",
]
DESCRIPTION_FOCUSES = [ 
    "its distinctive physical appearance", 
    "its personality and temperament", 
    "how it behaves in the wild", 
    "its unusual habits", 
    "how it interacts with other creatures", 
    "its preferred habitat and lifestyle", 
    "a distinctive physical feature", 
    "a curious behavior it is known for", 
]
NAME_STYLES = [ 
    "cute and playful", 
    "mysterious and fantastical", 
    "short and energetic", 
    "whimsical and unusual", 
    "ancient and mythical", 
    "quirky and memorable", 
    "a clever combination of concepts related to the creature", 
    "soft and friendly", 
    "wild and intimidating", 
    "magical and easy to pronounce",
]

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
    pokemon_data = _timed(
        "pokemon_data_fetch",
        get_pokemon_data,
        random_pokemon["url"],
    )
    pokemon_types = get_pokemon_types(pokemon_data) or [body.type]

    name, description = _timed(
        "text_generation",
        generate_creature_text,
        pokemon_types,
    )
    front_prompt = build_front_image_prompt(
        name,
        description,
        pokemon_types,
    )
    back_prompt = build_back_image_prompt(name, description)

    if PARALLEL_MODEL_CALLS:
        with ThreadPoolExecutor(max_workers=2) as executor:
            front_future = executor.submit(
                _timed,
                "front_image_generation_and_background_removal",
                generate_front_image,
                front_prompt,
            )
            audio_future = executor.submit(
                _timed,
                "audio_generation",
                generate_audio,
                description,
            )
            front_image = front_future.result()
            back_future = executor.submit(
                _timed,
                "back_image_and_background_removal",
                generate_back_image,
                front_image,
                back_prompt,
            )
            back_image = back_future.result()
            audio = audio_future.result()
    else:
        front_image = _timed(
            "front_image_generation_and_background_removal",
            generate_front_image,
            front_prompt,
        )
        back_image = _timed(
            "back_image_and_background_removal",
            generate_back_image,
            front_image,
            back_prompt,
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
    pokemon_data = get_pokemon_data(random_pokemon["url"])
    pokemon_types = get_pokemon_types(pokemon_data) or [body.type]
    name, description = generate_creature_text(
        pokemon_types,
    )
    print(f"Generated creature: {name} - {description}")
    prompt = build_front_image_prompt(
        name,
        description,
        pokemon_types,
    )
    image = generate_front_image(prompt)
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

def get_pokemon_data(pokemon_url: str) -> dict:
    pokemon_response = requests.get(pokemon_url, timeout=30)
    if pokemon_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch Pokemon data")
    return pokemon_response.json()

def get_pokemon_types(pokemon_data: dict) -> list[str]:
    return [
        entry["type"]["name"]
        for entry in pokemon_data.get("types", [])
        if entry.get("type", {}).get("name")
    ]

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

def generate_front_image(prompt: str) -> bytes:
    try:
        response = _timed(
            "image_front_service",
            requests.post,
            f"{IMAGE_SERVICE_URL}/generate/front",
            json={"prompt": prompt},
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

def generate_back_image(front_image: bytes, prompt: str) -> bytes:
    try:
        response = _timed(
            "image_back_service",
            requests.post,
            f"{IMAGE_SERVICE_URL}/generate/back",
            data={"prompt": prompt},
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

def generate_creature_text(
    pokemon_types: list[str],
) -> tuple[str, str]:
    prompt = build_name_description_prompt(pokemon_types)
    try:
        response = requests.post(
            f"{TEXT_SERVICE_URL}/generate",
            json={"prompt": prompt},
            timeout=600,
        )
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Text service is unavailable") from error
    _service_response(response, "Text")
    generated_text = response.json()
    return generated_text["name"], generated_text["description"]

def build_name_description_prompt( pokemon_types: list[str], 
) -> str: 
    types = ", ".join(pokemon_types) 
    name_style = random.choice(NAME_STYLES) 
    description_tone = random.choice(DESCRIPTION_TONES) 
    description_focus = random.choice(DESCRIPTION_FOCUSES) 
    return f"""Create an original fantasy creature inspired by these types: {types}. 
    Return exactly one JSON object with exactly two string fields: "name" "description" 
    NAME REQUIREMENTS: 
    - One word only. 
    - 3-12 letters. 
    - Easy to pronounce and remember. 
    - Original and distinctive. 
    - Do not use an existing famous character, creature, or franchise name. 
    - Do not use numbers, spaces, hyphens, apostrophes, or punctuation. 
    - The naming style should be {name_style}. 
    - The name should feel appropriate for a creature with these types: {types}. 
    DESCRIPTION REQUIREMENTS: 
    - Exactly 1 or 2 sentences. 
    - Write like an official fantasy creature encyclopedia entry. 
    - Describe the creature's visible appearance, personality, and behavior. 
    - Focus particularly on {description_focus}. 
    - Include at least one distinctive or memorable characteristic. 
    - Be specific and imaginative rather than generic. 
    - Use a {description_tone} tone. 
    - Do not mention Pokémon, Pokemon, AI, image generation, prompts, or these instructions. 
    OUTPUT REQUIREMENTS: 
    - Return valid JSON only. 
    - Do not use Markdown or code fences. 
    - Do not include explanations or commentary. 
    - Do not include any fields other than "name" and "description". 
    Example: {{"name":"ExampleName","description":"A small creature with..."}}"""

def build_front_image_prompt(
    name: str,
    description: str,
    pokemon_types: list[str],
) -> str:
    types = ", ".join(pokemon_types)

    return f"""Create an original fantasy creature named {name}.

    Creature types: {types}

    Creature description:
    {description}

    Use the creature description as the primary visual design reference. The creature's appearance, physical features, colors, proportions, and distinctive characteristics should clearly reflect the description and its type combination.

    Create a unique creature design rather than a generic animal or a simple representation of its types.

    RENDERING:
    - Full-body front-facing view.
    - The creature faces directly toward the camera.
    - Show the entire creature from the top of its head to the bottom of its feet.
    - One creature only.
    - Centered composition.
    - Clear, readable silhouette.
    - Pixel art video game sprite style.
    - Clean, crisp shapes and clearly defined features.
    - Plain solid white background.

    COMPOSITION:
    - Creature fully visible and entirely inside the image.
    - Leave a small amount of white space around the creature.
    - No cropping.
    - No environment or scenery.
    - No ground plane.

    DO NOT INCLUDE:
    - Shadows.
    - Reflections.
    - Text.
    - Logos.
    - Multiple creatures.
    - Additional objects.
    - Background elements.
    - UI elements."""

def build_back_image_prompt(name: str, description: str) -> str:
    return f"""Use the supplied front image as the identity reference for the same creature.

CAMERA AND ORIENTATION ARE CRITICAL:
The camera is positioned directly behind the creature. The creature is facing exactly 180 degrees away from the camera. Show a direct rear view of the creature's back, with the creature's central body axis aligned straight toward the background.

The creature must NOT face the camera.

- Full-body rear view.
- Back completely visible.
- Face completely hidden.
- No eyes, mouth, nose, or facial features visible.
- No head turned toward the camera.
- No looking over its shoulder.
- No side angle.
- No three-quarter angle.
- No front-facing pose.
- No profile view.
- Preserve the creature's identity, proportions, colors, markings, accessories, and distinctive physical characteristics from the reference image.
- Pixel-art video game sprite style.
- Centered composition.
- Plain solid white background.
- No ground plane.
- No shadows or reflections.
- No text or logos.
- No other objects or characters."""

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
