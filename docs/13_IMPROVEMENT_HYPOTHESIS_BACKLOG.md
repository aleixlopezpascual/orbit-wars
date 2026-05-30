# 13) Improvement Hypothesis Backlog (Documentation Phase)

## Purpose

This document is a prioritized backlog of strategy hypotheses to test in a later implementation phase.

- **Baseline for all future tests:** `control_hbx2.py` (HBX2 lineage).
- **Current phase:** documentation and planning only.
- **No code changes are executed from this document.**

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

---

## Tier B (medium-term impact, moderate complexity)

| ID | Hypothesis | Why it could work | Validation design (future) |
|---|---|---|---|
| H-B1 | Replay-derived opponent profiling | Better adaptation to aggressors/turtles should improve matchup consistency | Evaluate against mixed-opponent panel with slice metrics |
| H-B2 | Hybrid shot validator (small learned component) | Public notebooks show hybrid rule-based + ML validators as an emerging path | Keep inference lightweight; test impact vs pure heuristic planner |
| H-B3 | Runtime-guarded fallback policy | Discussion history shows runtime mismatch can silently kill strong logic | Track turn-time percentile and compare score stability |

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
