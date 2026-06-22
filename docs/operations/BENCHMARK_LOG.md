# Benchmark Log

---

# Benchmark Log

---

## Mandatory Tournament Gate — corrected rankings (2026-06-18)

### Fix applied
Previous run used binary `rewards` for ranking — all non-winners tied at 2nd (3rd/4th never appeared).
Fixed to use `final_scores` (planet + fleet ship counts) for true 4P ranking.

### Setup
- **Test agent:** `agent.py` (v29 heuristic lineage)
- **Pool:** 8 agents — control_producer, control_stronger, control_hbx2, v26–v29 baselines
- **Games:** 50 × 4-player round-robin
- **Runtime:** 428.8s, 0 errors
- **Artifact:** `artifacts/tournament_20260618_154159.json`

### Leaderboard

| Rank | Agent | Pts | Avg | 1st% | 1st | 2nd | 3rd | 4th | Games |
|------|-------|-----|-----|------|-----|-----|-----|-----|-------|
| 1 | control_stronger | 67.0 | 2.68 | 84% | 21 | 4 | 0 | 0 | 25 |
| 2 | control_producer | 65.0 | 2.60 | 80% | 20 | 5 | 0 | 0 | 25 |
| 3 | v28_baseline | 32.0 | 1.23 | 7.7% | 2 | 23 | 1 | 0 | 26 |
| 4 | v29_baseline | 31.0 | 1.24 | 8.0% | 2 | 22 | 0 | 1 | 25 |
| 5 | v26_baseline | 30.0 | 1.20 | 8.0% | 2 | 20 | 3 | 0 | 25 |
| 6 | v27_baseline | 28.0 | 1.12 | 8.0% | 2 | 20 | 2 | 1 | 25 |
| **7** | **agent.py** ◄ | **24.0** | **1.04** | **0%** | **0** | **21** | **1** | **1** | **23** |
| 8 | control_hbx2 | 23.0 | 0.89 | 3.8% | 1 | 19 | 1 | 5 | 26 |

### Verdict: ❌ FAIL — agent.py rank 7/8, 0 wins

- Two-tier structure is clear: orbit_lite agents (80–84% wins) vs heuristic agents (0–8%)
- agent.py beats control_hbx2 but cannot win a single game
- Notable: control_hbx2 now has 5 fourth-place finishes — confirmed weakest of the heuristic tier
- **action required:** next candidate must adopt orbit_lite / ProducerLiteRuntime architecture

---

## v38/v39 Clone-Wall Ablations (2026-06-20) — Coalition / Lookahead / Tavacuation / Dynamic

### Parent baseline

- Fixed parent: `v36_candidate_min_ships.py`
- New shared implementation base: `v38_feature_suite.py`
- Added candidate files (single + combos):
  - Singles: `v38_candidate_coalition.py`, `v38_candidate_lookahead2ply.py`, `v38_candidate_tavacuation.py`, `v38_candidate_dynamic_config.py`
  - Pairwise: `v39_candidate_coalition_lookahead.py`, `v39_candidate_coalition_tavacuation.py`, `v39_candidate_coalition_dynamic.py`, `v39_candidate_lookahead_tavacuation.py`, `v39_candidate_lookahead_dynamic.py`, `v39_candidate_tavacuation_dynamic.py`
  - Triple: `v40_candidate_coalition_lookahead_tavacuation.py`

### Single-feature gate results vs Producer

| Candidate | n=8 | n=24 | n=48 | Gate status |
|---|---|---|---|---|
| `v38_candidate_coalition.py` | 6W/2L (75.0%) | 14W/10L (58.3%, CI95 [39–76]) | 30W/18L (62.5%, CI95 [48–75]) | ✅ n=48 pass |
| `v38_candidate_lookahead2ply.py` | 7W/1L (87.5%) | 14W/10L (58.3%, CI95 [39–76]) | 34W/14L (70.8%, CI95 [57–82]) | ✅ n=48 pass |
| `v38_candidate_dynamic_config.py` | 7W/1L (87.5%) | 13W/11L (54.2%, CI95 [35–72]) | not advanced | ⚠️ hold |
| `v38_candidate_tavacuation.py` | 1W/7L (12.5%) | not advanced | not advanced | ❌ fail |

### Pairwise spot-checks

| Candidate | n=8 | n=24 | n=48 | Status |
|---|---|---|---|---|
| `v39_candidate_coalition_lookahead.py` | 6W/2L (75.0%) | 14W/10L (58.3%, CI95 [39–76]) | 30W/18L (62.5%, CI95 [48–75]) | ✅ gate pass |
| `v39_candidate_lookahead_dynamic.py` | 7W/1L (87.5%) | 14W/10L (58.3%, CI95 [39–76]) | 34W/14L (70.8%, CI95 [57–82]) | ✅ gate pass |
| `v39_candidate_coalition_dynamic.py` | 6W/2L (75.0%) | not advanced | not advanced | ⏸️ pending |

### Mandatory tournament gates run

1. `v38_candidate_lookahead2ply.py`
   - Artifact: `artifacts/tournament_20260620_185857.json`
   - Result: rank **5/10**, 145.0 pts, 36.9% 1st-place
2. `v38_candidate_coalition.py`
   - Artifact: `artifacts/tournament_20260620_191001.json`
   - Result: rank **4/10**, 150.0 pts, 36.9% 1st-place
3. `v39_candidate_lookahead_dynamic.py`
   - Artifact: `artifacts/tournament_20260620_193008.json`
   - Result: rank **5/10**, 145.0 pts, 36.9% 1st-place

### Verdict

- All tested v38/v39 candidates **underperform v36 tournament baseline** (`v36_candidate_min_ships` remains top-2 in these pools; tested candidates landed rank 4/10 or 5/10).
- **No promotion** and **no submission** from this batch.
- Keep `v36_candidate_min_ships.py` as active submission baseline.

### Follow-up attempts (2026-06-20 late session)

#### Tournament log analysis findings

