"""Render README benchmark values from saved reports without modifying the reports."""

import argparse
import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- RESULTS:START -->"
END = "<!-- RESULTS:END -->"


def read_report(name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads((ROOT / "reports/benchmarks" / name).read_text(encoding="utf-8")),
    )


def render_results() -> str:
    automl = read_report("neu_automl.json")["core"]
    custom = read_report("neu_custom.json")["core"]
    gc10 = read_report("gc10.json")["test"]
    return "\n".join(
        [
            START,
            "| Benchmark | Model | Key metrics |",
            "| --- | --- | --- |",
            "| NEU six-class (existing split) | "
            "[Google AutoML Vision, TFLite](reports/benchmarks/neu_automl.json) | "
            f"Accuracy {automl['accuracy']:.2%}; p50 latency {automl['inference_ms']['p50']:.2f} ms |",
            "| NEU six-class (existing split) | "
            "[Custom ResNet18](reports/benchmarks/neu_custom.json) | "
            f"Deployed accuracy {custom['accuracy']:.2%}; raw accuracy "
            f"{custom['raw_argmax_accuracy']:.2%}; p50 latency {custom['inference_ms']['p50']:.2f} ms |",
            "| GC10 ten-class multilabel | "
            "[Baseline – frozen ResNet18 backbone](reports/benchmarks/gc10.json) | "
            f"Macro-F1 {gc10['macro_f1']:.2%}; mAP {gc10['mean_average_precision']:.2%}; "
            f"exact-match {gc10['exact_match_accuracy']:.2%} |",
            END,
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if README values are stale")
    arguments = parser.parse_args()
    path = ROOT / "README.md"
    original = path.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise ValueError("README must contain exactly one results block")
    start = original.index(START)
    end = original.index(END) + len(END)
    updated = original[:start] + render_results() + original[end:]
    if arguments.check:
        if original != updated:
            parser.exit(
                1, "README results are stale; run python scripts/update_readme_results.py\n"
            )
    else:
        path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
