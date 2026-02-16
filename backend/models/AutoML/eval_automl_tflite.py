import glob
import json
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
)

try:
    from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter
except Exception:
    import tensorflow as tf

    TFLiteInterpreter = tf.lite.Interpreter


BASE_DIR = Path(__file__).resolve().parent

# ---------- CONFIG ----------
_CANDIDATE_TEST_DIRS = [
    BASE_DIR / "neu_final_dataset" / "test",
    BASE_DIR.parent / "CustomML" / "neu_final_dataset" / "test",
]
DATASET_TEST_DIR = next((p for p in _CANDIDATE_TEST_DIRS if p.exists()), _CANDIDATE_TEST_DIRS[0])
TFLITE_MODEL_PATH = BASE_DIR / "AutoML model.tflite"
LABELS_PATH = BASE_DIR / "labels.txt"

MODEL_NAME = "AutoML Edge (TFLite)"
DATASET_VERSION = "neu_final_dataset"
RUN_ID = f"automl_{int(time.time())}"
OUT_JSON = BASE_DIR / "automl_metrics.json"
# ---------------------------


def load_labels(path: Path):
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / np.sum(e)


def to_probabilities(scores: np.ndarray) -> np.ndarray:
    scores = scores.astype(np.float32)
    if np.all(scores >= 0.0) and np.all(scores <= 1.0):
        s = float(np.sum(scores))
        if 0.98 <= s <= 1.02:
            return scores / max(s, 1e-6)
    return softmax(scores)


def load_interpreter(model_path: Path):
    interpreter = TFLiteInterpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    return interpreter, input_details, output_details


def preprocess_image(img_path: Path, input_details: dict):
    from PIL import Image

    _, h, w, _ = input_details["shape"]
    img = Image.open(img_path).convert("RGB").resize((w, h))
    x = np.array(img)

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

    return np.expand_dims(x, axis=0)


def infer_one(interpreter, input_details, output_details, img_path: Path):
    x = preprocess_image(img_path, input_details)

    t0 = time.time()
    interpreter.set_tensor(input_details["index"], x)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details["index"])
    latency_ms = (time.time() - t0) * 1000.0

    out_dtype = output_details["dtype"]
    if out_dtype == np.float32:
        scores = output[0].astype(np.float32)
    else:
        scale, zero = output_details.get("quantization", (0.0, 0))
        if scale and scale > 0:
            scores = (output[0].astype(np.float32) - zero) * scale
        else:
            scores = output[0].astype(np.float32)

    probs = to_probabilities(scores)
    pred_idx = int(np.argmax(probs))
    conf = float(probs[pred_idx])
    return pred_idx, conf, latency_ms, probs


def compute_macro_fpr(cm: np.ndarray) -> float:
    k = cm.shape[0]
    fprs = []
    total = np.sum(cm)
    for i in range(k):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        tn = total - (tp + fp + fn)
        denom = fp + tn
        fpr = (fp / denom) if denom > 0 else 0.0
        fprs.append(fpr)
    return float(np.mean(fprs))


