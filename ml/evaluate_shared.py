"""Evaluate both exported models on one manifest; never changes deployed metrics."""

import argparse
import hashlib
import json
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ml.evaluation_metrics import summarize as summarize
from ml.neu.trainer.dataset_integrity import (
    CLASS_NAMES,
    IMAGE_EXTENSIONS,
    image_hashes,
)

BASE = Path(__file__).resolve().parents[1] / "models"
CLASSES = CLASS_NAMES
EXTENSIONS = IMAGE_EXTENSIONS
LOGGER = logging.getLogger(__name__)


def manifest(root):
    root = Path(root).resolve()
    folders = {p.name for p in root.iterdir() if p.is_dir()}
    if folders != set(CLASSES):
        raise ValueError(f"Expected exactly {CLASSES}; got {sorted(folders)}")
    rows = []
    for label in CLASSES:
        images = sorted(p for p in (root / label).rglob("*") if p.suffix.lower() in EXTENSIONS)
        if not images:
            raise ValueError(f"No images for {label}")
        for p in images:
            rows.append(dict(image_path=str(p), true_label=label, **image_hashes(p)))
    frame = pd.DataFrame(rows)
    if frame.sha256.duplicated().any() or frame.decoded_sha256.duplicated().any():
        raise ValueError("Duplicate image contents inside evaluation set")
    return frame


def audit_overlap(frame, reference_dirs):
    """Check byte and decoded-pixel overlap; source independence is unverified."""
    heldout = set(frame.sha256)
    heldout_pixels = set(frame.decoded_sha256)
    for directory in reference_dirs:
        root = Path(directory)
        if not root.is_dir():
            raise ValueError(f"Missing reference directory: {root}")
        for p in root.rglob("*"):
            if p.suffix.lower() not in EXTENSIONS:
                continue
            hashes = image_hashes(p)
            if hashes["sha256"] in heldout or hashes["decoded_sha256"] in heldout_pixels:
                raise ValueError(f"Evaluation/reference image overlap: {p}")


