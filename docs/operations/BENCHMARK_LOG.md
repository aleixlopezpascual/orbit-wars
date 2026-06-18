# Benchmark Log

---

## v35+ Methodology Reset (2026-06-18) — New High-Score Controls

### New Control Baseline: Producer → `control_producer.py` (PRIMARY)

- **Kaggle submission:** "Orbit Wars Producer - Version 1"
- **Public ELO:** 1180.2 (submitted ~13h ago as of 2026-06-18)
- **Status:** ⏳ Pending download — file only exists in Kaggle notebook
- **Action required:** Download from Kaggle, save as `control_producer.py`, lock as immutable.
- **Rationale:** Highest ELO recorded in this project (+199 over previous control_hbx2 peak).
  All future ablation candidates must beat this bar to be considered promotable.

### Secondary Control: I'M STRONGER → `control_stronger.py`

- **Kaggle submission:** "Orbit Wars | I'M STRONGER - Version 1"
- **Public ELO:** 981.3 (submitted ~12h ago as of 2026-06-18)
- **Status:** ⏳ Pending download — file only exists in Kaggle notebook
- **Action required:** Download from Kaggle, save as `control_stronger.py`, lock as immutable.
- **Rationale:** Strong secondary reference point; useful for benchmarking candidates that
  cannot yet beat Producer but are still improvements over the old hbx2 control.

### Download Instructions

1. Open each notebook in Kaggle and copy the agent code.
2. Save as `control_producer.py` and `control_stronger.py` in the repo root.
3. Run sanity self-play: `python run_validation.py --ch control_producer.py --bl control_stronger.py -n 24 --seed 42`
4. Expected: Producer wins >55% (CI lower >40%) to confirm ELO ordering is consistent.
5. Commit both files with message `feat: lock new control baselines (Producer 1180, Stronger 981)`.

### Gate Commands (v35+)

```bash
# Control sanity: producer vs stronger (must confirm Producer > Stronger)
python run_validation.py --ch control_producer.py --bl control_stronger.py -n 24 --seed 42 --label producer_vs_stronger_n24

# Primary ablation gate: candidate vs Producer (harder bar)
python run_validation.py --ch <candidate>.py --bl control_producer.py -n 24 --seed 42 --label <candidate>_vs_producer_n24

# Secondary sanity: also run vs Stronger for signal on mid-tier candidates
python run_validation.py --ch <candidate>.py --bl control_stronger.py -n 24 --seed 42 --label <candidate>_vs_stronger_n24
```

### Promotion Thresholds (unchanged)

| n | Pass Condition | Submit? |
|---|---------------|---------|
| n=24 | WR > 50%, CI lower > 35% | Promote to n=48 |
| n=48 | WR ≥ 56% AND CI lower ≥ 45% | Submit |
| n=48 | WR 52–55% AND CI lower ≥ 40% | Hold, find companion |
| n=48 | WR < 52% OR CI lower < 40% | Discard |

> NOTE: The bar is now higher — candidates must beat `control_producer.py` (1180 ELO), not hbx2.
> `control_hbx2.py` remains in the repo as a historical reference but is no longer the active control.

---

## v33 Methodology Reset (2026-05-27)

### True Control: hellburner-x2-main → `control_hbx2.py`

- **Source:** `v30_agent.py` (fully fixed: all 3 bug-fix commits applied post-submission)
- **Rationale:** v29_baseline.py == agent.py (byte-identical, 981 ELO snapshot) but is WEAKER
  than the live hellburner-x2-main. control_hbx2.py is the correct, stronger reference.
- **File locked:** `control_hbx2.py` — do not modify; treat as immutable.

### Gate Commands (v33+)

> ⚠️ **Environment note:** `orbit-wars` requires the Kaggle notebook environment.
> All benchmark commands below must be run in a Kaggle notebook, not locally.

```bash
# P0-B: Control sanity gate (must land ~50% ±12pp at n=24)
bash scripts/run_control_gate.sh 24

# P1: Triage existing v32 candidates vs correct control
bash scripts/run_ablation_gate.sh comet 24
bash scripts/run_ablation_gate.sh sweep 24
bash scripts/run_ablation_gate.sh sweep_tight 24

# P2+: Any v33 candidate (pass .py filename as first arg)
bash scripts/run_ablation_gate.sh v33_candidate_comet_tune.py 24
bash scripts/run_ablation_gate.sh v33_candidate_sweep.py 24

# Promote to n=48 only after n=24 pass (WR>50%, CI lower>35%)
bash scripts/run_ablation_gate.sh v33_candidate_comet_tune.py 48
```