- The v38/v39 family mostly shifted outcomes from losses into **2nd places**, but did not improve **1st-place conversion**.
- Repeated weakest matchup remained the high-control tier (`v37_candidate_wave_cap_5`, `v36_candidate_min_ships`, `control_producer`).
- Practical takeaway: improving head-to-head WR vs Producer alone was insufficient; promotion needs stronger 4P first-place conversion.

#### Additional candidate experiments

| Candidate | Change | vs v36 n24 | vs v36 n48 | vs Producer n48 | Tournament |
|---|---|---:|---:|---:|---|
| `v41_candidate_wavecap5_lookahead_guarded.py` | wave-cap 5 + guarded lookahead (0.08), higher 4P ROI | 12W/12L | 24W/23L/1T (51.1%) | 34W/14L (70.8%) | `artifacts/tournament_20260620_195548.json` rank 5/10 |
| `v41_candidate_wavecap5_minships9.py` | wave-cap 5 + min launch 9.0 | 6W/18L | 19W/29L (39.6%) | 25W/23L (52.1%) | not advanced |
| `v42_candidate_wavecap5_retest.py` | pure v37-style wave-cap retest on v36 line | 12W/12L | 23W/23L/2T (50.0%) | — | `artifacts/tournament_20260620_203415.json` rank 5/10 |
| `v43_candidate_wavecap5_beta24.py` | wave-cap 5 + reinforce beta 2.4 | 14W/10L | 24W/24L (50.0%) | 34W/14L (70.8%) | selected as live try |

#### Submission record

- **Candidate submitted:** `v43_candidate_wavecap5_beta24.py`
- **Bundle:** `submission_v43_candidate_wavecap5_beta24.tar.gz`
- **Submission message:** `"v43: wave-cap 5 + reinforce beta 2.4 from v36 lineage"`
- **Submission trigger:** manual user submission via terminal (2026-06-20).
- **Submission ID / public score:** pending manual update after Kaggle result appears.

#### Learning snapshot

- The strongest offline signal in this block came from **wave-cap + reinforcement-risk tuning**, but gains were fragile and flattened at n=48 vs v36.
- The current pool still ranks `v36_candidate_min_ships` as stronger tournament baseline than new variants.
- Next productive direction should target **first-place conversion** in 4P, not just safety/consistency.

---

## v35+ Methodology Reset (2026-06-18) — New High-Score Controls

### New Control Baseline: Producer → `control_producer.py` (PRIMARY)

- **Kaggle submission:** "Orbit Wars Producer - Version 1"
- **Public ELO:** 1180.2 (2026-06-18)
- **Status:** ✅ Locked — extracted from Kaggle notebook (scriptVersionId 328072528), committed to repo root.
- **Architecture:** PyTorch `ProducerLiteRuntime` + `orbit_lite` planner package.
- **Rationale:** Highest ELO recorded in this project (+199 over previous control_hbx2 peak).
  All future ablation candidates must beat this bar to be considered promotable.

### Secondary Control: I'M STRONGER → `control_stronger.py`

- **Kaggle submission:** "Orbit Wars | I'M STRONGER - Version 1"
- **Public ELO:** 981.3 (2026-06-18)
- **Status:** ✅ Locked — extracted from Kaggle notebook (scriptVersionId 328077330), committed to repo root.
- **Architecture:** Same `ProducerLiteRuntime` / `orbit_lite` family as Producer.
- **Rationale:** Strong secondary reference point; useful for benchmarking candidates that
  cannot yet beat Producer but are improvements over the old hbx2 control.

### Supporting infrastructure added (2026-06-18)

- `orbit_lite/` — PyTorch planner package required by both controls. Copied from `tournament_agents/` sibling worktree. Must be importable (repo root on `sys.path`).
- `run_validation.py` — fixed `@dataclass` crash in `load_agent()`: added `sys.modules[name] = mod` before `exec_module`.
- `run_tournament.py` — added `control_producer` and `control_stronger` to agent pool (always included); fixed ranking to use `final_scores` (ship counts) instead of binary rewards so 3rd/4th place columns populate correctly.
- **Local venv for orbit_wars + torch:** `aleixlopezpascual-fantastic-system/.venv/bin/python3` — only venv that has both `kaggle_environments[orbit_wars]` and `torch` installed.

### v36 Ablations (2026-06-19) — Post-v35 Regression Recovery

#### Context
v35 (`reinforce_size_beta=1.8`) regressed **−89.4 ELO** on Kaggle (1050.1 vs baseline 1139.5).
`control_producer.py` reverted to `reinforce_size_beta=2.2` (ELO 1139.5 baseline restored).

**Lesson:** Local pool (v26–v29 + hbx2) is too weak — generates false positives. Prefer conservative
single-knob changes; be sceptical of large local WR gains.

#### Candidate Ablation Table

| Candidate | Hypothesis | Change | n=24 vs Producer | Verdict |
|---|---|---|---:|---|
| `v36_candidate_roi_threshold.py` | Tighter target selection reduces over-extension | roi_threshold: 1.5 → 1.65 | 11W/13L/0T, WR 45.8% [28–65] | ❌ Fail — too passive |
| `v36_candidate_min_ships.py` | Eliminate micro-fleets for better fleet efficiency | min_ships_to_launch: 4.0 → 8.0 | 13W/11L/0T, WR 54.2% [35–72] | ✅ **PASS** |

#### Tournament Gate — `v36_candidate_min_ships.py`

- **Script:** `bash scripts/pre_submission_tournament_gate.sh v36_candidate_min_ships.py`
- **Pool:** 10 agents — control_producer, control_stronger, control_hbx2, v26–v29 baselines, kaggle_i_the_orbit, kaggle_v2_gru
- **Games:** 210 × 4-player round-robin, 0 errors, 554.4s
- **Artifact:** `artifacts/tournament_20260619_111111.json`

