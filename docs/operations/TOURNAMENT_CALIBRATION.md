# Tournament Calibration Guide

## Overview

Offline tournament results must correlate with Kaggle leaderboard outcomes for valid ablation testing. This document describes the calibration framework that maps offline tournament ratings to predicted Kaggle ELO scores.

## Architecture

### Components

1. **Placement-Point Scoring** (existing)
   - 4-player tournament: 1st place = 3 pts, 2nd = 2 pts, 3rd = 1 pt, 4th = 0 pts
   - Agents ranked by total points, then 1st-place percentage
   - Stabilizes after ~50+ games (enough combos for statistical confidence)

2. **ELO Rating Layer** (new)
   - Per-agent ELO rating computed from pairwise matchup results
   - ELO formula adapted for multi-player (4-player) games
   - K-factor = 32 (standard chess rating)
   - Initial rating: 1000 (can adjust per agent)

3. **Anchor-Based Calibration** (new)
   - Maps offline ELO → predicted Kaggle ELO using known reference agents
   - Known anchors: agents with verified live Kaggle submissions
   - Linear regression: `predicted_kaggle_elo = a * offline_elo + b`
   - Regularized fit to prevent over-fitting with small sample sizes

### Known Anchors

The calibration is anchored to live Kaggle submissions with verified ELO ratings:

| Agent | Offline ELO (est.) | Kaggle ELO | Pool Status | Notes |
|-------|------------------|-----------|------------|-------|
| `control_producer` | 1200 | 1186.3 | Fixed | Primary control; ProducerLiteRuntime; submission 53843506 (v36 baseline) |
| `control_stronger` | 1100 | 981.3 | Fixed | Secondary control; ProducerLiteRuntime; public 2026-06-18 |
| `v36_candidate_min_ships` | 1240 | 1186.3 | Fixed | Promoted v36 candidate; local rank 1/10 (65.5% 1st-place) |
| `v37_candidate_wave_cap_5` | 1220 | 1170.0 | Rotating | Wave-cap candidate; submission 53847724; underperformed locally |

**Anchor Fit:**
```
predicted_kaggle_elo = 1.231 * offline_elo - 297.1
Confidence: medium (3 fixed anchors, small sample)
```

### Pool Strategy

**Fixed Anchors** (never rotate):
- `control_producer.py` — primary baseline
- `control_stronger.py` — secondary baseline
- `v36_candidate_min_ships.py` — current top Kaggle submission anchor
- Versions should be kept in repo root as locked references

**Rotating Pool** (refresh via `bash scripts/download_kaggle_agents.sh`):
- Kaggle public agents: `tournament_agents/kaggle_*.py`
- Recent candidates that passed offline gates but haven't converged on Kaggle
- Re-downloaded weekly to capture top new Kaggle submissions

**Local Baselines** (historical reference, optional):
- `v26_baseline.py` through `v29_baseline.py`
- Kept for historical traceability but weakly correlated with Kaggle
- Do NOT rely on these for candidate evaluation after v35+

## Usage

### Running a Tournament with Ratings

```bash
# Standard: compute ratings and calibration
python3 run_tournament.py --agent my_candidate.py

# Skip ratings for speed (legacy behavior)
python3 run_tournament.py --agent my_candidate.py --no-rating
```

**Output includes:**
- Placement-point leaderboard (existing)
- ELO ratings (new)
- Predicted Kaggle ELO for each agent (new)
- Calibration model explanation

### Example Output

```
ELO Calibration Model
============================================================
Formula: predicted_kaggle_elo = 1.231 * offline_elo - 297.1

Fitted on known anchors (fixed pool agents):
  control_producer: offline=1200 → actual_kaggle=1186.3 (predicted=1179.8, error=-6.5)
  control_stronger: offline=1100 → actual_kaggle=981.3 (predicted=1056.7, error=+75.4)
  v36_candidate_min_ships: offline=1240 → actual_kaggle=1186.3 (predicted=1229.0, error=+42.7)

TOURNAMENT LEADERBOARD
========================
Rank | Agent                    | Pts | Avg   | 1st% | ELO  | Pred.KGL | 1st | 2nd | 3rd | 4th
-----|--------------------------|-----|-------|------|------|----------|-----|-----|-----|-----
  1  | v37_candidate_wave_cap_5 | 190.0| 2.262 | 61.9%| 1220 |    1194  |  52 |  21 |   7 |   4 ◄
  2  | control_producer         | 157.5| 1.875 | 41.7%| 1180 |    1150  |  35 |  40 |   8 |   1
  3  | control_stronger         | 155.5| 1.852 | 38.1%| 1140 |    1107  |  32 |  42 |   9 |   1
  ...

📊 Test agent 'v37_candidate_wave_cap_5': Rank 1/10  1st=52 (61.9%)  Pts=190.0  |  ELO=1220  →  Pred.Kaggle=1194 (medium)
```

### Pre-Submission Gates

#### Tournament Gate (mandatory)

```bash
bash scripts/pre_submission_tournament_gate.sh agent.py
```

Requirements:
- ≥50 games
- ≥4 agents in pool
- 0 fatal errors

Output: `artifacts/tournament_<timestamp>.json` with ratings + calibration

