#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
task=${1:?Specify neu or gc10}
shift
if [[ "$task" == neu ]]; then
  exec .venv/bin/python -m ml.evaluate_shared "$@"
elif [[ "$task" == gc10 ]]; then
  exec .venv/bin/python -m ml.evaluate_gc10 "$@"
else
  echo "Specify neu or gc10" >&2
  exit 2
fi
