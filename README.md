# Orbit Wars Workspace

This repository contains active agent code plus historical research/benchmark artifacts for the Orbit Wars competition.

## Top-level layout

- `agent.py` — current working agent variant
- `control_producer.py` — primary control baseline (active bar)
- `control_stronger.py` — secondary control baseline
- `control_hbx2.py` — historical control baseline
- `run_validation.py` — local head-to-head validation harness
- `run_tournament.py` — offline tournament gate harness
- `scripts/` — convenience benchmark/submission gate scripts
- `docs/` — competition docs, research notes, and archived phase docs
- `artifacts/logs/` — benchmark output logs and run artifacts

## Where older files went

To reduce root clutter, historical v30 planning/submission files were moved to:

- `docs/archive/v30/`

Operational benchmark tracking lives in:

- `docs/operations/BENCHMARK_LOG.md`

## Quick start

```bash
# Control sanity gate
bash scripts/run_control_gate.sh 24

# Candidate gate against Producer (example)
bash scripts/run_ablation_gate.sh agent.py 24

# Mandatory pre-submission offline tournament gate
bash scripts/pre_submission_tournament_gate.sh agent.py

# Batch download Kaggle replays/logs for one submission
python3 scripts/fetch_kaggle_match_artifacts.py \
  --submission-id <SUBMISSION_ID> \
  --limit 10 \
  --download-replays \
  --download-logs \
  --agent-index 0 \
  --out-dir artifacts/kaggle/submission_<SUBMISSION_ID>
```
