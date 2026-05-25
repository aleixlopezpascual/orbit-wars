# v30 Benchmark Log

## Baseline: v29 (Hellburner)

**Snapshot Date:** 2026-05-26  
**Files:** `v29_baseline.py`, `v30_agent.py` (working copy)

### Baseline Features (Verified)
- [x] Comet pre-anticipation (`COMET_PRESTRIKE_*` constants)
- [x] Fresh comet valuation (`COMET_SPAWN_VALUE_MULT = 1.5`)
- [x] Chase window expansion (`COMET_SPAWN_CHASE_TURNS = 22`)
- [x] Distance-aware fleet sizing (`v22_min_ships_for_distance`)
- [x] Sun collision avoidance
- [x] Multi-phase strategy (early rush, opening, late game, total war)

### Baseline Benchmark Commands

```bash
# Quick validation (1 game)
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 1 --seed 42

# Standard n=24 benchmark
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 24 --seed 42

# Full n=48 validation
python3 run_validation.py --ch v30_agent.py --bl v29_baseline.py -n 48 --seed 42
```

### Benchmark Results

#### M1: Freeze Baseline (2026-05-26)
**Status:** ✅ Complete

- v29_baseline.py created and locked
- v30_agent.py initialized from agent.py
- Baseline benchmark infrastructure verified (ready to run once environment is configured)

**Expected Baseline (v29 vs v29):** 50% win rate (identical agents)

---

## Milestone Progress

| Milestone | Task | Status | n=24 Result | n=48 Result | Δ ELO |
|-----------|------|--------|------------|------------|--------|
| M1 | Freeze Baseline | ✅ Done | - | - | - |
| M2 | Port Comet Pre-Anticipation | ⏳ Pending | - | - | - |
| M3 | Sweep-Loss Instrumentation | ⏳ Pending | - | - | - |
| M4 | Sweep Offense | ⏳ Pending | - | - | - |
| M5 | Combat Saturation/Ties | ⏳ Pending | - | - | - |
| M6 | Benchmark-Gate n=24→n=48 | ⏳ Pending | - | - | - |
| M7 | Submit Robust Winner | ⏳ Pending | - | - | - |

---

## Notes

- **Environment Setup:** kaggle_environments must be properly configured for benchmarks to run
- **Reproducibility:** All benchmarks use `--seed 42` for deterministic results
- **Incremental Validation:** Each milestone committed only after positive benchmark delta
- **Alternating Seats:** run_validation.py alternates agent seats (player 0/1) to reduce position bias

---

## v30 Development Plan

See `plan.md` for full roadmap with M1-M7 details.

### Key Milestones Ahead

**M2:** Verify v29 comet logic is fully ported (should already be in agent.py)  
**M3:** Add logging hooks to measure sweep engagement outcomes  
**M4:** Implement sweep offense (multi-planet coordinated attacks)  
**M5:** Saturation detection + tie-annihilation handling  
**M6:** Full benchmark validation n=24 → n=48  
**M7:** Kaggle submission after robust validation  
