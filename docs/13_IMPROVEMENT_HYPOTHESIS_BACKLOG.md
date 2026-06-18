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
| H-A1 | Add lightweight lookahead mission scoring on top of HBX2 | Public top strategies repeatedly converge on simulation-aware mission selection | Compare vs HBX2 with fixed seed panel (n=24 then n=48), split by 2P/4P |
| H-A2 | Add present-value target scoring + risk discount | Discussion evidence suggests naive target selection leaves value on table | Ablation against HBX2 with one change only; report winrate + CI + runtime |
| H-A3 | Build mode-specific weights for 2P vs 4P | Community reports 2P and 4P requiring different tactical behavior | Run separate 2P/4P benchmarks and combined weighted score |
| H-A4 | Per-planet behavioral cloning hybrid (dual-head MLP + orbit_lite geometry) | Forum signal indicates replacing large end-to-end models with per-planet supervised intent prediction can improve win rate quickly while keeping rule-based physics safety | Train on top replay datasets with no-op downsampling (keep all launch frames, keep ~10% hold frames), run n=24 then n=48 vs HBX2 and report winrate + CI + action validity |

---

## Tier B (medium-term impact, moderate complexity)

| ID | Hypothesis | Why it could work | Validation design (future) |
|---|---|---|---|
| H-B1 | Replay-derived opponent profiling | Better adaptation to aggressors/turtles should improve matchup consistency | Evaluate against mixed-opponent panel with slice metrics |
| H-B2 | Hybrid shot validator (small learned component) | Public notebooks show hybrid rule-based + ML validators as an emerging path | Keep inference lightweight; test impact vs pure heuristic planner |
| H-B3 | Runtime-guarded fallback policy | Discussion history shows runtime mismatch can silently kill strong logic | Track turn-time percentile and compare score stability |

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

---

## Guardrails for future implementation phase

1. Every candidate must declare parent: `control_hbx2.py`.
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