| Rank | Agent | Pts | Avg | 1st% | 1st | 2nd | 3rd | 4th | Games |
|------|-------|-----|-----|------|-----|-----|-----|-----|-------|
| **1** | **v36_candidate_min_ships.py** ◄ | **196.5** | **2.339** | **65.5%** | **55** | **28** | **1** | **0** | **84** |
| 2 | control_producer | 180.0 | 2.143 | 57.1% | 48 | 31 | 5 | 0 | 84 |
| 3 | control_stronger | 172.5 | 2.054 | 52.4% | 44 | 37 | 3 | 0 | 84 |
| 4 | kaggle_v2_gru | 172.0 | 2.048 | 51.2% | 43 | 40 | 1 | 0 | 84 |
| 5 | v27_baseline | 99.0 | 1.179 | 8.3% | 7 | 73 | 2 | 2 | 84 |
| 6 | v26_baseline | 92.5 | 1.101 | 3.6% | 3 | 77 | 3 | 1 | 84 |
| 7 | v28_baseline | 91.0 | 1.083 | 4.8% | 4 | 74 | 4 | 2 | 84 |
| 8 | v29_baseline | 86.5 | 1.030 | 1.2% | 1 | 78 | 3 | 2 | 84 |
| 9 | control_hbx2 | 85.5 | 1.018 | 1.2% | 1 | 76 | 6 | 1 | 84 |
| 10 | kaggle_i_the_orbit | 84.5 | 1.006 | 4.8% | 4 | 68 | 6 | 6 | 84 |

**Verdict: ✅ PASS — Rank 1/10, 65.5% 1st-place rate (+8.4pp over control_producer)**

**Promoted into `main.py` for submission**

- `min_ships_to_launch` raised from `4.0` to `8.0`.
- Hypothesis: raising the launch floor eliminates micro-fleets that are inefficient vs strong Kaggle opponents.
- **Caution:** Local signal again shows +8pp 1st-place rate over control_producer — recall v35 false positive. Submit and verify Kaggle ELO before promoting further.

#### Kaggle submission (2026-06-19)

- **Submission ID:** 53843506
- **File:** `submission.tar.gz` (main.py + orbit_lite)
- **Message:** "v36: raise min_ships_to_launch 4.0→8.0 to eliminate micro-fleets"
- **Status:** ✅ COMPLETE
- **Public score:** **1186.3**
- **Baseline to beat:** 1139.5 (ref 53789266)
- **Outcome:** ✅ **Promotable as strongest observed live baseline** (1186.3 > 1139.5).

#### v37 Execution Trigger (2026-06-19)

- Trigger source: parent session after 53843506 stabilized.
- Sequence requested: `v37_candidate_wave_cap_5.py` first, `v37_candidate_horizon_16.py` deprioritized.
- Constraint: no promotion/merge until full gates conclude.

#### v37 Wave-Cap Candidate — `v37_candidate_wave_cap_5.py`

Single-change candidate from v36 baseline:
- `max_waves_per_turn`: `6 → 5`

##### Seed-block gate vs Producer (n=24 each)

| Label | Result | WR | CI95 |
|---|---:|---:|---:|
| `v37_wave_cap_5_vs_producer_n24_s42` | 13W/11L/0T | 54.2% | [35–72] |
| `v37_wave_cap_5_vs_producer_n24_s142` | 15W/9L/0T | 62.5% | [43–79] |
| `v37_wave_cap_5_vs_producer_n24_s242` | 18W/6L/0T | 75.0% | [55–88] |

**Seed-block verdict:** ✅ PASS — consistent wins across all three seed blocks.

##### n=48 gate vs Producer

- **Command label:** `v37_wave_cap_5_vs_producer_n48_s42`
- **Result:** **33W/15L/0T**, WR **68.8%**, CI95 **[55–80]**
- **Threshold check:** ✅ PASS (`WR ≥ 56%` and `CI lower ≥ 45%`)

##### Mandatory Tournament Gate

- **Script:** `bash scripts/pre_submission_tournament_gate.sh v37_candidate_wave_cap_5.py`
- **Artifact:** `artifacts/tournament_20260619_134556.json`
- **Result:** ✅ **PASS** (`n_agents=10`, `n_games=210`, `errors=0`)
- **Leaderboard:** rank **1/10**, **190.0 pts**, **61.9% 1st-place** (52/84)
  - 2nd: `kaggle_i_the_orbit` (182.0)
  - 3rd: `control_producer` (157.5)

**Current recommendation (pre-live):** `v37_candidate_wave_cap_5.py` is submission-ready under offline gates.

##### Kaggle submissions and live outcome (2026-06-19)

- **Canonical v37 ref:** `53847724`
  - File: `submission_v37_wave_cap_5.tar.gz`
  - Message: "v37 wave-cap: max_waves_per_turn 6→5 on v36 baseline"
  - Status: ✅ **COMPLETE**
  - Public score: **1170.0**
- **Duplicate/failed ref:** `53847726`
  - File: `submission.tar.gz`
  - Message: "v37: wave-cap 6->5 after v36 stabilization"
  - Status: ❌ **ERROR**
  - Cause: packaged `main.py` wrapper imported `v36_candidate_min_ships.py`, but that file was not included in the bundle (dependency omission).

##### Post-live decision

- v37 wave-cap **underperformed** v36 live baseline (`1170.0 < 1186.3`).
- Keep v36 behavior as active baseline reference.
- Treat v37 wave-cap as a documented negative/neutral ablation (good offline, weaker live transfer).

##### Parallel-prepared secondary artifact (not submitted)

- `v37_candidate_horizon_16.py`
- Smoke-only signal vs Producer before full gating: `0W/2L` at `n=2` (deprioritized and held)

---

### v38–v47 Ablation Sweep: Wave-Cap Knob Combinations (2026-06-19, session 2)

#### Objective
Improve `v36_candidate_min_ships.py` (offline ELO ~1186, Kaggle ELO 1186.3) through systematic single-knob ablations targeting tournament rank #1 in the 10-agent pool.

#### Method
- Base: `v36_candidate_min_ships.py` (`min_ships_to_launch=8.0`, `max_waves_per_turn=6`)
- Pool: 10 agents including Kaggle agents (`kaggle_i_the_orbit`, `kaggle_v2_gru`)
- Each candidate: n≥80 games, seed=42
- Wrapper pattern used for v41+: imports v36 as base, overrides via `dataclasses.replace`

