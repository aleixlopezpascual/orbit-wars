# v43 Loss Analysis (2026-06-23)

- Source: submission **53927366** (v43, 1138.9), 30 episodes analyzed via `scripts/analyze_replays.py --our-name "Aleix López"`.

## Results

- Record in sample: **11 W / 19 L (~37%)**. Split: 2P 5W/8L, 4P 6W/11L (4P slightly worse).
- Focus-fire coordination (proxy metric):
  - Losses: avg **winner 26.5** vs **us 12.6** — large, consistent deficit.
  - Wins: ours ≈ winner (trivial; we are the winner).
- Worst blowouts are 4P with near-zero coordination on our side: e.g. 2-vs-45, 0-vs-18, 1-vs-19, 0-vs-12.

## Metric caveat

The focus-fire detector counts any ≥2 distinct-source arrivals at one target within 2 turns, so it also captures v43's *incidental* multi-planet convergence (v43 has no intentional focus-fire). Absolute counts overstate intent; the **comparative deficit** (winner vs us) is the trustworthy signal.

## Verdict

**GAP = FOCUS_FIRE (confirmed at the top), but porting is NOT the right final-day bet.**

- Winners systematically out-coordinate v43, especially in 4P → focus-fire/coordination is the real ceiling lever.
- However, the best public focus-fire agent (SMW, see [SMW987_AUTOPSY.md](SMW987_AUTOPSY.md)) scores **987 < v43's 1138** on the live board. A focus-fire port is therefore high-risk, unproven-upside, and unlikely to beat our proven agents within the final hours.
- The evidence redirects the final-day plan toward exploiting **submission variance with proven agents** (v36 1170.5, v43 1164.9 — both above the silver cutoff of ~1160.9) rather than a structural port.
