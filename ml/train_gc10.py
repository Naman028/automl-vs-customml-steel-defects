"""Train a separate GC10 multilabel classifier locally using frozen NEU features."""

import argparse
import copy
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, cast

import pandas as pd
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset

from backend.inference.gc10_model import create_backbone, image_transform
from ml.gc10_data import CLASS_NAMES, prepare_manifest, split_records
from ml.evaluation_metrics import calculate_metrics as calculate_metrics, select_thresholds

LOGGER = logging.getLogger(__name__)
SEED = 42
LEARNING_RATE = 0.01
WEIGHT_DECAY = 0.01
EARLY_STOPPING_PATIENCE = 10


class ImageDataset(Dataset[torch.Tensor]):
    def __init__(self, root: Path, records: list[dict[str, Any]]) -> None:
        self.root, self.records = root, records
        self.transform = image_transform()

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> torch.Tensor:
        with Image.open(self.root / self.records[index]["path"]) as image:
            return cast(torch.Tensor, self.transform(image.convert("RGB")))


def load_backbone(checkpoint):
    backbone, feature_count = create_backbone()
    stored = torch.load(checkpoint, map_location="cpu", weights_only=True)
    weights = {
        name: value
        for name, value in stored["model_state_dict"].items()
        if not name.startswith("fc.")
    }
    backbone.load_state_dict(weights, strict=True)
    backbone.requires_grad_(False)
    return backbone, feature_count


def extract_features(
    backbone: torch.nn.Module, dataset: ImageDataset, batch_size: int
) -> torch.Tensor:
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    features = []
    with torch.inference_mode():
        for batch_index, images in enumerate(loader):
            features.append(backbone(images))
            if batch_index % 10 == 0:
                LOGGER.info(
                    "Extracted images=%d/%d",
                    min((batch_index + 1) * batch_size, len(dataset)),
                    len(dataset),
                )
    return torch.cat(features).clone()


