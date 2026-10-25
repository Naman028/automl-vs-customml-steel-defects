"""Typed environment configuration. Optional cloud access is disabled by default."""

from dataclasses import dataclass
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
DATA_ROOT = REPO_ROOT / "data"
MODELS_ROOT = REPO_ROOT / "models"
REPORTS_ROOT = REPO_ROOT / "reports"


def environment_path(name: str, default: Path) -> Path:
    value = os.getenv(name, "").strip()
    path = Path(value) if value else default
    resolved = path if path.is_absolute() else REPO_ROOT / path
    # Existing local environment files may still name the retired artifact directory.
    legacy_root = BACKEND_ROOT / "models"
    if not resolved.exists() and resolved.is_relative_to(legacy_root):
        return MODELS_ROOT / resolved.relative_to(legacy_root)
    return resolved


@dataclass(frozen=True)
class Settings:
    custom_model: Path
    automl_model: Path
    automl_labels: Path
    gc10_output: Path
    max_upload_bytes: int
    enable_vertex: bool
    project_id: str
    region: str
    endpoint_id: str
    allowed_origins: tuple[str, ...]
    log_level: str

    @classmethod
    def from_environment(cls) -> "Settings":
        upload_limit = int(os.getenv("MAX_UPLOAD_BYTES", "5242880"))
        if upload_limit <= 0:
            raise ValueError("MAX_UPLOAD_BYTES must be positive")
        models = MODELS_ROOT
        return cls(
            custom_model=environment_path("CUSTOM_MODEL_PATH", models / "CustomML/outputs/best.pt"),
            automl_model=environment_path(
                "AUTOML_TFLITE_PATH", models / "AutoML/AutoML model.tflite"
            ),
            automl_labels=environment_path("AUTOML_LABELS_PATH", models / "AutoML/labels.txt"),
            gc10_output=environment_path("GC10_OUTPUT_DIR", models / "GC10/releases/v1.0.0"),
            max_upload_bytes=upload_limit,
            enable_vertex=os.getenv("ENABLE_VERTEX_AI", "false").lower() == "true",
            project_id=os.getenv("GCP_PROJECT_ID", ""),
            region=os.getenv("GCP_REGION", "us-central1"),
            endpoint_id=os.getenv("VERTEX_AI_AUTOML_ENDPOINT_ID", ""),
            allowed_origins=tuple(
                os.getenv(
                    "ALLOWED_ORIGINS",
                    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000",
                ).split(",")
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )


def assistant_mode() -> str:
    """Read per request so local tests and interactive mode changes remain supported."""
    return os.getenv("ASSISTANT_MODE", "local").strip().lower()


SETTINGS = Settings.from_environment()
