# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CC=gcc
ENV CXX=g++

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ARG TEXT_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
ENV TEXT_MODEL=${TEXT_MODEL}
ENV HF_HOME=/opt/huggingface
ENV HF_HUB_CACHE=/opt/huggingface/hub
RUN --mount=type=secret,id=hf_token,required=false \
    python -c 'import os; from pathlib import Path; from huggingface_hub import snapshot_download; token_file = Path("/run/secrets/hf_token"); token = (token_file.read_text().strip() or None) if token_file.exists() else None; snapshot_download(repo_id=os.environ["TEXT_MODEL"], cache_dir=os.environ["HF_HUB_CACHE"], token=token)'
ENV HF_HUB_OFFLINE=1

COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
