# Final-Day Medal Push — Design Spec

**Date:** 2026-06-22
**Author:** Aleix López (with Claude)
**Status:** Approved design → ready for implementation planning
**Deadline:** 2026-06-23 23:59 UTC (~1 working day remaining)

---

## 1. Objective

Over the final competition day, maximize the finishing medal: **defend the current
bronze position and push for silver**, by any Kaggle-allowed means, while keeping
`v43_candidate_wavecap5_beta24.py` as a protected floor.

### Success criteria (priority order)

1. **Floor held** — v43 (or an equivalent) remains live and *tracked* at the
   deadline; bronze is not lost.
2. **Silver attempt shipped** — at least one challenger that beats v43 on **both**
   total points **and** 1st-place rate in the `kaggle_latest10` tournament gate is
   submitted.
3. **Evidence-backed submissions** — no submission is made on a single lucky run.
   Promotion requires the gate criterion already established in
   `docs/13_IMPROVEMENT_HYPOTHESIS_BACKLOG.md`.

### Key prior facts driving this plan

- Heuristic scoring/threshold tuning is **saturated**: H-D1/D2/D7/D8, H-E2, H-E4,
  and final-hour variants v74–v79 were all no-go vs v43.
- The one confirmed structural lever is **`enable_focus_fire`** (multi-source /
  coordinated joint strikes). `tournament_agents/kaggle_smw_v2.py` has it, beats
  v36 ~81% head-to-head, and is reported at ~1300 ELO.
- **The public SMW V2 agent, submitted directly, scored only 987 for us** — a
  ~300-point collapse vs its reputation. This is the signature of a *runtime
  problem* (per-turn timeout, validation/version mismatch, or 4P-pool punishment),
  not a strategy problem. Diagnosing it is itself a high-value, low-cost lever.
- Kaggle API replay/log access is **confirmed working**.

### Hard constraints

- **5 submissions/day; latest 2 tracked; best-shown wins.** Slot budgeting and
  re-submitting v43 to keep it tracked are first-class concerns.
- Promotion gate: `run_tournament.py --pool-profile kaggle_latest10 --max-agents 10
  --steps 500`. `mixed20` is for stress/regression only, never the sole basis for a
  submission.
- One hypothesis family per candidate file; each candidate declares its parent.
- v43 is a thin config layer over v36 (`max_waves_per_turn=5`,
  `reinforce_size_beta=2.4`) with focus-fire **off**.

---

## 2. Architecture — four gated phases

```
Phase 0  Baseline & slot map
            → exact standing, gap to silver, slots used today, is v43 tracked?
            │
Phase 1  Two parallel forensics (time-boxed ~2h total)
   ├─ Track F: SMW-987 autopsy   → per-seat LOGS → timeout? error? 4P collapse?
   └─ Track L: v43 loss analysis → v43 lost games + top-player games → is gap focus-fire?
            │
   DECISION GATE (deterministic, evidence in hand)
            │
Phase 2  Build + LOCAL GATE the chosen challenger(s)   (kaggle_latest10)
            │
Phase 3  Submit with slot discipline → keep v43 rollback → final pick at deadline
```

The decision gate is the core idea: Phase 1 buys information cheaply so Phase 2
commits multi-hour effort to the right change. Each track produces a one-page dated
evidence artifact, not an impression.

---

## 3. Phase 0 — Baseline & slot map

Before any analysis, establish the ground truth:

- Current leaderboard standing, v43's actual Kaggle score, and the numeric gap to
  the silver cutoff (note: cutoffs may move on the last day as others submit).
- How many of today's 5 submission slots are already spent.
- Whether v43 is currently one of the latest-2 *tracked* submissions.
- Record the submission IDs needed for Phase 1: the **SMW-987 run** and the **v43
  run**.

Output: a short standing note (can live inline in the loss-analysis note).

---

## 4. Phase 1 — Forensics tracks

Both tracks are **time-boxed to ~2h total**. Each writes a dated evidence note
under `docs/operations/`.

### Track F — SMW-987 autopsy (cheapest shot at silver)

- **Input:** Kaggle submission ID of the 987 SMW run.
- **Method:** `scripts/fetch_kaggle_match_artifacts.py --download-logs` for **all
  four seats** across ~15 episodes, plus replays. Grep logs for: per-turn time near
  the limit, exceptions/tracebacks, validation warnings, "agent failed/skipped
  action," and version/import errors.
