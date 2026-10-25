"""Inference runtime module.

This module owns model lifecycle (load once at startup) and exposes helpers
consumed by route handlers in `app.py`.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from fastapi import HTTPException
from PIL import Image
from torchvision.models import resnet18

from label_normalization import (
    CANONICAL_AUTOML_LABELS,
    normalize_automl_label,
    normalize_automl_labels,
)
from automl_contract import prepare_image, read_contract, embedded_labels
from config import SETTINGS
from image_preprocessing import resnet_transform
from prediction_routing import optional_prediction
from uploads import load_validated_image as load_validated_image

VERTEX_AI_AVAILABLE = False
predict_with_automl = None
if SETTINGS.enable_vertex:
    try:
        from vertex_ai_integration import predict_with_automl

        VERTEX_AI_AVAILABLE = bool(SETTINGS.project_id and SETTINGS.endpoint_id)
    except ImportError:
        pass

logger = logging.getLogger("industrial_defect_api")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = str(SETTINGS.custom_model)
AUTOML_TFLITE_PATH = str(SETTINGS.automl_model)
AUTOML_LABELS_PATH = str(SETTINGS.automl_labels)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CLASS_NAMES = ["Cr", "In", "Pa", "PS", "RS", "Sc"]
IMG_SIZE = 224

CONF_THRESHOLD_NO_DEFECT = 0.55
TOP_K_DEFAULT = 3
MAX_BATCH_FILES = 50
MAX_UPLOAD_BYTES = SETTINGS.max_upload_bytes
AUTOML_UNAVAILABLE_DETAIL = (
    "Local AutoML TFLite is unavailable. Install requirements-local.txt and provide the exported model. "
    "Cloud fallback requires explicit ENABLE_VERTEX_AI=true and configured Vertex AI credentials."
)
DEFAULT_AUTOML_LABELS = CANONICAL_AUTOML_LABELS.copy()
model = None
preprocess = None


def _load_custom_model():
    global model, preprocess, CLASS_NAMES, IMG_SIZE
    if model is not None:
        return model
    if not Path(MODEL_PATH).exists():
        raise HTTPException(status_code=503, detail="Custom model weights are not available")
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state = checkpoint["model_state_dict"]
        CLASS_NAMES = checkpoint.get("classes", CLASS_NAMES)
        IMG_SIZE = int(checkpoint.get("image_size", IMG_SIZE))
    else:
        state = checkpoint
    loaded = resnet18(weights=None)
    loaded.fc = torch.nn.Linear(loaded.fc.in_features, len(CLASS_NAMES))
    loaded.load_state_dict(state, strict=True)
    model = loaded.to(DEVICE).eval()
    preprocess = resnet_transform(IMG_SIZE)
    logger.info("Custom model loaded device=%s classes=%s", DEVICE, CLASS_NAMES)
    return model


AUTOML_TFLITE_AVAILABLE = False
AUTOML_LABELS: List[str] = []
AUTOML_INPUT_DETAILS = None
AUTOML_OUTPUT_DETAILS = None
AUTOML_INTERPRETER = None


def _load_automl_tflite() -> None:
    global AUTOML_TFLITE_AVAILABLE
    global AUTOML_LABELS
    global AUTOML_INPUT_DETAILS
    global AUTOML_OUTPUT_DETAILS
    global AUTOML_INTERPRETER

    model_path = Path(AUTOML_TFLITE_PATH)
    if not model_path.exists():
        return
    try:
        from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter
    except ImportError:
        try:
            import tensorflow as tf

            TFLiteInterpreter = tf.lite.Interpreter
        except ImportError:
            logger.info("Local TFLite runtime is not installed")
            return

    labels_path = Path(AUTOML_LABELS_PATH)
    if labels_path.exists():
        AUTOML_LABELS = normalize_automl_labels(
            [
                line.strip()
                for line in labels_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        )
    else:
        # Vertex exports may not always include labels.txt; use project default labels.
        AUTOML_LABELS = DEFAULT_AUTOML_LABELS.copy()
        logger.warning("AutoML labels file not found at %s. Using defaults.", labels_path)

    AUTOML_INTERPRETER = TFLiteInterpreter(model_path=str(model_path))
    AUTOML_INTERPRETER.allocate_tensors()
    AUTOML_INPUT_DETAILS = AUTOML_INTERPRETER.get_input_details()
    AUTOML_INPUT_DETAILS[0]["normalization_contract"] = read_contract(str(model_path.resolve()))
    exported_labels = normalize_automl_labels(embedded_labels(model_path))
    if AUTOML_LABELS != exported_labels:
        raise ValueError("AutoML labels.txt does not match embedded output label order")
    AUTOML_OUTPUT_DETAILS = AUTOML_INTERPRETER.get_output_details()
    AUTOML_TFLITE_AVAILABLE = True
    logger.info("AutoML TFLite loaded. Labels: %s", AUTOML_LABELS)


_load_automl_tflite()


def _top_k(probs: np.ndarray, k: int) -> List[Dict[str, float]]:
    k = max(1, min(int(k), len(CLASS_NAMES)))
    idxs = np.argsort(probs)[::-1][:k]
    return [{"class_name": CLASS_NAMES[i], "confidence": float(probs[i])} for i in idxs]


def _predict_probs(img: Image.Image) -> np.ndarray:
    loaded = _load_custom_model()
    x: torch.Tensor = preprocess(img.convert("RGB")).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = loaded(x)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]
    return probs


def _softmax_np(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    exp = np.exp(x)
    return exp / np.sum(exp)


def _to_probabilities(scores: np.ndarray) -> np.ndarray:
    scores = scores.astype(np.float32)
    if np.all(scores >= 0.0) and np.all(scores <= 1.0):
        total = float(np.sum(scores))
        if 0.98 <= total <= 1.02:
            return scores / max(total, 1e-6)
    return _softmax_np(scores)


def _build_custom_prediction_payload(probs: np.ndarray, top_k: int) -> Dict:
    top_idx = int(np.argmax(probs))
    top_prob = float(probs[top_idx])
    top_class = CLASS_NAMES[top_idx]
    predicted_class = "No defect / Unknown" if top_prob < CONF_THRESHOLD_NO_DEFECT else top_class
    return {
        "predicted_class": predicted_class,
        "confidence": top_prob,
        "all_probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))},
        "top_k": _top_k(probs, top_k),
        "raw_top_class": top_class,
        "threshold": CONF_THRESHOLD_NO_DEFECT,
    }


def _automl_tflite_predict(img: Image.Image) -> Dict:
    if not AUTOML_TFLITE_AVAILABLE:
        raise RuntimeError("AutoML TFLite model not available")

    start = time.time()
    input_details = AUTOML_INPUT_DETAILS[0]
    output_details = AUTOML_OUTPUT_DETAILS[0]
    x = prepare_image(img, input_details, input_details["normalization_contract"])
    AUTOML_INTERPRETER.set_tensor(input_details["index"], x)
    AUTOML_INTERPRETER.invoke()
    output = AUTOML_INTERPRETER.get_tensor(output_details["index"])

    output_dtype = output_details["dtype"]
    if output_dtype == np.float32:
        scores = output[0].astype(np.float32)
    else:
        scale, zero = output_details.get("quantization", (0.0, 0))
        if scale and scale > 0:
            scores = (output[0].astype(np.float32) - zero) * scale
        else:
            scores = output[0].astype(np.float32)

    probs = _to_probabilities(scores)
    top_idx = int(np.argmax(probs))
    top_class = normalize_automl_label(
        AUTOML_LABELS[top_idx] if top_idx < len(AUTOML_LABELS) else f"index_{top_idx}"
    )

    labeled_probabilities: Dict[str, float] = {}
    for i in range(len(probs)):
        label = normalize_automl_label(AUTOML_LABELS[i] if i < len(AUTOML_LABELS) else f"index_{i}")
        labeled_probabilities[label] = labeled_probabilities.get(label, 0.0) + float(probs[i])

    return {
        "predicted_class": top_class,
        "confidence": float(probs[top_idx]),
        "all_probabilities": labeled_probabilities,
        "top_k": [
            {
                "class_name": normalize_automl_label(AUTOML_LABELS[i])
                if i < len(AUTOML_LABELS)
                else f"index_{i}",
                "confidence": float(probs[i]),
            }
            for i in np.argsort(probs)[::-1][:TOP_K_DEFAULT]
        ],
        "raw_top_class": top_class,
        "threshold": 0.0,
        "inference_time_ms": round((time.time() - start) * 1000, 2),
        "model_type": "automl",
    }


def _predict_automl_required(img: Image.Image) -> Dict:
    if AUTOML_TFLITE_AVAILABLE:
        return _automl_tflite_predict(img)
    if VERTEX_AI_AVAILABLE:
        return predict_with_automl(img)
    raise HTTPException(status_code=503, detail=AUTOML_UNAVAILABLE_DETAIL)


def _predict_automl_optional(
    img: Image.Image, context: str
) -> Tuple[Optional[Dict], Optional[str]]:
    return optional_prediction(
        img,
        _automl_tflite_predict if AUTOML_TFLITE_AVAILABLE else None,
        predict_with_automl if VERTEX_AI_AVAILABLE else None,
        context,
    )


def _predict_both_models(img: Image.Image, context: str) -> Dict:
    result = {"custom": infer(img), "automl": None, "model_type": "both"}
    automl_result, automl_error = _predict_automl_optional(img, context)
    result["automl"] = automl_result
    if automl_error is not None:
        result["automl_error"] = automl_error
    return result


def infer(img: Image.Image) -> Dict:
    start = time.time()
    probs = _predict_probs(img)
    payload = _build_custom_prediction_payload(probs, TOP_K_DEFAULT)
    payload["inference_time_ms"] = round((time.time() - start) * 1000, 2)
    payload["model_type"] = "custom"
    logger.info(
        "Prediction completed: class=%s confidence=%.4f",
        payload["predicted_class"],
        payload["confidence"],
    )
    return payload


def predict_single(img: Image.Image, model_type: Literal["custom", "automl", "both"]) -> Dict:
    if model_type == "custom":
        return infer(img)
    if model_type == "automl":
        return _predict_automl_required(img)
    return _predict_both_models(img, "/predict both mode")


def predict_batch_single(img: Image.Image, model_type: Literal["custom", "automl", "both"]) -> Dict:
    if model_type == "custom":
        return infer(img)
    if model_type == "automl":
        if AUTOML_TFLITE_AVAILABLE:
            return _automl_tflite_predict(img)
        if VERTEX_AI_AVAILABLE:
            return predict_with_automl(img)
        raise RuntimeError(AUTOML_UNAVAILABLE_DETAIL)

    custom_result = infer(img)
    automl_result, automl_error = _predict_automl_optional(img, "batch mode")
    return {"custom": custom_result, "automl": automl_result, "automl_error": automl_error}


def predict_debug_payload(img: Image.Image, top_k: int) -> Dict:
    probs = _predict_probs(img)
    payload = _build_custom_prediction_payload(probs, top_k)
    payload["classes"] = CLASS_NAMES
    payload["image_size"] = IMG_SIZE
    return payload


def health_payload() -> Dict:
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "device": DEVICE,
        "classes": CLASS_NAMES,
        "automl_tflite_loaded": AUTOML_TFLITE_AVAILABLE,
        "automl_labels": AUTOML_LABELS,
    }


def test_model_payload() -> Dict:
    try:
        loaded = _load_custom_model()
        test_input = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
        with torch.no_grad():
            output = loaded(test_input)
            probs = F.softmax(output, dim=1).cpu().numpy()[0]
        return {
            "model_loaded": True,
            "device": DEVICE,
            "classes": CLASS_NAMES,
            "num_classes": len(CLASS_NAMES),
            "image_size": IMG_SIZE,
            "model_path": MODEL_PATH,
            "test_output_shape": list(output.shape),
            "test_probabilities": {
                CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))
            },
        }
    except Exception as exc:
        return {"model_loaded": False, "error": str(exc)}


def model_info_payload() -> Dict:
    _load_custom_model()
    model_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    return {
        "model_path": Path(MODEL_PATH).name,
        "model_size_mb": round(model_size, 2),
        "device": DEVICE,
        "image_size": IMG_SIZE,
        "classes": CLASS_NAMES,
        "num_classes": len(CLASS_NAMES),
        "confidence_threshold": CONF_THRESHOLD_NO_DEFECT,
    }
