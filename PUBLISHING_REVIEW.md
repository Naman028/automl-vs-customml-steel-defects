# Publication cleanup review

This review records the approved local cleanup. It does not authorize a remote
creation, push, public release, history rewrite, or redistribution of third-party assets.

| Area | Before cleanup | After cleanup / verification |
| --- | --- | --- |
| Evaluation integrity | Existing corrected NEU reports and the trained GC10 baseline | Splits, labels, exclusions, thresholds, weights and saved metric values preserved. [Prediction verification](artifacts/refactor_verification.json). |
| Tests | 18 evaluation tests and 16 assistant tests confirmed during the audit | Full pytest collection: 54 passed, 2 explicitly skipped. CI-style selection with missing checkpoint paths: 53 passed, 3 artifact/live tests deselected. |
| Python quality | No Ruff or mypy project configuration | Ruff check and format check pass. Strict mypy passes on the 15 explicit new/refactored modules; untouched legacy modules are not blanket-checked. |
| Frontend | Build available; no configured lint/typecheck workflow | ESLint, strict TypeScript, production build and the Playwright fixture smoke test pass. |
| Optional Vertex AI | Local export plus explicitly enabled cloud integration | Preserved. Mocked tests cover local priority, disabled cloud access and cloud fallback without Google SDK credentials or network calls. |
| HTTP errors | Existing upload checks mixed into the runtime | Shared bounded upload validation; fixture tests cover wrong MIME, oversize, corrupt/empty input, batch limit and partial AutoML failure. |
| Report freshness | Current generated reports plus an unsafe legacy fallback | Dashboard fixture parity tests pass. Missing generated NEU metrics no longer fall back to legacy training scores. |
| Configuration | Scattered environment defaults; demo passwords in frontend source | Typed runtime configuration and `.env.example`; browser demo controls explicitly enabled, no embedded credential values. Demo controls remain non-authenticating. |
| Reproduction | Local datasets and checkpoints required | Frozen image identities/split assignments, SHA-256 model registry, pinned direct Python requirements, npm lockfile, PowerShell/Bash wrappers and dataset-source instructions. |
| Documentation | README contained measured outcomes | Main and GC10 READMEs link generated reports without quoting performance results. Scope and third-party provenance are explicit. |
| CI | No workflow | Push/PR workflow configured for small fixtures, scoped mypy, Ruff, coverage, frontend checks and mocked smoke test. Equivalent local commands passed; GitHub execution is not yet verified. |
| Git | Existing history and substantial pending changes | Cleanup recorded in logical local commits. Original history and original remote preserved. No push or new remote creation performed. |

## Numerical verification

NEU raw labels, deployed labels, confidences and classification metrics match the
pre-refactor evaluation. GC10 label decisions and test metrics match its saved
baseline. The maximum GC10 probability difference is recorded in the verification
JSON together with the floating-point tolerance; batched CPU inference is not
claimed to be bitwise identical. Timing naturally varies between runs and was
not copied back into the saved dashboard metrics.

The tracked report snapshots were also checked against their original generated
local outputs. No recorded result was manually adjusted during this cleanup.

## Files excluded from new commits

| Material | Handling and reason |
| --- | --- |
| NEU and GC10 image trees | Ignored; original-provider data with unverified redistribution terms. Only frozen manifests and attribution are tracked. |
| Checkpoints and TFLite binaries | Ignored and untracked from the latest tree; local copies retained and hashes verified. Release URLs remain unset pending permission/provenance review. |
| Raw evaluation/training directories | Ignored; reviewed summary JSON and code are tracked instead of local paths, feature data and transient run output. |
| `.env`, service-account credentials, dependency folders and caches | Excluded from version control. `.env.example` contains blank credentials and local defaults only. |
| Coverage, browser reports and build output | Generated locally or by CI; ignored rather than committed. |

## Publication decisions still required

- The earlier Git history still contains the old model entries and historical
  non-authenticating demo passwords. Untracking the current files did not remove
  history. A history rewrite was neither authorized nor performed.
- Tracked frontend demonstration photographs predate the cleanup. Their licensing
  has not been established. No original image file was deleted or replaced.
- Dataset/weight redistribution permissions and the original AutoML cloud job
  lineage remain unverified. Public availability does not establish those rights.
- The owner has not selected a licence for original project code. No third-party
  material has been relicensed by this cleanup.
- Model release upload/download cannot be completed until the owner approves the
  artifacts and their redistribution provenance. Existing local files can be
  verified/restored with the checksum tool in the meantime.
- The requested `Naman028/steel-defect-detection` repository has not been created.
  The existing `origin` still points to the earlier project repository. Any new
  remote and push require explicit approval, and public visibility requires a
  separate approval after CI succeeds.

The included credential scan checks known private-key/provider-token patterns in
working text and reachable history, with values redacted. It does not certify the
absence of every possible secret; dependencies, binaries, generated datasets and
oversize text blobs are explicitly outside that heuristic scan's scope.

Before publication, decide whether to retain the original history after verifying
asset rights or authorize a separate source-only publication history/copy that
excludes historical binaries and uncleared photographs. No such history change
or publication will be inferred from approval of this local cleanup.
