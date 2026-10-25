"""Provision approved model artifacts with mandatory SHA-256 verification."""

import argparse
import hashlib
import json
import logging
from pathlib import Path
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger(__name__)


def verify(path: Path, expected: str) -> bool:
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, help="Local approved bundle preserving manifest paths"
    )
    arguments = parser.parse_args()
    registry = json.loads((ROOT / "models/registry.json").read_text(encoding="utf-8"))
    for artifact in registry["models"]:
        destination = (ROOT / artifact["path"]).resolve()
        if not destination.is_relative_to(ROOT):
            raise ValueError("Artifact destination escapes the repository")
        if verify(destination, artifact["sha256"]):
            LOGGER.info("Verified model=%s", artifact["name"])
            continue
        if destination.exists():
            raise ValueError(
                f"Existing file checksum mismatch: {destination}; refusing to overwrite"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        pending = destination.with_suffix(destination.suffix + ".download")
        if pending.exists():
            raise FileExistsError(f"Review existing partial artifact: {pending}")
        if arguments.source_dir:
            source = arguments.source_dir / artifact["path"]
            if not source.is_file() and artifact.get("asset_name"):
                source = arguments.source_dir / artifact["asset_name"]
            shutil.copyfile(source, pending)
        elif artifact["url"]:
            if not artifact["url"].startswith("https://"):
                raise ValueError("Artifact download requires HTTPS")
            urllib.request.urlretrieve(artifact["url"], pending)
        else:
            raise RuntimeError(
                "Release assets are not published. Use --source-dir with an approved local bundle; do not download unverified weights."
            )
        if not verify(pending, artifact["sha256"]):
            raise ValueError(f"Checksum mismatch; partial file retained for review: {pending}")
        pending.replace(destination)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
