import ctypes
import fcntl
import hashlib
import os
import re
import shutil
import threading
import uuid
from contextlib import contextmanager
from importlib import import_module
from io import BytesIO
from time import perf_counter

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from PIL import Image
import numpy as np
import onnxruntime as ort


app = FastAPI(title="Pokemon Background Removal Service", version="1.0.0")
background_removal_model = None
inference_lock = threading.Lock()


@app.on_event("startup")
def startup():
    global background_removal_model
    startup_started = perf_counter()
    model_path = os.getenv(
        "BACKGROUND_REMOVAL_MODEL_PATH",
        "/opt/models/onnx/model_fp16.onnx",
    )
    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Background removal model is missing from the image: {model_path}"
        )

    # The CUDA and TensorRT wheels place shared libraries in site-packages,
    # which are not on the system loader's default search path in python:slim.
    try:
        ort.preload_dlls(directory="")
    except Exception as error:
        print(f"GPU library preload failed; trying provider fallbacks: {error!r}")

    trt_cache_root = os.getenv(
        "TRT_CACHE_DIR",
        "/var/cache/onnxruntime/trt",
    )

    available_providers = set(ort.get_available_providers())
    tensorrt_available = "TensorrtExecutionProvider" in available_providers
    tensorrt_version = None
    if tensorrt_available:
        try:
            import_module("tensorrt_libs")
            tensorrt_version = import_module("tensorrt").__version__
        except Exception as error:
            tensorrt_available = False
            print(f"TensorRT libraries could not be loaded: {error!r}")

    session_started = perf_counter()
    provider_mode = "TensorRT cache"
    if tensorrt_available:
        trt_cache_dir = get_trt_cache_dir(
            trt_cache_root,
            model_path,
            tensorrt_version,
        )
        with cache_initialization_lock(trt_cache_dir):
            os.makedirs(trt_cache_dir, exist_ok=True)
            try:
                background_removal_model = create_inference_session(
                    model_path,
                    trt_cache_dir=trt_cache_dir,
                    use_tensorrt=True,
                )
            except Exception as cache_error:
                print(
                    "TensorRT cache initialization failed; clearing the cache "
                    f"and rebuilding it: {cache_error!r}"
                )
                reset_cache_dir(trt_cache_dir)
                try:
                    background_removal_model = create_inference_session(
                        model_path,
                        trt_cache_dir=trt_cache_dir,
                        use_tensorrt=True,
                    )
                    provider_mode = "TensorRT rebuilt cache"
                except Exception as rebuild_error:
                    print(
                        "TensorRT engine rebuild failed; retrying without TensorRT: "
                        f"{rebuild_error!r}"
                    )
                    background_removal_model, provider_mode = create_fallback_session(
                        model_path
                    )
    else:
        print("TensorRT is unavailable; using CUDA/CPU providers.")
        background_removal_model, provider_mode = create_fallback_session(model_path)

    print(
        "Background removal model ready: "
        f"session_init_seconds={perf_counter() - session_started:.2f}, "
        f"startup_seconds={perf_counter() - startup_started:.2f}, "
        f"provider_mode={provider_mode}, "
        f"trt_cache_dir={trt_cache_dir if tensorrt_available else 'disabled'}, "
        f"providers={background_removal_model.get_providers()}"
    )