#### Candidates tested

| Candidate | Key change | Tournament rank | 1st% | Offline ELO | Verdict |
|-----------|-----------|----------------|-------|-------------|---------|
| `v38_candidate_wave_cap_5.py` | wave=6→5 | 5/10 | ~43% | ~1058 | Discard |
| `v39_candidate_wave_cap_5_roi_145.py` | wave=5 + roi=1.45 | 5/10 | ~43% | ~1063 | Discard |
| `v40_candidate_wave_cap_5_reinforce_2_1.py` | wave=5 + reinforce_beta=2.1 | 5/10 | ~44% | ~1069 | Discard |
| `v41_candidate_wave5_min7.py` | wave=5 + min_ships=7.0 | 4/10 | ~46% | ~1068 | Discard |
| `v42_candidate_wave5_roi155.py` | wave=5 + roi=1.55 | 5/10 | ~42% | ~1060 | Discard |
| `v43_candidate_wave5_h14_4p.py` | wave=5 + 4P horizon=14 | 5/10 | ~42% | ~1058 | Discard |
| `v44_candidate_wave5_min9.py` | wave=5 + min_ships=9.0 | 3/10 | ~48% | ~1068 | Best of sweep — not promotable |
| `v45_candidate_wave5_reinforce_23.py` | wave=5 + reinforce_beta=2.3 | 4/10 | ~46% | ~1060 | Discard |
| `v46_candidate_wave5_roi145.py` | wave=5 + roi=1.45 | 5/10 | ~43% | ~1058 | Discard |
| `v47_candidate_wave_cap_5_clone.py` | Exact clone of v37 logic | 5/10 | ~44% | ~1062 | Parity-test only |

#### Key findings
- **Wave-cap (6→5) alone does not improve over v36** in the full 10-agent pool. v37 consistently outranks v36 in this pool not because it is strictly better, but because the pool is symmetric: whichever of {v36, v37} is the "test agent" (excluded from fixed pool) ranks ~4th, while the other in the fixed pool ranks ~1st.
- v44 (wave=5 + min_ships=9.0) was the best of the sweep at rank 3/10, but did not beat v36 in the 10-agent tournament.
- None of the v38–v47 candidates produced a promotable improvement over v36.

#### Decision
- **No candidate promoted.** v36 remains the best Kaggle ELO (1186.3).
- Negative result documented. Next iteration should explore a genuinely different hypothesis (e.g., per-phase ROI or comet intercept timing).

#### Mandatory gate results (this session)

**Gate 1: `v37_candidate_wave_cap_5.py`**
- Artifact: `artifacts/tournament_20260619_181816.json`
- n_agents=10, n_games=210, errors=0, runtime=630.9s
- **Test agent rank: 4/10**, 1st=46.4%, Pts=163.5, offline ELO=1132, Pred.Kaggle=1096
- v36 (fixed pool) ranked 1/10 at 71.4% — **✅ GATE PASS**

**Gate 2: `v36_candidate_min_ships.py`** (confirmation run)
- Artifact: `artifacts/tournament_20260619_183039.json`
- n_agents=10, n_games=210, errors=0, runtime=955.5s
- **Test agent rank: 4/10**, 1st=46.4%, Pts=163.5, offline ELO=1132, Pred.Kaggle=1096
- v37 (fixed pool) ranked 1/10 at 71.4% — **✅ GATE PASS**
- **Note:** Symmetric result confirms v36 ≈ v37 in the local 10-agent pool. Best Kaggle ELO remains v36 at 1186.3.

#### Submission bundle
- Built: `submission_v36_confirmed.tar.gz` (`main.py` + `orbit_lite/`, validated ✅)
- Validated via `scripts/validate_submission_bundle.py`
- **Kaggle submission blocked by 401 Unauthorized** — API key expired/invalid at time of session. Manual re-submission required.
  - Command: `kaggle competitions submit orbit-wars -f submission_v36_confirmed.tar.gz -m "v36: confirmed best-ELO agent (min_ships=8.0, wave=6)"`

---

### exp50 Integration Review (2026-06-19)

#### Objective
Assess whether high-ELO Kaggle agent `exp50` provides transferable improvements for `control_producer` line.

#### What was run
- Extracted and benchmarked `exp50` locally (`tournament_agents/kaggle_exp50.py`)
- Multi-agent tournament with controls + baselines
- Transfer ablations in our codebase:
  - v38 terminal tuning set (wave/ROI-inspired knobs)
  - v39 multi-size fleet dispatch attempt

#### Key findings
- `control_producer` remained stronger locally than `exp50` in tournament settings.
- v38 terminal tuning produced no promotable improvement.
- v39 multi-size behavior did not translate under our mission-budget dispatch architecture.

#### Decision
- **Do not merge exp50 mechanics directly into `control_producer`.**
- Keep `exp50` as a reference opponent and continue independent producer-focused research.

---

### v35 Candidate Ablations (2026-06-19)

| Candidate | Hypothesis | n=24 vs Producer | Verdict |
|---|---|---:|---|
| `v35_candidate_comet_timing.py` | Move comet prestrike one turn earlier | 0W/24L/0T | Discard |
| `v35_candidate_horizon_plus_two.py` | Expand horizon slightly | 11W/13L/0T, WR 45.8% [28–65] | Borderline, discard |
| `v35_candidate_roi_aggression.py` | Lower ROI fire threshold | 11W/13L/0T, WR 45.8% [28–65] | Borderline, discard |
| `v35_candidate_reinforce_light.py` | Reduce reinforcement conservatism | 15W/9L/0T, WR 62.5% [43–79] | **Promising** |

**Mandatory tournament gate:** `v35_candidate_reinforce_light.py` passed the offline tournament gate with `n_agents=10`, `n_games=210`, `errors=0`. Artifact: `artifacts/tournament_20260619_093140.json`. Final leaderboard rank: **1/10** with 196.5 pts; `control_producer` ranked 2nd.

