
import argparse
import csv
import json
import os
import random
import time
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from tqdm import tqdm
from google.cloud import storage

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

def get_dataloaders(data_dir: Union[str, Path], image_size: int, batch_size: int, num_workers: int):
    data_dir = Path(data_dir)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    test_dir = data_dir / "test"

    train_tfms = transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.65, 1.0), ratio=(0.8, 1.2)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.25),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.1),
        transforms.RandomPerspective(distortion_scale=0.15, p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.12), ratio=(0.5, 2.0)),
    ])
    eval_tfms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
    ])

    train_ds = datasets.ImageFolder(train_dir, transform=train_tfms)
    val_ds = datasets.ImageFolder(val_dir, transform=eval_tfms)
    test_ds = datasets.ImageFolder(test_dir, transform=eval_tfms)

    pin_memory = torch.cuda.is_available()
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=pin_memory)
    val_dl = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)
    test_dl = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

    return train_ds, val_ds, test_ds, train_dl, val_dl, test_dl

@torch.no_grad()
def evaluate(model, dl, device, criterion):
    model.eval()
    all_preds, all_labels = [], []
    correct, total, running_loss = 0, 0, 0.0
    for x, y in dl:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        loss = criterion(logits, y)
        preds = torch.argmax(logits, dim=1)
        all_preds.append(preds.cpu())
        all_labels.append(y.cpu())
        correct += (preds == y).sum().item()
        total += y.numel()
        running_loss += loss.item() * x.size(0)
    acc = correct / max(total, 1)
    all_preds = torch.cat(all_preds).numpy()
    all_labels = torch.cat(all_labels).numpy()
    return running_loss / max(total, 1), acc, all_labels, all_preds


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def compute_metrics(y_true, y_pred, class_names):
    num_classes = len(class_names)
    cm = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
    for t, p in zip(y_true, y_pred):
        cm[int(t)][int(p)] += 1

    per_class = {}
    total_correct = 0
    total = 0
    for i, name in enumerate(class_names):
        tp = cm[i][i]
        fp = sum(cm[r][i] for r in range(num_classes)) - tp
        fn = sum(cm[i][c] for c in range(num_classes)) - tp
        support = sum(cm[i])
        total_correct += tp
        total += support

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_class[name] = {
            "precision": precision,
            "recall": recall,
            "f1-score": f1,
            "support": support,
        }

    accuracy = total_correct / max(total, 1)

    macro_precision = sum(v["precision"] for v in per_class.values()) / max(num_classes, 1)
    macro_recall = sum(v["recall"] for v in per_class.values()) / max(num_classes, 1)
    macro_f1 = sum(v["f1-score"] for v in per_class.values()) / max(num_classes, 1)

    weighted_precision = sum(v["precision"] * v["support"] for v in per_class.values()) / max(total, 1)
    weighted_recall = sum(v["recall"] * v["support"] for v in per_class.values()) / max(total, 1)
    weighted_f1 = sum(v["f1-score"] * v["support"] for v in per_class.values()) / max(total, 1)

    report = {
        **per_class,
        "accuracy": accuracy,
        "macro avg": {
            "precision": macro_precision,
            "recall": macro_recall,
            "f1-score": macro_f1,
            "support": total,
        },
        "weighted avg": {
            "precision": weighted_precision,
            "recall": weighted_recall,
            "f1-score": weighted_f1,
            "support": total,
        },
    }

    return report, cm

def _parse_gcs_uri(uri: str) -> Tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {uri}")
    path = uri[5:]
    parts = path.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix

def _download_gcs_prefix(gcs_uri: str, dest_dir: Path) -> Path:
    bucket_name, prefix = _parse_gcs_uri(gcs_uri)
    dest_dir.mkdir(parents=True, exist_ok=True)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    for blob in client.list_blobs(bucket, prefix=prefix):
        if blob.name.endswith("/"):
            continue
        rel_path = blob.name[len(prefix):].lstrip("/")
        local_path = dest_dir / rel_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(local_path)
    return dest_dir

def _write_history_csv(history, out_dir: Path) -> None:
    csv_path = out_dir / "history.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["epoch", "train_loss", "train_acc", "val_loss", "val_acc", "lr"],
        )
        writer.writeheader()
        for row in history:
            writer.writerow(row)

def _write_confusion_matrix_csv(cm, out_dir: Path) -> None:
    csv_path = out_dir / "confusion_matrix.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        for row in cm:
            writer.writerow(row)

