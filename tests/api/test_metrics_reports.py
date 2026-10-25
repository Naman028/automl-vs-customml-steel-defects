"""Verify dashboard values come from generated reports, using tiny fixtures."""

import json

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.api import app
from backend.inference import gc10 as gc10_runtime
from ml.evaluation_metrics import calculate_metrics, summarize
from ml.evaluate_shared import CLASSES


def test_neu_dashboard_matches_fixture_evaluator(workspace_tmp_path, monkeypatch):
    tmp_path = workspace_tmp_path
    frame = pd.DataFrame(
        dict(
            true_label=CLASSES,
            fixture_prediction=CLASSES,
            fixture_confidence=[0.9] * len(CLASSES),
            fixture_inference_ms=[1.0] * len(CLASSES),
        )
    )
    generated = summarize(frame, "fixture", 0.55)
    generated["metadata"] = {"classes": CLASSES}
    for name in ["neu_automl.json", "neu_custom.json"]:
        path = tmp_path / "benchmarks" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(generated))
    monkeypatch.setattr(app, "REPORTS_ROOT", tmp_path)
    response = TestClient(app.app).get("/compare/metrics")
    assert response.status_code == 200
    assert response.json()["automl"]["core"] == generated["core"]
    assert response.json()["custom"]["core"] == generated["core"]


def test_gc10_dashboard_matches_fixture_evaluator(workspace_tmp_path, monkeypatch):
    tmp_path = workspace_tmp_path
    targets = np.eye(10, dtype=int)
    generated = calculate_metrics(targets, targets * 0.8 + 0.1, [0.5] * 10)
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({"status": "trained", "test": generated}))
    monkeypatch.setattr(gc10_runtime, "output_directory", lambda: tmp_path)
    response = TestClient(app.app).get("/gc10/metrics")
    assert response.status_code == 200
    assert response.json()["test"] == generated
    assert response.json()["model_available"] is False


def test_dashboard_does_not_fall_back_to_legacy_training_results(workspace_tmp_path, monkeypatch):
    monkeypatch.setattr(app, "REPORTS_ROOT", workspace_tmp_path)
    report = {"metadata": {}, "core": {}, "ops": {}}
    automl = workspace_tmp_path / "benchmarks/neu_automl.json"
    automl.parent.mkdir(parents=True)
    automl.write_text(json.dumps(report))
    legacy = workspace_tmp_path / "models/CustomML/outputs/metrics.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text(json.dumps({"test_acc": 1.0}))
    assert TestClient(app.app).get("/compare/metrics").status_code == 404