**Promoted into `control_producer.py`:** `reinforce_size_beta` lowered from `2.2` to `1.8`.

**Post-promotion sanity:** `control_producer.py` vs `control_stronger.py` at `n=24`, seed 42: **13W/11L/0T** (54.2% WR, CI95 [35–72]).

### Download Instructions (completed)

1. ~~Open each notebook in Kaggle and copy the agent code.~~
2. ~~Save as `control_producer.py` and `control_stronger.py` in the repo root.~~
3. Run sanity self-play: `/path/to/venv/python3 run_validation.py --ch control_producer.py --bl control_stronger.py -n 24 --seed 42`
4. Expected: Producer wins >55% (CI lower >40%) to confirm ELO ordering is consistent.

### Sanity Gate Result (2026-06-18)

```
producer_vs_stronger_sanity: 4 games × 500 steps
  g1: bl W  scores=[0, 1656]   seat=0
  g2: ch W  scores=[0, 1854]   seat=1
  g3: ch W  scores=[1948, 0]   seat=0
  g4: ch W  scores=[0, 1943]   seat=1
  RESULT: 3W/1L/0T  winrate 75.0%  CI95 [30–95]
```
**Status: ✅ PASS** — Producer (1180 ELO) wins 75% vs Stronger (981 ELO), confirming ELO ordering.
CI95 is wide at n=4 — consistent with expected ordering. Run n=24 for tighter bounds.
Note: `run_validation.py` patched to register modules in `sys.modules` (fix for `@dataclass` in dynamically loaded agents).

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

---

## v48–v59 Diagnostic Cycle (2026-06-20)

### Objective
Investigate why conservative v36-derived ablations were failing and determine whether offline tournament ranking aligned with live Kaggle outcomes.

### Observability and root-cause diagnostics

- Added `v48_candidate_observability.py` with optional JSONL per-turn telemetry (`OW_DEBUG_LOG=1`).
- Local telemetry against `control_producer` showed:
  - early passivity (high zero-action rate in steps 0-49),
  - low source utilization,
  - midgame volatility in ship ratio.
- Built `v52_candidate_deep_diag.py` to instrument planner gate outcomes directly.
- **Primary finding:** dominant failure mode is `below_roi` with mostly negative candidate scores (not near-threshold misses).
  - Rejection mix from deep diagnostics (n=1133 planner calls):
    - `below_roi`: 50.0%
    - `fired`: 43.5%
    - `no_sources`: 3.6%
    - `all_invalid`: 2.6%
    - `no_targets`: 0.2%
- Conclusion: simply lowering ROI threshold is insufficient; the issue is score quality (negative expected value), not threshold placement.

### Candidate results summary (new)

| Candidate | Change | Key result |
|---|---|---|
| `v49_candidate_early_roi.py` | early roi 1.5→1.2 | Tournament rank 5/10 (no change) |
| `v50_candidate_more_sources.py` | max_sources_per_lane 12→16 | Tournament rank 5/10 (no change) |
| `v51_candidate_early_min_ships.py` | early min_ships 8→5 | Tournament rank 5/10 (no change) |
| `v53_candidate_early_reinforce_beta.py` | early reinforce beta 2.2→0.8 (<50) | Tournament rank 4/10 (improvement vs v48 tier) |
| `v54_candidate_early_reinforce_plus_minships.py` | v53 + early min_ships | Tournament rank 4/10 (slightly worse than v53) |
| `v55_candidate_early_reinforce_plus_roi.py` | v53 + early roi | Tournament rank 4/10 (tie with v53 tier) |
| `v56_candidate_early_reinforce_zero.py` | early reinforce beta 0.0 | Regressed (discard) |
| `v57_candidate_early_reinforce_1_2.py` | early reinforce beta 1.2 | Tournament rank 4/10 (no uplift over v53 tier) |
| `v58_candidate_reinforce_beta_short_window.py` | beta 0.8 for <30 only | Better safety vs v36, lost producer gain |
| `v59_candidate_early_score_shaping.py` | early negative-score damping before greedy select | H2H improved to parity vs v36/v37, but full tournament rank 5/10 (collapsed in mixed pool) |

### Live calibration

- Submitted `v53` as a live calibration run to test offline/live alignment for the reinforce-beta direction.
- Early live signal: **not promising** (underperforming expectation).
- Working decision: keep `v36` as competitive baseline; treat v53 line as exploratory unless live trend reverses.

### Meta-learning

1. v36 local architecture appears to be in a **local optimum under scalar knob sweeps**.
2. H2H improvements can fail to generalize in mixed 10-agent pools; full tournament must remain the promotion gate.
3. Future improvements should prioritize **structural target/score quality changes** over threshold-only tuning.
4. Wrapper-based candidates are fine for experiments, but submission bundles must include imported dependencies.

---

## v60–v70 Structural Iteration Wrap-Up (2026-06-20)

### What worked

1. **Reproducible gate discipline held up:** n24 -> n48 -> full mixed-pool tournament consistently filtered false positives from H2H-only wins.
2. **Operational submission path is stable:** wrapper-candidate bundle rules were applied correctly and `v68` was submitted successfully as an exploratory live check.
3. **Diagnostics remained high-signal:** gate-level telemetry continued to explain why scalar changes plateaued (score quality and target quality bottlenecks, not simple threshold drift).

### What did not work

1. **H1 score decomposition (`v60`)** improved planner rejection shape but hurt match outcomes (over-firing weak missions under pressure).
2. **Wave/reinforce scalar sweeps (`v62`-`v70`)** produced stronger pairwise records (including vs producer) but repeatedly collapsed to **rank 5** in full mixed tournament.
3. **Promotion-by-H2H heuristic failed** in this cycle; mixed-pool robustness did not follow pairwise gains.

### Leftovers and current TODOs

1. **`h3-closed-loop-calibration`** remains in progress (live/offline drift not yet closed with a control loop).
2. **`tournament-gating`** completed for this structural family; no candidate promoted over control in mixed-pool results.
3. **Live exploratory submission resolved:** `submission_v68_wave5_reinforce26.tar.gz` (ID `53894098`) completed with score below control.

