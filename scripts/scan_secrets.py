"""Redacted credential-pattern scan of project text and all reachable Git blobs.

This is a heuristic check, not a guarantee. Binary files, dependency directories,
generated datasets and text blobs above the size limit are excluded explicitly.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_BYTES = 2_000_000
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "github_token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,})"),
    "aws_access_key": re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "service_account": re.compile(r'"type"\s*:\s*"service_account"'),
}
TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".txt",
    ".toml",
    ".yml",
    ".yaml",
    ".ps1",
    ".sh",
    ".csv",
}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "__pycache__",
    "archive",
    "evaluation_reports",
    "raw",
    "processed",
    "runs",
    "neu_final_dataset_fullnames",
    "neu_final_dataset",
}


def matches(content: str, path: str) -> list[dict[str, str | int]]:
    return [
        dict(category=category, path=path, line=content.count("\n", 0, match.start()) + 1)
        for category, pattern in PATTERNS.items()
        for match in pattern.finditer(content)
    ]


def git_output(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT).decode("utf-8", errors="replace")


def scan(history: bool) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
            continue
        if path.suffix not in TEXT_SUFFIXES and not path.name.startswith(".env"):
            continue
        findings.extend(
            matches(path.read_text(encoding="utf-8", errors="replace"), relative.as_posix())
        )
    if history:
        for entry in git_output("rev-list", "--objects", "--all").splitlines():
            if " " not in entry:
                continue
            object_id, name = entry.split(" ", 1)
            if Path(name).suffix not in TEXT_SUFFIXES and not Path(name).name.startswith(".env"):
                continue
            if int(git_output("cat-file", "-s", object_id)) > MAX_TEXT_BYTES:
                continue
            findings.extend(
                matches(
                    git_output("cat-file", "blob", object_id), f"history:{object_id[:12]}:{name}"
                )
            )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    arguments = parser.parse_args()
    findings = scan(arguments.history)
    print(
        json.dumps(
            {"findings": findings, "values_redacted": True, "text_blob_limit": MAX_TEXT_BYTES},
            indent=2,
        )
    )
    if findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
