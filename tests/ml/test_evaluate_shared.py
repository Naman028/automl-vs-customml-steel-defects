import shutil
import unittest
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.evaluate_shared import CLASSES, audit_overlap, manifest, summarize


class SharedEvaluationTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame(
            dict(
                true_label=CLASSES,
                custom_prediction=CLASSES,
                custom_confidence=[0.9] * 5 + [0.2],
                custom_inference_ms=[1.0] * 6,
            )
        )

    def test_unknown_counts_as_missed_support(self):
        result = summarize(self.frame(), "custom", 0.55)
        cm = np.array(result["details"]["confusion_matrix_with_unknown"])
        self.assertEqual(cm.shape, (6, 7))
        self.assertEqual(cm.sum(), 6)
        self.assertEqual(cm[5, 6], 1)
        self.assertEqual(result["core"]["accuracy"], 5 / 6)
        self.assertEqual(result["details"]["per_class_metrics"][5]["recall"], 0)
        self.assertEqual(result["details"]["per_class_metrics"][5]["support"], 1)
        self.assertEqual(result["core"]["raw_argmax_accuracy"], 1)

    def test_unknown_does_not_create_false_positive(self):
        frame = self.frame()
        frame.loc[5, "true_label"] = CLASSES[0]
        result = summarize(frame, "custom", 0.55)
        self.assertEqual(result["details"]["per_class_metrics"][0]["precision"], 1)
        self.assertEqual(result["details"]["per_class_metrics"][0]["recall"], 0.5)

    def test_mismatch_and_invalid_confidence_fail(self):
        for column, value in [
            ("custom_prediction", "Scratch"),
            ("true_label", "Rust"),
            ("custom_confidence", float("nan")),
        ]:
            frame = self.frame()
            frame.loc[0, column] = value
            with self.assertRaises(ValueError):
                summarize(frame, "custom", 0.55)

    def test_error_pair_and_false_positive(self):
        frame = self.frame()
        frame.loc[0, "custom_prediction"] = CLASSES[1]
        result = summarize(frame, "custom", 0)
        self.assertEqual(result["details"]["per_class_metrics"][1]["precision"], 0.5)
        self.assertEqual(result["details"]["error_pairs"][0]["count"], 1)
        self.assertEqual(result["core"]["accuracy"], 5 / 6)

    def test_comparison_winner_directions_and_ties(self):
        from backend.services.comparison import build_comparison

        automl = summarize(self.frame(), "custom", 0.55)
        custom = summarize(self.frame(), "custom", 0)
        automl["ops"]["model_size_mb"] = 1
        custom["ops"]["model_size_mb"] = 2
        result = build_comparison(automl, custom)
        self.assertEqual(result["per_metric_winners"]["accuracy"], "custom")
        self.assertEqual(result["per_metric_winners"]["model_size_mb"], "automl")
        self.assertEqual(result["per_metric_winners"]["inference_ms_mean"], "tie")
        self.assertEqual(result["per_metric_winners"]["confidence"], "none")

    def test_manifest_and_leakage(self):
        from PIL import Image

        root = Path(__file__).resolve().parents[2] / "reports/runs" / f"test-{uuid.uuid4().hex}"
        root.mkdir(parents=True)
        try:
            for i, label in enumerate(CLASSES):
                (root / "test" / label).mkdir(parents=True)
                Image.new("RGB", (8, 8), (i * 30, 0, 0)).save(root / "test" / label / "a.png")
            frame = manifest(root / "test")
            (root / "train").mkdir()
            Image.new("RGB", (8, 8), (0, 0, 0)).save(root / "train" / "duplicate.bmp")
            with self.assertRaisesRegex(ValueError, "overlap"):
                audit_overlap(frame, [root / "train"])
            Image.new("RGB", (8, 8), (0, 0, 0)).save(root / "test" / CLASSES[0] / "b.bmp")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                manifest(root / "test")
        finally:
            # The directory is a unique child of this test's report root.
            shutil.rmtree(root)

    @pytest.mark.requires_weights
    @unittest.skipUnless(
        (Path(__file__).resolve().parents[2] / "models/AutoML/AutoML model.tflite").exists(),
        "Local TFLite export is unavailable",
    )
    def test_automl_export_contract_and_quantization(self):
        from backend.inference.automl_contract import read_contract, embedded_labels, prepare_image
        from PIL import Image

        model = Path(__file__).resolve().parents[2] / "models/AutoML/AutoML model.tflite"
        contract = read_contract(str(model.resolve()))
        self.assertEqual(contract, {"mean": [127.5], "std": [127.5]})
        expected_labels = (model.parent / "labels.txt").read_text().splitlines()
        self.assertEqual(embedded_labels(model), expected_labels)
        details = dict(shape=[1, 1, 3, 3], dtype=np.uint8, quantization=(1 / 127, 128))
        pixels = np.array([[[0, 0, 0], [127, 127, 127], [255, 255, 255]]], dtype=np.uint8)
        result = prepare_image(Image.fromarray(pixels), details, contract)
        self.assertEqual(result.shape, (1, 1, 3, 3))
        np.testing.assert_array_equal(result[0, 0, :, 0], [1, 128, 255])
        details["dtype"] = np.float32
        result = prepare_image(Image.fromarray(pixels), details, contract)
        np.testing.assert_allclose(result[0, 0, [0, 2], 0], [-1.0, 1.0])

    def test_training_guard_and_audit_detect_reencoded_overlap(self):
        from PIL import Image
        from ml.neu.trainer.dataset_integrity import validate_dataset_splits
        from ml.audit_dataset import audit

        root = Path(__file__).resolve().parents[2] / "reports/runs" / f"test-{uuid.uuid4().hex}"
        root.mkdir(parents=True)
        try:
            generator = np.random.default_rng(42)
            for split in ("train", "val", "test"):
                for label in CLASSES:
                    folder = root / split / label
                    folder.mkdir(parents=True)
                    pixels = generator.integers(0, 256, size=(16, 16, 3), dtype=np.uint8)
                    Image.fromarray(pixels).save(folder / "image.png")
            summary = validate_dataset_splits(root)
            self.assertEqual(summary["exact_duplicate_check"], "passed")
            source = root / "train" / CLASSES[0] / "image.png"
            destination = root / "test" / CLASSES[0] / "image.png"
            destination.unlink()
            with Image.open(source) as image:
                image.save(destination.with_suffix(".bmp"))
            with self.assertRaisesRegex(ValueError, "Duplicate decoded_sha256"):
                validate_dataset_splits(root)
            _, candidates, _, result = audit(root)
            self.assertEqual(len(result["exact_cross_split_groups"]["sha256"]), 0)
            self.assertEqual(len(result["exact_cross_split_groups"]["decoded_sha256"]), 1)
            self.assertTrue((candidates.phash_distance == 0).any())
        finally:
            shutil.rmtree(root)

    def test_independent_metric_cross_check(self):
        from ml.audit_predictions import independently_check_metrics

        result = independently_check_metrics(self.frame(), "custom", 0.55)
        self.assertEqual(result["independent_sklearn_check"], "passed")
        self.assertEqual(result["deployed_accuracy"], 5 / 6)

    def test_threshold_sweep_uses_raw_correctness(self):
        frame = self.frame()
        frame["custom_probabilities"] = np.eye(len(CLASSES)).tolist()
        result = summarize(frame, "custom", 0.55)
        self.assertEqual(result["core"]["accuracy"], 5 / 6)
        self.assertEqual(result["details"]["threshold_metrics"]["recall"][0], 1)
        self.assertEqual(len(result["details"]["pr_curves"]), len(CLASSES))


if __name__ == "__main__":
    unittest.main()