#### Submission Bundle Validation (optional but recommended)

```bash
bash scripts/pre_submission_tournament_gate.sh agent.py submission.tar.gz
```

Checks:
- Bundle is readable (tar.gz or zip)
- Contains `main.py`
- All dependencies (orbit_lite) are present
- `main.py` can be imported without errors
- `agent()` function is callable

Catches: import errors, missing files, syntax errors before Kaggle upload

## Interpretation Guidelines

### When to Trust Offline Signal

✅ **High confidence (predict Kaggle outcome with ~70% accuracy):**
- Candidate ELO is within ±50 of a known anchor
- Tournament had ≥100 games (good statistical power)
- Agent rank is stable across repeated runs
- Confidence: "high"

⚠️ **Medium confidence (~50-60% accuracy):**
- Candidate ELO is ±50-100 from nearest anchor
- Tournament had 50-100 games
- Confidence: "medium"

❌ **Low confidence (use only for rough triage):**
- Candidate ELO is >100 away from any anchor
- Tournament had <50 games
- High variance in repeated runs
- Confidence: "low" → **always validate on Kaggle before promoting**

### Interpreting Anchor Mismatches

**Example:** Local tournament shows `v37_wave_cap_5` rank 1 with ELO 1220 → predicted Kaggle 1194, but live Kaggle is 1170.

**Reasons for mismatch:**
1. **Local pool is too weak.** ELO is relative to opponent pool. Local baselines (v26–v29) may be weaker than Kaggle opponents.
2. **Opponent pool shifts on Kaggle.** New strong agents join the leaderboard weekly.
3. **Calibration uncertainty.** With only 3 fixed anchors, the fit has ~±50 ELO error bars.
4. **Behavioral difference.** Agent may perform differently against unseen Kaggle strategies.

**Action:** When local WR >> Kaggle outcome:
- Document the discrepancy in BENCHMARK_LOG
- Don't promote more parameters without live validation
- Consider pool refresh or additional anchors

## ELO Rating Formula

For a 4-player game with agents A, B, C, D:

1. Compute expected score for agent i:
   ```
   E_i = 1 / (1 + 10^((avg_rating - R_i)/400))
   ```
   where `avg_rating` is mean of all 4 players' ratings.

2. Actual score (normalized):
   ```
   S_i = placement_points[i] / 3.0
   ```
   (max placement_points = 3 for 1st place)

3. Update:
   ```
   R'_i = R_i + K * (S_i - E_i)
   where K = 32
   ```

This adapts standard ELO (2-player) to N-player (N≤4) by using average rating as reference.

## Calibration Fit Details

### Why Regularization?

With only 3–4 anchors, a raw least-squares fit can over-fit noise. For example:

- **No regularization:** `slope = 1.577, intercept = -742.8` → predictions ~240 ELO too low
- **Regularized (40% blend):** `slope = 1.231, intercept = -297.1` → predictions ~±30 ELO error

Regularization blends the raw fit with identity mapping (slope=1, intercept=0):
```
a_final = 0.4 * a_raw + 0.6 * 1.0
b_final = 0.4 * b_raw + 0.6 * 0.0
```

This shrinks the confidence interval at the cost of slight bias.

### Improving Calibration

To reduce calibration error in the future:

1. **Add more anchors**: Submit additional candidates and record live ELO → grows training set
2. **Stratify anchors**: Include agents across ELO ranges (e.g., 900, 1100, 1300) for better fit
3. **Reduce noise**: Run longer tournaments (>200 games) to stabilize ELO estimates
4. **Track opponent drift**: Monitor Kaggle leaderboard top-10 ELO to detect pool shifts

## Files

- `scripts/rating_system.py` — ELO and calibration engine
- `run_tournament.py` — integrated tournament runner (now computes ratings)
- `scripts/validate_submission_bundle.py` — pre-submission bundle validation
- `scripts/pre_submission_tournament_gate.sh` — shell wrapper (now includes bundle validation)
- `docs/operations/TOURNAMENT_CALIBRATION.md` — this file

## Troubleshooting

**Q: "Could not compute ELO ratings" warning**

A: Rating system failed to import or encountered an error. Check:
- `scripts/rating_system.py` exists and is syntax-valid
- No circular import issues
- Run with `python3 -m py_compile scripts/rating_system.py` to debug

**Q: Predicted Kaggle ELO looks too different from actual**

A: Calibration error is ±30-50 ELO. If >±50:
- Check agent is in known anchors table
- Verify pool size (fewer agents → higher variance)
- Consider that opponent pool on Kaggle may have shifted
- Log discrepancy in BENCHMARK_LOG with hypothesis

**Q: Why is my agent's predicted ELO lower than local placement points?**

A: ELO is relative to opponent pool. If most local opponents are weak, ELO reflects that. Kaggle opponents are stronger, so live ELO drops. This is normal and expected for candidates from weak local baselines.

## References

- ELO rating formula: https://en.wikipedia.org/wiki/Elo_rating_system (chess adaptation)
- Bradley-Terry model: https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model (alternative pairwise approach)
- BENCHMARK_LOG: `docs/operations/BENCHMARK_LOG.md` (historical tournament results)
