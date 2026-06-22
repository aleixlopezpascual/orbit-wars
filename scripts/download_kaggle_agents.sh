#!/usr/bin/env bash
# download_kaggle_agents.sh
# Downloads top public orbit-wars agent notebooks from Kaggle and places them
# in tournament_agents/ as usable Python agent files.
# Each file will expose an `agent(obs) -> list` function.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/tournament_agents"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

KAGGLE_BIN="${KAGGLE_BIN:-}"
if [[ -z "$KAGGLE_BIN" ]]; then
  # Try common locations
  for candidate in \
      kaggle \
      "$HOME/Library/Python/3.9/bin/kaggle" \
      "$HOME/Library/Python/3.10/bin/kaggle" \
      "$HOME/Library/Python/3.11/bin/kaggle" \
      "$HOME/.local/bin/kaggle"; do
    if command -v "$candidate" &>/dev/null 2>&1 || [[ -x "$candidate" ]]; then
      KAGGLE_BIN="$candidate"
      break
    fi
  done
fi
if [[ -z "$KAGGLE_BIN" ]]; then
  echo "ERROR: kaggle CLI not found. Install with: pip install kaggle" >&2
  exit 1
fi
echo "Using kaggle CLI: $KAGGLE_BIN"

# Top public agents — updated 2026-06-22 to capture meta shift
# Format: "agent_name kernel_ref [output|pull]"
#   output = use `kaggle kernels output` (gets submission.tar.gz; needed for orbit_lite-based agents)
#   pull   = use `kaggle kernels pull` (gets .ipynb/.py source; older agents)
KERNELS=(
  # --- Original pool (pull-based) ---
  "kaggle_producer        ranjeet258/orbit-wars-producer                              pull"
  "kaggle_i_the_orbit     olasadek/i-the-orbit                                        pull"
  "kaggle_v2_gru          caoyupeng/v2-gru                                            pull"
  "kaggle_v44_elo         itzzomkar/1266-elo-the-v44-agent-100-self-contained         pull"
  "kaggle_producer_v2     slawekbiel/the-producer-v2                                  output"
  # --- Meta-shift agents (output-based, orbit_lite bundles) ---
  "kaggle_smw_v2          shorooghahmadi/orbit-wars-strategic-multi-wave-fleet        output"  # 1300+ ELO
  "kaggle_apex_hybrid     AmgedAlfaqih/apex-hybrid-dynamic-ring-control-border-defense output"  # 107 votes, June 21
  "kaggle_meta0622        pilkwang/orbit-wars-meta-snapshot-0622                      output"  # 85 votes, June 22 (today)
  "kaggle_simple1200      alycemiki/light-ver-1200-simple-orbit-intruder              output"  # 168 votes, 1200+ ELO claimed
)

echo "Downloading ${#KERNELS[@]} Kaggle agents into ${OUT_DIR}/"
echo

for ENTRY in "${KERNELS[@]}"; do
  AGENT_NAME=$(echo "$ENTRY" | awk '{print $1}')
  KERNEL_REF=$(echo "$ENTRY" | awk '{print $2}')
  DOWNLOAD_MODE=$(echo "$ENTRY" | awk '{print $3}')
  PULL_DIR="${TMP_DIR}/${AGENT_NAME}"
  mkdir -p "$PULL_DIR"

  if [[ "$DOWNLOAD_MODE" == "output" ]]; then
    # output mode: downloads submission.tar.gz containing main.py + orbit_lite/
    echo "→ Fetching output ${KERNEL_REF} ..."
    if ! $KAGGLE_BIN kernels output "$KERNEL_REF" -p "$PULL_DIR" 2>&1; then
      echo "  WARNING: failed to fetch output ${KERNEL_REF}, skipping" >&2
      continue
    fi
    TAR_FILE=$(find "$PULL_DIR" -name "*.tar.gz" | head -1)
    if [[ -z "$TAR_FILE" ]]; then
      # No tarball — try a direct .py output
      PY_FILE=$(find "$PULL_DIR" -name "*.py" | grep -v "\.log" | head -1)
      if [[ -z "$PY_FILE" ]]; then
        echo "  WARNING: no .tar.gz or .py found in output for ${KERNEL_REF}, skipping" >&2
        continue
      fi
      cp "$PY_FILE" "${OUT_DIR}/${AGENT_NAME}.py"
      echo "  Saved: tournament_agents/${AGENT_NAME}.py (from output .py)"
    else
      EXTRACT_DIR="${TMP_DIR}/${AGENT_NAME}_extracted"
      mkdir -p "$EXTRACT_DIR"
      tar -xzf "$TAR_FILE" -C "$EXTRACT_DIR"
      MAIN_PY=$(find "$EXTRACT_DIR" -maxdepth 1 -name "main.py" | head -1)
      if [[ -z "$MAIN_PY" ]]; then
        echo "  WARNING: no main.py in tarball for ${KERNEL_REF}, skipping" >&2
        continue
      fi
      cp "$MAIN_PY" "${OUT_DIR}/${AGENT_NAME}.py"
      echo "  Saved: tournament_agents/${AGENT_NAME}.py (from output tarball main.py)"
    fi
  else
    # pull mode: downloads .ipynb or .py source
    echo "→ Pulling ${KERNEL_REF} ..."
    if ! $KAGGLE_BIN kernels pull "$KERNEL_REF" -p "$PULL_DIR" 2>&1; then
      echo "  WARNING: failed to pull ${KERNEL_REF}, skipping" >&2
      continue
    fi

    # Find the downloaded file — could be .py or .ipynb
    PY_FILE=$(find "$PULL_DIR" -name "*.py" | head -1)
    IPYNB_FILE=$(find "$PULL_DIR" -name "*.ipynb" | head -1)

    if [[ -n "$PY_FILE" ]]; then
      cp "$PY_FILE" "${OUT_DIR}/${AGENT_NAME}.py"
      echo "  Saved: tournament_agents/${AGENT_NAME}.py (from .py source)"
    elif [[ -n "$IPYNB_FILE" ]]; then
    # Extract notebook cells with proper handling of Jupyter magic commands:
    # - %%writefile <path>: write cell content to that path
    # - !...: shell commands — skip
    # - %%...: other cell magics — skip
    # - Regular Python cells: collect for the agent file
    python3 - "$IPYNB_FILE" "${OUT_DIR}/${AGENT_NAME}.py" "$OUT_DIR" <<'PYEOF'
