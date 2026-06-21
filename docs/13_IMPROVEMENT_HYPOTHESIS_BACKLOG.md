# 13) Improvement Hypothesis Backlog (Documentation Phase)

## Purpose

This document is a prioritized backlog of strategy hypotheses to test in a later implementation phase.

- **Baseline for all future tests:** `control_producer.py` (Orbit Wars Producer, 1180.2 ELO — PRIMARY). ✅ Locked in repo.
  Secondary reference: `control_stronger.py` (I'M STRONGER, 981.3 ELO). ✅ Locked in repo.
- **Current phase:** implementation — orbit_lite architecture adoption required.
- **Key finding (2026-06-18 tournament):** heuristic stack (`agent.py`, v26–v29, hbx2) is at the performance ceiling. orbit_lite agents win 80–84% of games; heuristics win 0–8%. **The next candidate must adopt `ProducerLiteRuntime` / `orbit_lite` to be competitive.**

---

## Prioritization rubric

Hypotheses are ranked by:

1. Expected leaderboard impact
2. Validation cost/risk
3. Compatibility with strict benchmark gating

---

## Tier A (highest expected near-term impact)

| ID | Hypothesis | Why it could work | Validation design (future) |
|---|---|---|---|
| H-A1 | Add lightweight 2-ply lookahead mission scoring on top of HBX2 | Public top strategies repeatedly converge on simulation-aware mission selection; stepping-stone captures are likely under-picked by 1-ply greedy policies | Compare vs HBX2 with fixed seed panel (n=24 then n=48), split by 2P/4P |
| H-A2 | Add present-value target scoring + risk discount | Discussion evidence suggests naive target selection leaves value on table | Ablation against HBX2 with one change only; report winrate + CI + runtime |
| H-A3 | Build mode-specific weights for 2P vs 4P | Community reports 2P and 4P requiring different tactical behavior | Run separate 2P/4P benchmarks and combined weighted score |
| H-A4 | Per-planet behavioral cloning hybrid (dual-head MLP + orbit_lite geometry) | Forum signal indicates replacing large end-to-end models with per-planet supervised intent prediction can improve win rate quickly while keeping rule-based physics safety | Train on top replay datasets with no-op downsampling (keep all launch frames, keep ~10% hold frames), run n=24 then n=48 vs HBX2 and report winrate + CI + action validity |
| H-A5 | Add multi-source coalition launches (2-3 synchronized planets per target) | Producer-style single-source launches miss captures when no single planet can meet floor alone; synchronized arrivals can unlock high-value targets | Add coalition candidate generator behind a flag, run ablation vs `control_producer.py` (n=24 then n=48), and log capture success delta on contested planets |
| H-A6 | Add mathematically-lost planet evacuation ("tavacuation") | Reactive defenses often overcommit to doomed holds; pre-impact evacuation can preserve fleet mass and create immediate counterplay | Trigger evacuation only when projected defense deficit remains negative at arrival; benchmark vs controls with event logging for saved ships and post-evac recapture rate |
| H-A7 | Add state-dependent parameter ensembling in `_config_for` | Deterministic thresholding makes policies predictable in clone-heavy pools; mild dynamic knobs can reduce exploitability without full refactors | Gate dynamic ROI/aggression modifiers by turn/rank/player-count, then run seed-sweep stability tests (n=24 per seed set) to ensure no catastrophic regressions |

### Producer V2 clone-wall feedback mapping (2026-06-19)

- **Already covered:** 2-ply lookahead and stepping-stone planning (H-A1, now made explicit).
- **Newly added from feedback:** coalition launches (H-A5), lost-planet evacuation (H-A6), and dynamic parameter ensembling (H-A7).

### Execution status update (2026-06-20)

| Item | Candidate(s) tested | Outcome | Repeat policy |
|---|---|---|---|
| H-A5 coalition launches | `v38_candidate_coalition.py`, `v39_candidate_coalition_lookahead.py` | Strong in H2H vs Producer but weak transfer in 10-agent tournament (best: rank 4/10) | Do not rerun same coalition params (`max_pairs=2`, `eta_slack=1.5`) |
| H-A1 lightweight lookahead | `v38_candidate_lookahead2ply.py`, `v39_candidate_lookahead_dynamic.py` | Strong H2H but tournament rank 5/10 | Do not rerun same lookahead weight (`0.12`) without additional mechanism |
| H-A6 tavacuation | `v38_candidate_tavacuation.py` | Early failure (1W/7L at n=8) | Park current tavacuation rule (`pressure_ratio=1.2`, full-leftover evac) |
| H-A7 dynamic ensembling | `v38_candidate_dynamic_config.py`, `v39_candidate_lookahead_dynamic.py` | No tournament uplift vs lookahead-only variant | Keep as optional modifier; not a standalone promotion path yet |
| Combination scan | `v39_candidate_coalition_lookahead.py`, `v39_candidate_coalition_dynamic.py`, `v39_candidate_lookahead_dynamic.py` | No tested combo beat v36 in tournament context | Avoid retesting these exact combos unless core primitives change |
| Wave-cap follow-up | `v41_candidate_wavecap5_lookahead_guarded.py`, `v42_candidate_wavecap5_retest.py` | Consistent neutral vs v36 at n=48 and tournament rank 5/10 | Do not rerun identical wave-cap-only variants |
| Reinforcement-risk follow-up | `v43_candidate_wavecap5_beta24.py` | Best short gate vs v36 (n=24) but neutral at n=48 | Keep as live probe only; require stronger n=48 edge before promotion |

---

## Tier B (medium-term impact, moderate complexity)

| ID | Hypothesis | Why it could work | Validation design (future) |
|---|---|---|---|
| H-B1 | Replay-derived opponent profiling | Better adaptation to aggressors/turtles should improve matchup consistency | Evaluate against mixed-opponent panel with slice metrics |
| H-B2 | Hybrid shot validator (small learned component) | Public notebooks show hybrid rule-based + ML validators as an emerging path | Keep inference lightweight; test impact vs pure heuristic planner |
| H-B3 | Runtime-guarded fallback policy | Discussion history shows runtime mismatch can silently kill strong logic | Track turn-time percentile and compare score stability |
| H-B4 | CMA-ES/Optuna search for planner knobs under mixed-pool objective | Manual one-knob sweeps appear saturated; black-box search can find non-intuitive coupled settings | Optimize only 6-10 bounded knobs with tournament score as objective; require reproducibility on held-out seed blocks |
| H-B5 | Split-vs-stack launch optimizer exploiting non-linear speed curve | Current launch sizing may miss score-positive "faster smaller wave" opportunities due to mass-speed nonlinearity | Add offline what-if evaluator on replay states; promote only if mixed-pool 1st-place conversion improves |
| H-B6 | Uncertainty-aware mission filter (ensemble disagreement gate) | Current failures include false-positive mission fires; uncertainty gating can suppress brittle launches | Train 3 light scorers on replay rows; fire only when mean score positive and disagreement below threshold |

### Notes for H-A4 implementation design (future)

1. Training unit should be **owned-planet decision rows** rather than full-board snapshots.
2. Feature blocks should include: local planet state, distance-to-sun, and top-k neighbor context (distance, ETA, owner).
3. Policy shape should be a small dual-head MLP:
   - Head A: launch gate (hold/fire binary)
   - Head B: target selector over top-k candidates
4. Inference should remain hybrid: ML predicts intent; `orbit_lite` computes angle/ship sizing/safety constraints.

---

## Tier C (longer-horizon R&D)

| ID | Hypothesis | Why it could work | Validation design (future) |
|---|---|---|---|
| H-C1 | Structured RL track with strict one-change-at-a-time policy | RL may surpass heuristic ceiling, but only with disciplined training | Separate R&D branch, explicit instability monitors, delayed promotion |
| H-C2 | Learned value function for mission ranking | Could improve high-variance tactical decisions where heuristics are brittle | Offline training on replay data, then online A/B against HBX2 |
| H-C3 | League self-play with periodic snapshot distillation | Fixed-opponent training overfits; league rotation can improve robustness in mixed pools | Train against rotating snapshot pool (including controls and prior candidates), then distill to lightweight runtime head for deployment |

### H-C3 execution spec (2026-06-21)

1. **League pool definition**
   - Seed pool with `control_producer.py`, `control_stronger.py`, `v36_candidate_min_ships.py`, and top recent exploratory candidates.
   - Maintain 8-12 active opponents with Elo-weighted sampling (bias toward stronger opponents, keep exploration floor for weaker styles).

2. **Snapshot cadence**
   - Save learner checkpoints every fixed training window (e.g., every N environment steps).
   - Promote only snapshots that beat current champion in fixed-seed H2H and do not regress in mixed-pool slice metrics.

3. **Distillation target**
   - Distill league-trained policy into a lightweight runtime head compatible with current `orbit_lite` execution path.
   - Keep runtime constraints strict (single-turn inference budget, no heavyweight online rollouts).

4. **Offline promotion gates**
   - Stage A: n24 vs `v36_candidate_min_ships.py`
   - Stage B: n48 vs same baseline
   - Stage C: mandatory full tournament gate (210 games / mixed pool)
   - Require tournament rank uplift over current mid-tier (~rank 5 band) before considering submission.

5. **Failure monitors**
   - Overfit detector: large gap between in-league winrate and mixed-pool tournament rank.
   - Stability detector: seed sensitivity drift across at least 3 seed blocks.
   - Action-quality detector: spike in low-value launches / reduced first-place conversion.

### External research delta note (2026-06-21)

- User-provided strategy research strongly supports the current direction toward hybrid IL/RL.
- The main **new** addition from that review is formalizing algorithmic hyperparameter search (H-B4) and uncertainty-aware decision gating (H-B6), which were not explicitly tracked before.
- Engine-behavior claims from external text (e.g., edge-case turn cutoffs) should be treated as hypotheses requiring local instrumentation before strategy changes.

### H-B4 implementation status (2026-06-21)

- Added reproducible bounded-search harness: `scripts/hb4_search.py`.
- Current bounded knobs: `min_ships_to_launch`, `roi_threshold`, `reinforce_size_beta`, `max_waves_per_turn`, `max_sources_per_lane`, `max_regroup_time`, `horizon_4p`, `max_sources_per_lane_4p`.
- Objective currently logged as: `avg_pts * 100 + first_pct` from mixed-pool tournament output (`run_tournament.py` JSON artifact).

---

## Kaggle competition intelligence sweep (2026-06-21)

### Summary of findings

Full research sweep of 243 Kaggle discussion threads, recent notebooks, and GitHub agent repos (YuriNakayama/orbit-wars, slawekbiel Producer v2).

**Meta state:**
- RL agents dominate top ~9 spots (PPO + JAX; 1303+ ELO on GH200 in 6.5h, ~$15)
- Heuristic/planner agents competitive up to ~1200-1250 ELO but ceiling exists without optimization
- Our v36 at 1170.5 is in competitive heuristic tier; gap to RL leaders ~130+ ELO

**Key structural gaps identified (YuriNakayama/orbit-wars agent):**

| Feature | Status | Priority |
|---|---|---|
| Elimination bonus: extra score when attacking nearly-eliminated players | ❌ missing | HIGH |
| Safe vs contested neutral classification (reaction time) | ❌ missing | HIGH |
| Snipe missions: time fleet to arrive when enemy inbound to neutral | ❌ missing | MEDIUM |
| Crash exploit (4P): capture planet weakened by enemy fleet collision | ❌ missing | MEDIUM |
| Indirect wealth map: augment target value with downstream planet access | ❌ missing | MEDIUM |
| Mode-aware aggression (domination ratio tracking) | ❌ missing | MEDIUM |
| Comet lifetime cap: `turns_profit = min(remaining, comet_life - eta)` | ❌ unknown | LOW |

**Top-tier heuristic gap (Radek's research comment):**
> "Think how you can incorporate solving optimization problems into your code. Static code will not cut it given how varied the situations you encounter are."
The jump from ~1200 to higher heuristic ELO requires moving from static greedy scoring to actual optimization (minimax, LP/IP for ship allocation, MCTS).

**Why behavior cloning fails (souldrive notebook finding):**
LB #1 bot runs a 1-ply search. A 2.4M-parameter neural clone of it loses ~5:1 to the greedy Producer. Search structure cannot be cloned via imitation learning — the autoregressive coupling of fleet-budget decisions is the key unlock.

**obs.step bug (Thread #709392):**
p0 gets `step` in observation; non-p0 players may not. Our adapter already defaults to `obs.get("step", 0)` — **already handled**.

**Platform insight:**
- At 1170 ELO we get mixed 2p/4p games
- At 1250+ ELO, players mostly get 2p games (matchmaking bias)
- Farming weak opponents: min ELO change is now ~+0/-0 (system fixed June 8)

### New hypotheses from research

| ID | Hypothesis | Source | Est. impact |
|---|---|---|---|
| H-D1 | Add elimination bonus (+2.0 score) for attacking opponents with < 20% of our total ships | YuriNakayama agent | MEDIUM |
| H-D2 | Add safe-neutral bonus (+1.5 score) for neutrals where our closest planet is < 70% of enemy's closest | YuriNakayama agent | MEDIUM |
| H-D3 | Snipe missions: infer enemy fleet destinations, generate candidate to race them to neutral targets | YuriNakayama agent | HIGH |
| H-D4 | Crash exploit (4P): detect enemy fleet-planet collision turns, queue fleet to arrive POST_CRASH delay | YuriNakayama agent | HIGH (4P only) |
| H-D5 | Add 1-ply lookahead (expand candidate search before scoring, not just single-source drain) | Radek / LB #1 analysis | HIGH |
| H-D6 | Per-owner domination tracking: when domination > 0.6, increase offensive target priority | YuriNakayama agent | MEDIUM |

### Implementation status

| ID | Candidate | Status |
|---|---|---|
| H-D1 + H-D2 | `v74_candidate_structural.py` | planned / in progress |

---

## Guardrails for future implementation phase

1. Every candidate must declare parent: `control_producer.py`.
2. One hypothesis family per candidate file.
3. Promotion gate: n=24 pass before n=48.
4. Submission decisions use confidence intervals and stability, not single peak runs.
5. Keep a safe rollback submission equal to baseline.

---

## Deferred items intentionally excluded from this phase

- Candidate code creation
- Benchmark execution
- Live Kaggle submissions
- Parameter tuning sweeps

These are implementation tasks for a separate, explicit build phase.
