"""Reproducible split audit. Similarity candidates require human review."""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from scipy.fft import dctn
from CustomML.trainer.dataset_integrity import IMAGE_EXTENSIONS, SPLITS, image_hashes

EXTENSIONS = IMAGE_EXTENSIONS
PHASH_IMAGE_SIZE = 32
PHASH_FREQUENCY_SIZE = 8
MAX_PHASH_DISTANCE = 6
LOGGER = logging.getLogger(__name__)


def inspect_image(path):
    with Image.open(path) as source:
        image = source.convert("RGB")
        small = np.asarray(
            image.convert("L").resize((PHASH_IMAGE_SIZE, PHASH_IMAGE_SIZE)), dtype=float
        )
        low = dctn(small, norm="ortho")[:PHASH_FREQUENCY_SIZE, :PHASH_FREQUENCY_SIZE].flatten()[1:]
        bits = low > np.median(low)
        return bits, image.size


def collect_images(root):
    rows, hashes = [], []
    for split in SPLITS:
        for path in sorted((root / split).rglob("*")):
            if path.suffix.lower() not in EXTENSIONS:
                continue
            perceptual, size = inspect_image(path)
            rows.append(
                dict(
                    split=split,
                    label=path.parent.name,
                    path=path.relative_to(root).as_posix(),
                    basename=path.name,
                    **image_hashes(path),
                    width=size[0],
                    height=size[1],
                )
            )
            hashes.append(perceptual)
    frame = pd.DataFrame(rows)
    if frame.empty or set(frame.split) != {"train", "val", "test"}:
        raise ValueError("All three nonempty splits are required")
    return frame, np.asarray(hashes)


def find_similar_images(frame, bits):
    candidates, nearest = [], []
    for i, row in frame.iterrows():
        other = np.flatnonzero(frame.split.to_numpy() != row.split)
        distances = np.count_nonzero(bits[other] != bits[i], axis=1)
        for j, distance in zip(other, distances):
            if j > i and distance <= MAX_PHASH_DISTANCE:
                candidates.append(
                    dict(
                        left=row.path,
                        right=frame.iloc[j].path,
                        phash_distance=int(distance),
                    )
                )
        if row.split == "test":
            training = np.flatnonzero(frame.split.to_numpy() == "train")
            distance = np.count_nonzero(bits[training] != bits[i], axis=1)
            j = training[int(distance.argmin())]
            nearest.append(
                dict(
                    test=row.path,
                    nearest_train=frame.iloc[j].path,
                    phash_distance=int(distance.min()),
                )
            )
    return candidates, nearest


def audit_imports(frame, imports):
    imported = []
    for split in SPLITS:
        path = imports / f"automl_import_{split}_edgeautoml_fullnames_dedup.csv"
        table = pd.read_csv(path, header=None, names=["uri", "label"])
        table["split"] = split
        table["key"] = table.label + "/" + table.uri.str.rsplit("/", n=1).str[-1]
        imported.append(table)
    all_imports = pd.concat(imported, ignore_index=True)
    local_keys = frame.label + "/" + frame.basename
    local_test = set(local_keys[frame.split == "test"])
    train_keys = set(all_imports.loc[all_imports.split == "train", "key"])
    val_keys = set(all_imports.loc[all_imports.split == "val", "key"])
    return dict(
        test_images_listed_as_automl_train=sorted(local_test & train_keys),
        test_images_listed_as_automl_val=sorted(local_test & val_keys),
        duplicate_source_keys=all_imports.loc[all_imports.key.duplicated(False), "key"].tolist(),
        per_split={
            split: dict(
                local_count=int((frame.split == split).sum()),
                imported_count=int((all_imports.split == split).sum()),
                missing_from_import=sorted(
                    set(local_keys[frame.split == split])
                    - set(all_imports.loc[all_imports.split == split, "key"])
                ),
            )
            for split in SPLITS
        },
        limitation="Local CSV split intent only; no verified cloud training-job lineage",
    )


def audit(root, imports=None):
    frame, bits = collect_images(root)
    duplicates = {}
    for column in ("sha256", "decoded_sha256"):
        duplicates[column] = [
            group[["split", "path"]].to_dict("records")
            for _, group in frame.groupby(column)
            if group.split.nunique() > 1
        ]
    candidates, nearest = find_similar_images(frame, bits)
    manifest_report = audit_imports(frame, imports) if imports else {}
    summary = dict(
        image_count=len(frame),
        counts=frame.groupby(["split", "label"]).size().to_dict(),
        exact_cross_split_groups=duplicates,
        near_duplicate_candidate_count=len(candidates),
        phash_max_distance=MAX_PHASH_DISTANCE,
        automl_import_audit=manifest_report,
        independence_verified=False,
        limitations=[
            "Perceptual hashes are screening heuristics, not proof of common source.",
            "Sheet/session identities and cloud training-job lineage are unavailable.",
            "Existing test scores have already informed development.",
        ],
    )
    summary["counts"] = {f"{s}/{c}": int(n) for (s, c), n in summary["counts"].items()}
    return (
        frame,
        pd.DataFrame(candidates, columns=["left", "right", "phash_distance"]),
        pd.DataFrame(nearest),
        summary,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--automl-imports", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.out_dir.exists():
        parser.error("Output directory must be new")
    frame, candidates, nearest, summary = audit(args.dataset_root, args.automl_imports)
    args.out_dir.mkdir(parents=True)
    frame.to_csv(args.out_dir / "image_manifest.csv", index=False)
    candidates.to_csv(args.out_dir / "near_duplicate_candidates.csv", index=False)
    nearest.to_csv(args.out_dir / "test_nearest_train.csv", index=False)
    (args.out_dir / "audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    LOGGER.info("Audit summary=%s", json.dumps(summary))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
