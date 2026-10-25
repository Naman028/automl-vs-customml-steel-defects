#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend/models/CustomML"
exec ../../../.venv/bin/python -m trainer.train "$@"
