"""Artifact relocation keeps existing model environment settings usable."""

from pathlib import Path

import pytest

from backend.core import config


@pytest.mark.parametrize("absolute", [False, True])
def test_legacy_model_environment_path_is_relocated(monkeypatch, absolute):
    relative = Path("backend/models/CustomML/outputs/best.pt")
    configured = config.REPO_ROOT / relative if absolute else relative
    monkeypatch.setenv("FIXTURE_MODEL_PATH", str(configured))
    assert config.environment_path("FIXTURE_MODEL_PATH", Path("unused")) == (
        config.MODELS_ROOT / "CustomML/outputs/best.pt"
    )


def test_external_model_path_is_preserved(monkeypatch, workspace_tmp_path):
    external = workspace_tmp_path / "custom/model.pt"
    monkeypatch.setenv("FIXTURE_MODEL_PATH", str(external))
    assert config.environment_path("FIXTURE_MODEL_PATH", Path("unused")) == external
