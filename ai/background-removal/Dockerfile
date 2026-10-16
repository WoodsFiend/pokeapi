# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ARG BACKGROUND_REMOVAL_MODEL=studioludens/birefnet-lite-512
ENV BACKGROUND_REMOVAL_MODEL=${BACKGROUND_REMOVAL_MODEL}
ENV BACKGROUND_REMOVAL_MODEL_PATH=/opt/models/onnx/model_fp16.onnx
RUN --mount=type=secret,id=hf_token,required=false \
    python -c 'import os; from pathlib import Path; from huggingface_hub import snapshot_download; token_file = Path("/run/secrets/hf_token"); token = (token_file.read_text().strip() or None) if token_file.exists() else None; snapshot_download(repo_id=os.environ["BACKGROUND_REMOVAL_MODEL"], allow_patterns=["onnx/model_fp16.onnx"], local_dir="/opt/models", token=token)'
ENV HF_HUB_OFFLINE=1

COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
