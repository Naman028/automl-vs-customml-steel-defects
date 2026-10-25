"""Content-only inference controls; diagnostic perturbations are not new holdouts."""

import argparse
import json
import logging
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from ml.evaluate_shared import BASE, CLASSES, adapters, manifest, summarize

LOGGER = logging.getLogger(__name__)
SEED = 42
PERMUTATION_COUNT = 1000


def write_control_image(source, destination, condition, random_generator):
    if condition == "opaque_original":
        shutil.copyfile(source, destination)
        return
    with Image.open(source) as original:
        image = original.convert("RGB")
    if condition == "blank":
        image = Image.new("RGB", image.size, (127, 127, 127))
    elif condition == "shuffled_pixels":
        pixels = np.asarray(image).copy()
        pixels = random_generator.permutation(pixels.reshape(-1, 3)).reshape(pixels.shape)
        image = Image.fromarray(pixels)
    elif condition == "blur_low_contrast":
        image = ImageEnhance.Contrast(image.filter(ImageFilter.GaussianBlur(radius=3))).enhance(0.5)
    else:
        raise ValueError(f"Unknown control: {condition}")
    image.save(destination, format="PNG")


def independently_check_metrics(frame, model_name, threshold):
    actual = frame.true_label.to_numpy()
    raw = frame[f"{model_name}_prediction"].to_numpy()
    deployed = np.where(frame[f"{model_name}_confidence"] >= threshold, raw, "Unknown")
    precision, recall, f1, _ = precision_recall_fscore_support(
        actual, deployed, labels=CLASSES, average="macro", zero_division=0
    )
    expected = dict(
        accuracy=accuracy_score(actual, deployed),
        precision=precision,
        recall=recall,
        f1=f1,
    )
    calculated = summarize(frame, model_name, threshold)["core"]
    for metric, value in expected.items():
        if not np.isclose(value, calculated[metric]):
            raise AssertionError(
                f"{model_name}: {metric} differs from independent sklearn calculation"
            )
    generator = np.random.default_rng(SEED)
    shuffled_scores = [
        accuracy_score(generator.permutation(actual), raw) for _ in range(PERMUTATION_COUNT)
    ]
    return dict(
        raw_accuracy=float(accuracy_score(actual, raw)),
        deployed_accuracy=float(expected["accuracy"]),
        coverage=float(np.mean(deployed != "Unknown")),
        mean_confidence=float(frame[f"{model_name}_confidence"].mean()),
        shuffled_label_mean_accuracy=float(np.mean(shuffled_scores)),
        shuffled_label_max_accuracy=float(np.max(shuffled_scores)),
        independent_sklearn_check="passed",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument("--baseline-csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.out_dir.exists():
        parser.error("Output directory must be new")
    original = manifest(args.test_dir).sample(frac=1, random_state=SEED).reset_index(drop=True)
    baseline = pd.read_csv(args.baseline_csv)
    if set(original.sha256) != set(baseline.sha256):
        parser.error("Baseline CSV and test images do not match")
    predictors = adapters(
        BASE / "CustomML/outputs/best.pt",
        BASE / "AutoML/AutoML model.tflite",
        BASE / "AutoML/labels.txt",
    )[:2]
    args.out_dir.mkdir(parents=True)
    control_path = args.out_dir / "input.png"
    report = dict(
        sample_count=len(original),
        seed=SEED,
        permutation_count=PERMUTATION_COUNT,
        independence_verified=False,
        conditions={},
        limitation="Controls and synthetic perturbations test evaluator behavior, not independent generalization.",
    )
    baseline_by_hash = baseline.set_index("sha256")
    for condition in (
        "opaque_original",
        "blank",
        "shuffled_pixels",
        "blur_low_contrast",
    ):
        LOGGER.info("Running condition=%s samples=%d", condition, len(original))
        frame = original.copy()
        generator = np.random.default_rng(SEED)
        predictions = {"custom": [], "automl": []}
        for row in frame.itertuples():
            # Both adapters receive only the same opaque path, never labels or source paths.
            write_control_image(row.image_path, control_path, condition, generator)
            for model_name, predictor in zip(("custom", "automl"), predictors):
                predictions[model_name].append(predictor(control_path))
        condition_result = {}
        for model_name, threshold in (("custom", 0.55), ("automl", 0.0)):
            for index, suffix in enumerate(("prediction", "confidence", "inference_ms")):
                frame[f"{model_name}_{suffix}"] = [
                    result[index] for result in predictions[model_name]
                ]
            condition_result[model_name] = independently_check_metrics(frame, model_name, threshold)
            if condition == "opaque_original":
                expected = baseline_by_hash.loc[frame.sha256, f"{model_name}_prediction"].to_numpy()
                matches = frame[f"{model_name}_prediction"].to_numpy() == expected
                if not matches.all():
                    raise AssertionError("Renaming/reordering changed model predictions")
                condition_result[model_name]["baseline_prediction_agreement"] = float(
                    matches.mean()
                )
        frame.to_csv(args.out_dir / f"{condition}.csv", index=False)
        report["conditions"][condition] = condition_result
        LOGGER.info("Completed condition=%s results=%s", condition, condition_result)
    (args.out_dir / "controls.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
