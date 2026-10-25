# Dataset acquisition and frozen splits

Images are not distributed with the code. Obtain the appropriate dataset from its
provider and retain its terms and provenance before use:

- NEU: [Kechen Song and Yunhui Yan, official NEU database](https://faculty.neu.edu.cn/songkc/en/zdylm/263270/list/index.htm).
  This project performs image-level classification. The provider distinguishes
  NEU-CLS from detection annotations. Use the exact local image identities listed
  in `neu_manifest.json`, arranged by the recorded train/val/test paths.
- GC10: [Xiaoming Lv and coauthors' repository](https://github.com/lvxiaoming2019/GC10-DET-Metallic-Surface-Defect-Datasets).
  Follow the provider's download link. The reviewed archive has numbered image
  folders, `lable/*.xml`, and `Defects Description.xlsx`. Cite Lv, Duan, Jiang, Fu
  and Gan, *Deep Metallic Surface Defect Detection: The New Benchmark and Detection
  Network*, Sensors (2020), DOI [10.3390/s20061562](https://doi.org/10.3390/s20061562).

The reviewed source pages do not establish a dataset redistribution licence for
this repository. No bulk mirror or new download permission is implied here.
Dataset acquisition is a documented manual step, followed by automated checksum
verification. The project does not silently download different mirrors or images.

`neu_manifest.json` records file hashes and the existing split assignment.
`gc10_manifest.json` is copied from the trained experiment's saved manifest,
including labels, decoded-pixel hashes and capture-group assignments. The cleanup
does not regenerate any split or reapply different exclusions to the saved run.

Use `scripts/prepare_data.ps1` or `scripts/prepare_data.sh` to verify your local
copies. A mismatch fails rather than changing labels or rebuilding a split.
The full GC10 exclusion list and explicit spelling repairs remain in its generated
metrics report. Capture tokens are inferred and are not verified physical sheet IDs.
