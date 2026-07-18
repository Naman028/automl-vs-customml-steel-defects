import argparse
import glob
import json
import time
from pathlib import Path
from typing import List

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import precision_recall_curve
from torchvision import transforms
from torchvision.models import resnet18


BASE_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate CustomML PyTorch model on test split.")
    parser.add_argument(
        "--model",
        default=str(BASE_DIR / "outputs" / "best.pt"),
        help="Path to best.pt checkpoint",
    )
    parser.add_argument(
        "--test_dir",
        default=str(BASE_DIR / "neu_final_dataset" / "test"),
        help="Path to dataset test directory",
    )
    parser.add_argument(
        "--out",
        default=str(BASE_DIR / "custom_metrics_v2.json"),
        help="Output metrics JSON path",
    )
    parser.add_argument(
        "--run_id",
        default=f"custom_{int(time.time())}",
        help="Run id for metadata",
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.55,
        help="Production confidence threshold; lower predictions are counted as abstentions.",
    )
    return parser.parse_args()


def compute_macro_fpr(cm: np.ndarray) -> float:
    k = cm.shape[0]
    total = np.sum(cm)
    fprs: List[float] = []
    for i in range(k):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        tn = total - (tp + fp + fn)
        denom = fp + tn
        fprs.append(float(fp / denom) if denom > 0 else 0.0)
    return float(np.mean(fprs)) if fprs else 0.0