def adapters(custom_path, automl_path, labels_path):
    # Lazy imports keep metric tests independent of Torch/TensorFlow installations.
    from ml.neu.eval_custom_pt import load_model, build_transform
    from ml.automl.eval_automl_tflite import load_interpreter, infer_one
    from backend.inference.automl_contract import embedded_labels
    import torch
    from PIL import Image

    model, device, labels, size = load_model(custom_path)
    transform = build_transform(size)
    if len(labels) != 6 or set(labels) != set(CLASSES):
        raise ValueError(f"Custom checkpoint labels mismatch: {labels}")
    # Preserve output index order; do not use a normalizer that drops duplicates.
    automl_labels = [
        s.strip() for s in labels_path.read_text(encoding="utf-8").splitlines() if s.strip()
    ]
    if len(automl_labels) != 6 or set(automl_labels) != set(CLASSES):
        raise ValueError(f"AutoML labels mismatch: {automl_labels}")
    if automl_labels != embedded_labels(automl_path):
        raise ValueError("AutoML labels differ from embedded output label order")
    interpreter, inputs, outputs = load_interpreter(automl_path)
    if int(np.prod(outputs["shape"])) != 6:
        raise ValueError("AutoML output must contain six class scores")

    def predict_custom(path):
        with Image.open(path) as image:
            x = transform(image.convert("RGB")).unsqueeze(0).to(device)
        if device == "cuda":
            torch.cuda.synchronize()
        started = time.perf_counter()
        with torch.inference_mode():
            probabilities = torch.softmax(model(x), dim=1)[0].cpu().numpy()
        elapsed = (time.perf_counter() - started) * 1000
        idx = int(probabilities.argmax())
        ordered = probabilities[[labels.index(label) for label in CLASSES]]
        return labels[idx], float(probabilities[idx]), elapsed, ordered.tolist()

    def predict_automl(path):
        idx, confidence, elapsed, probabilities = infer_one(
            interpreter, inputs, outputs, Path(path)
        )
        ordered = probabilities[[automl_labels.index(label) for label in CLASSES]]
        return automl_labels[idx], confidence, elapsed, ordered.tolist()

    return (
        predict_custom,
        predict_automl,
        dict(
            input_dtype=str(inputs["dtype"]),
            input_shape=inputs["shape"].tolist(),
            input_quantization=list(inputs["quantization"]),
            normalization=inputs["normalization_contract"],
            label_order_verified_against_export=True,
        ),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument(
        "--reference-dir",
        type=Path,
        action="append",
        required=True,
        help="Training/validation roots from BOTH models; repeat for each root",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="New report directory; must not exist",
    )
    parser.add_argument("--custom-model", type=Path, default=BASE / "CustomML/outputs/best.pt")
    parser.add_argument("--automl-model", type=Path, default=BASE / "AutoML/AutoML model.tflite")
    parser.add_argument("--automl-labels", type=Path, default=BASE / "AutoML/labels.txt")
    parser.add_argument("--custom-threshold", type=float, default=0.55)
    parser.add_argument("--automl-threshold", type=float, default=0.0)
    args = parser.parse_args()
    if args.out_dir.exists():
        parser.error("--out-dir must be a new directory")
    if not all(0 <= t <= 1 for t in (args.custom_threshold, args.automl_threshold)):
        parser.error("Thresholds must be in [0, 1]")
    frame = manifest(args.test_dir)
    audit_overlap(frame, args.reference_dir)
    custom, automl, contract = adapters(args.custom_model, args.automl_model, args.automl_labels)
    # Warm up once; measured latency excludes image loading and preprocessing.
    for name, predict in [("custom", custom), ("automl", automl)]:
        predict(frame.image_path.iloc[0])
        predictions = [predict(path) for path in frame.image_path]
        for i, suffix in enumerate(["prediction", "confidence", "inference_ms", "probabilities"]):
            frame[f"{name}_{suffix}"] = [p[i] for p in predictions]
    fingerprint = hashlib.sha256(
        frame[["true_label", "sha256"]].to_csv(index=False).encode()
    ).hexdigest()
    results = {}
    timestamp = int(time.time())
    for name, path, threshold in [
        ("custom", args.custom_model, args.custom_threshold),
        ("automl", args.automl_model, args.automl_threshold),
    ]:
        payload = summarize(frame, name, threshold)
        model_name = "Custom ML (ResNet18)" if name == "custom" else "AutoML Edge (TFLite)"
        payload["metadata"] = dict(
            model_name=model_name,
            run_id=f"shared_{timestamp}",
            timestamp=timestamp,
            dataset_version=args.test_dir.resolve().name,
            dataset_sha256=fingerprint,
            sample_count=len(frame),
            classes=CLASSES,
            confidence_threshold=threshold,
            model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            evaluation_profile="internal_benchmark",
            reference_dirs=[p.as_posix() for p in args.reference_dir],
            independence_verified=False,
            evaluation_scope="Internal benchmark; independent generalization unverified",
            limitation="File and decoded-pixel overlap checked only; source groups and cloud training-job lineage need verification",
            automl_input_contract=contract,
        )
        payload["ops"].update(
            training_time=None,
            model_size_mb=path.stat().st_size / 1024**2,
            gpu_required=False,
            setup_complexity="medium",
        )
        counts = {
            split: sum(
                1
                for image in (args.test_dir.parent / split).rglob("*")
                if image.suffix.lower() in EXTENSIONS
            )
            for split in ("train", "val")
        }
        counts["test"] = len(frame)
        counts["total"] = sum(counts.values())
        payload["details"]["dataset_counts"] = counts
        results[name] = payload
        frame[f"{name}_deployed_prediction"] = np.where(
            frame[f"{name}_confidence"] >= threshold,
            frame[f"{name}_prediction"],
            "Unknown",
        )
    args.out_dir.mkdir(parents=True, exist_ok=False)
    frame.to_csv(args.out_dir / "predictions.csv", index=False)
    for name, payload in results.items():
        filename = "custom_metrics_v2.json" if name == "custom" else "automl_metrics.json"
        (args.out_dir / filename).write_text(
            json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
        )
        LOGGER.info("Model=%s metrics=%s", name, payload["core"])
    LOGGER.info("Reports=%s; dashboard files were not replaced", args.out_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
