# Steel Defect Detection (AutoML vs CustomML)

## Overview
Web app + API to compare two image classification models:
- AutoML Edge model (TFLite)
- Custom PyTorch ResNet18 model

## Requirements
- Python 3.11+ recommended
- Node 18+ recommended

## Backend
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```

## Comparison Endpoint

`GET /compare/metrics`
Returns metrics + deterministic winners for both models.