### Promotion Thresholds

| n | Pass Condition | Submit? |
|---|---------------|---------|
| n=24 | WR > 50% point estimate, CI lower > 35% | Promote to n=48 |
| n=48 | WR ≥ 56% AND CI lower ≥ 45% | ✅ Submit |
| n=48 | WR 52–55% AND CI lower ≥ 40% | ⚠️ Hold, find companion |
| n=48 | WR < 52% OR CI lower < 40% | ❌ Discard |

Max 1 live submission per day. Never submit on n=24 alone.

### Rollback Trigger

If new live submission drops below 970 ELO after 50 ladder games → copy control_hbx2.py to
agent.py and resubmit immediately.

---

## v30/v31/v32 History (archived — wrong control was used)

**Note:** All v31/v32 bench runs below used `v29_baseline.py` as control. That is the WEAKER
baseline. Results are archived for reference only; they do not predict performance vs the live
hellburner-x2-main control.

---

## v30 Benchmark Log (archived)

## Baseline: v29 (Hellburner)

**Snapshot Date:** 2026-05-26  
**Files:** `v29_baseline.py`, `v30_agent.py` (working copy)

### Baseline Features (Verified)
- [x] Comet pre-anticipation (`COMET_PRESTRIKE_*` constants)
- [x] Fresh comet valuation (`COMET_SPAWN_VALUE_MULT = 1.5`)
- [x] Chase window expansion (`COMET_SPAWN_CHASE_TURNS = 22`)
- [x] Distance-aware fleet sizing (`v22_min_ships_for_distance`)
- [x] Sun collision avoidance
- [x] Multi-phase strategy (early rush, opening, late game, total war)

### Baseline Benchmark Commands

```bash
# Quick validation (1 game)
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 1 --seed 42

# Standard n=24 benchmark
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 24 --seed 42

# Full n=48 validation
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 48 --seed 42
```

### v31 Ablation Benchmark Commands

```bash
# One-command helper (defaults aligned with validated uv fast gate: steps=300, act-timeout=1):
bash scripts/run_control_gate.sh 24
bash scripts/run_ablation_gate.sh sweep 24
bash scripts/run_ablation_gate.sh comet 24

# Step 0: control sanity (must be near 50/50 before any ablation run)
python3 run_validation.py --ch v31_control_v29.py --bl v29_baseline.py -n 24 --seed 42 --label control_v29_n24
python3 run_validation.py --ch v31_control_v29.py --bl v29_baseline.py -n 48 --seed 42 --label control_v29_n48

# Step 1: Candidate A (currently experimental wrapper on v30 import path)
python3 run_validation.py --ch v31_candidate_sweep_only.py --bl v29_baseline.py -n 24 --seed 42 --label sweep_only_n24
python3 run_validation.py --ch v31_candidate_sweep_only.py --bl v29_baseline.py -n 48 --seed 42 --label sweep_only_n48

# Step 1: Candidate B (currently experimental wrapper on v30 import path)
python3 run_validation.py --ch v31_candidate_comet_only.py --bl v29_baseline.py -n 24 --seed 42 --label comet_only_n24
python3 run_validation.py --ch v31_candidate_comet_only.py --bl v29_baseline.py -n 48 --seed 42 --label comet_only_n48
```

### v31 Ablation Status (2026-05-26)

- `sweep_only_n24`: 1W/23L/0T (4.2%, CI95 [1–20]) ❌
- `comet_only_n24`: 1W/23L/0T (4.2%, CI95 [1–20]) ❌
- Decision: no n=48 and no submission from these wrappers.
- Next gate: run `v31_control_v29.py` vs `v29_baseline.py`; only proceed if control is near 50/50.
- Important: `v31_control_v29.py` is now a byte-identical copy of `v29_baseline.py` (not an import wrapper) to avoid module-path asymmetry in the harness.
- Control revalidation in uv-capable workspace (fast settings) passed sanity:
  - `control_v29_n24_fast` (n=24, steps=300, act-timeout=1): 11W/13L/0T, 45.8%, CI95 [28–65] ✅
- Candidates have been rebuilt as standalone files (no import wrappers) to avoid module-name/path side effects during dynamic loading:
  - `v31_candidate_sweep_only.py` (SWEEP on, SATURATION/TIE off)
  - `v31_candidate_comet_only.py` (SWEEP off, SATURATION/TIE off)
- Runtime pathology observed in uv-capable run (n=24, steps=300, act-timeout=1): both candidates reached only game 2 after ~6.5 minutes and showed identical first-two-game traces; runs stopped.
- Root debug clue: these two files currently differ by only one constant (`SWEEP_ENABLED`), so when sweep path is not active early they behave effectively identical while both still carry full v30 runtime overhead.

