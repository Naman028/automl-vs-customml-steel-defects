import logging
import glob
import argparse
import json
import time
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
)

try:
    from label_normalization import normalize_automl_label, normalize_automl_labels
except ImportError:
    _BACKEND_DIR = Path(__file__).resolve().parents[2]
    if str(_BACKEND_DIR) not in sys.path:
        sys.path.append(str(_BACKEND_DIR))
    from label_normalization import normalize_automl_label, normalize_automl_labels

from automl_contract import prepare_image, read_contract, embedded_labels

try:
    from tflite_runtime.interpreter import Interpreter as TFLiteInterpreter
except Exception:
    import tensorflow as tf

    TFLiteInterpreter = tf.lite.Interpreter


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR.parent

# ---------- CONFIG ----------
_CANDIDATE_TEST_DIRS = [
    MODELS_DIR / "neu_final_dataset_fullnames" / "test",
    BASE_DIR.parent / "CustomML" / "neu_final_dataset" / "test",
]
DEFAULT_DATASET_TEST_DIR = next(
    (p for p in _CANDIDATE_TEST_DIRS if p.exists()), _CANDIDATE_TEST_DIRS[0]
)
DEFAULT_TFLITE_MODEL_PATH = BASE_DIR / "AutoML model.tflite"
DEFAULT_LABELS_PATH = BASE_DIR / "labels.txt"
FOLDER_TO_LABEL = {
    "Cr": "Crazing",
    "In": "Inclusion",
    "Pa": "Patches",
    "PS": "Pitted_Surface",
    "RS": "Rolled_in_Scale",
    "Sc": "Scratches",
}

MODEL_NAME = "AutoML Edge (TFLite)"
DEFAULT_OUT_JSON = BASE_DIR / "automl_metrics.json"
# ---------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate AutoML TFLite model on dataset test split."
    )
    parser.add_argument(
        "--model",
        default=str(DEFAULT_TFLITE_MODEL_PATH),
        help="Path to .tflite model file.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT_JSON),
        help="Path to output metrics JSON file.",
    )
    parser.add_argument(
        "--dataset_test_dir",
        default=str(DEFAULT_DATASET_TEST_DIR),
        help="Path to dataset test directory.",
    )
    parser.add_argument(
        "--labels",
        default=str(DEFAULT_LABELS_PATH),
        help="Path to labels.txt.",
    )
    return parser.parse_args()


def load_labels(path: Path):
    raw = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return normalize_automl_labels(raw)


def resolve_gt_label(folder_name: str, labels: list[str]) -> str:
    # Supports either short-code folders (Cr/In/...) or full label folders.
    normalized_folder = normalize_automl_label(folder_name)
    if normalized_folder in labels:
        return normalized_folder
    mapped = FOLDER_TO_LABEL.get(folder_name)
    if mapped in labels:
        return mapped
    return normalized_folder


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
    input_details["normalization_contract"] = read_contract(str(model_path.resolve()))
    output_details = interpreter.get_output_details()[0]
    return interpreter, input_details, output_details


def preprocess_image(img_path: Path, input_details: dict):
    from PIL import Image

    with Image.open(img_path) as img:
        return prepare_image(img, input_details, input_details["normalization_contract"])


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
    args = parse_args()
    dataset_test_dir = Path(args.dataset_test_dir)
    tflite_model_path = Path(args.model)
    labels_path = Path(args.labels)
    out_json = Path(args.out)

    if not dataset_test_dir.exists():
        raise RuntimeError(f"Missing test dir: {dataset_test_dir}")
    if not tflite_model_path.exists():
        raise RuntimeError(f"Missing model: {tflite_model_path}")
    if not labels_path.exists():
        raise RuntimeError(f"Missing labels file: {labels_path}")

    labels = load_labels(labels_path)
    if labels != embedded_labels(tflite_model_path):
        raise ValueError("AutoML labels must match the embedded output label order")
    interpreter, in_det, out_det = load_interpreter(tflite_model_path)

    class_folders = sorted([p for p in dataset_test_dir.iterdir() if p.is_dir()])
    gt_class_names = [p.name for p in class_folders]
    label_to_idx = {name: i for i, name in enumerate(labels)}

    resolved_gt_names = [resolve_gt_label(c, labels) for c in gt_class_names]
    missing = [c for c in resolved_gt_names if c not in label_to_idx]
    if missing:
        raise RuntimeError(
            f"These test folders are not in labels.txt: {missing}\nlabels.txt has: {labels}"
        )

    y_true = []
    y_pred = []
    confidences = []
    latencies = []
    probs_all = []
    sample_count = 0

    for folder_name, resolved_name in zip(gt_class_names, resolved_gt_names):
        cls_idx = label_to_idx[resolved_name]
        img_paths = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
            img_paths.extend(glob.glob(str(dataset_test_dir / folder_name / ext)))
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
        raise RuntimeError(f"No images found under: {dataset_test_dir}")

    y_true = np.array(y_true, dtype=int)
    y_pred = np.array(y_pred, dtype=int)

    acc = float(accuracy_score(y_true, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(
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

    dataset_root = dataset_test_dir.parent
    dataset_counts = {
        "train": count_images(dataset_root / "train"),
        "val": count_images(dataset_root / "val"),
        "test": count_images(dataset_test_dir),
    }
    dataset_counts["total"] = (
        dataset_counts["train"] + dataset_counts["val"] + dataset_counts["test"]
    )

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
            "run_id": f"automl_{int(time.time())}",
            "timestamp": int(time.time()),
            "dataset_version": dataset_root.name,
            "model_path": str(tflite_model_path),
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
            "model_size_mb": round(tflite_model_path.stat().st_size / (1024 * 1024), 3),
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

    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info(" ".join(str(value) for value in (f"Wrote: {out_json} ({sample_count} samples)",)))
    logger.info(
        " ".join(
            str(value)
            for value in (
                f"Accuracy={acc:.4f}  MacroF1={float(f1):.4f}  MeanLatency={inference_ms['mean']:.2f}ms",
            )
        )
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
