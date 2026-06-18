#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_PY="${VENV_PY:-python3}"
SEED="${SEED:-42}"
N="${1:-24}"
# v35+: Producer is the active primary control; sanity compares Producer vs Stronger.
LABEL="${2:-producer_vs_stronger_n${N}}"
STEPS="${STEPS:-300}"
ACT_TIMEOUT="${ACT_TIMEOUT:-1}"
JSON_OUT="${JSON_OUT:-}"

if [[ ! -f "run_validation.py" ]]; then
  echo "error: run_validation.py not found in repo root" >&2
  exit 1
fi

if [[ ! -f "control_producer.py" ]]; then
  echo "error: expected control_producer.py in repo root (PRIMARY control)" >&2
  exit 1
fi

if [[ ! -f "control_stronger.py" ]]; then
  echo "error: expected control_stronger.py in repo root (secondary control)" >&2
  exit 1
fi

echo "Running control sanity gate: n=${N}, seed=${SEED}, steps=${STEPS}, act-timeout=${ACT_TIMEOUT}, label=${LABEL}"
echo "  control_producer.py (ch) vs control_stronger.py (bl) — expect Producer > Stronger"

CMD=(
  "${VENV_PY}" run_validation.py
  --ch control_producer.py
  --bl control_stronger.py
  -n "${N}"
  --steps "${STEPS}"
  --act-timeout "${ACT_TIMEOUT}"
  --seed "${SEED}"
  --label "${LABEL}"
)

if [[ -n "${JSON_OUT}" ]]; then
  CMD+=(--json-out "${JSON_OUT}")
fi

"${CMD[@]}"