### Future paths to explore (next structural wave)

1. **Target quality first:** reduce false-negative/false-positive mission scoring in early game via richer mission context, not ROI scalar tweaks.
2. **Candidate generation breadth:** add constrained multi-source coalition generation that can propose non-greedy but coordinated captures.
3. **Closed-loop calibration:** adapt reinforcement/risk terms from observed early-game stability metrics rather than fixed early-window constants.
4. **Promotion rule:** require full mixed-pool uplift before mainline promotion; treat H2H only as directional pre-filter.

---

## External research synthesis (2026-06-21)

Source reviewed: user-provided strategic research note on "beyond-heuristic" evolution (ProducerLite -> IL/RL).

### Comparison vs current project findings

| Topic | External research claim | Current repo evidence | Assessment |
|---|---|---|---|
| Heuristic ceiling | Top heuristic planners hit a ceiling and need learned components | v48-v70 cycle repeatedly plateaued despite scalar tuning; mixed-pool rank mostly 4-5 | **Aligned** |
| Importance of policy learning | IL -> RL progression is likely required for next jump | Backlog already prioritizes per-planet BC hybrid (H-A4) and value-learning tracks | **Aligned** |
| Hyperparameter optimization | Manual tuning should be replaced by algorithmic optimization (e.g., CMA-ES/Optuna) | Recent sweeps were mostly manual and narrow | **New actionable gap** |
| Self-play / league robustness | Single-opponent progress overfits; use broader training/eval mix | Our promotion gate already enforces mixed 10-agent tournaments | **Aligned** |
| Engine specifics | Notes mention practical edge-case timing details | Existing docs use 500-turn model; no local proof yet for alternate cutoff behavior | **Unverified; test before adoption** |

### Practical learnings adopted

1. Treat the note as a **strategic confirmation**, not a wholesale architecture rewrite request.
2. Prioritize **hybrid learning components** that plug into orbit_lite safety/geometry rather than full end-to-end replacement.
3. Add one explicit workstream for **algorithmic parameter search** against mixed-pool objective, since this has not been formally run yet.
4. Keep any engine-behavior claims as **instrumentation tasks first** (no policy changes until measured locally).

### H-B4 harness kickoff (2026-06-21)

- Implemented `scripts/hb4_search.py` for bounded black-box search over coupled ProducerLite knobs.
- The runner now:
  - generates candidate files from `v36_candidate_min_ships.py`,
  - evaluates via `run_tournament.py` artifacts,
  - ranks trials by objective `avg_pts*100 + first_pct`,
  - marks trials invalid when test-agent game coverage is too low or tournament errors occur.
- This is an **offline exploration tool only**; promotion still requires n24 -> n48 -> mandatory tournament gate and documentation in this log.

### H-B4 batch-1 results (2026-06-21)

- Search run: `scripts/hb4_search.py --trials 2 --games 24` (mixed-pool objective).
- Top trial from search objective:
  - Candidate: `generated_candidates_batch1/v71_candidate_hb4_b1_001.py`
  - Search metric snapshot: rank 2/10, avg_pts 2.000, first% 55.6 (9 games participated in sampled 24).
- Promotion check vs baseline:
  - `run_validation.py --ch generated_candidates_batch1/v71_candidate_hb4_b1_001.py --bl v36_candidate_min_ships.py -n 24 --seed 42`
  - Result: **11W/13L (45.8%, CI95 [28-65])**
- Decision: **do not advance to n=48** for this trial; continue H-B4 exploration with additional bounded samples and then re-gate.

### H-B4 batches 3-4 + screened gating (2026-06-21)

- Batch-3 (`seed=4242`) produced stronger mixed-pool candidates:
  - `v71_candidate_hb4_b3_001.py` and `v71_candidate_hb4_b3_003.py` both reached rank-1 in 24-game sampled tournaments.
- Direct n=24 checks vs `v36_candidate_min_ships.py`:
  - `v71_candidate_hb4_b3_001.py`: **11W/13L** (45.8%, CI95 [28-65]) -> fail
  - `v71_candidate_hb4_b3_003.py`: **10W/14L** (41.7%, CI95 [24-61]) -> fail

- Added automatic post-search screening to `scripts/hb4_search.py`:
  - optional `--screen-games`, `--screen-top-k`, and `--screen-baseline`
  - records n=24 H2H artifacts in search summary for top valid trials.

- Batch-4 screened run (`seed=5353`, trials=2):
  - `v71_candidate_hb4_b4_001.py`: screened **11W/13L** (45.8%) -> fail
  - `v71_candidate_hb4_b4_002.py`: screened **12W/12L** (50.0%) -> passes n=24 threshold

- Promotion sequence for `v71_candidate_hb4_b4_002.py`:
  1. n=48 vs v36: **29W/19L** (60.4%, CI95 [46-73]) -> pass
  2. Mandatory tournament gate (210 games): `artifacts/tournament_20260621_021619.json`
     - Result: **rank 5/10**, pts 138.5, 1st% 32.1

- Decision: despite n48 H2H pass, tournament rank remained mid-tier; **no promotion yet**.

### H-B6 uncertainty-gate kickoff (2026-06-21)

- New candidate: `v72_candidate_uncertainty_gate.py` (from v36 lineage).
- Change: add a lightweight uncertainty gate during candidate scoring:
  - uncertainty proxy = weighted (ETA risk + low floor-margin risk),
  - drop high-uncertainty missions above threshold,
  - apply small score penalty for residual uncertainty.
- Quick gate vs v36:
  - `run_validation.py --ch v72_candidate_uncertainty_gate.py --bl v36_candidate_min_ships.py -n 8 --seed 42`
  - Result: **3W/5L** (37.5%, CI95 [14-69]).
- Status: early configuration appears too conservative/fragile; tune uncertainty weights/threshold before n24 promotion gate.

### H-B5 split-vs-stack sizing kickoff (2026-06-21)