def confusion_and_macro_metrics(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int):
    cm = np.zeros((n_classes, n_classes), dtype=np.int64)
    rejected = np.zeros(n_classes, dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        if 0 <= int(p) < n_classes:
            cm[int(t), int(p)] += 1
        else:
            rejected[int(t)] += 1

    correct = np.trace(cm)
    total = len(y_true)
    acc = float(correct / max(total, 1))

    precisions = []
    recalls = []
    f1s = []
    for i in range(n_classes):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp + rejected[i]
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = (2.0 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    macro_precision = float(np.mean(precisions)) if precisions else 0.0
    macro_recall = float(np.mean(recalls)) if recalls else 0.0
    macro_f1 = float(np.mean(f1s)) if f1s else 0.0
    return cm, rejected, acc, macro_precision, macro_recall, macro_f1


def load_model(model_path: Path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load(model_path, map_location=device)

    if not isinstance(ckpt, dict) or "model_state_dict" not in ckpt:
        raise RuntimeError("Checkpoint must contain model_state_dict/classes/image_size.")

    classes = ckpt.get("classes")
    if not isinstance(classes, list) or not classes:
        raise RuntimeError("Checkpoint missing classes list.")

    image_size = int(ckpt.get("image_size", 224))

    model = resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(classes))
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model = model.to(device).eval()

    return model, device, classes, image_size


def build_transform(image_size: int):
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def count_images(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        count += len(list(root.rglob(ext)))
    return count


def main():
    args = parse_args()
    model_path = Path(args.model)
    test_dir = Path(args.test_dir)
    out_path = Path(args.out)

    if not model_path.exists():
        raise RuntimeError(f"Missing model file: {model_path}")
    if not test_dir.exists():
        raise RuntimeError(f"Missing test directory: {test_dir}")

    model, device, classes, image_size = load_model(model_path)
    transform = build_transform(image_size)
    label_to_idx = {name: i for i, name in enumerate(classes)}

    class_folders = sorted([p for p in test_dir.iterdir() if p.is_dir()])
    gt_class_names = [p.name for p in class_folders]
    missing = [c for c in gt_class_names if c not in label_to_idx]
    if missing:
        raise RuntimeError(f"Test folders not found in model classes: {missing} | classes={classes}")

    y_true = []
    y_pred = []
    confidences = []
    latencies = []
    probs_all = []
    sample_count = 0

    for cls in gt_class_names:
        cls_idx = label_to_idx[cls]
        image_paths = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
            image_paths.extend(glob.glob(str(test_dir / cls / ext)))

        for image_path in image_paths:
            img = Image.open(image_path).convert("RGB")
            x = transform(img).unsqueeze(0).to(device)

            t0 = time.perf_counter()
            with torch.no_grad():
                logits = model(x)
                probs = F.softmax(logits, dim=1)[0].detach().cpu().numpy()
            latency_ms = (time.perf_counter() - t0) * 1000.0

            pred_idx = int(np.argmax(probs))
            conf = float(probs[pred_idx])

            y_true.append(cls_idx)
            y_pred.append(pred_idx)
            confidences.append(conf)
            latencies.append(latency_ms)
            probs_all.append(probs.tolist())
            sample_count += 1

    if sample_count == 0:
        raise RuntimeError(f"No test images found under: {test_dir}")

    y_true_np = np.array(y_true, dtype=int)
    raw_y_pred_np = np.array(y_pred, dtype=int)
    conf_np = np.array(confidences, dtype=float)
    y_pred_np = np.where(conf_np >= args.confidence_threshold, raw_y_pred_np, -1)

    cm, rejected, acc, prec, rec, f1 = confusion_and_macro_metrics(
        y_true_np, y_pred_np, len(classes)
    )
    raw_accuracy = float(np.mean(y_true_np == raw_y_pred_np))
    fpr = compute_macro_fpr(cm)

    lat_arr = np.array(latencies, dtype=float)
    inference_ms = {
        "mean": float(np.mean(lat_arr)),
        "p50": float(np.percentile(lat_arr, 50)),
        "p95": float(np.percentile(lat_arr, 95)),
        "min": float(np.min(lat_arr)),
        "max": float(np.max(lat_arr)),
    }

    # Per-class metrics from confusion matrix.
    per_class_metrics = []
    for i, cls in enumerate(classes):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp + rejected[i]
        precision_i = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall_i = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1_i = (
            (2.0 * precision_i * recall_i / (precision_i + recall_i))
            if (precision_i + recall_i) > 0
            else 0.0
        )
        per_class_metrics.append(
            {
                "class_name": cls,
                "precision": precision_i,
                "recall": recall_i,
                "f1": f1_i,
                "support": int(np.sum(cm[i, :]) + rejected[i]),
                "abstentions": int(rejected[i]),
            }
        )

    probs_arr = np.array(probs_all, dtype=float)
    correct_mask = (y_true_np == y_pred_np).astype(float)
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
    for i, cls in enumerate(classes):
        y_bin = (y_true_np == i).astype(int)
        precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_bin, probs_arr[:, i])
        pr_curves[cls] = {
            "precision": [float(x) for x in precision_vals.tolist()],
            "recall": [float(x) for x in recall_vals.tolist()],
            "thresholds": [float(x) for x in pr_thresholds.tolist()],
        }

    dataset_root = test_dir.parent
    dataset_counts = {
        "train": count_images(dataset_root / "train"),
        "val": count_images(dataset_root / "val"),
        "test": count_images(test_dir),
    }
    dataset_counts["total"] = dataset_counts["train"] + dataset_counts["val"] + dataset_counts["test"]

    payload = {
        "metadata": {
            "model_name": "Custom ML (ResNet18)",
            "run_id": args.run_id,
            "timestamp": int(time.time()),
            "dataset_version": "neu_final_dataset",
            "sample_count": sample_count,
            "classes": classes,
            "evaluation_profile": "deployed_threshold",
            "confidence_threshold": args.confidence_threshold,
        },
        "core": {
            "accuracy": acc,
            "raw_argmax_accuracy": raw_accuracy,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "confidence": float(np.mean(np.array(confidences, dtype=float))),
            "inference_ms": inference_ms,
        },
        "ops": {
            "training_time": None,
            "model_size_mb": round(model_path.stat().st_size / (1024 * 1024), 3),
            "gpu_required": torch.cuda.is_available(),
            "setup_complexity": "medium",
            "false_positive_rate": fpr,
        },
        "explainability": {
            "feature_importance": [],
            "focus_areas": [],
            "advantages": [],
        },
        "details": {
            "confusion_matrix": cm.tolist(),
            "y_true": y_true_np.tolist(),
            "y_pred": y_pred_np.tolist(),
            "raw_y_pred": raw_y_pred_np.tolist(),
            "abstentions_by_class": rejected.tolist(),
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

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path} ({sample_count} samples)")
    print(
        f"Accuracy={acc:.4f}  MacroF1={f1:.4f}  MeanLatency={inference_ms['mean']:.2f}ms  "
        f"FPR={fpr:.4f}"
    )


if __name__ == "__main__":
    main()
