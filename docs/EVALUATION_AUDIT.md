# Evaluation audit — 2026-10-25

The 100% raw accuracy on the existing NEU test split is reproducible. This audit
did not find evidence that the evaluator substitutes labels for predictions.
It also did not establish independent generalization or verify the cloud training
job that produced the exported AutoML model.

## Confirmed bugs corrected

- AutoML normalization now follows the embedded mean/std of 127.5, followed by
  quantization. The previous `/255` normalization did not match the export.
- AutoML output labels now follow embedded `dict.txt`: Pitted_Surface precedes
  Rolled_in_Scale. The old external file reversed those two entries.
- Shared evaluation maps output indices to names before mapping to a common class
  order. Different model output orders cannot silently swap class scores.
- Mean confidence no longer awards comparison wins. Greater certainty is not
  evidence of greater correctness or better calibration.
- Dashboard metrics have been regenerated from the corrected adapters. They are
  marked as an internal benchmark, and the Comparison page explains the scope
  and the models' different abstention policies.

## Checks performed

All 1,800 local images were decoded and inspected. The intended split is
1,440 train / 180 validation / 180 test, balanced across six classes.

| Check | Observed result |
| --- | --- |
| Identical file contents across splits | None |
| Identical decoded RGB pixels across splits, including alternate encodings | None |
| Perceptual-hash candidates across splits, Hamming distance at most 6 of 63 bits | None |
| Closest test/train perceptual-hash distance | 14 |
| Local AutoML CSV test entries also listed as training/validation | None |
| Local AutoML CSV membership versus local image membership | Matches all three splits |
| All 180 images renamed to one opaque input path and inference order shuffled | Predictions unchanged for both models |
| Independent scikit-learn accuracy and macro precision/recall/F1 calculation | Matches NumPy evaluator |
| 1,000 random permutations of the test labels | Mean raw accuracy about 16.7% |

Perceptual hashes are heuristics. These findings do not rule out related crops,
shared sheets/batches, or leakage in an earlier data preparation process.
The import CSVs establish intended local membership, not cloud job lineage.

## Observed model limitations

Each condition below uses the same 180 original test images and fixed model
checkpoints. Perturbations were specified before running the controls; neither
model was retrained or selected against these outcomes.

| Input condition | CustomML raw accuracy | CustomML deployed accuracy | AutoML accuracy |
| --- | --- | --- | --- |
| Original, renamed and reordered | 100% | 99.44% | 100% |
| Flat gray replacement | 16.67% | 0% (all abstained) | 16.67% |
| Pixels randomly shuffled within each image | 25.56% | 16.11% | 39.44% |
| Gaussian blur radius 3 and contrast factor 0.5 | 40.00% | 23.89% | 36.67% |

CustomML uses a 0.55 confidence threshold; AutoML currently always chooses a class.
Scores on blank or shuffled images are negative controls, not useful defect
classification benchmarks. The blur/contrast result is a robustness diagnostic,
not an estimate of accuracy on an independently collected camera dataset.

Both models depend on image content, but performance falls sharply under the
specified acquisition-like changes. The clean-split score must not be presented
as production accuracy, immunity to overfitting, or successful unknown-defect detection.

## Changes to future training

The trainer now checks file and decoded-pixel identities across train/validation/
test before optimization. Missing/empty class folders and duplicates fail early.
Each new checkpoint records the split fingerprint and counts, and training refuses
to overwrite an existing `best.pt` output directory. The integrity helper is part
of the trainer package so the same guard is available in cloud training.

These guards prevent a specific form of leakage. They do not reconstruct source
group identities or make an already-used test set independent. Existing checkpoints
were not retrained, and their binary hashes are retained in the audit summary.
The old `CustomML/outputs/metrics.json` is explicitly marked as a legacy artifact
whose history does not describe the deployed checkpoint.

## Remaining evidence before a generalization claim

1. Verify AutoML training job/model ID, export, dataset, and actual split settings.
2. Collect a fresh, appropriately licensed holdout from distinct sheets/batches/
   capture sessions. Keep those source identities with each image.
3. Keep final holdout images out of training, augmentation, threshold selection,
   and hyperparameter tuning. Group related source images before splitting.
4. If lineage reveals training overlap, train new versions of both models on the
   corrected splits. Choose acquisition-appropriate augmentation and thresholds
   on training/validation data, then evaluate the untouched holdout once.

Do not repeatedly repartition images that the existing models may already have
seen and call the new partition independent. Do not manually lower the reported
100% to make it appear more believable.

For a CV, describe the implementation and audit without a production accuracy
claim: “Built a PyTorch/AutoML steel-defect comparison app with reproducible
Pandas/NumPy evaluation, export-contract validation, and split-integrity checks.”

## Reproduce

Install `requirements/requirements-evaluation.txt`, then run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m ml.audit_dataset `
  --dataset-root data/processed/neu `
  --automl-imports data/manifests/automl `
  --out-dir reports/runs/my-split-audit

.\.venv\Scripts\python.exe -m ml.evaluate_shared `
  --test-dir data/processed/neu/test `
  --reference-dir data/processed/neu/train `
  --reference-dir data/processed/neu/val `
  --out-dir reports/runs/my-benchmark

.\.venv\Scripts\python.exe -m ml.audit_predictions `
  --test-dir data/processed/neu/test `
  --baseline-csv reports/runs/my-benchmark/predictions.csv `
  --out-dir reports/runs/my-controls

.\.venv\Scripts\python.exe -m pytest tests/ml/test_evaluate_shared.py
```

The portable, machine-readable findings are in
[`reports/benchmarks/evaluation_audit_summary.json`](../reports/benchmarks/evaluation_audit_summary.json).
Per-image local reports are ignored by Git because they include dataset paths.
Datasets and checkpoints must retain their appropriate licenses and provenance
when distributed. This audit does not publish or push anything to GitHub.

## Publication wording and provenance

The owner confirms that they trained the Google AutoML Vision model on Google
Cloud (Vertex AI AutoML) for the course project. Original cloud-job metadata is
not available, so this confirmation does not independently verify cloud training
membership or the model's train/validation/test split.

GC10 capture tokens are inferred from filenames, not verified physical sheet
identities. Keeping tokens within one split reduces this leakage risk but does
not establish independent camera generalization. The README summarizes this as
capture-group separation; the underlying limitations remain unchanged here.

The NEU split has informed development and is not a new independent holdout.
Near-saturated results on this split should not be presented as evidence of
independent field generalization. GC10 is a harder, separate multilabel task.
The README Results table is generated exclusively from the existing benchmark
JSON files. Release preparation must preserve those files and the frozen manifests.