import sys, json, os, re, ast

nb_path, out_path, base_dir = sys.argv[1], sys.argv[2], sys.argv[3]
with open(nb_path) as f:
    nb = json.load(f)

regular_cells = []
wrote_files = []
main_py_content = None  # extracted MAIN_PY string from producer pattern

for cell in nb.get("cells", []):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    lines = src.split("\n")
    first = lines[0].strip() if lines else ""

    # Producer pattern: cell contains MAIN_PY = '...' string with the agent code.
    # Extract it even if the cell also has packaging code.
    if "MAIN_PY" in src and "def agent" in src:
        try:
            # Use AST to safely extract the MAIN_PY string value
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign) and
                        len(node.targets) == 1 and
                        isinstance(node.targets[0], ast.Name) and
                        node.targets[0].id == "MAIN_PY" and
                        isinstance(node.value, ast.Constant)):
                    main_py_content = node.value.value
                    break
        except Exception:
            pass

    # Skip cells with packaging/submission code — they try to access the filesystem
    PACKAGING_MARKERS = ['submission.tar.gz', 'tarfile.open', '/kaggle/working']
    if any(marker in src for marker in PACKAGING_MARKERS):
        continue

    # Skip pure shell command cells
    if first.startswith("!"):
        continue

    # %%writefile <path>: write the remaining lines to that file
    if first.startswith("%%writefile"):
        parts = first.split(None, 1)
        if len(parts) == 2:
            rel_path = parts[1].strip()
            content = "\n".join(lines[1:])
            if rel_path == "main.py":
                # This IS the agent code — collect as a regular cell
                regular_cells.append(content)
            else:
                full_path = os.path.join(base_dir, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as fw:
                    fw.write(content)
                wrote_files.append(rel_path)
        continue

    # Skip other cell magics (%%bash, %%html, etc.)
    if first.startswith("%%"):
        continue

    # Strip line magics (%...) and shell lines (!...) within regular cells
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%") or stripped.startswith("!"):
            cleaned.append("# " + line)  # comment them out
        else:
            cleaned.append(line)
    regular_cells.append("\n".join(cleaned))

# Build agent file: add sys.path injection so orbit_lite can be found
# If MAIN_PY string was found (producer pattern), use that as the agent code
if main_py_content and "def agent" in main_py_content:
    combined = main_py_content
    print(f"  Using MAIN_PY string as agent code ({len(main_py_content)} chars)")
else:
    combined = "\n\n".join(regular_cells)

# __future__ imports must be first, so check for and hoist them
future_imports = []
other_lines = []
for line in combined.split("\n"):
    if line.strip().startswith("from __future__"):
        if line not in future_imports:
            future_imports.append(line)
    else:
        other_lines.append(line)

path_inject = (
    "\nimport sys as _sys, os as _os\n"
    "_sys.path.insert(0, _os.path.dirname(_os.path.abspath(_os.path.realpath(__file__))))\n"
)

with open(out_path, "w") as f:
    if future_imports:
        f.write("\n".join(future_imports) + "\n")
    f.write(path_inject + "\n")
    f.write("\n".join(other_lines))

if wrote_files:
    print(f"  Extracted {len(wrote_files)} package files: {', '.join(wrote_files[:3])}{'...' if len(wrote_files) > 3 else ''}")
PYEOF
    echo "  Saved: tournament_agents/${AGENT_NAME}.py (extracted from .ipynb)"
  else
    echo "  WARNING: no .py or .ipynb found for ${KERNEL_REF}, skipping" >&2
    continue
  fi
  fi  # end pull mode

  # Quick validation: check agent() function is present
  OUT_FILE="${OUT_DIR}/${AGENT_NAME}.py"
  python3 - "$OUT_FILE" <<'PYEOF' || echo "  WARNING: agent() not directly accessible in ${AGENT_NAME}.py — file kept but may need wrapper" >&2
import importlib.util, sys
path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tmp_agent', path)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception:
    pass  # some agents fail at module level without a full obs
if not hasattr(mod, 'agent'):
    print('  WARNING: agent() function not found in ' + path, file=sys.stderr)
    sys.exit(1)
print('  OK: agent() function found')
PYEOF

done

echo
echo "Done. Contents of tournament_agents/:"
ls -lh "${OUT_DIR}/"*.py 2>/dev/null || echo "  (no .py files — all downloads may have failed)"
