"""Comparison and metrics normalization utilities.

This module converts legacy/custom metrics into a shared schema and computes
deterministic winners consumed by frontend comparison dashboards.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from fastapi import HTTPException


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

    parts = raw.split()
    if not parts:
        return None

    try:
        num = float(parts[0])
    except ValueError:
        return None

    unit = parts[1] if len(parts) > 1 else "seconds"
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

    total = float(np.sum(cm_np))
    fprs: List[float] = []
    for i in range(cm_np.shape[0]):
        tp = cm_np[i, i]
        fp = float(np.sum(cm_np[:, i]) - tp)
        fn = float(np.sum(cm_np[i, :]) - tp)
        tn = total - (tp + fp + fn)
        denom = fp + tn
        fprs.append((fp / denom) if denom > 0 else 0.0)
    return float(np.mean(fprs)) if fprs else 0.0


def _safe_pct(value: Optional[float]) -> Optional[float]:
    if not _is_number(value):
        return None
    return round(float(value) * 100.0, 1)


def _derive_feature_importance(metrics: Dict) -> List[Dict]:
    details = metrics.get("details") or {}
    per_class = details.get("per_class_metrics") or []
    if isinstance(per_class, list) and per_class:
        rows = []
        for item in per_class:
            name = str(item.get("class_name", "Unknown"))
            f1 = item.get("f1")
            recall = item.get("recall")
            if _is_number(f1):
                importance = max(1.0, min(100.0, float(f1) * 100.0))
            elif _is_number(recall):
                importance = max(1.0, min(100.0, float(recall) * 100.0))
            else:
                importance = 50.0
            rows.append(
                {
                    "feature": f"{name} pattern quality",
                    "importance": round(float(importance), 1),
                    "description": f"Derived from class-level evaluation performance for {name}.",
                }
            )
        rows.sort(key=lambda x: x["importance"], reverse=True)
        return rows[:6]

    core = metrics.get("core") or {}
    fallback = []
    for feature, raw in [
        ("Classification consistency", core.get("f1")),
        ("Class separation", core.get("precision")),
        ("Detection coverage", core.get("recall")),
        ("Prediction confidence", core.get("confidence")),
    ]:
        pct = _safe_pct(raw)
        if pct is None:
            continue
        fallback.append(
            {
                "feature": feature,
                "importance": pct,
                "description": f"Estimated from aggregate {feature.lower()} metric.",
            }
        )
    return fallback


def _derive_focus_areas(metrics: Dict) -> List[str]:
    details = metrics.get("details") or {}
    per_class = details.get("per_class_metrics") or []
    if isinstance(per_class, list) and per_class:
        sorted_rows = sorted(
            per_class,
            key=lambda r: float(r.get("recall", 0.0)) if _is_number(r.get("recall")) else 0.0,
        )
        low = [str(r.get("class_name", "Unknown")) for r in sorted_rows[:2]]
        high = [str(r.get("class_name", "Unknown")) for r in sorted_rows[-2:]]
        areas: List[str] = []
        if high:
            areas.append(f"Strongest classes: {', '.join(high)}")
        if low:
            areas.append(f"Needs review: {', '.join(low)}")
        return areas

    classes = (metrics.get("metadata") or {}).get("classes") or []
    if classes:
        return [f"Class coverage: {', '.join(map(str, classes[:4]))}"]
    return []


def _derive_advantages(metrics: Dict, model_hint: str) -> List[str]:
    core = metrics.get("core") or {}
    ops = metrics.get("ops") or {}
    inf_ms = (core.get("inference_ms") or {}).get("mean")
    size_mb = ops.get("model_size_mb")
    acc = core.get("accuracy")
    fpr = ops.get("false_positive_rate")

    advantages: List[str] = []
    if _is_number(inf_ms):
        advantages.append(f"Average inference latency: {float(inf_ms):.2f} ms.")
    if _is_number(size_mb):
        advantages.append(f"Model size: {float(size_mb):.2f} MB.")
    if _is_number(acc):
        advantages.append(f"Evaluation accuracy: {float(acc) * 100:.1f}%.")
    if _is_number(fpr):
        advantages.append(f"False positive rate: {float(fpr) * 100:.2f}%.")
    if model_hint == "automl":
        advantages.append("AutoML offers simpler deployment and maintenance workflow.")
    if model_hint == "custom":
        advantages.append("Custom ML allows architecture and training control for tuning.")
    return advantages[:4]


def _ensure_explainability(metrics: Dict, model_hint: str) -> Dict:
    explain = metrics.get("explainability")
    if not isinstance(explain, dict):
        explain = {}

    feature_importance = explain.get("feature_importance")
    if not isinstance(feature_importance, list) or len(feature_importance) == 0:
        feature_importance = _derive_feature_importance(metrics)

    focus_areas = explain.get("focus_areas")
    if not isinstance(focus_areas, list) or len(focus_areas) == 0:
        focus_areas = _derive_focus_areas(metrics)

    advantages = explain.get("advantages")
    if not isinstance(advantages, list) or len(advantages) == 0:
        advantages = _derive_advantages(metrics, model_hint)

    metrics["explainability"] = {
        "feature_importance": feature_importance,
        "focus_areas": focus_areas,
        "advantages": advantages,
    }
    return metrics


def read_json_file(path: Path) -> Dict:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Metrics file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON {path}: {exc}")


def normalize_metrics(
    raw: Dict, metrics_path: Path, model_path: Path, class_names: List[str]
) -> Dict:
    # If the file already matches the v2 schema, keep it untouched.
    if isinstance(raw.get("metadata"), dict) and isinstance(raw.get("core"), dict):
        return raw

    report = raw.get("classification_report", {})
    macro = report.get("macro avg", {})
    cm = raw.get("confusion_matrix", [])

    test_acc = raw.get("test_acc")
    accuracy = test_acc if _is_number(test_acc) else report.get("accuracy", 0.0)

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
            "classes": raw.get("classes", class_names),
        },
        "core": {
            "accuracy": float(accuracy) if _is_number(accuracy) else 0.0,
            "precision": float(macro.get("precision", 0.0)),
            "recall": float(macro.get("recall", 0.0)),
            "f1": float(macro.get("f1-score", 0.0)),
            "confidence": None,
            "inference_ms": {"mean": None, "p50": None, "p95": None, "min": None, "max": None},
        },
        "ops": {
            "training_time": None,
            "model_size_mb": model_size_mb,
            "gpu_required": False,
            "setup_complexity": "medium",
            "false_positive_rate": _compute_macro_fpr(cm) if cm else None,
        },
        "explainability": {"feature_importance": [], "focus_areas": [], "advantages": []},
        "details": {"confusion_matrix": cm},
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


def build_comparison(automl_metrics: Dict, custom_metrics: Dict) -> Dict:
    automl_metrics = _ensure_explainability(automl_metrics, "automl")
    custom_metrics = _ensure_explainability(custom_metrics, "custom")

    # Core comparison set for the main table/cards. Higher/lower direction is explicit.
    metric_specs = [
        (
            "accuracy",
            "Accuracy",
            True,
            automl_metrics["core"].get("accuracy"),
            custom_metrics["core"].get("accuracy"),
        ),
        (
            "precision",
            "Precision",
            True,
            automl_metrics["core"].get("precision"),
            custom_metrics["core"].get("precision"),
        ),
        (
            "recall",
            "Recall",
            True,
            automl_metrics["core"].get("recall"),
            custom_metrics["core"].get("recall"),
        ),
        (
            "f1",
            "F1 Score",
            True,
            automl_metrics["core"].get("f1"),
            custom_metrics["core"].get("f1"),
        ),
        # Confidence measures certainty, not correctness or calibration.
        (
            "confidence",
            "Confidence",
            None,
            automl_metrics["core"].get("confidence"),
            custom_metrics["core"].get("confidence"),
        ),
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
        if higher_is_better is not None and _is_number(automl_val) and _is_number(custom_val):
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
        "summary": {"winner": winner, "reason": " | ".join(reason_parts)},
    }
