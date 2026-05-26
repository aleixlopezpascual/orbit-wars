#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SEED="${SEED:-42}"
N="${1:-24}"
LABEL="${2:-control_v29_n${N}}"

if [[ ! -f "run_validation.py" ]]; then
  echo "error: run_validation.py not found in repo root" >&2
  exit 1
fi

if [[ ! -f "v31_control_v29.py" || ! -f "v29_baseline.py" ]]; then
  echo "error: expected v31_control_v29.py and v29_baseline.py in repo root" >&2
  exit 1
fi

echo "Running control gate: n=${N}, seed=${SEED}, label=${LABEL}"
python3 run_validation.py \
  --ch v31_control_v29.py \
  --bl v29_baseline.py \
  -n "${N}" \
  --seed "${SEED}" \
  --label "${LABEL}"