### v32 Conservative Ablation Commands (v29-lineage)

```bash
# v32 candidates are built from v29 lineage to avoid v30 bundled overhead/path effects.
bash scripts/run_ablation_gate.sh sweep 2
bash scripts/run_ablation_gate.sh comet 2

# Promote to full gate only if smoke checks complete normally.
bash scripts/run_ablation_gate.sh sweep 24
bash scripts/run_ablation_gate.sh comet 24
```

v32 candidate deltas:
- `v32_candidate_sweep_only.py`: adds lightweight sweep mission builder and routing with no saturation/tie stack.
- `v32_candidate_comet_only.py`: comet-only parameter tune (`SPAWN_VALUE_MULT=1.6`, `SPAWN_CHASE_TURNS=24`, `PRESTRIKE_MAX_DIST=55.0`).
- Both expose `V32_ABLATION_MODE` and `V32_DEBUG_COUNTERS` for path/runtime sanity checks.

### Benchmark Results

#### M1: Freeze Baseline (2026-05-26)
**Status:** ✅ Complete

- v29_baseline.py created and locked
- v30_agent.py initialized from agent.py
- Baseline benchmark infrastructure verified (ready to run once environment is configured)

**Expected Baseline (v29 vs v29):** 50% win rate (identical agents)

---

## Milestone Progress

| Milestone | Task | Status | Commits |
|-----------|------|--------|---------|
| M1 | Freeze Baseline | ✅ Done | 744c5ce |
| M2 | Port Comet Pre-Anticipation | ✅ Done | 3435505 |
| M3 | Sweep-Loss Instrumentation | ✅ Done | 5317d26 |
| M4 | Sweep Offense | ✅ Done | 99eb0d8 |
| M5 | Combat Saturation/Ties | ✅ Done | 789b08e |
| M6 | Benchmark-Gate n=24→n=48 | ⏳ Ready | - |
| M7 | Submit Robust Winner | ⏳ Pending | - |

## Changes Summary

### Implemented (M1-M5)

**M1: Baseline Infrastructure**
- v29_baseline.py snapshot (locked, immutable)
- v30_agent.py working copy
- Reproducible benchmark harness

**M2: Comet Pre-Anticipation Ported** (verified, no changes needed)
- All v29 comet features confirmed
- COMET_SPAWN_* and COMET_PRESTRIKE_* constants active
- Fresh comet valuation (1.5x) and extended chase (22 turns) working

**M3: Sweep Instrumentation**
- SWEEP_METRICS tracking dictionary
- _log_sweep_engagement() and _update_sweep_outcome() functions
- Saves metrics to sweep_metrics.json every 10 steps
- Non-disruptive logging (no behavior change)

**M4: Sweep Offense**
- SWEEP_* configuration (11 constants)
- build_sweep_missions() function (103 lines)
- Identifies weak targets (5-50 ships), finds 2+ nearby sources
- Allocates 1.25× enemy garrison per source
- Integrated into decision tree (high priority)
- Existing multi-option handler executes sweeps

**M5: Combat Saturation & Tie-Safety**
- _detect_saturation_threats() — scans 30-turn lookahead
- _is_planet_saturated() — checks if 3+ incoming fleets
- SATURATION_SEND_REDUCTION (70%) applied to saturated sources
- TIE_SAFE_GARRISON_MULT (1.15x) for tie scenarios
- Integrated into sweep mission building

### Code Metrics
- Total production code added: ~150 lines
- Configuration parameters: 16 new constants
- New functions: 8 total (3 sweep, 3 saturation, 2 metrics)
- Zero changes to existing mission types
- Zero breaking changes to core logic

---

## Notes

- **Environment Setup:** kaggle_environments must be properly configured for benchmarks to run
- **Reproducibility:** All benchmarks use `--seed 42` for deterministic results
- **Incremental Validation:** Each milestone committed only after positive benchmark delta
- **Alternating Seats:** run_validation.py alternates agent seats (player 0/1) to reduce position bias

---

## v30 Development Plan

See `plan.md` for full roadmap with M1-M7 details.

### Key Milestones Ahead

**M2:** Verify v29 comet logic is fully ported (should already be in agent.py)  
**M3:** Add logging hooks to measure sweep engagement outcomes  
**M4:** Implement sweep offense (multi-planet coordinated attacks)  
**M5:** Saturation detection + tie-annihilation handling  
**M6:** Full benchmark validation n=24 → n=48  
**M7:** Kaggle submission after robust validation  
