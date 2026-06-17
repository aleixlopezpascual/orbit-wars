#!/usr/bin/env bash
# setup_tournament_env.sh
# Sets up a local Python environment with all dependencies for running the tournament.
# Requires: uv (https://docs.astral.sh/uv/)
#
# Usage: bash scripts/setup_tournament_env.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

UV_BIN="${UV_BIN:-}"
if [[ -z "$UV_BIN" ]]; then
  for candidate in uv "$HOME/.local/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv; do
    if command -v "$candidate" &>/dev/null 2>&1 || [[ -x "$candidate" ]]; then
      UV_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$UV_BIN" ]]; then
  echo "ERROR: uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

echo "Using uv: $UV_BIN"
echo "Installing dependencies (this may take a while — torch is ~500MB)..."

"$UV_BIN" sync --project "$ROOT_DIR"

echo
echo "✅ Environment ready. To activate:"
echo "   source .venv/bin/activate"
echo
echo "Then run the tournament with:"
echo "   python run_tournament.py --agent agent.py"
