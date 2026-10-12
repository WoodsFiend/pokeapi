import os
from pathlib import Path
import re
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse


app = FastAPI(title="Pokemon Asset Storage", version="1.0.0")

SPRITE_OUTPUT_DIR = Path(
    os.getenv("SPRITE_OUTPUT_DIR", "/data/sprites/")
)
CRY_OUTPUT_DIR = Path(
    os.getenv("CRY_OUTPUT_DIR", "/data/cries/")
)
STORAGE_PUBLIC_BASE_URL = os.getenv(
    "STORAGE_PUBLIC_BASE_URL",
    "http://localhost:8002",
).rstrip("/")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/assets/{asset_id}/{asset_name}")
def get_asset(asset_id: str, asset_name: str):
    if not re.fullmatch(r"[0-9a-f]{32}", asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")

    asset_paths = {
        "front.png": (SPRITE_OUTPUT_DIR / "front" / f"{asset_id}.png", "image/png"),
        "back.png": (
            SPRITE_OUTPUT_DIR / "back" / f"{asset_id}.png",
            "image/png",
        ),
        "cry.wav": (CRY_OUTPUT_DIR / f"{asset_id}.wav", "audio/wav"),
    }
    asset = asset_paths.get(asset_name)
    if asset is None or not asset[0].is_file():
        raise HTTPException(status_code=404, detail="Asset not found")

    return FileResponse(
        asset[0],
        media_type=asset[1],
        content_disposition_type="inline",
    )


@app.post("/assets")
async def store_assets(
    front_image: UploadFile = File(...),
    back_image: UploadFile = File(...),
    audio: UploadFile = File(...),
):
    asset_id = uuid4().hex
    front_output_dir = SPRITE_OUTPUT_DIR / "front"
    back_output_dir = SPRITE_OUTPUT_DIR / "back"

    SPRITE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    front_output_dir.mkdir(parents=True, exist_ok=True)
    back_output_dir.mkdir(parents=True, exist_ok=True)
    CRY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (front_output_dir / f"{asset_id}.png").write_bytes(await front_image.read())
    (back_output_dir / f"{asset_id}.png").write_bytes(await back_image.read())
    (CRY_OUTPUT_DIR / f"{asset_id}.wav").write_bytes(await audio.read())

    return {
        "front_default": f"{STORAGE_PUBLIC_BASE_URL}/assets/{asset_id}/front.png",
        "back_default": f"{STORAGE_PUBLIC_BASE_URL}/assets/{asset_id}/back.png",
        "latest": f"{STORAGE_PUBLIC_BASE_URL}/assets/{asset_id}/cry.wav",
    }
