#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/run_ablation_gate.sh <sweep|comet> [n_games] [label]" >&2
  exit 1
fi

MODE="$1"
N="${2:-24}"
SEED="${SEED:-42}"
STEPS="${STEPS:-300}"
ACT_TIMEOUT="${ACT_TIMEOUT:-1}"

case "$MODE" in
  sweep)
    CH="v32_candidate_sweep_only.py"
    DEFAULT_LABEL="v32_sweep_only_n${N}_fast"
    ;;
  comet)
    CH="v32_candidate_comet_only.py"
    DEFAULT_LABEL="v32_comet_only_n${N}_fast"
    ;;
  *)
    echo "error: mode must be 'sweep' or 'comet'" >&2
    exit 1
    ;;
esac

LABEL="${3:-$DEFAULT_LABEL}"

echo "Running ablation gate: mode=${MODE}, n=${N}, seed=${SEED}, steps=${STEPS}, act-timeout=${ACT_TIMEOUT}, label=${LABEL}"
python3 run_validation.py \
  --ch "${CH}" \
  --bl v29_baseline.py \
  -n "${N}" \
  --steps "${STEPS}" \
  --act-timeout "${ACT_TIMEOUT}" \
  --seed "${SEED}" \
  --label "${LABEL}"
