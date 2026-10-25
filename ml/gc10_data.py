"""Validate GC10 XML labels and prepare one record per unique image."""

import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
from sklearn.model_selection import GroupShuffleSplit

CLASS_NAMES = [
    "punching_hole",
    "welding_line",
    "crescent_gap",
    "water_spot",
    "oil_spot",
    "silk_spot",
    "inclusion",
    "rolled_pit",
    "crease",
    "waist_folding",
]
RAW_LABELS = [
    "1_chongkong",
    "2_hanfeng",
    "3_yueyawan",
    "4_shuiban",
    "5_youban",
    "6_siban",
    "7_yiwu",
    "8_yahen",
    "9_zhehen",
    "10_yaozhe",
]
LABEL_INDEX = {label: index for index, label in enumerate(RAW_LABELS)}
# Explicit spelling repair: the spreadsheet defines category 10 as 10_yaozhe.
LABEL_ALIASES = {"10_yaozhed": "10_yaozhe"}
CAPTURE_PATTERN = re.compile(r"^img_\d+_(\d+)_\d+$")


def capture_group(filename):
    match = CAPTURE_PATTERN.fullmatch(Path(filename).stem)
    if match is None:
        raise ValueError(f"Cannot infer capture group: {filename}")
    return match.group(1)


def decoded_identity(path):
    with Image.open(path) as source:
        image = source.convert("RGB")
        identity = str(image.size).encode() + image.tobytes()
        return hashlib.sha256(identity).hexdigest(), image.size


def parse_annotation(path):
    root = ET.parse(path).getroot()
    filename = root.findtext("filename")
    if not filename or Path(filename).name != filename:
        raise ValueError("invalid_filename")
    dimensions = (int(root.findtext("size/width")), int(root.findtext("size/height")))
    labels, repairs = set(), Counter()
    objects = root.findall("object")
    if not objects:
        raise ValueError("no_objects")
    for item in objects:
        raw_label = item.findtext("name")
        label = LABEL_ALIASES.get(raw_label, raw_label)
        if label not in LABEL_INDEX:
            raise ValueError(f"unknown_label:{raw_label}")
        if label != raw_label:
            repairs[raw_label] += 1
        left, top, right, bottom = [
            float(item.findtext(f"bndbox/{name}")) for name in ("xmin", "ymin", "xmax", "ymax")
        ]
        if not (0 <= left < right <= dimensions[0] and 0 <= top < bottom <= dimensions[1]):
            raise ValueError("invalid_box")
        labels.add(LABEL_INDEX[label])
    return filename, dimensions, sorted(labels), repairs


def prepare_manifest(archive_root):
    archive_root = Path(archive_root)
    images = defaultdict(list)
    for path in sorted(archive_root.rglob("*.jpg")):
        images[path.name].append(path)
    annotations = sorted((archive_root / "lable").glob("*.xml"))
    if not images or not annotations:
        raise ValueError("Expected GC10 image folders and lable/*.xml")
    records, excluded, repaired = [], [], Counter()
    seen_pixels = {}
    duplicate_copies = 0
    for annotation in annotations:
        try:
            filename, dimensions, labels, repairs = parse_annotation(annotation)
            candidates = images.get(filename, [])
            if not candidates:
                raise ValueError("missing_image")
            identities = [decoded_identity(path) for path in candidates]
            if any(size != dimensions for _, size in identities):
                raise ValueError("size_mismatch")
            if len({identity for identity, _ in identities}) != 1:
                raise ValueError("conflicting_image_copies")
            identity = identities[0][0]
            group = capture_group(filename)
            if identity in seen_pixels:
                raise ValueError("duplicate_pixels_under_another_filename")
            seen_pixels[identity] = filename
            duplicate_copies += len(candidates) - 1
            records.append(
                dict(
                    path=candidates[0].relative_to(archive_root).as_posix(),
                    filename=filename,
                    labels=labels,
                    capture_group=group,
                    decoded_sha256=identity,
                )
            )
            repaired.update(repairs)
        except (ValueError, TypeError, ET.ParseError, OSError) as error:
            excluded.append(dict(annotation=annotation.name, reason=str(error)))
    summary = dict(
        image_files=sum(map(len, images.values())),
        unique_filenames=len(images),
        annotations=len(annotations),
        usable_images=len(records),
        duplicate_copies_removed=duplicate_copies,
        explicit_label_repairs=dict(repaired),
        excluded_annotations=excluded,
        images_without_annotations=len(set(images) - {path.stem + ".jpg" for path in annotations}),
        class_names=CLASS_NAMES,
        independence_verified=False,
        limitation="Capture groups inferred from filename batch tokens; physical sheet IDs and licensing not independently verified.",
    )
    return records, summary


def split_records(records, seed=42):
    targets = np.zeros((len(records), len(CLASS_NAMES)), dtype=np.float32)
    for index, record in enumerate(records):
        targets[index, record["labels"]] = 1
    groups = np.array([record["capture_group"] for record in records])
    for attempt in range(200):
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + attempt)
        train, remaining = next(splitter.split(targets, groups=groups))
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed + attempt)
        val_local, test_local = next(splitter.split(targets[remaining], groups=groups[remaining]))
        splits = dict(train=train, val=remaining[val_local], test=remaining[test_local])
        if all((targets[indices].sum(axis=0) > 0).all() for indices in splits.values()):
            return splits, targets
    raise ValueError("Could not create group-disjoint splits with all ten classes represented")
