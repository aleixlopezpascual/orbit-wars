# 11) HBX2 Baseline Correction

## Purpose

This document records the baseline correction for current competition analysis:

- **Top baseline lineage:** `hellburner-x2-main.py`
- **In-repo reference snapshot:** `control_hbx2.py`

This is a documentation update only. No solution implementation is performed in this phase.

---

## Confirmed baseline decision

`control_hbx2.py` is the canonical local baseline for planning, benchmarking, and future candidate comparisons.

### Evidence

| Claim | Evidence |
|---|---|
| `hellburner-x2-main` is the true control | `docs/operations/BENCHMARK_LOG.md` explicitly states: “True Control: hellburner-x2-main -> control_hbx2.py” and marks it as immutable. |
| Benchmark scripts are already aligned to HBX2 | `scripts/run_control_gate.sh` runs `control_hbx2.py` vs `control_hbx2.py`; `scripts/run_ablation_gate.sh` sets baseline `BL="control_hbx2.py"`. |
| HBX2 has stronger live snapshot evidence than legacy baselines | Captured submissions history includes `hellburner-x2-main.py` with public score 930.6. |
| `agent.py` should not be treated as equivalent baseline | Code diff shows `agent.py` lacks sweep/saturation blocks that exist in `control_hbx2.py` (configuration + mission logic sections). |

---

## Documentation rules going forward

1. Any strategy/status document must state baseline as `control_hbx2.py` unless explicitly changed.
2. Any candidate analysis must specify:
   - parent baseline file,
   - exact deltas,
   - benchmark context (`vs control_hbx2.py`).
3. `agent.py` can be discussed as an alternate or stripped variant, but not as the default competition baseline.

---

## Scope boundary for this phase

- ✅ In scope: correcting documentation and planning assumptions.
- ❌ Out of scope: implementing new candidates, modifying strategy code, or submitting new agents.
