# Orbit Wars Experiment Log

Track active and historical experiments with their hypothesis, status, and results.

## Active Experiments

> **Status Legend:** 🟡 In-Progress | ✅ Completed | ❌ Failed | 🔵 Pending | ⏸️ Blocked

| Version | Feature | Hypothesis | Status | Started | Completed | Result | Link |
|---------|---------|-----------|--------|---------|-----------|--------|------|
| v34 | Early rush logic | Earlier aggression (turn 30 vs 32) reduces comet race delays | 🟡 | 2026-06-17 | — | — | [agent.py](../../agent.py) |

---

## Completed Experiments

### v33: Contested Neutral Margin Tuning
- **Hypothesis:** Increasing `CONTESTED_NEUTRAL_MARGIN` from 1 to 2 improves safety on multi-player neutral captures
- **Test Method:** 24 episodes vs `control_hbx2.py`
- **Status:** ✅ Completed
- **Result:** +2.3 Elo vs baseline (not merged—needs validation with 50-episode set)
- **Date:** 2026-06-10
- **Notes:** Promising but margin of error still high. Retest with larger sample.

### v32: Sweep + Comet Hybrid
- **Hypothesis:** Combining distance-based sweep logic with comet pre-positioning yields better late-game scores
- **Test Method:** 24 episodes vs `control_hbx2.py` and `v31_candidate_sweep_only.py`
- **Status:** ✅ Completed
- **Result:** +1.8 Elo vs sweep-only, +0.9 vs baseline (merged into `v32_baseline.py`)
- **Date:** 2026-06-08
- **Notes:** Comet pre-positioning adds minimal overhead. Safe to keep as default.

### v31: Comet-Only Isolation
- **Hypothesis:** Pre-anticipation logic alone (without sweep) provides measurable gain
- **Test Method:** 24 episodes vs `control_hbx2.py`
- **Status:** ✅ Completed
- **Result:** +1.1 Elo vs baseline (marginal, kept for reference)
- **Date:** 2026-06-06
- **Notes:** Comet feature is valuable but not sufficient alone. Combine with other tactics.

### v30: Agent Refactor + Phase Tuning
- **Hypothesis:** Consolidating decision logic + tighter phase boundaries improves consistency
- **Test Method:** 50 episodes vs multiple baselines
- **Status:** ✅ Completed
- **Result:** +3.2 Elo vs v29 (significant, merged as `v30_agent.py`)
- **Date:** 2026-06-01
- **Notes:** Major refactor. Phase boundaries were the key win.

---

## Experiment Template

When starting a new experiment, copy this template:

```markdown
### vXX: [Feature Name]
- **Hypothesis:** [What you expect to happen and why]
- **Test Method:** [Gate script, opponent, episode count]
- **Status:** 🟡 In-Progress (or ✅/❌)
- **Started:** [YYYY-MM-DD]
- **Completed:** [YYYY-MM-DD or "—"]
- **Result:** [Elo delta, observations, decision]
- **Notes:** [Key findings, blockers, next steps]
```

Then move it to **Completed Experiments** when done.

---

## Quick Reference

### Files to Check
- **Current candidate:** `agent.py`
- **Recent baseline:** `control_producer.py`
- **Test harness:** `python test_agent.py`
- **Gate scripts:** `scripts/run_control_gate.sh`, `scripts/run_ablation_gate.sh`

### Commit Naming
- Feature branch: `v{N}_<feature_name>`
- Commit: `v{N}: [title] – Hypothesis: [brief description]`

### How to Run Tests
```bash
# Sanity check (ensure baseline stable)
bash scripts/run_control_gate.sh 24

# Test new candidate
bash scripts/run_ablation_gate.sh v34_candidate_early_rush 24

# Head-to-head
python run_validation.py --ch agent.py --bl control_producer.py -n 24 --seed 42
```
