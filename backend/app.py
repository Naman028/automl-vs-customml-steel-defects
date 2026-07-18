import logging
import os
from pathlib import Path
from typing import Literal, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from assistant.assistant_service import answer_question
from comparison import build_comparison, normalize_metrics, read_json_file
from inference import (
    BASE_DIR,
    CLASS_NAMES,
    MAX_BATCH_FILES,
    MODEL_PATH,
    TOP_K_DEFAULT,
    load_validated_image,
    model_info_payload,
    predict_batch_single,
    predict_debug_payload,
    predict_single,
    test_model_payload,
    health_payload,
)
from schemas import AssistantRequest


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("industrial_defect_api")

app = FastAPI(title="Industrial Defect API", version="1.0")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000",
).split(",")


#cors middleware to allow requests from frontend origins during development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Helper function to standardize error handling in prediction endpoints, ensuring consistent HTTP 500 responses for unhandled exceptions while allowing HTTPExceptions to pass through as intended.
def _raise_unhandled_prediction_error(exc: Exception, log_message: str, detail: str):
    """Normalize unhandled exceptions into a stable HTTP 500 response."""
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception(log_message)
    raise HTTPException(status_code=500, detail=detail)

def _load_normalized_metrics(path: Path, model_path: Path):
    """Read and normalize metrics file into the shared comparison schema."""
    return normalize_metrics(read_json_file(path), path, model_path, CLASS_NAMES)


@app.get("/")
def root():
    return {
        "service": "Industrial Defect API",
        "status": "ok",
        "health_url": "/health",
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    return health_payload()


@app.get("/test-model")
def test_model():
    return test_model_payload()


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model_type: Literal["custom", "automl", "both"] = "custom",
):
    try:
        img = await load_validated_image(file)
        return predict_single(img, model_type)
    except Exception as exc:
        _raise_unhandled_prediction_error(
            exc,
            "Unhandled error in /predict",
            "Prediction failed due to an internal error",
        )


@app.post("/predict/batch")
async def predict_batch(
    files: List[UploadFile] = File(..., description="List of image files to process"),
    model_type: Literal["custom", "automl", "both"] = "custom",
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400, detail=f"Maximum {MAX_BATCH_FILES} images per batch"
        )

    results = []
    for file in files:
        try:
            img = await load_validated_image(file)
            prediction = predict_batch_single(img, model_type)
            prediction["filename"] = file.filename
            results.append(prediction)
        except HTTPException as exc:
            results.append({"filename": file.filename, "error": exc.detail})
        except Exception:
            logger.exception("Unhandled batch prediction error for file %s", file.filename)
            results.append({"filename": file.filename, "error": "Prediction failed for file"})

    return {"results": results, "total": len(results)}


@app.post("/assistant")
async def assistant(req: AssistantRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    return answer_question(req.question, req.prediction)


@app.post("/predict/debug")
async def predict_debug(file: UploadFile = File(...), top_k: int = TOP_K_DEFAULT):
    try:
        img = await load_validated_image(file)
        return predict_debug_payload(img, top_k)
    except Exception as exc:
        _raise_unhandled_prediction_error(
            exc, "Unhandled error in /predict/debug", "Debug prediction failed"
        )


@app.get("/model/info")
async def get_model_info():
    try:
        return model_info_payload()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(exc)}")


@app.get("/compare/metrics")
async def compare_metrics():
    automl_path = BASE_DIR / "models" / "AutoML" / "automl_metrics.json"
    custom_v2_path = BASE_DIR / "models" / "CustomML" / "custom_metrics_v2.json"
    custom_legacy_path = BASE_DIR / "models" / "CustomML" / "outputs" / "metrics.json"
    custom_model_path = Path(MODEL_PATH)

    automl_metrics = _load_normalized_metrics(automl_path, custom_model_path)

    if custom_v2_path.exists():
        custom_metrics = _load_normalized_metrics(custom_v2_path, custom_model_path)
    else:
        custom_metrics = _load_normalized_metrics(custom_legacy_path, custom_model_path)

    return build_comparison(automl_metrics, custom_metrics)
