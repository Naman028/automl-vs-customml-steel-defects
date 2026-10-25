"""Optional local artifact checks, explicitly excluded from small-fixture CI."""

import json
import os
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.requires_weights,
    pytest.mark.requires_datasets,
    pytest.mark.skipif(
        os.getenv("RUN_ARTIFACT_TESTS") != "true",
        reason="Opt in with RUN_ARTIFACT_TESTS=true after provisioning artifacts",
    ),
]


def test_saved_gc10_groups_and_pixels_do_not_cross_splits():
    path = Path(__file__).resolve().parents[2] / "models/GC10/outputs_local_v1/manifest.json"
    records = json.loads(path.read_text())
    for field in ("capture_group", "decoded_sha256"):
        values = {
            split: {row[field] for row in records if row["split"] == split}
            for split in ("train", "val", "test")
        }
        assert not values["train"] & values["val"]
        assert not values["train"] & values["test"]
        assert not values["val"] & values["test"]