def _plot_curves(history, out_dir: Path) -> None:
    if plt is None:
        print("Matplotlib not available. Skipping curve plots.")
        return
    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    val_acc = [h["val_acc"] for h in history]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(epochs, train_loss, marker="o", color="#2563eb")
    axes[0].plot(epochs, val_loss, marker="o", color="#ef4444")
    axes[0].legend(["Train", "Validation"])
    axes[0].set_title("Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(epochs, val_acc, marker="o", color="#10b981")
    axes[1].set_title("Validation Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(str(out_dir / "training_curves.png"), dpi=150)
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True, help="Path to dataset root containing train/val/test")
    ap.add_argument("--output_dir", default="outputs", help="Where to write model + metrics")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-4, help="Classifier-head learning rate")
    ap.add_argument("--backbone_lr", type=float, default=2e-5)
    ap.add_argument("--weight_decay", type=float, default=1e-3)
    ap.add_argument("--label_smoothing", type=float, default=0.1)
    ap.add_argument("--patience", type=int, default=4)
    ap.add_argument("--min_delta", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--image_size", type=int, default=224)
    ap.add_argument("--num_workers", type=int, default=2)
    ap.add_argument("--no_pretrained", action="store_true")
    args = ap.parse_args()
    seed_everything(args.seed)

    output_dir = os.getenv("AIP_MODEL_DIR", args.output_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if args.data_dir.startswith("gs://"):
        local_data_dir = _download_gcs_prefix(args.data_dir, Path("/tmp/data"))
    else:
        local_data_dir = Path(args.data_dir)

    env_batch_size = os.getenv("TRAIN_BATCH_SIZE")
    env_num_workers = os.getenv("TRAIN_NUM_WORKERS")
    if env_batch_size:
        args.batch_size = int(env_batch_size)
    if env_num_workers:
        args.num_workers = int(env_num_workers)

    train_ds, val_ds, test_ds, train_dl, val_dl, test_dl = get_dataloaders(
        str(local_data_dir), args.image_size, args.batch_size, args.num_workers
    )

    # ResNet18 is cheap and stable for local verification.
    weights = None if args.no_pretrained else models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, len(train_ds.classes))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=args.label_smoothing)
    backbone_parameters = [p for name, p in model.named_parameters() if not name.startswith("fc.")]
    optimizer = optim.AdamW(
        [
            {"params": backbone_parameters, "lr": args.backbone_lr},
            {"params": model.fc.parameters(), "lr": args.lr},
        ],
        weight_decay=args.weight_decay,
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.3, patience=2, min_lr=1e-7
    )

    best_val = -1.0
    best_val_loss = float("inf")
    epochs_without_improvement = 0
    history = []
    started_at = time.perf_counter()

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss, train_correct, train_total = 0.0, 0, 0
        for x, y in tqdm(train_dl, desc=f"Epoch {epoch}/{args.epochs}", leave=False):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)
            train_correct += (torch.argmax(logits, dim=1) == y).sum().item()
            train_total += y.numel()

        train_loss = running_loss / max(len(train_ds), 1)
        train_acc = train_correct / max(train_total, 1)
        val_loss, val_acc, _, _ = evaluate(model, val_dl, device, criterion)
        scheduler.step(val_loss)

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "lr": optimizer.param_groups[0]["lr"],
        })
        print(json.dumps(history[-1]))

        # Validation loss is more sensitive to overconfidence than accuracy and is
        # therefore the primary selection metric. Accuracy breaks near-ties.
        improved = val_loss < (best_val_loss - args.min_delta)
        tied_loss_better_acc = abs(val_loss - best_val_loss) <= args.min_delta and val_acc > best_val
        if improved or tied_loss_better_acc:
            best_val_loss = val_loss
            best_val = val_acc
            epochs_without_improvement = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "classes": train_ds.classes,
                "image_size": args.image_size,
                "architecture": "resnet18",
                "best_epoch": epoch,
                "best_val_loss": best_val_loss,
                "best_val_acc": best_val,
                "training_config": vars(args),
            }, out / "best.pt")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"Early stopping at epoch {epoch}; best validation loss={best_val_loss:.6f}")
                break

    # Final test report using best model
    ckpt = torch.load(out / "best.pt", map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    test_loss, test_acc, y_true, y_pred = evaluate(model, test_dl, device, criterion)

    report, cm = compute_metrics(y_true, y_pred, train_ds.classes)

    metrics = {
        "device": device,
        "num_classes": len(train_ds.classes),
        "classes": train_ds.classes,
        "best_val_acc": best_val,
        "best_val_loss": best_val_loss,
        "test_loss": test_loss,
        "test_acc": test_acc,
        "training_time_seconds": round(time.perf_counter() - started_at, 2),
        "selection_metric": "validation_loss",
        "history": history,
        "classification_report": report,
        "confusion_matrix": cm,
    }

    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out / "classification_report.json").write_text(json.dumps(report, indent=2))
    _write_history_csv(history, out)
    _write_confusion_matrix_csv(cm, out)
    _plot_curves(history, out)
    print("Saved:", str(out / "best.pt"), str(out / "metrics.json"))

if __name__ == "__main__":
    main()
