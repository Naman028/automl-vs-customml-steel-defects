# Repository layout

This layout adapts the separation used by
[Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science),
[PyTorch Template](https://github.com/victoresque/pytorch-template#folder-structure),
and the [FastAPI full-stack template](https://github.com/fastapi/full-stack-fastapi-template).
It keeps only directories this project uses; no notebooks, database, generic trainer
framework or extra service layers are added just to match a template.

```text
backend/                 Importable FastAPI application package
  api/                   HTTP app, request schemas and upload validation
  core/                  Configuration, shared paths and label vocabulary
  inference/             NEU/GC10 runtimes, preprocessing and prediction routing
  integrations/          Optional Vertex AI provider
  services/              Report comparison and winner logic
  assistant/             Assistant code, index and knowledge base
frontend/                React source, public assets and build configuration
ml/                      Offline training, dataset auditing and evaluation
  neu/                   NEU custom trainer and evaluator
  automl/                Exported AutoML evaluation and command-line inference
  assistant/             Offline retrieval index preparation
data/
  raw/gc10/              Original GC10 archive, local and ignored
  raw/assistant/         Assistant training records, local and ignored
  processed/neu/         Existing NEU train/validation/test images, local and ignored
  manifests/automl/      Original cloud import split CSVs
  *_manifest.json        Frozen image identities, labels and split assignments
models/
  AutoML/                Exported TFLite model and output labels
  CustomML/              Custom checkpoint and training runs
  GC10/                  Locally trained GC10 checkpoint and run metadata
  registry.json          Approved artifact identities and provisioning metadata
reports/
  benchmarks/            Versioned dashboard metrics and audit summary snapshots
  verification/          Recorded verification metadata (internal bundle inventory ignored)
  runs/                  Local audit/evaluation outputs, ignored
requirements/            Layered runtime, evaluation and developer dependencies
scripts/                 Launch, provisioning, training and maintenance entrypoints
tests/                   HTTP, ML fixtures, artifact integration and browser tests
deploy/                  API container definition
docs/                    Essential deployment, evaluation and attribution guides
  local/                 Internal working notes, ignored
```

Source packages contain code and their required resources. Datasets and model
weights are provisioned separately and are excluded from Git and the Docker build.
Small dashboard snapshots, frozen manifests and model identity metadata stay versioned.
Saved run directories retain their original contents; historical reports may still
record their original absolute paths. Use image hashes to match historical predictions
to the relocated dataset. No labels, splits, thresholds or measured results were edited.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api.app:app --port 8001
```

Use `python -m ml.evaluate_shared`, `python -m ml.evaluate_gc10`,
`python -m ml.train_gc10`, `python -m ml.neu.trainer.train`, or the existing wrappers.
The backend entrypoint is unchanged by this artifact relocation. Existing model
paths under `backend/models/` in environment settings are resolved to `models/`
when the old files are absent. New configurations should use `.env.example`.
Data paths passed explicitly to offline commands should use their new locations.

Use `scripts/clean_generated.ps1 -WhatIf` to preview cache/build cleanup. It does
not remove datasets, weights, reports, installed dependencies or Git history.
Dependencies are local development inputs; each API worker loads its own models.

The outstanding correctness findings remain in the local
[clean-code audit](../reports/runs/clean-code-audit-20261025/REVIEW.md).
Folder organization does not fix those findings or establish production readiness.
