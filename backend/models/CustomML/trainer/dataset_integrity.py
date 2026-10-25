"""Image identities and split checks included in the cloud trainer package."""

import hashlib
from pathlib import Path

from PIL import Image

CLASS_NAMES = [
    "Crazing",
    "Inclusion",
    "Patches",
    "Pitted_Surface",
    "Rolled_in_Scale",
    "Scratches",
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ("train", "val", "test")


def is_supported_image(path):
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def image_hashes(path):
    with Image.open(path) as source:
        image = source.convert("RGB")
        decoded = str(image.size).encode() + image.tobytes()
    return dict(
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        decoded_sha256=hashlib.sha256(decoded).hexdigest(),
    )


def validate_dataset_splits(dataset_root):
    """Reject missing classes and duplicated file/pixel contents before training."""
    dataset_root = Path(dataset_root)
    seen_files, seen_pixels, counts, identities = {}, {}, {}, []
    for split in SPLITS:
        split_root = dataset_root / split
        if not split_root.is_dir():
            raise ValueError(f"Missing split: {split_root}")
        labels = {folder.name for folder in split_root.iterdir() if folder.is_dir()}
        if labels != set(CLASS_NAMES):
            raise ValueError(f"{split}: expected classes {CLASS_NAMES}, got {sorted(labels)}")
        for label in CLASS_NAMES:
            paths = sorted(
                path
                for path in (split_root / label).rglob("*")
                if path.suffix.lower() in IMAGE_EXTENSIONS
            )
            if not paths:
                raise ValueError(f"Empty class: {split}/{label}")
            counts[f"{split}/{label}"] = len(paths)
            for path in paths:
                hashes = image_hashes(path)
                for key, seen in (
                    ("sha256", seen_files),
                    ("decoded_sha256", seen_pixels),
                ):
                    if hashes[key] in seen:
                        raise ValueError(f"Duplicate {key} image: {path} and {seen[hashes[key]]}")
                    seen[hashes[key]] = path
                identities.append(f"{split}/{label}/{hashes['sha256']}")
    fingerprint = hashlib.sha256("\n".join(sorted(identities)).encode()).hexdigest()
    return dict(
        dataset_sha256=fingerprint,
        counts=counts,
        exact_duplicate_check="passed",
        independence_verified=False,
    )