- **Split metric:** score/placement in **2P vs 4P** episodes separately.
- **Decision output (one of):** `RUNTIME_BUG (fixable)` / `4P_WEAKNESS` /
  `GENUINELY_WEAK_HERE` / `INCONCLUSIVE`.
- **Artifact:** `docs/operations/SMW987_AUTOPSY.md`.

### Track L — v43 loss analysis (confirm the lever before paying for it)

- **Input:** v43's submission ID (its lost games) + 5–10 top-player public
  episodes.
- **Method:** download replays; run the new `scripts/analyze_replays.py` to count,
  per game: multi-source/coordinated arrivals at one target within a small time
  window (focus-fire proxy), snipe captures (arrive as an enemy fleet hits a
  neutral), elimination pile-ons, and planets v43 lost while contesting
  single-source.
- **The one question it must answer:** in games v43 loses, do winners
  systematically win contested planets via **multi-source coordination** that
  single-source greedy structurally cannot produce? Quantified, not eyeballed.
- **Decision output (one of):** `GAP=FOCUS_FIRE` / `GAP=SNIPE/ELIM` / `GAP=OTHER` /
  `NO_CLEAR_GAP`.
- **Artifact:** `docs/operations/V43_LOSS_ANALYSIS.md`.

---

## 5. Decision gate (deterministic)

Pick the first branch that fires:

1. **Track F = `RUNTIME_BUG`** → fix SMW + resubmit corrected SMW (highest ceiling,
   lowest effort). If time allows, still run the v43 port in parallel.
2. **Track L = `GAP=FOCUS_FIRE`** → port `enable_focus_fire` into the v43 lineage
   (the H-E1 structural change), validated locally.
3. **Track L = `GAP=SNIPE/ELIM`** → implement that one specific mission type
   (H-D3 snipe / H-D1 elimination) — only the one the data shows winners actually
   use.
4. **All inconclusive** → fall back to a single narrow game-derived heuristic,
   accepting it is the low-EV branch.

---

## 6. Phase 2 — Build & local gate

- New candidate as `vNN_candidate_<family>.py`, declaring parent. One hypothesis
  family only.
- Validation ladder:
  1. Parser sanity: metrics correct on one known replay before bulk analysis.
  2. n=24 vs v43 (`run_validation.py`) — must not regress.
  3. Full `kaggle_latest10` tournament — must beat v43 on **points and** 1st-rate.
  4. Runtime: per-turn time percentile within limit in the gate (same failure mode
     suspected for SMW-987).

---

## 7. Phase 3 — Submission & slot discipline

- **Inventory first:** confirm slots spent today and whether v43 is in the
  latest-2 tracked.
- **Rollback rule:** never let v43 fall out of tracking unless a challenger has
  passed the gate. If two challengers are submitted, re-submit v43 to keep it
  tracked.
- **Gate before submit:** every challenger must clear the points + 1st-rate bar in
  `kaggle_latest10` before a slot is spent.
- **Final pick:** at deadline, the tracked pair should be {v43 floor, best gated
  challenger}.

---

## 8. Components

**New (small, focused):**

- `scripts/analyze_replays.py` — parse replay JSON → behavioral metrics (focus-fire
  proxy, snipes, eliminations, lost-contested-planets). Shared by both tracks.
- Evidence notes: `docs/operations/SMW987_AUTOPSY.md`,
  `docs/operations/V43_LOSS_ANALYSIS.md`.
- A focus-fire port candidate `vNN_candidate_*.py` — only if the gate selects it.

**Reused:** `scripts/fetch_kaggle_match_artifacts.py`, `run_validation.py`,
`run_tournament.py`, `scripts/validate_submission_bundle.py`,
`scripts/pre_submission_tournament_gate.sh`.

---

## 9. Error handling & risks

- **Kaggle CLI rate limits / partial downloads** → use `--best-effort`, cap
  `--limit`, cache locally.
- **Unknown replay schema** → validate `analyze_replays.py` on one downloaded
  replay before scaling.
- **Running out of day on the port (biggest risk)** → Track F (fix-SMW) is the
  parallel cheap path; the Phase-1 time-box protects build time; the v43 floor means
  worst case = bronze defended.
- **Focus-fire port adds runtime cost** → must check per-turn time in the local
  gate; this is the exact failure mode that may have sunk SMW-987.

---

## 10. Out of scope

- RL / neural training (no time; prior finding: imitation cannot clone search).
- Generic multi-knob parameter sweeps (saturated).
- Any submission that has not cleared the `kaggle_latest10` gate.