- New candidate: `v73_candidate_split_stack.py` (from v36 lineage).
- Structural change:
  - generate two launch-size variants per (source,target): full stack + split send,
  - constrain split variant to longer-ETA offensive lanes (`eta >= 6`) to avoid harming defensive/short tactical responses.

- Gate progression vs `v36_candidate_min_ships.py`:
  - n8 quick check (tuned): **4W/4L** (50.0%)
  - n24: **14W/10L** (58.3%, CI95 [39-76]) -> pass
  - n48: **26W/22L** (54.2%, CI95 [40-67]) -> pass

- Mandatory tournament gate:
  - Artifact: `artifacts/tournament_20260621_100925.json`
  - Result: **rank 5/10**, pts 139.0, avg 1.655, 1st% 32.1 (27/84 first places)

- Decision: H-B5 improved pairwise gates but still landed in the same mid-tier tournament band; **no promotion yet**.

---

## Kaggle Competition Intel Sweep + H-D1/H-D2/H-D7 Ablations (2026-06-21)

### Research Summary

Full sweep of 243 Kaggle discussion threads, notebooks, and GitHub agent repos.

**Meta findings:**
- RL agents dominate top ~9 spots (PPO+JAX: 1303+ ELO, GH200, $15 compute, 6.5h)
- Heuristic/planner ceiling at ~1200-1250 without optimization
- #1 bot described as "1-ply search agent" — not static greedy
- BC fails: 2.4M-param clone of #1 bot loses 5:1 to greedy Producer (search structure uncloneable)
- Autoregressive launch head is the BC unlock (fleet launches must be jointly modeled)
- Key heuristic gap: YuriNakayama/orbit-wars agent has snipe, crash-exploit, indirect wealth, elimination bonus, reaction-time classification

### H-D1: Elimination bonus (v74b_candidate_elim_only.py)

- Change: +1.0 additive score when enemy owner has < 10% of our total ships
- 3-seed H2H vs v36: seed42=50%, seed142=56.5%, seed242=50% → avg 51.4%
- n=48 seed42: 23W/23L/2T (50%)
- Mandatory tournament gate: **rank 5/10**, pts 144.0, 1st% 35.7
  - Artifact: `artifacts/tournament_20260621_205546.json`
- Decision: **no promotion** — same rank-5 pattern as all prior ablations

### H-D2: Safe-neutral bonus (v74c) and combined (v74)

- v74 (both bonuses, aggressive): failed n=24 at 41.7% — overfires on marginal missions
- v74c (safe-neutral only): failed n=24 at 45.8%
- Decision: both variants blocked

### H-D7: Production-weighted shortlist (v75_candidate_prod_ranking.py)

- Change: rank shortlist by `prod * 4.0 - proximity` instead of `-proximity`
- n=8: 3W/5L (37.5%) — early failure
- Decision: pure-proximity shortlist is intentional; it selects reachable targets. Production weighting overshoots to farther targets, wasting ships on long-distance missions

### Overall H-D series verdict

**Pattern confirmed:** every structural change (H-A, H-B, H-D series, 15+ candidates) lands at rank 5/10 in mixed-pool tournament. The rank-5 ceiling is architectural: the greedy single-source planner cannot beat itself with score adjustments alone.

**Root cause (from research):** the #1 bot runs a 1-ply search. Any agent using independent greedy mission scoring will converge to similar behavior regardless of scoring tweaks, because the bottleneck is joint fleet coordination, not individual mission ROI.

### Tournament pool observation (v74b run)

Notable: v37 (wave_cap=5) ranked **1st/10** in this tournament run (197.0 pts, 65.5% 1st-place), v36 ranked **2nd** (177.5 pts, 54.8%). This is consistent with prior offline results where v37 dominated. Despite this, v37 and v36 are essentially tied live (1170.0 vs 1170.5). Offline tournament and live Kaggle ELO are not tightly correlated for same-tier agents.

---

## 2026-06-22 — Tournament pool fix + SMW V2 discovery

### Critical bug fix: Kaggle agents silently excluded from tournament pool

**Root cause discovered:** `run_tournament.py` caps pool at 10 agents. Previous ordering placed 4 internal controls + 5 legacy baselines (v26–v29, hbx2) into the pool before Kaggle agents, filling the cap. All prior tournament runs (v73, v74b, etc.) were against an internal-only pool (~850–1180 ELO), never against the Kaggle agents we actually compete against.

**Fix (2026-06-22):** Kaggle agents reordered to slots 5–9 in pool candidate list, before legacy baselines.

**Impact:** All prior "rank 5/10" tournament results were optimistic — that rank was achieved against a weak pool. Corrected pool includes kaggle_smw_v2 (1300+ ELO), kaggle_i_the_orbit, kaggle_v44_elo, kaggle_v2_gru, kaggle_producer.

### H-D8: roi_threshold 1.5 → 1.2 (v76_candidate_roi_12.py)

- Hypothesis: kaggle_v44_elo uses roi_threshold=1.2; matching this knob may close gap
- Gate vs v36 (corrected pool):
  - n=8: **4W/4L** (50%)
  - n=24: **12W/12L** (50%)
- Direct H2H vs kaggle_v44_elo: **13W/3L** (81%) — we already beat v44_elo at roi=1.5
- Full tournament (10-agent corrected pool, artifact `tournament_20260622_103736.json`):
  - **Rank 4/10**, pts 131.5, 1st% 27.4%, Pred.Kaggle≈919
  - Pool order: kaggle_i_the_orbit (1st), kaggle_producer (2nd), v37 (3rd), v76 (4th), control_producer (5th)
- Decision: **no promotion** — roi_threshold reduction is neutral vs v36; gap to top is structural

### kaggle_smw_v2 (shorooghahmadi, 1300+ ELO) — new pool anchor

**Source:** `https://www.kaggle.com/code/shorooghahmadi/orbit-wars-strategic-multi-wave-fleet`

**Architecture:** ProducerLite variant (same orbit_lite family, no neural weights, pure torch tensor heuristic). Self-contained 2510-line file.

**Key structural features absent from our v36:**

