#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/run_ablation_gate.sh <sweep|comet> [n_games] [label]" >&2
  exit 1
fi

VENV_PY="${VENV_PY:-python3}"
MODE="$1"
N="${2:-24}"
SEED="${SEED:-42}"
STEPS="${STEPS:-300}"
ACT_TIMEOUT="${ACT_TIMEOUT:-1}"
JSON_OUT="${JSON_OUT:-}"
# v35+: baseline defaults to Producer; callers may override with BASELINE=<file>.
BL="${BASELINE:-control_producer.py}"
BL_STEM="$(basename "${BL}" .py)"

if [[ ! -f "${BL}" ]]; then
  echo "error: ${BL} not found — active baseline must exist before ablation runs" >&2
  exit 1
fi

case "$MODE" in
  sweep)
    CH="v32_candidate_sweep_only.py"
    DEFAULT_LABEL="v32_sweep_only_n${N}_vs_${BL_STEM}"
    ;;
  comet)
    CH="v32_candidate_comet_only.py"
    DEFAULT_LABEL="v32_comet_only_n${N}_vs_${BL_STEM}"
    ;;
  sweep_tight)
    CH="v32_candidate_sweep_tight.py"
    DEFAULT_LABEL="v32_sweep_tight_n${N}_vs_${BL_STEM}"
    ;;
  hybrid)
    CH="v32_candidate_sweep_comet_hybrid.py"
    DEFAULT_LABEL="v32_sweep_comet_hybrid_n${N}_vs_${BL_STEM}"
    ;;
  *)
    # v33+ candidates: pass full filename as MODE
    if [[ -f "${MODE}" ]]; then
      CH="${MODE}"
      DEFAULT_LABEL="$(basename "${MODE}" .py)_n${N}_vs_${BL_STEM}"
    else
      echo "error: mode must be 'sweep', 'comet', 'sweep_tight', 'hybrid', or a .py filename" >&2
      exit 1
    fi
    ;;
esac

LABEL="${3:-$DEFAULT_LABEL}"

echo "Running ablation gate: ch=${CH}, bl=${BL}, n=${N}, seed=${SEED}, steps=${STEPS}, act-timeout=${ACT_TIMEOUT}, label=${LABEL}"

CMD=(
  "${VENV_PY}" run_validation.py
  --ch "${CH}"
  --bl "${BL}"
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
