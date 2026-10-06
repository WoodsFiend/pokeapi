from io import BytesIO
import threading

from fastapi import FastAPI
from fastapi.responses import Response
import torch
import torchaudio
from pydantic import BaseModel
from stable_audio_3 import StableAudioModel


app = FastAPI(title="Pokemon Audio Model Service", version="1.0.0")
audio_model = None
inference_lock = threading.Lock()


class GenerateAudioRequest(BaseModel):
    description: str


@app.on_event("startup")
def startup():
    global audio_model
    audio_model = StableAudioModel.from_pretrained("small-sfx")
    print("Audio model ready")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": audio_model is not None}


@app.post("/generate")
def generate_audio(request: GenerateAudioRequest):
    prompt = (
        "Create a completely original creature cry sound effect inspired by "
        f"the description: {request.description}. "
        "Make the sound effect suitable for a video game."
    )

    with inference_lock, torch.inference_mode():
        audio = audio_model.generate(prompt=prompt, duration=1)
    if audio.dim() == 3:
        audio = audio.squeeze(0)
    audio = audio.detach().cpu()

    buffer = BytesIO()
    torchaudio.save(buffer, audio, sample_rate=44100, format="wav")
    return Response(content=buffer.getvalue(), media_type="audio/wav")
