#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SEED="${SEED:-42}"
N="${1:-24}"
# v33: control is hellburner-x2-main (control_hbx2.py), not the weaker v29 snapshot
LABEL="${2:-control_hbx2_n${N}}"
STEPS="${STEPS:-300}"
ACT_TIMEOUT="${ACT_TIMEOUT:-1}"

if [[ ! -f "run_validation.py" ]]; then
  echo "error: run_validation.py not found in repo root" >&2
  exit 1
fi

if [[ ! -f "control_hbx2.py" ]]; then
  echo "error: expected control_hbx2.py in repo root (hellburner-x2-main snapshot)" >&2
  exit 1
fi

echo "Running control sanity gate: n=${N}, seed=${SEED}, steps=${STEPS}, act-timeout=${ACT_TIMEOUT}, label=${LABEL}"
echo "  control_hbx2.py (ch) vs control_hbx2.py (bl) — expect ~50%"
python3 run_validation.py \
  --ch control_hbx2.py \
  --bl control_hbx2.py \
  -n "${N}" \
  --steps "${STEPS}" \
  --act-timeout "${ACT_TIMEOUT}" \
  --seed "${SEED}" \
  --label "${LABEL}"
