"""Prepare owner-approved release files locally; never creates or publishes a release."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any, cast

import torch

ROOT = Path(__file__).resolve().parents[1]


def file_sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def prepare_assets(output: Path, include_automl: bool) -> list[dict[str, Any]]:
    if output.exists():
        raise FileExistsError("Choose a new release preparation directory")
    custom_path = ROOT / "models/CustomML/outputs/best.pt"
    gc10_path = ROOT / "models/GC10/outputs_local_v1/model.pt"
    custom = cast(dict[str, Any], torch.load(custom_path, map_location="cpu", weights_only=True))
    gc10 = cast(dict[str, Any], torch.load(gc10_path, map_location="cpu", weights_only=True))
    backbone = {
        name: value
        for name, value in custom["model_state_dict"].items()
        if not name.startswith("fc.")
    }
    if set(backbone) != set(gc10["backbone"]) or any(
        not torch.equal(value, gc10["backbone"][name]) for name, value in backbone.items()
    ):
        raise ValueError(
            "GC10 backbone differs from the NEU checkpoint; cannot export only its head"
        )
    head = {name: value for name, value in gc10.items() if name != "backbone"}
    head.update(format="gc10-head-v1", backbone_sha256=file_sha256(custom_path))
    output.mkdir(parents=True)
    shutil.copyfile(custom_path, output / "neu-resnet18.pt")
    torch.save(head, output / "gc10-head.pt")
    if include_automl:
        shutil.copyfile(ROOT / "models/AutoML/AutoML model.tflite", output / "automl-vision.tflite")
    assets = [
        dict(name=path.name, sha256=file_sha256(path), bytes=path.stat().st_size)
        for path in sorted(output.iterdir())
    ]
    (output / "assets.json").write_text(json.dumps(assets, indent=2), encoding="utf-8")
    return assets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--include-automl",
        action="store_true",
        help="Include only with confirmed owner training provenance",
    )
    arguments = parser.parse_args()
    print(json.dumps(prepare_assets(arguments.output_dir, arguments.include_automl), indent=2))


if __name__ == "__main__":
    main()
