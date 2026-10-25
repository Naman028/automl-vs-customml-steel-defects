# Shared evaluation with Pandas and NumPy

`evaluate_shared.py` uses **Pandas** for the shared image manifest,
`predictions.csv`, and `groupby` error-pair analysis. It uses **NumPy** for the
6×7 confusion matrices, precision, recall, F1, coverage, and latency summaries.
Both adapters are implemented using the existing Torch and TFLite evaluators.

Verified internal benchmark on 2026-10-25, after fixing the AutoML contract:

| Model | Raw accuracy | Deployed accuracy | Abstentions |
| --- | --- | --- | --- |
| CustomML | 180/180 (100%) | 179/180 (99.44%) | 1 Inclusion |
| AutoML | 180/180 (100%) | 180/180 (100%) | 0 |

There were no exact file duplicates across the supplied train/validation/test
splits. The earlier AutoML result of 70.56% used incorrect preprocessing/labels.
The corrected local artifacts are in
`evaluation_reports/release-metrics-20261025/` (ignored by Git).
These 180 images are the existing internal test set, not an external holdout.
The deeper audit and negative controls are documented in
[`../../EVALUATION_AUDIT.md`](../../EVALUATION_AUDIT.md).

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/models/requirements-evaluation.txt
.\.venv\Scripts\python.exe backend/models/evaluate_shared.py `
  --test-dir D:/steel-independent-holdout `
  --reference-dir backend/models/neu_final_dataset_fullnames/train `
  --reference-dir backend/models/neu_final_dataset_fullnames/val `
  --out-dir backend/models/evaluation_reports/independent-run-01
```

Repeat `--reference-dir` for any additional AutoML training/validation image
roots. The tool cannot infer which images Google AutoML saw from a TFLite file.
All six canonical class folders must be present, nonempty, and spelled exactly
as in `CLASSES` in the script. Normal/no-defect and novel defect ground truths
require a separate open-set evaluation; Unknown here means abstention only.

For a **smoke test only**, use
`--test-dir backend/models/neu_final_dataset_fullnames/test` with the same reference
roots above. This remains an internal benchmark, not a new independent set.

Outputs in the new directory:

- `predictions.csv`: paths, image hashes, true labels, raw and deployed predictions,
  confidences, and inference latencies for both models.
- `custom_metrics_v2.json` and `automl_metrics.json`: the existing comparison schema,
  plus dataset/model fingerprints, coverage, raw accuracy, error pairs, and a
  `confusion_matrix_with_unknown` with six true-label rows and seven prediction columns.
  The legacy six-column matrix and separate abstention counts remain for dashboard compatibility.

The default deployed thresholds match current behavior: CustomML 0.55, AutoML
0.0. Raw argmax accuracy provides a threshold-free comparison. To choose deployment
thresholds, use validation data and a stated recall/coverage target; never tune on
the final holdout. A common numeric threshold does not imply comparable calibration.
Abstentions count in recall denominators and image counts; precision is zero when a
class has no predicted positives. All six classes contribute to macro metrics.

The script fails on duplicate file or decoded-pixel contents within the holdout or overlap with
any reference root. This does not detect near-duplicates or correlated crops.
Split by original source image, sheet, batch, or capture session before augmentation,
and verify AutoML training membership separately. `independence_verified` remains
false because these conditions cannot be proven from file hashes.

AutoML reads normalization from the exported TFLite metadata, applies
`(pixel - mean) / std`, and then rounds/clips quantized input. The current export
specifies mean and std of 127.5. The previous `/255` adapter was incorrect.
The embedded `dict.txt` also puts Pitted_Surface before Rolled_in_Scale; the
external label file has been corrected to match. Runtime inference and both
AutoML evaluation entry points now use the same preprocessing helper and reject
label files with a different order. The old AutoML metrics were stale and have been regenerated.
The new report records the contract; no input scaling is selected using test accuracy.

The script warms both models up and measures inference excluding image decoding
and preprocessing, using their existing runtime/device choices. Hardware differences
must be considered before interpreting speed differences.

The script never replaces deployed dashboard metrics automatically. The checked-in
dashboard files were refreshed from the audited internal benchmark and explicitly
mark independent generalization as unverified. Review any future report and its
dataset provenance before copying it into the deployed model directories.

Tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/models -p test_evaluate_shared.py -v
```

The old `CustomML/outputs/metrics.json` has a different training history from the
deployed checkpoint. Do not use it as the deployed checkpoint's training record.
Future training runs should retain checkpoint, config, history, and metrics together
in a unique output directory. No checkpoint is retrained or overwritten by this tool.
