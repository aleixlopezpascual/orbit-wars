#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/run_ablation_gate.sh <sweep|comet|sweep_tight|hybrid|path-to-agent.py> [n_games] [label]" >&2
  exit 1
fi

MODE="$1"
N="${2:-24}"
SEED="${SEED:-42}"
STEPS="${STEPS:-300}"
ACT_TIMEOUT="${ACT_TIMEOUT:-1}"
# v33: baseline is always hellburner-x2-main (control_hbx2.py), not v29_baseline.py
BL="control_hbx2.py"
VARIANTS_DIR="agents/variants"

if [[ ! -f "${BL}" ]]; then
  echo "error: ${BL} not found — run P0 first to lock the control" >&2
  exit 1
fi

case "$MODE" in
  sweep)
    CH="${VARIANTS_DIR}/v32_candidate_sweep_only.py"
    DEFAULT_LABEL="v32_sweep_only_n${N}_vs_hbx2"
    ;;
  comet)
    CH="${VARIANTS_DIR}/v32_candidate_comet_only.py"
    DEFAULT_LABEL="v32_comet_only_n${N}_vs_hbx2"
    ;;
  sweep_tight)
    CH="${VARIANTS_DIR}/v32_candidate_sweep_tight.py"
    DEFAULT_LABEL="v32_sweep_tight_n${N}_vs_hbx2"
    ;;
  hybrid)
    CH="${VARIANTS_DIR}/v32_candidate_sweep_comet_hybrid.py"
    DEFAULT_LABEL="v32_sweep_comet_hybrid_n${N}_vs_hbx2"
    ;;
  *)
    # Accept either an explicit file path or a filename living in agents/variants/.
    if [[ -f "${MODE}" ]]; then
      CH="${MODE}"
      DEFAULT_LABEL="$(basename "${MODE}" .py)_n${N}_vs_hbx2"
    elif [[ -f "${VARIANTS_DIR}/${MODE}" ]]; then
      CH="${VARIANTS_DIR}/${MODE}"
      DEFAULT_LABEL="$(basename "${MODE}" .py)_n${N}_vs_hbx2"
    else
      echo "error: mode must be 'sweep', 'comet', 'sweep_tight', 'hybrid', a .py path, or a filename in ${VARIANTS_DIR}" >&2
      exit 1
    fi
    ;;
esac

if [[ ! -f "${CH}" ]]; then
  echo "error: challenger file not found: ${CH}" >&2
  exit 1
fi

LABEL="${3:-$DEFAULT_LABEL}"

echo "Running ablation gate: ch=${CH}, bl=${BL}, n=${N}, seed=${SEED}, steps=${STEPS}, act-timeout=${ACT_TIMEOUT}, label=${LABEL}"
python3 run_validation.py \
  --ch "${CH}" \
  --bl "${BL}" \
  -n "${N}" \
  --steps "${STEPS}" \
  --act-timeout "${ACT_TIMEOUT}" \
  --seed "${SEED}" \
  --label "${LABEL}"
