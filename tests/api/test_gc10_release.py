"""Compact release checkpoints reconstruct the original frozen-backbone predictions."""

from dataclasses import replace
import hashlib

import pytest
import torch

from backend.inference import gc10


class FixtureBackbone(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.body = torch.nn.Linear(2, 2, bias=False)

    def forward(self, features):
        return self.body(features)


@pytest.fixture
def checkpoints(workspace_tmp_path, monkeypatch):
    backbone = FixtureBackbone()
    head = torch.nn.Linear(2, 2)
    custom_path = workspace_tmp_path / "neu.pt"
    torch.save({"model_state_dict": backbone.state_dict()}, custom_path)
    common = {
        "head": head.state_dict(),
        "mean": torch.zeros(2),
        "std": torch.ones(2),
        "classes": ["first", "second"],
        "thresholds": [0.5, 0.5],
    }
    full_path, head_path = workspace_tmp_path / "full.pt", workspace_tmp_path / "head.pt"
    torch.save(dict(common, backbone=backbone.state_dict()), full_path)
    compact = dict(
        common,
        format="gc10-head-v1",
        backbone_sha256=hashlib.sha256(custom_path.read_bytes()).hexdigest(),
    )
    torch.save(compact, head_path)
    monkeypatch.setattr(gc10, "SETTINGS", replace(gc10.SETTINGS, custom_model=custom_path))
    monkeypatch.setattr(gc10, "create_backbone", lambda: (FixtureBackbone(), 2))
    gc10.load_model.cache_clear()
    try:
        yield full_path, head_path, custom_path
    finally:
        gc10.load_model.cache_clear()


def test_head_only_checkpoint_matches_full_checkpoint(checkpoints):
    features = torch.tensor([[0.2, 0.7], [0.8, 0.1]])
    predictions = []
    for path in checkpoints[:2]:
        backbone, head, checkpoint = gc10.load_model(str(path))
        with torch.inference_mode():
            predictions.append(
                torch.sigmoid(head((backbone(features) - checkpoint["mean"]) / checkpoint["std"]))
            )
    torch.testing.assert_close(predictions[0], predictions[1], rtol=0, atol=0)


def test_head_rejects_different_backbone_file(checkpoints):
    _, head_path, custom_path = checkpoints
    custom_path.write_bytes(b"wrong model")
    with pytest.raises(ValueError, match="matching NEU backbone"):
        gc10.load_model(str(head_path))
