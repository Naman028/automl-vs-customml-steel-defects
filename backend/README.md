# Backend Guide

This backend is a FastAPI service for steel-defect inference and model comparison.

## Runtime

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api.app:app --port 8001
```


- App entrypoint: `backend/api/app.py`
- Inference runtime: `backend/inference/neu.py`
- Metrics comparison: `backend/services/comparison.py`

## API Endpoints

- `GET /`
- `GET /health`
- `GET /test-model`
- `POST /predict?model_type=custom|automl|both`
- `POST /predict/batch?model_type=custom|automl|both`
- `POST /predict/debug`
- `GET /model/info`
- `GET /compare/metrics`
- `POST /assistant`

## Assistant Dataset Training (Safe Local Mode)

You can train the assistant retrieval index from:
- `data/raw/assistant/train_simple.jsonl`

Train/build index:

```powershell
python -m ml.assistant.train_retriever
```

This creates:
- `backend/assistant/assistant_dataset_index.json`

Enable dataset-based assistant mode (optional):

```powershell
.\scripts\run_backend.ps1 -AssistantMode dataset
```

Behavior:
- Default mode remains `local` (knowledge-base retrieval).
- `dataset` mode uses the trained JSONL index.
- No changes to prediction endpoints or model inference.

## Start Backend

From project root:

```powershell
.\scripts\run_backend.ps1
```

One-command full app startup (backend + frontend):

```powershell
.\scripts\run_dev.ps1
```

One-command full app startup with explicit backend model/mode:

```powershell
.\scripts\run_dev.ps1 -AutoMLModelPath ".\models\AutoML\AutoML model.tflite" -AssistantMode dataset
```

Run with explicit AutoML model path:

```powershell
.\scripts\run_backend.ps1 -AutoMLModelPath ".\models\AutoML\AutoML model.tflite"
```

If backend is already running and you need to apply new settings:

```powershell
.\scripts\run_backend.ps1 -AssistantMode dataset -RestartIfRunning
```

Notes:
- The script prevents starting a second backend on port `8001` by default.
- `-AutoMLModelPath` accepts absolute paths and project-relative paths.
- Default AutoML path is auto-selected: `models/AutoML/AutoML model.tflite`.
- Assistant mode auto-selection:
  - `dataset` if `backend/assistant/assistant_dataset_index.json` exists
  - otherwise `local`

## AutoML Artifacts

Active AutoML model:
- `models/AutoML/AutoML model.tflite`

AutoML labels:
- `models/AutoML/labels.txt`

Current label order:
1. `Crazing`
2. `Inclusion`
3. `Scratches`
4. `Rolled_in_Scale`
5. `Pitted_Surface`
6. `Patches`

This order is required to map output indices correctly for the current TFLite model.

## Evaluate AutoML Model

`ml/automl/eval_automl_tflite.py` supports:
- `--model`
- `--out`
- `--dataset_test_dir`
- `--labels`

Example:

```powershell
python -m ml.automl.eval_automl_tflite `
  --model models/AutoML/AutoML model.tflite `
  --labels models/AutoML/labels.txt `
  --dataset_test_dir data/processed/neu/test `
  --out reports/benchmarks/neu_automl.json
```

## CustomML Commands

Train:

```powershell
python -m ml.neu.trainer.train --data_dir data/processed/neu --output_dir models/CustomML/outputs_new --epochs 12
```

Evaluate to v2 metrics:

```powershell
python -m ml.neu.eval_custom_pt --model models/CustomML/outputs/best.pt --test_dir data/processed/neu/test --out reports/runs/new-custom-metrics.json
```

## Troubleshooting

- If `GET /` works but your UI fails, check frontend URL and CORS origins.
- If AutoML is unavailable in `/health`, verify:
  - model path exists
  - labels file exists
  - `AUTOML_TFLITE_PATH` points to the intended file
- If predictions look swapped across classes, verify `labels.txt` order.
