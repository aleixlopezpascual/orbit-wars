# M6: Benchmark-Gate Validation (n=24 → n=48)

**Date:** 2026-05-26  
**Status:** ⏳ READY FOR EXECUTION

## Purpose

Validate v30 improvements across comprehensive benchmark suite:
- **n=24 sample:** Quick validation after each milestone (completed: M1-M5)
- **n=48 sample:** Full validation before final submission (this milestone)

## Cumulative Changes in v30

### M1: Baseline Frozen
- v29 baseline (Hellburner) locked: v29_baseline.py, v30_agent.py
- Benchmark infrastructure ready

### M2: Comet Pre-Anticipation Ported ✓
- All v29 comet features verified: COMET_SPAWN_*, COMET_PRESTRIKE_*
- No regressions expected (v30_agent ≡ v29 baseline)

### M3: Sweep Instrumentation ✓
- Non-disruptive metrics logging added
- Zero impact on gameplay

### M4: Sweep Offense ✓
- Coordinated multi-planet attacks on weak targets (5-50 ships)
- 2+ sources per sweep, 1.25× enemy garrison per source
- Conservative tuning to avoid over-commitment
- Expected gain: +10-30 ELO

### M5: Combat Saturation & Tie-Safety ✓
- Saturation detection prevents over-commitment on attacked planets
- Reduces sends to 70% when saturated (3+ incoming fleets)
- Tie-safe garrison multiplier (1.15×) for defense
- Expected gain: +0-10 ELO (mostly defensive/stability)

## M6 Execution Plan

### Phase 1: n=24 Spot-Check (Pre-Benchmark Validation)

**Command:**
```bash
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 24 --seed 42
```

**Validation Points:**
- [ ] Agent produces valid moves (no crashes)
- [ ] Sweep missions created (check sweep_metrics.json)
- [ ] Sweep execution occurs (fleet coordination observed)
- [ ] Saturation logic activates (watch for garrison preservation)

**Pass Criteria:**
- Zero crashes or invalid actions
- n=24 win rate > 50% (expected: 55-65% vs v29 baseline)
- Sweep metrics show active sweeps (≥ 10 sweep initiations)
- Saturation triggers in test (≥ 2 saturation detections)

**If Regress:**
- Compare sweep_metrics output vs expected sweep patterns
- Debug specific sweep that led to defeat
- Adjust tuning constants if needed
- Re-run n=24

### Phase 2: n=48 Full Validation

**Command:**
```bash
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 48 --seed 42
```

**Validation Points:**
- [ ] Consistency with n=24 results (allow ±3% variance)
- [ ] Cumulative win rate vs v29 baseline
- [ ] Stability across larger sample
- [ ] No unexpected regressions

**Pass Criteria:**
- Cumulative gain: **+20-50 ELO** vs v29 baseline (n=48 sample)
- Win rate: **55-70%** (expected range for successful improvements)
- Variance: **≤5%** delta from n=24 trend
- No crashes or consistency issues

**Interpretation:**
| Win Rate | Result | Action |
|----------|--------|--------|
| >70% | Excellent gain | Proceed to M7 |
| 55-70% | Strong gain | Proceed to M7 |
| 50-55% | Incremental gain | Proceed (borderline) |
| <50% | Regress | Investigate, fix, re-benchmark |

### Phase 3: Analysis & Reporting

**Metrics to Record:**
- n=24 sample: wins, losses, ties, win %
- n=48 sample: wins, losses, ties, win %
- Sweep metrics: initiated, completed, won/lost/tied
- Performance delta: v30 vs v29 baseline

**Sweep Analytics:**
```bash
python3 -c "
import json
m = json.load(open('sweep_metrics.json'))
print(f'Sweeps Initiated: {m.get(\"sweep_initiated\", 0)}')
print(f'Sweep Completed: {m.get(\"sweep_completed\", 0)}')
print(f'Sweep Win Rate: {100*m.get(\"sweep_won\", 0)/max(1, m.get(\"sweep_completed\", 1)):.1f}%')
print(f'Total Ships Sent: {m.get(\"sweep_total_sent\", 0)}')
print(f'Total Ships Lost: {m.get(\"sweep_total_lost\", 0)}')
"
```

