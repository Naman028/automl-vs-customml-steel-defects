"""Optional Vertex AI endpoint adapter; importing it never contacts Google Cloud."""

import base64
import io
from typing import Any

from PIL import Image

from config import SETTINGS
from label_normalization import automl_to_short_code, normalize_automl_label


def _endpoint() -> Any:
    from google.cloud import aiplatform

    aiplatform.init(project=SETTINGS.project_id, location=SETTINGS.region)
    return aiplatform.Endpoint(SETTINGS.endpoint_id)


def predict_with_automl(image: Image.Image) -> dict[str, Any]:
    """Call only an explicitly enabled endpoint, preserving the exported API shape."""
    if not SETTINGS.enable_vertex or not SETTINGS.project_id or not SETTINGS.endpoint_id:
        raise ValueError("Vertex AI is disabled or its project/endpoint configuration is missing")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    content = base64.b64encode(buffer.getvalue()).decode("utf-8")
    response = _endpoint().predict(
        instances=[{"content": content}],
        parameters={"confidenceThreshold": 0.5, "maxPredictions": 5},
    )
    predictions = response.predictions[0] if response.predictions else {}
    names = predictions.get("displayNames", [])
    confidences = predictions.get("confidences", [])
    top_class = normalize_automl_label(names[0]) if names else "Unknown"
    confidence = float(confidences[0]) if names and confidences else (0.5 if names else 0.0)
    probabilities: dict[str, float] = {}
    for name, probability in zip(names, confidences):
        label = normalize_automl_label(name)
        probabilities[label] = probabilities.get(label, 0.0) + float(probability)
    return {
        "predicted_class": top_class,
        "confidence": confidence,
        "all_probabilities": probabilities,
        "raw_top_class": automl_to_short_code(top_class),
        "threshold": 0.5,
        "inference_time_ms": 0,
        "model_type": "automl",
    }
