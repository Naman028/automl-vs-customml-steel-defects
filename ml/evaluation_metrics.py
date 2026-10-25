"""Canonical evaluation mathematics for distinct NEU and GC10 tasks.

Inference, training reports and fixture tests use these functions; no test fitting occurs here.
"""

from typing import Any
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support
from ml.neu.trainer.dataset_integrity import CLASS_NAMES as CLASSES
from ml.gc10_data import CLASS_NAMES as GC10_CLASS_NAMES

Array = NDArray[Any]


def summarize(frame: pd.DataFrame, model: str, threshold: float) -> dict[str, Any]:
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0, 1]")
    raw = frame[f"{model}_prediction"]
    confidence = frame[f"{model}_confidence"].to_numpy(dtype=float)
    if not np.isfinite(confidence).all() or ((confidence < 0) | (confidence > 1)).any():
        raise ValueError("Invalid confidence")
    index = {name: i for i, name in enumerate(CLASSES)}
    if not frame.true_label.isin(CLASSES).all() or not raw.isin(CLASSES).all():
        raise ValueError("Unexpected label")
    actual = frame.true_label.map(index).to_numpy(dtype=int)
    predicted = raw.map(index).to_numpy(dtype=int)
    accepted = confidence >= threshold
    deployed = np.where(accepted, predicted, 6)
    cm = np.zeros((6, 7), dtype=np.int64)
    np.add.at(cm, (actual, deployed), 1)
    tp = np.diag(cm[:, :6]).astype(float)
    support = cm.sum(axis=1)
    predicted_counts = cm[:, :6].sum(axis=0)
    precision = np.divide(tp, predicted_counts, out=np.zeros(6), where=predicted_counts != 0)
    recall = np.divide(tp, support, out=np.zeros(6), where=support != 0)
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros(6),
        where=precision + recall != 0,
    )
    negatives = len(frame) - support
    fpr = np.divide(predicted_counts - tp, negatives, out=np.zeros(6), where=negatives != 0)
    latency = frame[f"{model}_inference_ms"].to_numpy(dtype=float)
    errors = frame[["true_label"]].copy()
    errors["predicted_label"] = np.where(accepted, raw, "Unknown")
    errors = (
        errors[errors.true_label != errors.predicted_label]
        .groupby(["true_label", "predicted_label"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    result: dict[str, Any] = {
        "core": dict(
            accuracy=float(tp.sum() / len(frame)),
            raw_argmax_accuracy=float(np.mean(actual == predicted)),
            precision=float(precision.mean()),
            recall=float(recall.mean()),
            f1=float(f1.mean()),
            confidence=float(confidence.mean()),
            coverage=float(accepted.mean()),
            inference_ms=dict(
                mean=float(latency.mean()),
                p50=float(np.percentile(latency, 50)),
                p95=float(np.percentile(latency, 95)),
                min=float(latency.min()),
                max=float(latency.max()),
            ),
        ),
        "ops": dict(false_positive_rate=float(fpr.mean())),
        "details": dict(
            confusion_matrix=cm[:, :6].tolist(),
            confusion_matrix_with_unknown=cm.tolist(),
            confusion_matrix_columns=CLASSES + ["Unknown"],
            abstentions_by_class=cm[:, 6].tolist(),
            y_true=actual.tolist(),
            y_pred=np.where(accepted, predicted, -1).tolist(),
            raw_y_pred=predicted.tolist(),
            error_pairs=errors.to_dict("records"),
            per_class_metrics=[
                dict(
                    class_name=c,
                    precision=float(precision[i]),
                    recall=float(recall[i]),
                    f1=float(f1[i]),
                    support=int(support[i]),
                    abstentions=int(cm[i, 6]),
                )
                for i, c in enumerate(CLASSES)
            ],
        ),
    }
    probability_column = f"{model}_probabilities"
    if probability_column in frame:
        result["details"].update(probability_details(frame, model, actual, predicted, confidence))
    return result


def probability_details(
    frame: pd.DataFrame, model: str, actual: Array, predicted: Array, confidence: Array
) -> dict[str, Any]:
    from sklearn.metrics import precision_recall_curve

    probabilities = np.asarray(frame[f"{model}_probabilities"].tolist(), dtype=float)
    if probabilities.shape != (len(frame), len(CLASSES)) or not np.isfinite(probabilities).all():
        raise ValueError("Invalid probability matrix")
    curves = {}
    for index, label in enumerate(CLASSES):
        precision, recall, thresholds = precision_recall_curve(
            actual == index, probabilities[:, index]
        )
        curves[label] = dict(
            precision=precision.tolist(),
            recall=recall.tolist(),
            thresholds=thresholds.tolist(),
        )
    thresholds = np.linspace(0, 1, 51)
    accepted = confidence[:, None] >= thresholds
    correct = (actual == predicted)[:, None] & accepted
    accepted_count = accepted.sum(axis=0)
    precision = np.divide(
        correct.sum(axis=0),
        accepted_count,
        out=np.zeros(len(thresholds)),
        where=accepted_count != 0,
    )
    return dict(
        probabilities=probabilities.tolist(),
        pr_curves=curves,
        threshold_metrics=dict(
            thresholds=thresholds.tolist(),
            precision=precision.tolist(),
            recall=(correct.sum(axis=0) / len(frame)).tolist(),
            coverage=accepted.mean(axis=0).tolist(),
        ),
    )


def select_thresholds(targets: Array, probabilities: Array) -> list[float]:
    thresholds = []
    for index in range(len(GC10_CLASS_NAMES)):
        candidates = np.linspace(0.1, 0.9, 17)
        scores = [
            precision_recall_fscore_support(
                targets[:, index],
                probabilities[:, index] >= threshold,
                average="binary",
                zero_division=0,
            )[2]
            for threshold in candidates
        ]
        thresholds.append(float(candidates[int(np.argmax(scores))]))
    return thresholds


def calculate_metrics(
    targets: Array, probabilities: Array, thresholds: list[float]
) -> dict[str, Any]:
    predicted = probabilities >= np.asarray(thresholds)
    precision, recall, f1, support = precision_recall_fscore_support(
        targets, predicted, average=None, zero_division=0
    )
    return dict(
        macro_f1=float(f1.mean()),
        micro_f1=float(
            precision_recall_fscore_support(targets, predicted, average="micro", zero_division=0)[2]
        ),
        mean_average_precision=float(
            average_precision_score(targets, probabilities, average="macro")
        ),
        exact_match_accuracy=float(np.all(targets == predicted, axis=1).mean()),
        per_class=[
            dict(
                class_name=name,
                precision=float(precision[index]),
                recall=float(recall[index]),
                f1=float(f1[index]),
                support=int(support[index]),
                threshold=float(thresholds[index]),
            )
            for index, name in enumerate(GC10_CLASS_NAMES)
        ],
    )
