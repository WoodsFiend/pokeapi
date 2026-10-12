import os

from fastapi import HTTPException
import requests


STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://storage:8000")


def store_generated_assets(
    front_image: bytes,
    back_image: bytes,
    audio: bytes,
) -> dict[str, str]:
    files = {
        "front_image": ("front.png", front_image, "image/png"),
        "back_image": ("back.png", back_image, "image/png"),
        "audio": ("cry.wav", audio, "audio/wav"),
    }

    try:
        response = requests.post(
            f"{STORAGE_SERVICE_URL.rstrip('/')}/assets",
            files=files,
            timeout=60,
        )
        response.raise_for_status()
        asset_urls = response.json()
    except (requests.RequestException, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail="Storage service failed to save generated assets",
        ) from error

    required_urls = ("front_default", "back_default", "latest")
    if not isinstance(asset_urls, dict) or any(
        not isinstance(asset_urls.get(key), str) for key in required_urls
    ):
        raise HTTPException(
            status_code=502,
            detail="Storage service returned invalid asset URLs",
        )

    return asset_urls
