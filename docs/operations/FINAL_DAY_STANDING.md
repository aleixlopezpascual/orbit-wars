# Final Day Standing (2026-06-23)

Snapshot source: public leaderboard CSV 2026-06-22T22:06 UTC; submissions list 2026-06-23.

## Standing

- **You: rank 338 / 4756, score 1138.9** (currently tracked agent = v43).
- Silver cutoff (top 5%): ~rank 238, score ~1160.9 → **silver is ~22 pts away**.
- Bronze cutoff (top 10%, 4756 basis): ~rank 476, score ~1117.2.
- **Bronze is marginal:** on the 3245 official-team basis, bronze cutoff ≈ rank 324 — you are 338, just below. Not safe.

## Submission IDs

- SMW-987: **53942735**, score 987.0 (2026-06-22 10:27) — **latest submission**.
- v43 (tracked): **53927366**, score 1138.9 (2026-06-21 23:57).
- v43 (earlier draw): 53894119, score **1164.9** (2026-06-20) — not tracked.
- v36 best-ever: 53843506, score **1170.5** (2026-06-19) — not tracked.

## Tracked pair (latest 2)

- Currently **{SMW-987 (987), v43 (1138.9)}**; best-shown = 1138.9.
- **SMW-987 is dead weight in a tracked slot.** The final two submissions of today determine the tracked pair.

## Key variance fact

- Same code, very different draws: v36 1170.5 vs 1046.8; v43 1164.9 vs 1138.9.
- With best-of-latest-2 shown, submitting the strongest proven agent as the final two submissions yields the **max of two independent draws** — a legitimate variance play toward silver with no code risk.

## Decision Gate (2026-06-23)

- Track F verdict: NOT a runtime bug (SMW 53% W/L, warmup absorbed by overage; 4P-weak + converging).
- Track L verdict: GAP=FOCUS_FIRE confirmed at the top (winners 26.5 vs us 12.6 in losses, worst in 4P).
- Counter-evidence: SMW (focus-fire flagship) = 987 < v43 1138 live.
- **User decision: BRANCH = FOCUS_FIRE port** (accept higher ceiling + risk).
- **Safety rail:** tracked pair = {v43 proven floor, focus-fire port}. Port goes live only if it clears local kaggle_latest10 gate vs v43. v43 best-shown protects bronze if the port flops.

## v80 Gate Result (2026-06-23) — FAILED

Identical 8-agent `kaggle_latest10` field, seed 42, 500 steps:

| Metric | v80 (focus-fire) | v43 | Promotion needs |
|---|---|---|---|
| n=24 H2H vs v43 | 58.3% (CI [39–76]) | — | informative only |
| Tournament points | 59.5 | **60.5** | v80 > v43 ✗ |
| Tournament 1st% | 34.3% | **37.1%** | v80 > v43 ✗ |
| ELO / Pred.Kaggle | 1036 / 978 | 1031 / 972 | ~tie |

- **Verdict: v80 does NOT clear the gate.** Strong H2H, zero tournament uplift — the H-A5 pattern repeats; consistent with SMW (focus-fire flagship) = 987 live.
- **Decision: v80 does not go live.** Fall back to defending with proven agents.
- v36 ranked **1st in both** tournaments (64.5 / 68.0 pts) → strongest owned agent (live best 1170.5).

## FINAL DECISION (2026-06-23): HOLD — submit nothing further

Keep the current tracked pair **{SMW-987, v43-1138.9}** untouched. No final-day submission.

### Why (the decisive reasoning)

1. **The dead SMW-987 is not costing points.** Leaderboard shows the *max* of the tracked
   pair: `max(987, 1138.9) = 1138.9`. The wasted slot is an opportunity cost only, not an
   active drag — so there is no urgency to replace it.
2. **The current v43 is already converged** against a recent pool (low σ). It is the safest
   form of the (marginal) bronze position we can hold.
3. **Resubmitting has neutral-to-negative EV under meta shift.** ELO is relative to the pool,
   and the pool strengthened sharply in the final days (many Jun-22 submissions at 1400–1800).
   Fixed heuristic agents do not improve; their rating drifts down or holds as the field rises.
   A fresh v36/v43 would most likely converge **at or below** its historical score, not above.
   A fresh v43 is identical code to the current v43 → same true skill, measured over a *harder*
   window → no gain. The only upside (max-of-two effect) is ~cancelled by the meta downdraft and
   re-convergence variance, while the downside (both draws land low) is real.
4. **No agent of higher converged skill exists for the current meta.** Heuristic tuning is
   saturated; the focus-fire port (v80) failed the gate. There is no last-day change that
   reliably buys silver.

### Residual risk (acknowledged, unavoidable)

Bronze is marginal (rank 338 vs ~324 cutoff on the strict 3245-team basis) and the tracked v43
will keep drifting during final eval (Jun 24 – Jul 8). No resubmission we can make reduces this
risk — they only add variance. Holding is the minimum-variance choice.
