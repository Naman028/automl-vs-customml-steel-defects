"""Read GC10 experiment results and run the separately trained local model."""

import json
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Any, cast
from PIL import Image

import torch

from backend.inference.gc10_model import create_backbone, image_transform
from backend.core.config import environment_path, MODELS_ROOT, REPORTS_ROOT, SETTINGS

DEFAULT_OUTPUT_DIR = MODELS_ROOT / "GC10/releases/v1.0.0"


def output_directory() -> Path:
    return environment_path("GC10_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def metrics_payload() -> dict[str, Any]:
    path = output_directory() / "metrics.json"
    if not path.exists() and output_directory() == DEFAULT_OUTPUT_DIR:
        path = REPORTS_ROOT / "benchmarks/gc10.json"
    if not path.exists():
        return dict(status="not_trained", task="GC10 image-level multilabel classification")
    payload = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    payload["model_available"] = (output_directory() / "model.pt").exists()
    return payload


@lru_cache(maxsize=1)
def load_model(model_path: str) -> tuple[torch.nn.Module, torch.nn.Linear, dict[str, Any]]:
    checkpoint = cast(dict[str, Any], torch.load(model_path, map_location="cpu", weights_only=True))
    backbone, feature_count = create_backbone()
    if "backbone" in checkpoint:
        backbone_weights = checkpoint["backbone"]
    else:
        if checkpoint.get("format") != "gc10-head-v1":
            raise ValueError("Unsupported GC10 checkpoint format")
        with SETTINGS.custom_model.open("rb") as source:
            identity = hashlib.file_digest(source, "sha256").hexdigest()
        if identity != checkpoint["backbone_sha256"]:
            raise ValueError("GC10 head requires the matching NEU backbone checkpoint")
        neu_checkpoint = torch.load(SETTINGS.custom_model, map_location="cpu", weights_only=True)
        backbone_weights = {
            name: value
            for name, value in neu_checkpoint["model_state_dict"].items()
            if not name.startswith("fc.")
        }
    backbone.load_state_dict(backbone_weights, strict=True)
    head = torch.nn.Linear(feature_count, len(checkpoint["classes"]))
    head.load_state_dict(checkpoint["head"], strict=True)
    return backbone.eval(), head.eval(), checkpoint


def predict(image: Image.Image) -> dict[str, Any]:
    path = output_directory() / "model.pt"
    if not path.exists():
        raise FileNotFoundError("GC10 local model has not been trained")
    backbone, head, checkpoint = load_model(str(path))
    image_tensor = image_transform()(image.convert("RGB")).unsqueeze(0)
    with torch.inference_mode():
        features = (backbone(image_tensor) - checkpoint["mean"]) / checkpoint["std"]
        probabilities = torch.sigmoid(head(features))[0].tolist()
    classes = [
        dict(
            class_name=name,
            probability=probability,
            threshold=threshold,
            predicted=probability >= threshold,
        )
        for name, probability, threshold in zip(
            checkpoint["classes"], probabilities, checkpoint["thresholds"]
        )
    ]
    return dict(
        task="GC10 image-level multilabel classification",
        classes=classes,
        predicted_labels=[item["class_name"] for item in classes if item["predicted"]],
        limitation="Presence predictions only; this model does not localize defects or certify a surface as defect-free.",
    )
