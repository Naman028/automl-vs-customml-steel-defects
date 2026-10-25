"""Small HTTP and provider fixtures; no checkpoints, datasets, or GCP SDK needed."""

from dataclasses import replace
import io
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient
from PIL import Image
import pytest

from backend.api import app
from backend.inference import neu as inference
from backend.inference.routing import optional_prediction
from backend.integrations import vertex_ai as vertex


@pytest.fixture
def client():
    return TestClient(app.app)


def image_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), (20, 40, 60)).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.parametrize(
    "filename,content,mime,status",
    [
        ("file.txt", b"text", "text/plain", 415),
        ("bad.png", b"not an image", "image/png", 400),
        ("empty.png", b"", "image/png", 400),
    ],
)
def test_upload_validation(client, filename, content, mime, status):
    response = client.post("/predict", files={"file": (filename, content, mime)})
    assert response.status_code == status


def test_upload_size_limit(client, monkeypatch):
    from backend.api import uploads

    monkeypatch.setattr(uploads, "SETTINGS", replace(uploads.SETTINGS, max_upload_bytes=4))
    response = client.post("/predict", files={"file": ("image.png", image_bytes(), "image/png")})
    assert response.status_code == 413


def test_batch_limit(client):
    files = [
        ("files", (f"{index}.png", b"x", "image/png"))
        for index in range(inference.MAX_BATCH_FILES + 1)
    ]
    assert client.post("/predict/batch", files=files).status_code == 400


def test_both_mode_keeps_custom_result_when_automl_fails(client, monkeypatch):
    expected = {"predicted_class": "Crazing", "confidence": 0.8}
    monkeypatch.setattr(inference, "infer", lambda image: expected.copy())
    monkeypatch.setattr(inference, "AUTOML_TFLITE_AVAILABLE", True)
    monkeypatch.setattr(
        inference, "_automl_tflite_predict", Mock(side_effect=RuntimeError("fixture failure"))
    )
    response = client.post(
        "/predict?model_type=both", files={"file": ("image.png", image_bytes(), "image/png")}
    )
    assert response.status_code == 200
    assert response.json()["custom"] == expected
    assert response.json()["automl"] is None


def test_local_tflite_has_priority_over_vertex():
    local, cloud = Mock(return_value={"source": "local"}), Mock()
    assert optional_prediction(Image.new("RGB", (1, 1)), local, cloud, "test")[0] == {
        "source": "local"
    }
    cloud.assert_not_called()


def test_vertex_fallback_is_mocked(monkeypatch):
    monkeypatch.setattr(
        vertex,
        "SETTINGS",
        replace(
            vertex.SETTINGS,
            enable_vertex=True,
            project_id="fixture-project",
            endpoint_id="fixture-endpoint",
        ),
    )
    endpoint = Mock()
    endpoint.predict.return_value = SimpleNamespace(
        predictions=[{"displayNames": ["Crazing"], "confidences": [0.8]}]
    )
    monkeypatch.setattr(vertex, "_endpoint", lambda: endpoint)
    prediction, error = optional_prediction(
        Image.new("RGB", (8, 8)), None, vertex.predict_with_automl, "test"
    )
    assert error is None and prediction["predicted_class"] == "Crazing"
    endpoint.predict.assert_called_once()


def test_vertex_disabled_without_opt_in(monkeypatch):
    monkeypatch.setattr(vertex, "SETTINGS", replace(vertex.SETTINGS, enable_vertex=False))
    with pytest.raises(ValueError, match="disabled"):
        vertex.predict_with_automl(Image.new("RGB", (8, 8)))