def count_images(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        count += len(list(root.rglob(ext)))
    return count


def main():
    if not DATASET_TEST_DIR.exists():
        raise RuntimeError(f"Missing test dir: {DATASET_TEST_DIR}")
    if not TFLITE_MODEL_PATH.exists():
        raise RuntimeError(f"Missing model: {TFLITE_MODEL_PATH}")
    if not LABELS_PATH.exists():
        raise RuntimeError(f"Missing labels file: {LABELS_PATH}")

    labels = load_labels(LABELS_PATH)
    interpreter, in_det, out_det = load_interpreter(TFLITE_MODEL_PATH)

    class_folders = sorted([p for p in DATASET_TEST_DIR.iterdir() if p.is_dir()])
    gt_class_names = [p.name for p in class_folders]
    label_to_idx = {name: i for i, name in enumerate(labels)}

    missing = [c for c in gt_class_names if c not in label_to_idx]
    if missing:
        raise RuntimeError(
            f"These test folders are not in labels.txt: {missing}\n"
            f"labels.txt has: {labels}"
        )

    y_true = []
    y_pred = []
    confidences = []
    latencies = []
    probs_all = []
    sample_count = 0

    for cls in gt_class_names:
        cls_idx = label_to_idx[cls]
        img_paths = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
            img_paths.extend(glob.glob(str(DATASET_TEST_DIR / cls / ext)))
        img_paths = [Path(p) for p in img_paths]

        for img_path in img_paths:
            pred_idx, conf, ms, probs = infer_one(interpreter, in_det, out_det, img_path)
            y_true.append(cls_idx)
            y_pred.append(pred_idx)
            confidences.append(conf)
            latencies.append(ms)
            probs_all.append(probs.tolist())
            sample_count += 1

    if sample_count == 0:
        raise RuntimeError(f"No images found under: {DATASET_TEST_DIR}")

    y_true = np.array(y_true, dtype=int)
    y_pred = np.array(y_pred, dtype=int)

    acc = float(accuracy_score(y_true, y_pred))
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    per_prec, per_rec, per_f1, per_support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(labels))), average=None, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(labels))))
    fpr = compute_macro_fpr(cm)

    lat_arr = np.array(latencies, dtype=float)
    inference_ms = {
        "mean": float(np.mean(lat_arr)),
        "p50": float(np.percentile(lat_arr, 50)),
        "p95": float(np.percentile(lat_arr, 95)),
        "min": float(np.min(lat_arr)),
        "max": float(np.max(lat_arr)),
    }

    probs_arr = np.array(probs_all, dtype=float)
    correct_mask = (y_true == y_pred).astype(float)
    conf_arr = np.array(confidences, dtype=float)
    thresholds = np.linspace(0.0, 1.0, 51)
    thr_precision = []
    thr_recall = []
    thr_coverage = []
    for t in thresholds:
        sel = conf_arr >= t
        sel_count = int(np.sum(sel))
        if sel_count == 0:
            p_t = 0.0
            r_t = 0.0
        else:
            correct_sel = float(np.sum(correct_mask[sel]))
            p_t = correct_sel / sel_count
            r_t = correct_sel / len(correct_mask)
        thr_precision.append(float(p_t))
        thr_recall.append(float(r_t))
        thr_coverage.append(float(sel_count / len(correct_mask)))

    pr_curves = {}
    for i, cls in enumerate(labels):
        y_bin = (y_true == i).astype(int)
        precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_bin, probs_arr[:, i])
        pr_curves[cls] = {
            "precision": [float(x) for x in precision_vals.tolist()],
            "recall": [float(x) for x in recall_vals.tolist()],
            "thresholds": [float(x) for x in pr_thresholds.tolist()],
        }

    dataset_root = DATASET_TEST_DIR.parent
    dataset_counts = {
        "train": count_images(dataset_root / "train"),
        "val": count_images(dataset_root / "val"),
        "test": count_images(DATASET_TEST_DIR),
    }
    dataset_counts["total"] = dataset_counts["train"] + dataset_counts["val"] + dataset_counts["test"]

    per_class_metrics = []
    for idx, cls in enumerate(labels):
        per_class_metrics.append(
            {
                "class_name": cls,
                "precision": float(per_prec[idx]),
                "recall": float(per_rec[idx]),
                "f1": float(per_f1[idx]),
                "support": int(per_support[idx]),
            }
        )

    payload = {
        "metadata": {
            "model_name": MODEL_NAME,
            "run_id": RUN_ID,
            "timestamp": int(time.time()),
            "dataset_version": DATASET_VERSION,
            "sample_count": sample_count,
            "classes": labels,
        },
        "core": {
            "accuracy": acc,
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "confidence": float(np.mean(np.array(confidences, dtype=float))),
            "inference_ms": inference_ms,
        },
        "ops": {
            "training_time": None,
            "model_size_mb": round(TFLITE_MODEL_PATH.stat().st_size / (1024 * 1024), 3),
            "gpu_required": False,
            "setup_complexity": "low",
            "false_positive_rate": fpr,
        },
        "explainability": {
            "feature_importance": [],
            "focus_areas": [],
            "advantages": [],
        },
        "details": {
            "confusion_matrix": cm.tolist(),
            "y_true": y_true.tolist(),
            "y_pred": y_pred.tolist(),
            "probabilities": probs_all,
            "per_class_metrics": per_class_metrics,
            "pr_curves": pr_curves,
            "threshold_metrics": {
                "thresholds": [float(x) for x in thresholds.tolist()],
                "precision": thr_precision,
                "recall": thr_recall,
                "coverage": thr_coverage,
            },
            "dataset_counts": dataset_counts,
        },
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote: {OUT_JSON} ({sample_count} samples)")
    print(
        f"Accuracy={acc:.4f}  MacroF1={float(f1):.4f}  MeanLatency={inference_ms['mean']:.2f}ms"
    )


if __name__ == "__main__":
    main()