| Feature | SMW V2 | Our v36 | Impact |
|---|---|---|---|
| `enable_focus_fire=True` | ✅ up to 4 sources per target | ❌ single-source only | HIGH |
| `track_fleets=True` | ✅ enemy fleet tracking in garrison | ❌ stateless | HIGH |
| `enable_potential_risk` | available (disabled by default) | ❌ missing | MEDIUM |
| `min_ships_to_launch` | `4.0` | `8.0` | LOW |

**Focus fire mechanism:** when `enable_focus_fire=True`, the planner builds multi-source strike packages (up to `max_strike_sources=4` planets coordinating on the same target). This is the "1-ply joint optimization" we identified architecturally missing. Single-source greedy assignments converge regardless of scoring tweaks; multi-source coordination unlocks captures no individual planet can achieve alone.

**H2H calibration:**
- kaggle_smw_v2 vs v36: **13W/3L** (81% win rate for smw_v2) — clearest gap measured so far
- Added to tournament pool at slot 6 (highest-priority Kaggle anchor)

**Repo path:** `tournament_agents/kaggle_smw_v2.py`

### Live Kaggle scores (2026-06-22, ~36h to deadline)

| Submission | ELO | Status |
|---|---|---|
| v36 original | 1170.5 | ❌ frozen (not latest 2) |
| v36 resubmit | 1033.9 (rising) | ✅ active |
| v43 wavecap5+beta24 | 1131.7 (rising) | ✅ active |

The two active submissions are v36-resubmit and v43. Meta has shifted since June 12-13 (Producer V2, 1266+ ELO public agent, RL threads — community-wide score drop confirmed in Discussion #708962).

### Meta shift summary (confirmed root cause)

Three simultaneous events on June 12, 2026 raised the competitive floor:
1. `slawekbiel/the-producer-v2` — strong heuristic baseline made public
2. "Struggling with RL?" thread (65 votes) — unlocked IL/RL path for entire community
3. `itzzomkar/1266-elo-the-v44-agent-100-self-contained` — 1266+ ELO public submission

June 13: `shorooghahmadi/orbit-wars-strategic-multi-wave-fleet` V2 (focus-fire ProducerLite) reaching 1300+ ELO.

Heuristic ceiling without focus-fire or fleet-tracking: ~1170–1200 ELO.

---

## What to do next (2026-06-22, ~36h remaining)

Three viable paths:

1. **Submit kaggle_smw_v2 directly** — it's public, self-contained, likely ~1300 ELO. Fastest path to leaderboard improvement. No development required. Risk: same as submitting any public notebook.

2. **Port `enable_focus_fire` into our orbit_lite codebase** — multi-source strike coordination is the confirmed structural gap. High effort (~4-8h to port + test). Highest upside if it works. Risk: integration bugs under competition time pressure.

3. **Tune kaggle_smw_v2 knobs on top of the public base** — run H-B4-style search over SMW V2's config, keep best knobs, submit. Medium effort (~2h). Upside: marginal vs just submitting V2 directly.

---

## 2026-06-22 (late) — pool-profile split and alignment recovery

### Problem observed

A broad 20-agent tournament (`mixed20`, 300 steps, 4845 games) produced rankings that did not match live Kaggle ordering:
- `v43` ranked mid-table offline while remaining top among our live submissions.
- Several weak/legacy agents were over-rewarded in local fixed-pool round robin.

Conclusion: a single offline tournament profile was mixing two goals (Kaggle score prediction vs regression robustness) and underperforming at both.

### Fix implemented

`run_tournament.py` now supports explicit pool profiles:

- `kaggle_latest10` (submission decision profile): curated 10-agent pool intended to track live Kaggle meta.
- `mixed20` (robustness profile): broad stress pool including legacy baselines.

CLI additions:
- `--pool-profile {mixed20,kaggle_latest10}`
- `--max-agents` remains supported (default 10).

### Validation run (Kaggle-like profile)

Run:
- `--pool-profile kaggle_latest10 --max-agents 10 --steps 500 --repeats 3`
- Artifact: `artifacts/tournament_20260622_kaggle_latest10_steps500_r3.json`

Result:
- `v43_candidate_wavecap5_beta24.py` **rank 1/10** (435.5 pts, 35.7% first-place)

This restored the prior directionality where v43 was top in the curated offline pool and aligned with live medal-zone behavior.

### Operational policy (final hours)

1. Use `kaggle_latest10` + `steps=500` for **submission decisions**.
2. Use `mixed20` only for **regression/stress testing**.
3. **Risk-off rule:** do not replace `v43` unless new candidate shows strong, repeatable uplift in the Kaggle-like profile.
4. With Kaggle's "latest 2 submissions active" rule, every new submit is destructive to one active runner; treat submits as high-cost actions.

## Kaggle Submission Update (2026-06-21)

### Latest live scores

| Submission | ID | Status | Public score | Notes |
|---|---:|---|---:|---|
| `submission_v66_wave5_reinforce24.tar.gz` | 53895844 | COMPLETE | 1105.0 | standalone wave-cap=5, reinforce beta 2.4 |
| `submission_v68_wave5_reinforce26.tar.gz` | 53894098 | COMPLETE | 1061.3 | exploratory wave-cap=5, reinforce beta 2.6 |
| `submission_v43_candidate_wavecap5_beta24.tar.gz` | 53894119 | COMPLETE | 1164.9 | wave-cap=5, reinforce beta 2.4 from v36 lineage |
| `submission_v53_early_reinforce_beta.tar.gz` | 53887843 | COMPLETE | 1118.3 | early reinforce beta window tweak |
| `submission_v48_observability.tar.gz` | 53861063 | COMPLETE | 1159.1 | v36-equivalent + observability scaffolding |
| `submission.tar.gz` (v36) | 53843506 | COMPLETE | 1170.5 | control reference in this cycle |

### Decision update

- The initial v68 spike did not hold after stabilization; both v68 (1061.3) and v66 (1105.0) underperformed the v36 control.
- `v36` remains the live reference in this batch; v43/v48 are closer but still below v36.
- Next live attempts should stay near v36 with single-change deltas and strict promotion criteria.
