import shutil
import unittest
import uuid
import json
from unittest.mock import patch
from pathlib import Path

import numpy as np
from PIL import Image

from gc10_data import (
    CLASS_NAMES,
    capture_group,
    parse_annotation,
    prepare_manifest,
    split_records,
)
from train_gc10 import calculate_metrics


class Gc10Tests(unittest.TestCase):
    def setUp(self):
        self.root = (
            Path(__file__).resolve().parent / "evaluation_reports" / f"test_gc10_{uuid.uuid4().hex}"
        )
        (self.root / "lable").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root)

    def annotation(self, filename, labels):
        path = self.root / "lable" / f"{Path(filename).stem}.xml"
        objects = "".join(
            f"<object><name>{label}</name><bndbox><xmin>1</xmin><ymin>1</ymin><xmax>7</xmax><ymax>7</ymax></bndbox></object>"
            for label in labels
        )
        path.write_text(
            f"<annotation><filename>{filename}</filename><size><width>8</width><height>8</height></size>{objects}</annotation>"
        )
        return path

    def test_explicit_alias_and_multiple_labels(self):
        path = self.annotation("img_01_123_00001.jpg", ["7_yiwu", "10_yaozhed"])
        _, _, labels, repairs = parse_annotation(path)
        self.assertEqual(labels, [6, 9])
        self.assertEqual(repairs["10_yaozhed"], 1)

    def test_unknown_label_and_empty_annotation_fail(self):
        for labels in (["d"], []):
            with self.assertRaises(ValueError):
                parse_annotation(self.annotation("img_01_123_00001.jpg", labels))

    def test_verified_duplicate_copies_are_deduplicated(self):
        filename = "img_01_123_00001.jpg"
        for folder in ("1", "2"):
            (self.root / folder).mkdir()
            Image.new("RGB", (8, 8), (30, 40, 50)).save(self.root / folder / filename, format="PNG")
        self.annotation(filename, ["7_yiwu"])
        records, summary = prepare_manifest(self.root)
        self.assertEqual(len(records), 1)
        self.assertEqual(summary["duplicate_copies_removed"], 1)
        Image.new("RGB", (8, 8), (90, 40, 50)).save(self.root / "2" / filename, format="PNG")
        records, summary = prepare_manifest(self.root)
        self.assertEqual(records, [])
        self.assertEqual(summary["excluded_annotations"][0]["reason"], "conflicting_image_copies")

    def test_capture_views_share_group(self):
        self.assertEqual(
            capture_group("img_01_123_00001.jpg"), capture_group("img_08_123_00002.jpg")
        )
        with self.assertRaises(ValueError):
            capture_group("unknown.jpg")

    def test_group_splits_are_disjoint_and_reproducible(self):
        records = [
            dict(capture_group=str(group), labels=list(range(len(CLASS_NAMES))))
            for group in range(30)
            for _ in range(2)
        ]
        splits, targets = split_records(records)
        repeated, _ = split_records(records)
        groups = {
            name: {records[int(index)]["capture_group"] for index in indices}
            for name, indices in splits.items()
        }
        for name in splits:
            np.testing.assert_array_equal(splits[name], repeated[name])
            self.assertTrue((targets[splits[name]].sum(0) > 0).all())
        self.assertFalse(groups["train"] & groups["val"])
        self.assertFalse(groups["train"] & groups["test"])
        self.assertFalse(groups["val"] & groups["test"])

    def test_metrics_require_exact_label_set(self):
        targets = np.eye(len(CLASS_NAMES), dtype=int)
        probabilities = targets * 0.8 + 0.1
        result = calculate_metrics(targets, probabilities, [0.5] * len(CLASS_NAMES))
        self.assertEqual(result["macro_f1"], 1)
        self.assertEqual(result["exact_match_accuracy"], 1)
        probabilities[0, 1] = 0.9
        result = calculate_metrics(targets, probabilities, [0.5] * len(CLASS_NAMES))
        self.assertEqual(result["exact_match_accuracy"], 0.9)

    def test_feature_normalization_uses_training_only(self):
        import torch
        from train_gc10 import fit_head

        features = torch.arange(60, dtype=torch.float32).reshape(20, 3)
        features[16:] = 10000
        targets = torch.tensor(
            [[index % 2] * len(CLASS_NAMES) for index in range(20)], dtype=torch.float32
        )
        splits = dict(train=np.arange(12), val=np.arange(12, 16), test=np.arange(16, 20))
        _, mean, std, _ = fit_head(features, targets, splits, epochs=1)
        torch.testing.assert_close(mean, features[:12].mean(0))
        torch.testing.assert_close(std, features[:12].std(0))

    def test_unconfigured_experiment_does_not_show_another_runs_metrics(self):
        from gc10_runtime import metrics_payload

        with patch("gc10_runtime.output_directory", return_value=self.root):
            self.assertEqual(metrics_payload()["status"], "not_trained")
            (self.root / "metrics.json").write_text(json.dumps(dict(status="trained")))
            self.assertFalse(metrics_payload()["model_available"])


if __name__ == "__main__":
    unittest.main()
