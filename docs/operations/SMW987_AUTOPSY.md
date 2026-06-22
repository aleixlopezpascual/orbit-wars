# SMW-987 Autopsy (2026-06-23)

- Submission id: **53942735** (`submission_smw_v2.tar.gz`), public score **987.0**, submitted 2026-06-22 10:27 UTC.
- Episodes analyzed: 15 (replays) + our-seat logs (15).

## Runtime evidence

- Engine config: `actTimeout=1s` per turn, `agentTimeout=2s` init, `runTimeout=1200s`, `episodeSteps=500`.
- **First-turn duration: 8.9–14.6 s every game** (torch import + runtime warmup).
- **Max non-first-turn duration: 0.249 s** — comfortably under the 1 s action timeout.
- No tracebacks / errors / "invalid action" / timeout strings in any downloaded log (stdout/stderr empty).
- Conclusion: the ~10–14 s warmup is absorbed by the overage bank; it is slow but **non-fatal**. Games run to completion with fast steady-state turns.

## Performance (from our seat, ground-truth `rewards`)

- Record: **8 W / 7 L (≈53%)** across the 15 episodes.
- Losses focus-fire gap: avg **winner 19.2** vs **us 10.7** coordinated strikes.
- **4P is the weak spot:** both 4P games were losses with large focus-fire deficits (0 vs 8; 7 vs 18).
- SMW is itself a heavy focus-fire agent (11–57 coordinated strikes/game).

## Verdict

**NOT a runtime bug. Closest label: 4P_WEAKNESS + rating still converging from μ₀=600.**

- There is no crash/timeout to fix → no "free silver" by repairing SMW.
- Key strategic implication: **a focus-fire agent (SMW) is scoring 987, *below* our v43 at 1138.9.** Porting focus-fire into v43 is therefore a weak bet for the final day — its flagship implementation underperforms what we already hold.
