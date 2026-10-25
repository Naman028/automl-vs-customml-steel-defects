#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3.13 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt -r backend/models/requirements-evaluation.txt
npm --prefix frontend ci
if [[ ! -f .env ]]; then cp .env.example .env; fi
