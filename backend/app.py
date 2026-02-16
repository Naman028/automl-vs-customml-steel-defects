import io
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn.functional as F
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18

# Vertex AI integration (optional, only if configured)
try:
    from vertex_ai_integration import predict_with_automl
    VERTEX_AI_AVAILABLE = os.getenv("GCP_PROJECT_ID") and os.getenv("VERTEX_AI_AUTOML_ENDPOINT_ID")
except ImportError:
    VERTEX_AI_AVAILABLE = False
    predict_with_automl = None

from assistant.assistant_service import answer_question

# AutoML TFLite (local) integration (optional)
try:
    from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter
except Exception:
    try:
        import tensorflow as tf
        TFLiteInterpreter = tf.lite.Interpreter
    except Exception:
        TFLiteInterpreter = None


# ImageFolder alphabetical order used by training
CLASS_NAMES = ["Cr", "In", "Pa", "PS", "RS", "Sc"]

IMG_SIZE = 224
_BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = os.getenv(
    "CUSTOM_MODEL_PATH",
    str(_BASE_DIR / "models" / "CustomML" / "outputs" / "best.pt"),
)

AUTOML_TFLITE_PATH = os.getenv(
    "AUTOML_TFLITE_PATH",
    str(_BASE_DIR / "models" / "AutoML" / "AutoML model.tflite"),
)
AUTOML_LABELS_PATH = os.getenv(
    "AUTOML_LABELS_PATH",
    str(_BASE_DIR / "models" / "AutoML" / "labels.txt"),
)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Demo-only abstention. Not a real "no defect" class.
CONF_THRESHOLD_NO_DEFECT = 0.55
TOP_K_DEFAULT = 3

app = FastAPI(title="Industrial Defect API", version="1.0")

# CORS configuration - allow frontend origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build same architecture used during training (ResNet18 classifier)
print(f"Loading model from: {MODEL_PATH}")
print(f"Using device: {DEVICE}")
print(f"Initial classes: {CLASS_NAMES}")

model = resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))

try:
    ckpt = torch.load(MODEL_PATH, map_location=DEVICE)
    
    # Unwrap training checkpoint
    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
        # Use saved metadata if present
        if "classes" in ckpt and isinstance(ckpt["classes"], list):
            CLASS_NAMES = ckpt["classes"]
            model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
            print(f"Loaded classes from checkpoint: {CLASS_NAMES}")
        if "image_size" in ckpt:
            IMG_SIZE = int(ckpt["image_size"])
            print(f"Loaded image size from checkpoint: {IMG_SIZE}")
    else:
        state = ckpt
    
    model.load_state_dict(state, strict=True)
    model = model.to(DEVICE).eval()
    print(f"OK: Model loaded successfully. Classes: {CLASS_NAMES}, Image size: {IMG_SIZE}")
except Exception as e:
    print(f"ERROR loading model: {e}")
    raise RuntimeError(f"Failed to load model: {e}")

AUTOML_TFLITE_AVAILABLE = False
AUTOML_LABELS: List[str] = []
AUTOML_INPUT_DETAILS = None
AUTOML_OUTPUT_DETAILS = None
AUTOML_INTERPRETER = None

def _load_automl_tflite():
    global AUTOML_TFLITE_AVAILABLE, AUTOML_LABELS, AUTOML_INPUT_DETAILS, AUTOML_OUTPUT_DETAILS, AUTOML_INTERPRETER
    if TFLiteInterpreter is None:
        return
    model_path = Path(AUTOML_TFLITE_PATH)
    if not model_path.exists():
        return
    labels_path = Path(AUTOML_LABELS_PATH)
    if labels_path.exists():
        AUTOML_LABELS = [
            line.strip()
            for line in labels_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    AUTOML_INTERPRETER = TFLiteInterpreter(model_path=str(model_path))
    AUTOML_INTERPRETER.allocate_tensors()
    AUTOML_INPUT_DETAILS = AUTOML_INTERPRETER.get_input_details()
    AUTOML_OUTPUT_DETAILS = AUTOML_INTERPRETER.get_output_details()
    AUTOML_TFLITE_AVAILABLE = True
    print(f"OK: AutoML TFLite loaded. Labels: {AUTOML_LABELS}")

_load_automl_tflite()

preprocess = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "model_loaded": True,
        "device": DEVICE,
        "classes": CLASS_NAMES,
        "automl_tflite_loaded": AUTOML_TFLITE_AVAILABLE,
        "automl_labels": AUTOML_LABELS,
    }

