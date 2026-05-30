# Orbit Wars Workspace

This repository contains active agent code plus historical research/benchmark artifacts for the Orbit Wars competition.

## Top-level layout

- `agent.py` — current working agent variant
- `control_hbx2.py` — locked Hellburner-X2 control baseline
- `agents/variants/` — versioned experimental and historical agent snapshots (`v26`–`v34`)
- `run_validation.py` — local head-to-head validation harness
- `scripts/` — convenience benchmark gate scripts
- `docs/` — competition docs, research notes, and archived phase docs
- `artifacts/logs/` — benchmark output logs and run artifacts

## Where older files went

To reduce root clutter, historical v30 planning/submission files were moved to:

- `docs/archive/v30/`

Operational benchmark tracking lives in:

- `docs/operations/BENCHMARK_LOG.md`

Versioned agent files were also moved out of root:

- `agents/variants/`

## Quick start

```bash
# Control sanity gate
bash scripts/run_control_gate.sh 24

# Candidate gate (example)
bash scripts/run_ablation_gate.sh sweep 24

# Candidate by explicit filename in agents/variants/
bash scripts/run_ablation_gate.sh v34_candidate_planet_priority.py 24
```
