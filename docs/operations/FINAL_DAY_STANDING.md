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
