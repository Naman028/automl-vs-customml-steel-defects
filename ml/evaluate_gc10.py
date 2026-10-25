"""Evaluate the frozen GC10 test manifest without training or threshold selection."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from backend.inference.gc10 import load_model
from ml.evaluation_metrics import calculate_metrics
from ml.train_gc10 import ImageDataset, extract_features


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parents[1] / "models"
    parser.add_argument("--archive-dir", type=Path, default=base.parent / "data/raw/gc10")
    parser.add_argument("--run-dir", type=Path, default=base / "GC10/outputs_local_v1")
    parser.add_argument("--out-dir", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.out_dir.exists():
        parser.error("Use a new output directory")
    records = json.loads((arguments.run_dir / "manifest.json").read_text(encoding="utf-8"))
    test = [record for record in records if record["split"] == "test"]
    backbone, head, checkpoint = load_model(str(arguments.run_dir / "model.pt"))
    torch.set_num_threads(min(4, torch.get_num_threads()))
    features = extract_features(backbone, ImageDataset(arguments.archive_dir, test), 16)
    with torch.inference_mode():
        probabilities = torch.sigmoid(
            head((features - checkpoint["mean"]) / checkpoint["std"])
        ).numpy()
    targets = np.zeros_like(probabilities)
    for index, record in enumerate(test):
        targets[index, record["labels"]] = 1
    result = calculate_metrics(targets, probabilities, checkpoint["thresholds"])
    arguments.out_dir.mkdir(parents=True)
    (arguments.out_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    pd.DataFrame(
        [
            dict(
                filename=record["filename"],
                probabilities=probabilities[index].tolist(),
                predicted=(probabilities[index] >= checkpoint["thresholds"]).tolist(),
            )
            for index, record in enumerate(test)
        ]
    ).to_json(arguments.out_dir / "predictions.json", orient="records", indent=2)


if __name__ == "__main__":
    main()
