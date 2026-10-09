from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import logging
import os
from pathlib import Path
import types
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import requests

from random_choices import (
    get_description_focus,
    get_description_tone,
    get_name_style,
    get_pokemon_type_body_plan,
    get_pokemon_type_colors,
    get_random_pokemon,
)


app = FastAPI(
    title="Pokemon AI Service",
    version="1.0.0",
)
logger = logging.getLogger("uvicorn.error")

IMAGE_SERVICE_URL = os.getenv("IMAGE_SERVICE_URL", "http://image-model:8000")
BACKGROUND_SERVICE_URL = os.getenv(
    "BACKGROUND_SERVICE_URL",
    "http://background-removal-model:8000",
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
    pokemon_data = _timed(
        "pokemon_data_fetch",
        get_pokemon_data,
        random_pokemon["url"],
    )
    pokemon_types = get_pokemon_types(pokemon_data) or [body.type]
    body_plan = get_pokemon_type_body_plan(pokemon_types)

    name, description = _timed(
        "text_generation",
        generate_creature_text,
        pokemon_types,
        body_plan,
    )
    front_prompt = build_front_image_prompt(
        name,
        description,
        pokemon_types,
        body_plan,
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
    body_plan = get_pokemon_type_body_plan(pokemon_types)
    name, description = generate_creature_text(
        pokemon_types,
        body_plan,
    )
    print(f"Generated creature: {name} - {description}")
    prompt = build_front_image_prompt(
        name,
        description,
        pokemon_types,
        body_plan,
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
    return get_random_pokemon(pokemon_entries)["pokemon"]

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
    body_plan: str,
) -> tuple[str, str]:
    prompt = build_name_description_prompt(pokemon_types, body_plan)
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
    name = generated_text["name"].strip()
    description = generated_text["description"].strip()
    return name, description

def build_name_description_prompt(
    pokemon_types: list[str],
    body_plan: str,
) -> str: 
    types = ", ".join(pokemon_types) 
    name_style = get_name_style()
    description_tone = get_description_tone()
    description_focus = get_description_focus()
    return f"""Create an original fantasy creature inspired by these types: {types}. 
    Return exactly one JSON object with exactly two string fields: "name" "description" 
    LANGUAGE AND CHARACTERS:
    - Write both fields in English using ASCII characters only.
    - Do not use Chinese, Japanese, Korean, or any other non-ASCII characters.
    - Use standard English letters and basic ASCII punctuation; do not use accented letters or emoji.
    NAME REQUIREMENTS: 
    - One word only.
    - Only the first letter of the name is capitalized.
    - STRICT RULE: the type labels are design context only and must not appear in the name.
    - Forbidden type labels for this creature: {types}.
    - This restriction is case-insensitive: "steel", "Steel", and "STEEL" are equally forbidden.
    - The name must not equal, start with, end with, or contain any forbidden label as a recognizable word or word fragment.
    - Do not use a spelling variant, plural, abbreviation, prefix, suffix, compound, or portmanteau based on a forbidden label.
    - Invent the name from unrelated sounds; base its mood on the creature's personality and appearance, not on its type labels.
    - 3-12 letters. 
    - Easy to pronounce and remember. 
    - Original and distinctive. 
    - Do not use an existing famous character, creature, or franchise name. 
    - Do not use numbers, spaces, hyphens, apostrophes, or punctuation. 
    - The naming style should be {name_style}. 
    CREATURE ANATOMY:
    - Use this assigned body plan: {body_plan}
    - Describe visible anatomy that clearly matches this body plan.
    - Do not replace it with a generic upright humanoid design.
    - Creatures without the Bug type must not have six or eight legs.
    DESCRIPTION REQUIREMENTS:
    - Do not include the body plan in the description.
    - Exactly 2 or 3 sentences.
    - Between 20 and 50 words.
    - Write like an official fantasy creature encyclopedia entry. 
    - Describe the creature's visible appearance, personality, and behavior. 
    - Focus particularly on {description_focus}. 
    - Include at least one distinctive or memorable characteristic. 
    - Be specific and imaginative rather than generic. 
    - Use a {description_tone} tone. 
    - Do not mention Pokémon, Pokemon, AI, image generation, prompts, or these instructions. 
    OUTPUT REQUIREMENTS: 
    - Return valid JSON only. 
    - Before returning, check the "name" against every forbidden type label and its recognizable variants. If any appear, invent a different name and check again.
    - This type-name restriction applies only to the "name" field; the description may describe type-inspired features.
    - Do not use Markdown or code fences. 
    - Do not include explanations or commentary. 
    - Do not include any fields other than "name" and "description". 
    Example: {{"name":"ExampleName","description":"A small creature with..."}}"""

def build_front_image_prompt(
    name: str,
    description: str,
    pokemon_types: list[str],
    body_plan: str,
) -> str:
    types = ", ".join(pokemon_types)
    type_palettes = [
        (
            pokemon_type,
            get_pokemon_type_colors(pokemon_type),
        )
        for pokemon_type in pokemon_types
    ]

    if type_palettes:
        primary_type, primary_colors = type_palettes[0]
        color_guidance = (
            f"- Primary colors: use the {primary_type} palette "
            f"({', '.join(primary_colors)}) as the creature's dominant colors."
        )
        if len(type_palettes) > 1:
            secondary_palettes = "; ".join(
                f"{pokemon_type}: {', '.join(colors)}"
                for pokemon_type, colors in type_palettes[1:]
            )
            color_guidance += (
                "\n- Secondary colors: use these palettes as smaller accents, "
                f"keeping the primary palette dominant: {secondary_palettes}."
            )
    else:
        color_guidance = "- Use a balanced, cohesive natural color palette."

    return f"""Create an original fantasy creature named {name}.

    Creature types: {types}

    Creature description:
    {description}

    TYPE-BASED COLOR PALETTE:
    {color_guidance}

    Use the creature description as the primary visual design reference. The creature's appearance, physical features, colors, proportions, and distinctive characteristics should clearly reflect the description and its type combination.

    ANATOMY AND SILHOUETTE (follow this assigned body plan):
    {body_plan}
    Make this body plan immediately recognizable from the silhouette. Keep the body axis, posture, limb count, and locomotion appropriate to it. Do not default to a human-like torso, arms, hands, or upright stance unless the assigned body plan calls for them.
    Six- or eight-legged designs are allowed only when Bug is one of the creature's types.

    Create a unique creature design rather than a generic animal or a simple representation of its types.

    RENDERING:
    - Show the entire creature from its natural front, angled ten degrees to the left side of the camera.
    - Preserve the assigned body's natural horizontal, coiled, radial, or hovering orientation; do not force it upright.
    - Keep every limb, tail, fin, wing, and tendril fully visible.
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
