"""Verify supplied local datasets against frozen split manifests; never re-split."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--neu-root", type=Path)
    parser.add_argument("--gc10-root", type=Path)
    arguments = parser.parse_args()
    if arguments.neu_root is None and arguments.gc10_root is None:
        parser.error(
            "Supply --neu-root or --gc10-root after downloading from the documented sources"
        )
    for dataset, directory in (("neu", arguments.neu_root), ("gc10", arguments.gc10_root)):
        if directory is None:
            continue
        manifest = json.loads((ROOT / f"data/{dataset}_manifest.json").read_text(encoding="utf-8"))
        seen_splits: dict[str, str] = {}
        for row in manifest:
            path = (directory / row["path"]).resolve()
            if not path.is_relative_to(directory.resolve()):
                raise ValueError("Dataset path escapes its root")
            if dataset == "neu":
                identity = hashlib.sha256(path.read_bytes()).hexdigest()
                expected = row["sha256"]
            else:
                with Image.open(path) as source:
                    image = source.convert("RGB")
                    identity = hashlib.sha256(
                        str(image.size).encode() + image.tobytes()
                    ).hexdigest()
                expected = row["decoded_sha256"]
                group = row["capture_group"]
                if group in seen_splits and seen_splits[group] != row["split"]:
                    raise ValueError("Capture group crosses frozen splits")
                seen_splits[group] = row["split"]
            if identity != expected:
                raise ValueError(f"Dataset mismatch: {dataset}/{row['path']}")


if __name__ == "__main__":
    main()
