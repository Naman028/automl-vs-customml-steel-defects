#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements/requirements-dev.txt -r requirements/requirements-evaluation.txt
npm --prefix frontend ci
if [[ ! -f .env ]]; then cp .env.example .env; fi
