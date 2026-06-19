#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "usage: bash scripts/pre_submission_tournament_gate.sh <candidate_agent.py> [submission.tar.gz|submission.zip]" >&2
  echo "" >&2
  echo "Options:" >&2
  echo "  <candidate_agent.py>      Agent to test against tournament pool" >&2
  echo "  [submission bundle]       Optional: validate submission bundle after tournament PASS" >&2
  exit 1
fi

CANDIDATE="$1"
BUNDLE="${2:-}"

if [[ ! -f "$CANDIDATE" ]]; then
  echo "error: candidate file not found: $CANDIDATE" >&2
  exit 1
fi

START_TS="$(date +%s)"
VENV_PY="${VENV_PY:-$ROOT_DIR/.venv/bin/python3}"

echo "Preparing tournament environment..."
bash scripts/setup_tournament_env.sh

echo "Refreshing Kaggle tournament agents (best effort)..."
if ! bash scripts/download_kaggle_agents.sh; then
  echo "warning: Kaggle agent refresh failed; continuing with fallback pool if available" >&2
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "error: Python interpreter not found at $VENV_PY" >&2
  echo "hint: run bash scripts/setup_tournament_env.sh first" >&2
  exit 1
fi

echo "Running offline tournament gate for: $CANDIDATE"
"$VENV_PY" run_tournament.py --agent "$CANDIDATE"

LATEST_ARTIFACT="$(ls -1t artifacts/tournament_*.json 2>/dev/null | head -1 || true)"
if [[ -z "$LATEST_ARTIFACT" ]]; then
  echo "error: no tournament artifact found in artifacts/" >&2
  exit 1
fi

"$VENV_PY" - "$LATEST_ARTIFACT" "$(basename "$CANDIDATE")" "$START_TS" <<'PYEOF'
import json
import os
import sys

artifact, expected_agent, start_ts = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(artifact) as f:
    data = json.load(f)

mtime = int(os.path.getmtime(artifact))
if mtime < start_ts:
    raise SystemExit(f"error: latest artifact predates this run: {artifact}")

test_agent = data.get("test_agent")
n_games = int(data.get("n_games", 0))
n_agents = int(data.get("n_agents", 0))
errors = int(data.get("errors", 0))

if test_agent != expected_agent:
    raise SystemExit(
        f"error: artifact test_agent mismatch: expected {expected_agent}, got {test_agent}"
    )
if n_games < 50:
    raise SystemExit(f"error: gate requires >=50 games, artifact has {n_games}")
if n_agents < 4:
    raise SystemExit(f"error: gate requires >=4 agents, artifact has {n_agents}")

print(f"Gate PASS: {artifact}")
print(f"  agent={test_agent}, n_agents={n_agents}, n_games={n_games}, errors={errors}")
if n_agents < 10:
    print("  note: fewer than 10 agents loaded; record fallback reason in docs/operations/BENCHMARK_LOG.md")
PYEOF

# Optional: validate submission bundle if provided
if [[ -n "$BUNDLE" && -f "$BUNDLE" ]]; then
  echo ""
  echo "Validating submission bundle: $BUNDLE"
  if "$VENV_PY" scripts/validate_submission_bundle.py "$BUNDLE"; then
    echo "✅ Submission bundle validation PASS"
  else
    echo "❌ Submission bundle validation FAIL"
    exit 1
  fi
else
  if [[ -n "$BUNDLE" ]]; then
    echo "warning: submission bundle not found: $BUNDLE (skipping validation)" >&2
  fi
fi

echo ""
echo "Next mandatory step: log this run in docs/operations/BENCHMARK_LOG.md before Kaggle submission."

