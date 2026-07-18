# Steel Defect Detection: AutoML vs CustomML

A full-stack steel-surface inspection demo that compares:

- Google AutoML Edge exported as TensorFlow Lite
- A refined PyTorch ResNet18 CustomML classifier

The application supports single-image and batch prediction, camera capture, a live comparison dashboard, prediction history, and a domain assistant for the six NEU surface-defect classes.

## Supported classes

1. Crazing
2. Inclusion
3. Patches
4. Pitted Surface
5. Rolled-in Scale
6. Scratches

The classifiers are not trained for rust, normal/no-defect surfaces, aluminum defects, or unknown defect classes. The system is a screening demo and must not replace qualified inspection or an applicable acceptance standard.

Authentication is also demo-only: the frontend contains mock local credentials and tokens for UI demonstration. It does not provide server-side authentication, authorization, or production security.

## Architecture

```text
React/Vite frontend (localhost:5173)
             |
             | HTTP/JSON + multipart uploads
             v
FastAPI backend (localhost:8001)
       |                    |
       v                    v
PyTorch CustomML       AutoML TFLite
       |
       +-- comparison metrics + assistant retrieval index
```

Important paths:

- `frontend/` — React/TypeScript UI
- `backend/app.py` — FastAPI routes
- `backend/inference.py` — model loading, validation, and inference
- `backend/comparison.py` — shared metric schema and winner logic
- `backend/assistant/` — intent routing, knowledge base, and retrieval index
- `backend/models/AutoML/` — TFLite model, labels, evaluator, and metrics
- `backend/models/CustomML/` — trainer, checkpoint, evaluator, and metrics
- `scripts/` — PowerShell launch helpers
- `tests/` — assistant, API, and browser smoke tests

## Requirements

- Windows PowerShell
- Python 3.11+ recommended
- Node.js 18+
- npm

The current environment uses CPU inference. GPU is optional for CustomML training.

## Installation

From the repository root:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

cd frontend
npm install
cd ..
```

## Running the application

Run backend and frontend together:

```powershell
.\scripts\run_dev.ps1
```

Run both from one VS Code terminal session:

```powershell
.\scripts\run_dev.ps1 -InTerminal
```

Run separately:

```powershell
# Terminal 1
.\scripts\run_backend.ps1

# Terminal 2
cd frontend
npm run dev
```

Open `http://localhost:5173`. The frontend calls the backend at `http://localhost:8001` by default. Override the frontend endpoint with `VITE_API_BASE_URL` if required.

Backend options:

```powershell
.\scripts\run_backend.ps1 -AssistantMode dataset
.\scripts\run_backend.ps1 -RestartIfRunning
.\scripts\run_backend.ps1 -Port 8001
```

Do not start multiple backend processes on the same port.

## API endpoints

- `GET /health` — model and service readiness
- `GET /model/info` — CustomML metadata
- `GET /test-model` — model diagnostic
- `POST /predict?model_type=custom|automl|both` — single image
- `POST /predict/batch?model_type=custom|automl|both` — batch images
- `POST /predict/debug` — detailed CustomML result
- `POST /assistant` — domain assistant
- `GET /compare/metrics` — normalized live comparison payload

Accepted uploads: JPEG/JPG, PNG, WebP, and BMP, up to 5 MB per image. Batch requests accept at most 50 files.

## Live comparison dashboard

The Comparison page polls `/compare/metrics` every five seconds and refreshes when the browser tab becomes visible. It shows the latest contents of:

- `backend/models/AutoML/automl_metrics.json`
- `backend/models/CustomML/custom_metrics_v2.json`

CustomML comparison accuracy uses the deployed 55% confidence threshold. Predictions below the threshold count as abstentions/Unknown rather than being forced into a class.

### Evaluation warning

The included NEU split contains 1,440 training, 180 validation, and 180 test images from one clean dataset distribution. A high score on this test split does not prove production generalization. A trustworthy production estimate requires an external holdout captured with the intended camera, optics, lighting, steel grades, normal surfaces, and unknown defects.