**Update BENCHMARK_LOG.md** with:
```markdown
### M6: Benchmark-Gate Validation (2026-05-26)

**n=24 Results:**
- Challenger (v30): W/L/T
- Win Rate: X%

**n=48 Results:**
- Challenger (v30): W/L/T
- Win Rate: Y%

**Cumulative Gain:** +Z ELO vs v29 baseline

**Sweep Metrics:**
- Initiated: X
- Completed: Y
- Win Rate: Z%
- Total Sent: N ships
- Total Lost: M ships

**Status:** ✅ PASSED / ❌ FAILED
**Decision:** Proceed to M7 / Iterate & Re-benchmark
```

## Expected Outcomes

### Best Case (>65% win rate)
- Sweep offense highly effective
- Saturation logic working well
- Strong cumulative gain (+40-50 ELO)
- Clear improvement over v29 baseline
- **Action:** Proceed directly to M7 (submission)

### Good Case (55-65% win rate)
- Sweep offense effective with saturation protection
- Solid cumulative gain (+20-40 ELO)
- Consistent across n=24 and n=48
- **Action:** Proceed to M7 with minor tuning recommendations

### Borderline Case (50-55% win rate)
- Sweep adds some value but offset by saturation overreach
- Incremental gain (+10-20 ELO)
- Consider tuning SWEEP_FLEET_SIZE_MULT or SATURATION_SEND_REDUCTION
- **Action:** Proceed to M7 (still positive delta) or iterate

### Failure Case (<50% win rate)
- Sweeps causing unexpected losses
- Saturation logic too conservative or buggy
- **Action:** Revert to v29, debug sweep logic, re-implement M4

## Tuning Levers (If Regress)

**If sweeps too aggressive:**
- Reduce SWEEP_FLEET_SIZE_MULT: 1.25 → 1.15
- Increase SWEEP_MIN_TARGET_SHIPS: 5 → 10
- Disable sweeps during early phase: SWEEP_ENABLED = False

**If saturation too conservative:**
- Increase SATURATION_SEND_REDUCTION: 0.7 → 0.8
- Decrease SATURATION_ATTACK_COUNT_THRESHOLD: 3 → 2
- Reduce SATURATION_LOOKAHEAD_TURNS: 30 → 20

**If tie-safety problematic:**
- Disable TIE_SAFETY_ENABLED: True → False
- Reduce TIE_SAFE_GARRISON_MULT: 1.15 → 1.05

All changes immediately testable via n=24 quick re-run.

---

## Success Criteria for M6 → M7 Transition

✅ **Required:**
- n=24 and n=48 both show net positive delta vs v29
- No crashes or invalid actions in benchmark
- Cumulative ELO gain ≥ +10 (minimum)
- Consistency: n=48 result within ±5% of n=24 trend

✅ **Strongly Recommended:**
- Cumulative ELO gain ≥ +30 (meaningful improvement)
- Win rate ≥ 55% (clear advantage)
- Sweep efficiency ≥ 60% (most sweeps lead to wins)
- Saturation triggers observed but not excessive

---

## Timeline

**Typical Execution:**
- n=24 validation: 5-10 minutes
- Analysis & tuning (if needed): 10-15 minutes
- n=48 validation: 20-30 minutes
- Total: ~1 hour for complete M6

**If regress detected:**
- Debug & tune: 15-30 minutes
- Re-run n=24: 5-10 minutes
- Re-run n=48 (if improved): 20-30 minutes
- Iterate up to 2 rounds recommended

---

## Next Steps

### If M6 Passes (Expected)
→ **M7: Submit Robust Winner**
- Create PR with v30 improvements
- Final Kaggle submission
- Monitor first 100 matches
- Record actual ELO vs predicted

### If M6 Fails
→ **Investigate & Iterate**
- Analyze sweep_metrics.json for failure patterns
- Review specific games where v30 lost
- Adjust tuning constants
- Re-run M6 (n=24, then n=48)
- Maximum 2 iterations before escalation

---

## Reference: v30 Summary

**Total Changes:**
- M1: Baseline infrastructure (0 logic changes)
- M2: Comet verification (0 new logic)
- M3: Instrumentation (logging only, 0 behavior change)
- M4: Sweep offense (103 lines, new tactic)
- M5: Saturation safety (25 lines, defense enhancement)

**Total Code Added:** ~150 lines of production logic
**Risk Level:** Low (conservative tuning, defensive additions)
**Expected Benefit:** +30-50 ELO (based on M4/M5 design)

**Configuration Tuned to:**
- Aggressive enough: 1.25× multiplier, 2+ sources
- Safe enough: Saturation detection, 70% reduction, 1.15× garrison
- Early-phase safe: Disabled in rush phase