def fit_head(features, targets, splits, epochs):
    train_features, validation_features = (
        features[splits["train"]],
        features[splits["val"]],
    )
    train_targets, validation_targets = targets[splits["train"]], targets[splits["val"]]
    mean, std = train_features.mean(0), train_features.std(0).clamp_min(1e-6)
    train_features = (train_features - mean) / std
    validation_features = (validation_features - mean) / std
    head = torch.nn.Linear(features.shape[1], len(CLASS_NAMES))
    positive = train_targets.sum(0)
    loss_function = torch.nn.BCEWithLogitsLoss(
        pos_weight=(len(train_targets) - positive) / positive
    )
    validation_loss_function = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(head.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    best_loss, best_state, stale_epochs = float("inf"), None, 0
    history = []
    for epoch in range(epochs):
        optimizer.zero_grad()
        train_loss = loss_function(head(train_features), train_targets)
        train_loss.backward()
        optimizer.step()
        with torch.no_grad():
            validation_loss = float(
                validation_loss_function(head(validation_features), validation_targets)
            )
        history.append(
            dict(
                epoch=epoch + 1,
                train_loss=float(train_loss.detach()),
                validation_loss=validation_loss,
            )
        )
        if validation_loss < best_loss - 1e-4:
            best_loss, best_state, stale_epochs = (
                validation_loss,
                copy.deepcopy(head.state_dict()),
                0,
            )
        else:
            stale_epochs += 1
        if stale_epochs >= EARLY_STOPPING_PATIENCE:
            break
    head.load_state_dict(best_state)
    return head.eval(), mean, std, history


def write_reports(output_dir, records, splits, probabilities, targets, thresholds, audit, history):
    assignment = {int(index): split for split, indices in splits.items() for index in indices}
    manifest = [dict(**record, split=assignment[index]) for index, record in enumerate(records)]
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    test = splits["test"]
    metrics = dict(
        status="trained",
        task="GC10 image-level multilabel classification",
        classes=CLASS_NAMES,
        feature_extractor="Frozen NEU-trained ResNet18; only the GC10 classifier head was trained",
        source="GC10 archive; XML object labels converted to per-image presence labels",
        split_counts={name: len(indices) for name, indices in splits.items()},
        group_counts={
            name: len({records[int(index)]["capture_group"] for index in indices})
            for name, indices in splits.items()
        },
        split_method="Group-disjoint filename capture tokens; fixed seed, all classes present",
        seed=SEED,
        independence_verified=False,
        epochs_completed=len(history),
        limitation="Local group-held-out baseline. Capture tokens are inferred; independent camera generalization and dataset licensing remain unverified.",
        audit=audit,
        validation=calculate_metrics(
            targets[splits["val"]], probabilities[splits["val"]], thresholds
        ),
        test=calculate_metrics(targets[test], probabilities[test], thresholds),
        thresholds_selected_on="validation only",
        test_sample_count=len(test),
        history=history,
    )
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    rows = []
    for index in test:
        row = dict(
            filename=records[int(index)]["filename"],
            capture_group=records[int(index)]["capture_group"],
        )
        for class_index, name in enumerate(CLASS_NAMES):
            row[f"true_{name}"] = int(targets[index, class_index])
            row[f"probability_{name}"] = float(probabilities[index, class_index])
            row[f"predicted_{name}"] = int(
                probabilities[index, class_index] >= thresholds[class_index]
            )
        rows.append(row)
    pd.DataFrame(rows).to_csv(output_dir / "test_predictions.csv", index=False)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parents[1] / "models"
    parser.add_argument("--archive-dir", type=Path, default=base.parent / "data/raw/gc10")
    parser.add_argument("--out-dir", type=Path, default=base / "GC10/outputs_local_v1")
    parser.add_argument(
        "--backbone-checkpoint", type=Path, default=base / "CustomML/outputs/best.pt"
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    if args.out_dir.exists():
        parser.error("Choose a new output directory; existing experiments are never overwritten")
    if args.epochs < 1 or args.batch_size < 1:
        parser.error("Epochs and batch size must be positive")
    torch.manual_seed(SEED)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    started = time.perf_counter()
    records, audit = prepare_manifest(args.archive_dir)
    splits, targets = split_records(records, SEED)
    args.out_dir.mkdir(parents=True)
    LOGGER.info(
        "Prepared images=%d excluded=%d splits=%s",
        len(records),
        len(audit["excluded_annotations"]),
        {s: len(i) for s, i in splits.items()},
    )
    backbone, _ = load_backbone(args.backbone_checkpoint)
    features = extract_features(backbone, ImageDataset(args.archive_dir, records), args.batch_size)
    # Copy inference tensors before autograd trains the small classification head.
    features = features.detach().clone()
    head, mean, std, history = fit_head(features, torch.from_numpy(targets), splits, args.epochs)
    with torch.no_grad():
        probabilities = torch.sigmoid(head((features - mean) / std)).numpy()
    thresholds = select_thresholds(targets[splits["val"]], probabilities[splits["val"]])
    torch.save(
        dict(
            backbone=backbone.state_dict(),
            head=head.state_dict(),
            mean=mean,
            std=std,
            classes=CLASS_NAMES,
            thresholds=thresholds,
        ),
        args.out_dir / "model.pt",
    )
    metrics = write_reports(
        args.out_dir,
        records,
        splits,
        probabilities,
        targets,
        thresholds,
        audit,
        history,
    )
    metrics["training_seconds"] = round(time.perf_counter() - started, 2)
    metrics["backbone_sha256"] = hashlib.sha256(args.backbone_checkpoint.read_bytes()).hexdigest()
    metrics["model_sha256"] = hashlib.sha256((args.out_dir / "model.pt").read_bytes()).hexdigest()
    assignment = {int(index): split for split, indices in splits.items() for index in indices}
    identities = sorted(
        f"{assignment[index]}/{record['decoded_sha256']}/{record['labels']}"
        for index, record in enumerate(records)
    )
    metrics["dataset_manifest_sha256"] = hashlib.sha256("\n".join(identities).encode()).hexdigest()
    metrics["training_configuration"] = dict(
        learning_rate=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
        max_epochs=args.epochs,
        early_stopping_patience=EARLY_STOPPING_PATIENCE,
        positive_class_weights="training split only",
        feature_normalization="training split only",
        feature_extractor_frozen=True,
    )
    (args.out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    LOGGER.info(
        "Completed GC10 training seconds=%.1f test=%s",
        metrics["training_seconds"],
        metrics["test"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