@app.get("/test-model")
def test_model():
    """Test endpoint to verify model is loaded correctly"""
    try:
        # Create a dummy tensor to test model forward pass
        test_input = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
        with torch.no_grad():
            output = model(test_input)
            probs = F.softmax(output, dim=1).cpu().numpy()[0]
        
        return {
            "model_loaded": True,
            "device": DEVICE,
            "classes": CLASS_NAMES,
            "num_classes": len(CLASS_NAMES),
            "image_size": IMG_SIZE,
            "model_path": MODEL_PATH,
            "test_output_shape": list(output.shape),
            "test_probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
        }
    except Exception as e:
        return {"model_loaded": False, "error": str(e)}

def _predict_probs(img: Image.Image) -> np.ndarray:
    """Return softmax probabilities for a single image."""
    x: torch.Tensor = preprocess(img.convert("RGB")).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = model(x)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]
    return probs

def _top_k(probs: np.ndarray, k: int) -> List[Dict[str, float]]:
    k = max(1, min(int(k), len(CLASS_NAMES)))
    idxs = np.argsort(probs)[::-1][:k]
    return [
        {"class_name": CLASS_NAMES[i], "confidence": float(probs[i])}
        for i in idxs
    ]

def _softmax_np(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    exp = np.exp(x)
    return exp / np.sum(exp)

def _to_probabilities(scores: np.ndarray) -> np.ndarray:
    scores = scores.astype(np.float32)
    if np.all(scores >= 0.0) and np.all(scores <= 1.0):
        s = float(np.sum(scores))
        if 0.98 <= s <= 1.02:
            return scores / max(s, 1e-6)
    return _softmax_np(scores)

def _automl_tflite_predict(img: Image.Image) -> Dict:
    """Run inference on a single image using local AutoML TFLite model."""
    if not AUTOML_TFLITE_AVAILABLE:
        raise RuntimeError("AutoML TFLite model not available")

    start_time = time.time()
    input_details = AUTOML_INPUT_DETAILS[0]
    output_details = AUTOML_OUTPUT_DETAILS[0]
    _, h, w, _ = input_details["shape"]

    # Preprocess
    img_resized = img.convert("RGB").resize((w, h))
    x = np.array(img_resized)
    input_dtype = input_details["dtype"]
    if input_dtype == np.float32:
        x = x.astype(np.float32) / 255.0
    else:
        scale, zero = input_details.get("quantization", (0.0, 0))
        if scale and scale > 0:
            x = x.astype(np.float32) / 255.0
            x = x / scale + zero
            info = np.iinfo(input_dtype)
            x = np.clip(x, info.min, info.max).astype(input_dtype)
        else:
            x = x.astype(input_dtype)

    x = np.expand_dims(x, axis=0)
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
    top_prob = float(probs[top_idx])
    top_class = AUTOML_LABELS[top_idx] if top_idx < len(AUTOML_LABELS) else f"index_{top_idx}"

    inference_time = (time.time() - start_time) * 1000

    all_probs = {
        (AUTOML_LABELS[i] if i < len(AUTOML_LABELS) else f"index_{i}"): float(probs[i])
        for i in range(len(probs))
    }
    top_k = [
        {"class_name": (AUTOML_LABELS[i] if i < len(AUTOML_LABELS) else f"index_{i}"), "confidence": float(probs[i])}
        for i in np.argsort(probs)[::-1][:TOP_K_DEFAULT]
    ]

    return {
        "predicted_class": top_class,
        "confidence": top_prob,
        "all_probabilities": all_probs,
        "top_k": top_k,
        "raw_top_class": top_class,
        "threshold": 0.0,
        "inference_time_ms": round(inference_time, 2),
        "model_type": "automl",
    }


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_duration_seconds(value) -> Optional[float]:
    if _is_number(value):
        return float(value)
    if not isinstance(value, str):
        return None

    raw = value.strip().lower()
    if not raw:
        return None

    tokens = raw.split()
    if not tokens:
        return None

    try:
        num = float(tokens[0])
    except ValueError:
        return None

    unit = tokens[1] if len(tokens) > 1 else "seconds"
    if unit.startswith("hour"):
        return num * 3600.0
    if unit.startswith("min"):
        return num * 60.0
    if unit.startswith("ms"):
        return num / 1000.0
    return num


def _compute_macro_fpr(cm: List[List[int]]) -> float:
    cm_np = np.array(cm, dtype=float)
    if cm_np.ndim != 2 or cm_np.shape[0] == 0 or cm_np.shape[0] != cm_np.shape[1]:
        return 0.0

    k = cm_np.shape[0]
    total = float(np.sum(cm_np))
    fprs: List[float] = []
    for i in range(k):
        tp = cm_np[i, i]
        fp = float(np.sum(cm_np[:, i]) - tp)
        fn = float(np.sum(cm_np[i, :]) - tp)
        tn = total - (tp + fp + fn)
        denom = fp + tn
        fpr = (fp / denom) if denom > 0 else 0.0
        fprs.append(float(fpr))
    return float(np.mean(fprs)) if fprs else 0.0


def _read_json_file(path: Path) -> Dict:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Metrics file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON {path}: {exc}")


def _normalize_custom_metrics(raw: Dict, metrics_path: Path) -> Dict:
    # Already in v2 schema.
    if isinstance(raw.get("metadata"), dict) and isinstance(raw.get("core"), dict):
        return raw

    report = raw.get("classification_report", {})
    macro = report.get("macro avg", {})
    cm = raw.get("confusion_matrix", [])

    test_acc = raw.get("test_acc")
    accuracy = test_acc if _is_number(test_acc) else report.get("accuracy", 0.0)

    model_path = Path(MODEL_PATH)
    model_size_mb = None
    if model_path.exists():
        model_size_mb = round(model_path.stat().st_size / (1024 * 1024), 3)

    sample_count = 0
    if isinstance(macro, dict) and _is_number(macro.get("support")):
        sample_count = int(macro["support"])
    elif isinstance(cm, list) and cm:
        sample_count = int(np.sum(np.array(cm, dtype=int)))

    mtime = int(metrics_path.stat().st_mtime) if metrics_path.exists() else int(time.time())

    return {
        "metadata": {
            "model_name": "Custom ML (ResNet18)",
            "run_id": f"custom_{mtime}",
            "timestamp": mtime,
            "dataset_version": "neu_final_dataset",
            "sample_count": sample_count,
            "classes": raw.get("classes", CLASS_NAMES),
        },
        "core": {
            "accuracy": float(accuracy) if _is_number(accuracy) else 0.0,
            "precision": float(macro.get("precision", 0.0)),
            "recall": float(macro.get("recall", 0.0)),
            "f1": float(macro.get("f1-score", 0.0)),
            "confidence": None,
            "inference_ms": {
                "mean": None,
                "p50": None,
                "p95": None,
                "min": None,
                "max": None,
            },
        },
        "ops": {
            "training_time": None,
            "model_size_mb": model_size_mb,
            "gpu_required": False,
            "setup_complexity": "medium",
            "false_positive_rate": _compute_macro_fpr(cm) if cm else None,
        },
        "explainability": {
            "feature_importance": [],
            "focus_areas": [],
            "advantages": [],
        },
        "details": {
            "confusion_matrix": cm,
        },
    }


def _as_percent(value: Optional[float]) -> Optional[float]:
    if not _is_number(value):
        return None
    return float(value) * 100.0


def _format_metric(metric_key: str, value):
    if value is None:
        return "N/A"
    if metric_key in {"accuracy", "precision", "recall", "f1", "confidence", "false_positive_rate"}:
        return f"{float(value) * 100:.1f}%"
    if metric_key == "inference_ms_mean":
        return f"{float(value):.2f}ms"
    if metric_key == "model_size_mb":
        return f"{float(value):.3f}MB"
    if metric_key == "training_time_seconds":
        return f"{float(value):.1f}s"
    return str(value)


def _build_comparison(automl_metrics: Dict, custom_metrics: Dict) -> Dict:
    metric_specs = [
        ("accuracy", "Accuracy", True, automl_metrics["core"].get("accuracy"), custom_metrics["core"].get("accuracy")),
        ("precision", "Precision", True, automl_metrics["core"].get("precision"), custom_metrics["core"].get("precision")),
        ("recall", "Recall", True, automl_metrics["core"].get("recall"), custom_metrics["core"].get("recall")),
        ("f1", "F1 Score", True, automl_metrics["core"].get("f1"), custom_metrics["core"].get("f1")),
        ("confidence", "Confidence", True, automl_metrics["core"].get("confidence"), custom_metrics["core"].get("confidence")),
        (
            "inference_ms_mean",
            "Inference Time",
            False,
            (automl_metrics["core"].get("inference_ms") or {}).get("mean"),
            (custom_metrics["core"].get("inference_ms") or {}).get("mean"),
        ),
        (
            "false_positive_rate",
            "False Positives",
            False,
            automl_metrics["ops"].get("false_positive_rate"),
            custom_metrics["ops"].get("false_positive_rate"),
        ),
        (
            "model_size_mb",
            "Model Size",
            False,
            automl_metrics["ops"].get("model_size_mb"),
            custom_metrics["ops"].get("model_size_mb"),
        ),
    ]

    automl_train_secs = _parse_duration_seconds(automl_metrics["ops"].get("training_time"))
    custom_train_secs = _parse_duration_seconds(custom_metrics["ops"].get("training_time"))
    if automl_train_secs is not None and custom_train_secs is not None:
        metric_specs.append(
            ("training_time_seconds", "Training Time", False, automl_train_secs, custom_train_secs)
        )

    wins = {"automl": 0, "custom": 0}
    per_metric_winners: Dict[str, str] = {}
    rows = []

    for metric_key, label, higher_is_better, automl_val, custom_val in metric_specs:
        winner = "none"
        if _is_number(automl_val) and _is_number(custom_val):
            if abs(float(automl_val) - float(custom_val)) <= 1e-9:
                winner = "tie"
            elif higher_is_better:
                winner = "automl" if float(automl_val) > float(custom_val) else "custom"
            else:
                winner = "automl" if float(automl_val) < float(custom_val) else "custom"

            if winner in wins:
                wins[winner] += 1

        per_metric_winners[metric_key] = winner
        rows.append(
            {
                "key": metric_key,
                "metric": label,
                "automl": _format_metric(metric_key, automl_val),
                "custom": _format_metric(metric_key, custom_val),
                "winner": winner,
            }
        )

    winner = "tie"
    if wins["automl"] > wins["custom"]:
        winner = "automl"
    elif wins["custom"] > wins["automl"]:
        winner = "custom"

    a_acc = _as_percent(automl_metrics["core"].get("accuracy"))
    c_acc = _as_percent(custom_metrics["core"].get("accuracy"))
    a_ms = (automl_metrics["core"].get("inference_ms") or {}).get("mean")
    c_ms = (custom_metrics["core"].get("inference_ms") or {}).get("mean")

    reason_parts = [f"Wins - AutoML: {wins['automl']}, Custom: {wins['custom']}"]
    if _is_number(a_acc) and _is_number(c_acc):
        reason_parts.append(f"Accuracy delta (Custom - AutoML): {c_acc - a_acc:+.2f}%")
    if _is_number(a_ms) and _is_number(c_ms) and float(c_ms) > 0:
        reason_parts.append(f"Speed ratio (AutoML/Custom): {float(a_ms) / float(c_ms):.2f}x")

    return {
        "automl": automl_metrics,
        "custom": custom_metrics,
        "wins": wins,
        "per_metric_winners": per_metric_winners,
        "comparison_rows": rows,
        "summary": {
            "winner": winner,
            "reason": " | ".join(reason_parts),
        },
    }

class AssistantRequest(BaseModel):
    question: str
    prediction: Optional[Dict] = None

def infer(img: Image.Image) -> Dict:
    """Run inference on a single image using the trained model."""
    start_time = time.time()
    
    try:
        probs = _predict_probs(img)

        # Get top prediction
        top_idx = int(np.argmax(probs))
        top_prob = float(probs[top_idx])
        top_class = CLASS_NAMES[top_idx]

        is_no_defect = top_prob < CONF_THRESHOLD_NO_DEFECT
        inference_time = (time.time() - start_time) * 1000

        result = {
            "predicted_class": "No defect / Unknown" if is_no_defect else top_class,
            "confidence": top_prob,
            "all_probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))},
            "top_k": _top_k(probs, TOP_K_DEFAULT),
            "raw_top_class": top_class,
            "threshold": CONF_THRESHOLD_NO_DEFECT,
            "inference_time_ms": round(inference_time, 2),
            "model_type": "custom"
        }
        
        print(f"Prediction: {result['predicted_class']} ({result['confidence']:.2%})")
        return result
    except Exception as e:
        print(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model_type: Optional[str] = "custom"
):
    """
    Predict defect type for a single uploaded image using trained model(s).
    
    Args:
        file: Image file to predict
        model_type: "custom" (default), "automl", or "both"
    
    Returns:
        Prediction results from the trained model(s)
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        img = Image.open(io.BytesIO(content))
        img.verify()
        img = Image.open(io.BytesIO(content))  # Reopen after verify
        
        if model_type == "automl":
            if AUTOML_TFLITE_AVAILABLE:
                return _automl_tflite_predict(img)
            if VERTEX_AI_AVAILABLE:
                return predict_with_automl(img)
            raise HTTPException(
                status_code=503,
                detail="AutoML not configured. Provide local TFLite model or set Vertex AI environment variables.",
            )
        
        elif model_type == "both":
            # Run custom model (always available)
            custom_result = infer(img)
            
            # Try AutoML if available
            if AUTOML_TFLITE_AVAILABLE:
                try:
                    automl_result = _automl_tflite_predict(img)
                    return {
                        "custom": custom_result,
                        "automl": automl_result,
                        "model_type": "both"
                    }
                except Exception as e:
                    print(f"AutoML TFLite prediction failed: {e}")
                    return {
                        "custom": custom_result,
                        "automl": None,
                        "automl_error": str(e),
                        "model_type": "both"
                    }
            if VERTEX_AI_AVAILABLE:
                try:
                    automl_result = predict_with_automl(img)
                    return {
                        "custom": custom_result,
                        "automl": automl_result,
                        "model_type": "both"
                    }
                except Exception as e:
                    print(f"AutoML prediction failed: {e}")
                    return {
                        "custom": custom_result,
                        "automl": None,
                        "automl_error": str(e),
                        "model_type": "both"
                    }
            return {
                "custom": custom_result,
                "automl": None,
                "model_type": "both"
            }
        
        else:  # model_type == "custom" or default
            return infer(img)
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(
    files: List[UploadFile] = File(..., description="List of image files to process"),
    model_type: Optional[str] = "custom",
):
    """Predict defect types for multiple uploaded images."""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 50:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 50 images per batch")
    
    results = []
    for file in files:
        try:
            content = await file.read()
            if not content:
                results.append({
                    "filename": file.filename,
                    "error": "Empty file"
                })
                continue
            
            img = Image.open(io.BytesIO(content))
            img.verify()
            img = Image.open(io.BytesIO(content))
            
            if model_type == "automl":
                if AUTOML_TFLITE_AVAILABLE:
                    prediction = _automl_tflite_predict(img)
                elif VERTEX_AI_AVAILABLE:
                    prediction = predict_with_automl(img)
                else:
                    raise RuntimeError(
                        "AutoML not configured. Provide local TFLite model or set Vertex AI environment variables."
                    )
                prediction["filename"] = file.filename
                results.append(prediction)
            elif model_type == "both":
                custom_result = infer(img)
                automl_result = None
                automl_error = None
                if AUTOML_TFLITE_AVAILABLE:
                    try:
                        automl_result = _automl_tflite_predict(img)
                    except Exception as e:
                        automl_error = str(e)
                elif VERTEX_AI_AVAILABLE:
                    try:
                        automl_result = predict_with_automl(img)
                    except Exception as e:
                        automl_error = str(e)
                results.append({
                    "filename": file.filename,
                    "custom": custom_result,
                    "automl": automl_result,
                    "automl_error": automl_error,
                })
            else:
                prediction = infer(img)
                prediction["filename"] = file.filename
                results.append(prediction)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}

@app.post("/assistant")
async def assistant(req: AssistantRequest):
    """Answer questions and explain predictions using local knowledge."""
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    return answer_question(req.question, req.prediction)

@app.post("/predict/debug")
async def predict_debug(
    file: UploadFile = File(...),
    top_k: int = TOP_K_DEFAULT
):
    """Return raw probabilities and top-k for debugging."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        img = Image.open(io.BytesIO(content))
        img.verify()
        img = Image.open(io.BytesIO(content))

        probs = _predict_probs(img)
        top_idx = int(np.argmax(probs))
        top_prob = float(probs[top_idx])
        top_class = CLASS_NAMES[top_idx]
        is_no_defect = top_prob < CONF_THRESHOLD_NO_DEFECT

        return {
            "predicted_class": "No defect / Unknown" if is_no_defect else top_class,
            "confidence": top_prob,
            "all_probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))},
            "top_k": _top_k(probs, top_k),
            "raw_top_class": top_class,
            "threshold": CONF_THRESHOLD_NO_DEFECT,
            "classes": CLASS_NAMES,
            "image_size": IMG_SIZE,
            "model_path": MODEL_PATH,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded model."""
    try:
        import os
        model_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)  # Size in MB
        
        return {
            "model_path": MODEL_PATH,
            "model_size_mb": round(model_size, 2),
            "device": DEVICE,
            "image_size": IMG_SIZE,
            "classes": CLASS_NAMES,
            "num_classes": len(CLASS_NAMES),
            "confidence_threshold": CONF_THRESHOLD_NO_DEFECT,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@app.get("/compare/metrics")
async def compare_metrics():
    """Return normalized AutoML/Custom metrics with deterministic winners."""
    automl_path = _BASE_DIR / "models" / "AutoML" / "automl_metrics.json"
    custom_v2_path = _BASE_DIR / "models" / "CustomML" / "custom_metrics_v2.json"
    custom_legacy_path = _BASE_DIR / "models" / "CustomML" / "outputs" / "metrics.json"

    automl_raw = _read_json_file(automl_path)

    if custom_v2_path.exists():
        custom_raw = _read_json_file(custom_v2_path)
        custom_metrics = _normalize_custom_metrics(custom_raw, custom_v2_path)
    else:
        custom_raw = _read_json_file(custom_legacy_path)
        custom_metrics = _normalize_custom_metrics(custom_raw, custom_legacy_path)

    # Ensure AutoML payload also has expected top-level keys.
    automl_metrics = _normalize_custom_metrics(automl_raw, automl_path)

    return _build_comparison(automl_metrics, custom_metrics)