def get_trt_cache_dir(cache_root, model_path, tensorrt_version):
    gpu_identity = get_gpu_identity()
    model_hash = hashlib.sha256()
    with open(model_path, "rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            model_hash.update(chunk)

    version_parts = (
        "cache-v1",
        f"ort-{safe_cache_component(ort.__version__)}",
        f"trt-{safe_cache_component(tensorrt_version)}",
        "fp16",
        f"model-{model_hash.hexdigest()}",
    )
    return os.path.join(cache_root, gpu_identity, *version_parts)


def get_gpu_identity():
    try:
        cuda = ctypes.CDLL("libcuda.so.1")
        device = ctypes.c_int()
        major = ctypes.c_int()
        minor = ctypes.c_int()
        driver_version = ctypes.c_int()
        name = ctypes.create_string_buffer(256)

        cuda.cuInit.argtypes = [ctypes.c_uint]
        cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        cuda.cuDeviceGetName.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        cuda.cuDeviceComputeCapability.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
        ]
        cuda.cuDriverGetVersion.argtypes = [ctypes.POINTER(ctypes.c_int)]

        if cuda.cuInit(0) != 0:
            raise RuntimeError("cuInit failed")
        if cuda.cuDeviceGet(ctypes.byref(device), 0) != 0:
            raise RuntimeError("cuDeviceGet failed")
        if cuda.cuDeviceGetName(name, len(name), device) != 0:
            raise RuntimeError("cuDeviceGetName failed")
        if cuda.cuDeviceComputeCapability(
            ctypes.byref(major), ctypes.byref(minor), device
        ) != 0:
            raise RuntimeError("cuDeviceComputeCapability failed")
        if cuda.cuDriverGetVersion(ctypes.byref(driver_version)) != 0:
            raise RuntimeError("cuDriverGetVersion failed")

        gpu_name = name.value.decode("utf-8", errors="replace")
        return (
            f"{safe_cache_component(gpu_name)}-sm{major.value}{minor.value}"
            f"-cuda{driver_version.value}"
        )
    except Exception as error:
        # Never let unknown GPU hardware share a cache with another worker.
        fallback_identity = f"unknown-gpu-{uuid.uuid4().hex}"
        print(
            "Could not identify the GPU for the TensorRT cache; using a "
            f"worker-specific cache directory: {error!r}"
        )
        return fallback_identity


def safe_cache_component(value):
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value)).strip("-.") or "unknown"


@contextmanager
def cache_initialization_lock(cache_dir):
    os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
    with open(f"{cache_dir}.lock", "a+b") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def reset_cache_dir(cache_dir):
    if os.path.isdir(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)


def create_fallback_session(model_path):
    try:
        return (
            create_inference_session(model_path, use_tensorrt=False),
            "CUDA/CPU fallback",
        )
    except Exception as cuda_error:
        print(
            "CUDA provider initialization failed; retrying on CPU: "
            f"{cuda_error!r}"
        )
        return (
            create_inference_session(
                model_path,
                use_tensorrt=False,
                use_cuda=False,
            ),
            "CPU fallback",
        )


def create_inference_session(
    model_path,
    trt_cache_dir=None,
    use_tensorrt=True,
    use_cuda=True,
):
    opts = ort.SessionOptions()
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    opts.enable_cpu_mem_arena = True

    providers = []
    if use_tensorrt:
        providers.append((
            "TensorrtExecutionProvider",
            {
                "device_id": 0,
                "trt_fp16_enable": True,
                "trt_engine_cache_enable": True,
                "trt_engine_cache_path": trt_cache_dir,
                "trt_timing_cache_enable": True,
                "trt_timing_cache_path": trt_cache_dir,
            },
        ))
    if use_cuda:
        providers.append((
            "CUDAExecutionProvider",
            {
                "device_id": 0,
                "arena_extend_strategy": "kNextPowerOfTwo",
                "cudnn_conv_algo_search": "EXHAUSTIVE",
                "do_copy_in_default_stream": True,
            },
        ))
    providers.append("CPUExecutionProvider")

    return ort.InferenceSession(
        model_path,
        session_options=opts,
        providers=providers,
    )


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": background_removal_model is not None}


@app.post("/remove-background")
def remove_background(image: UploadFile = File(...)):
    source_image = Image.open(BytesIO(image.file.read())).convert("RGBA")
    with inference_lock:
        result = apply_background_mask(source_image)

    buffer = BytesIO()
    result.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")


def apply_background_mask(image: Image.Image) -> Image.Image:
    original_size = image.size
    input_image = image.convert("RGB").resize(
        (512, 512),
        Image.Resampling.BILINEAR,
    )
    image_array = np.asarray(input_image, dtype=np.float32) / 255.0
    image_array = np.transpose(image_array, (2, 0, 1))
    image_array = np.expand_dims(image_array, axis=0)

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 3, 1, 1)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 3, 1, 1)
    image_array = (image_array - mean) / std

    input_name = background_removal_model.get_inputs()[0].name
    outputs = background_removal_model.run(None, {input_name: image_array})
    mask = np.squeeze(outputs[0])
    mask = 1.0 / (1.0 + np.exp(-mask))
    mask = (np.clip(mask, 0.0, 1.0) * 255).astype(np.uint8)
    mask_image = Image.fromarray(mask, mode="L").resize(
        original_size,
        Image.Resampling.BILINEAR,
    )

    result = image.convert("RGBA")
    result.putalpha(mask_image)
    return result