Do not manually lower metrics. Generate new metrics by evaluating both models on the same independent dataset.

## AI assistant

The assistant is a deterministic domain assistant, not a general-purpose generative LLM. It combines:

- Explicit intent handlers for definitions, metrics, equipment, lighting, supported scope, and safety limits
- BM25 retrieval over the steel-defect QA index
- Optional prediction context only when the question refers to the current result

Rebuild its retrieval index after changing `train_simple.jsonl`:

```powershell
.\.venv\Scripts\python.exe backend\assistant\train_dataset_retriever.py
```

The raw synthetic assistant dataset is intentionally ignored by Git; the generated runtime index is retained.

## CustomML training

The refined trainer uses pretrained ResNet18 weights, stronger augmentation, random erasing, label smoothing, AdamW weight decay, differential learning rates, validation-loss checkpointing, learning-rate reduction, deterministic seeds, and early stopping.

Expected dataset layout:

```text
backend/models/neu_final_dataset_fullnames/
  train/<class>/*.jpg
  val/<class>/*.jpg
  test/<class>/*.jpg
```

Train from the CustomML directory:

```powershell
cd backend\models\CustomML
..\..\..\.venv\Scripts\python.exe -m trainer.train `
  --data_dir ..\neu_final_dataset_fullnames `
  --output_dir outputs `
  --epochs 30 `
  --batch_size 32
```

The production checkpoint is `backend/models/CustomML/outputs/best.pt`.

Regenerate deployed CustomML metrics:

```powershell
.\.venv\Scripts\python.exe backend\models\CustomML\eval_custom_pt.py `
  --model backend\models\CustomML\outputs\best.pt `
  --test_dir backend\models\neu_final_dataset_fullnames\test `
  --out backend\models\CustomML\custom_metrics_v2.json `
  --confidence_threshold 0.55
```

Regenerate AutoML metrics on the same split:

```powershell
.\.venv\Scripts\python.exe backend\models\AutoML\eval_automl_tflite.py `
  --dataset_test_dir backend\models\neu_final_dataset_fullnames\test `
  --model "backend\models\AutoML\AutoML model.tflite" `
  --labels backend\models\AutoML\labels.txt `
  --out backend\models\AutoML\automl_metrics.json
```

## Verification

Assistant behavior tests:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.api.test_assistant_unittest -v
```

Backend API tests:

```powershell
pip install -r backend\requirements-dev.txt
python -m pytest tests\api -q -s
```

Frontend production build:

```powershell
cd frontend
npm run build
```

Optional Playwright smoke test instructions are in `tests/README.md`.

## Data and GitHub

Image datasets, virtual environments, caches, generated reports, and TestSprite temporary output are ignored. Do not commit secrets, `.env` files, cloud credentials, or the raw NEU dataset unless its license and repository size are appropriate.

The CustomML checkpoint is about 43 MB. GitHub accepts individual files below 100 MB, but Git LFS is recommended for model binaries:

```powershell
git lfs install
git lfs track "*.pt" "*.tflite"
git add .gitattributes
```

Review and push the code yourself:

```powershell
git status
git diff --check
git diff --stat

git add .
git status
git diff --cached --check

git commit -m "Prepare steel defect application for release"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
git push -u origin main
```

If `origin` already exists, inspect it with `git remote -v` and update it only if necessary:

```powershell
git remote set-url origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
```

Before pushing, inspect staged files carefully and confirm that no dataset, token, credential, local environment, or unwanted binary was added.

## Troubleshooting

- Script not found: run commands from the repository root.
- Script execution disabled: `Set-ExecutionPolicy -Scope Process Bypass`.
- Frontend cannot reach backend: check `http://localhost:8001/health` and `VITE_API_BASE_URL`.
- Old assistant answers: ensure only one backend process is running and restart it.
- Comparison not updating: verify both metrics JSON files, then use the live status/Refresh control.
- AutoML label mismatch: do not reorder `backend/models/AutoML/labels.txt` for the current TFLite model.
