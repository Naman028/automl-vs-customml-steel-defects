# GC10 local multilabel baseline

This is a separate ten-label experiment, not a replacement for the six-class NEU
CustomML checkpoint or the exported NEU AutoML comparison. It runs locally without
Vertex AI, credentials, or weight downloads when the approved NEU checkpoint is present.

## Model and methodology

The existing NEU-trained ResNet18 is a frozen feature extractor. A new multilabel
linear head is trained with class-weighted binary cross-entropy. Labels represent
all supported object categories present in an image, not a folder's primary category.
This predicts category presence, not bounding boxes or defect-free certification.

Feature normalization and positive-class weights use training data only.
Validation loss selects the head checkpoint; validation F1 selects per-class
thresholds. The saved test split is used for reporting only. The fixed backbone
and resized inputs may lose small-defect detail.

## Archive preparation

The supplied spreadsheet defines canonical category names. The code verifies
pixel equality before deduplicating filename copies, explicitly records the
`10_yaozhed` to `10_yaozhe` repair, and excludes unknown labels, empty annotations,
conflicting copies, invalid boxes and filenames that cannot be grouped.

The saved manifest preserves labels, decoded-image hashes and split assignment.
Filename capture tokens remain in a single split. They are not verified physical
sheet identities. The publication cleanup does not change those labels, splits,
thresholds or exclusions. See the [frozen manifest](../../../data/gc10_manifest.json).

## Report

The generated [metrics report](metrics.json) includes evaluation values, supports,
exclusions and model provenance. This README deliberately does not quote result
figures. GC10 multilabel metrics are not directly comparable to NEU accuracy.

The test has already been evaluated. Future model choices must use training and
validation data; a new final holdout is needed for an independent claim.

## Reproduce

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/models/requirements-evaluation.txt
.\scripts\train_gc10.ps1 --out-dir backend/models/GC10/outputs_local_v2
.\scripts\evaluate.ps1 gc10 --out-dir backend/models/evaluation_reports/new-gc10-evaluation
```

Bash wrappers have the same names with `.sh`. Training never overwrites an existing
run directory. Set `GC10_OUTPUT_DIR` before backend startup to serve a different
run. Each run writes its checkpoint, manifest, metrics and per-image test predictions.
The checked-in metrics file is the reviewed snapshot. If only the snapshot is
present, the UI disables image prediction until local weights are provisioned.

Open **GC10 experiment** in the app. Its endpoints are `GET /gc10/metrics` and
`POST /gc10/predict`. Dataset and model redistribution terms remain subject to the
[third-party notices](../../../THIRD_PARTY_NOTICES.md).
