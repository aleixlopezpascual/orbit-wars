# Copilot Instructions for Orbit Wars

## Project Overview

**Orbit Wars** is a Kaggle competition requiring AI agents to compete in a real-time strategy game on a 100×100 board. The goal is to maximize planetary control and fleet strength over 500 turns.

- **Competition deadline:** June 23, 2026
- **Submission limit:** 5 per day (2 tracked)
- **Main agent file:** `agent.py` (current working version)
- **Testing:** `test_agent.py` (local validation harness)
- **Validation:** `run_validation.py` (head-to-head testing framework)

## Key Architecture Concepts

### Agent Core Loop
The agent receives observations and returns action lists:
- **Input:** Observation dict with planets, fleets, comets, player state
- **Output:** List of `[planet_id, angle, ships]` moves from owned planets
- **Function signature:** `def agent(observation) -> list`

The agent operates in decision cycles, repeatedly:
1. **Evaluate current board state** — map planets, fleets, comets, enemy positions
2. **Prioritize targets** — neutral planets, comets (based on game phase), enemy planets
3. **Calculate fleet routes** — use orbital mechanics to reach targets
4. **Send fleets** — maintain minimum garrison, avoid sun collisions

### Game Phases

The agent adapts strategy based on turn count:
- **Early Rush Phase** (`turns < 30`) — aggressive expansion, minimal defense
- **Early Opening** (`turns < 40`) — conservative neutral planet captures
- **Opening Phase** (`turns < 80`) — balanced expansion and defense
- **Late Game** (`remaining_turns < 70`) — comet focus and consolidation
- **Very Late Game** (`remaining_turns < 25`) — all-out offense and comet battles
- **Total War** (`remaining_turns < 55`) — endgame collision and capture

### Comet Pre-Anticipation (v29+)

Comets spawn predictably at fixed steps: **50, 150, 250, 350, 450**.
- **Fresh Comet Boost:** Newly spawned comets have 1.5× value multiplier for ~8 turns
- **Pre-positioning:** Fleet launches 3 turns before spawn to intercept at entry zones
- **Entry zones:** Outer corners of board quadrants (e.g., Q1: 15,15)
- **Fleet sizing:** Min 20–45 ships for pre-positioning, max 50 unit travel distance

### Distance-Aware Fleet Sizing

Minimum fleet sizes scale with travel distance to prevent orbital prediction errors:
- Distance ≤15: 16 ships (speed ~2.6, ~4 turns)
- Distance ≤30: 24 ships
- Distance ≤50: 35 ships
- Distance ≤70: 50 ships
- Distance >70: 65 ships

## Testing & Validation

### Local Tests
```bash
python test_agent.py
```
Tests:
- Basic observation handling
- Enemy fleet responses
- Comet planet interactions
- Low ship count scenarios
- Empty/no-action cases

All tests validate action format: `[[planet_id, angle, ships], ...]`

### Head-to-Head Validation
```bash
python run_validation.py <agent1.py> <agent2.py> [seed] [episodes]
```
Simulates multiple matches and returns final scores. Use to benchmark against baselines.

### Control Gate (Sanity Check)
```bash
# Primary control sanity (Producer vs Stronger — must confirm Producer wins ~60%+)
VENV=/Users/aleix.lopez/copilot-worktrees/orbit-wars/aleixlopezpascual-fantastic-system/.venv/bin/python3
$VENV run_validation.py --ch control_producer.py --bl control_stronger.py -n 24 --seed 42
```
`control_producer.py` (1180.2 ELO) is the **primary control**. `control_stronger.py` (981.3 ELO) is the secondary reference.
`control_hbx2.py` is retained as a historical snapshot but is no longer the active control.

> **Venv note:** `orbit_wars` + `torch` are only available in `aleixlopezpascual-fantastic-system/.venv`. Use that Python for all local validation and tournament runs.

### Candidate Gate (Ablation Testing)
```bash
VENV=/Users/aleix.lopez/copilot-worktrees/orbit-wars/aleixlopezpascual-fantastic-system/.venv/bin/python3
# Run candidate vs primary control
$VENV run_validation.py --ch <candidate>.py --bl control_producer.py -n 24 --seed 42
```
Tests a candidate against the primary control (`control_producer.py`).

### Mandatory Pre-Submission Tournament Gate
Before any Kaggle submission, every candidate agent must pass the offline tournament gate.

Required workflow:
1. Run the required gate script:
```bash
bash scripts/pre_submission_tournament_gate.sh <candidate_agent.py>
```
2. Check result artifact:
`artifacts/tournament_<timestamp>.json`
3. Log outcome in `docs/operations/BENCHMARK_LOG.md` before submitting.

Policy:
- Do **not** submit agents that skip this tournament evaluation step.
- Use the full 10-agent pool whenever available. The default priority pool includes
  `control_producer.py`, `control_stronger.py`, `control_hbx2.py`, the versioned local baselines,
  and Kaggle public agents.
- If Kaggle agents are unavailable, run fallback tournament (50+ games) and document why.
- Tournament rankings use **final ship-count scores** (not binary rewards) — 3rd/4th place columns must populate for a valid run.

## Versioning and Ablation Studies

The repo maintains a history of agent versions to track improvements:

**Baseline versions** (locked references):
- `v26_baseline.py`, `v27_baseline.py`, etc. — research snapshots
- `control_hbx2.py` — Hellburner-X2 (historical, ~981 ELO, no longer active control)
- `control_producer.py` — **PRIMARY control** (Orbit Wars Producer, 1180.2 ELO, 2026-06-18) ✅ locked
- `control_stronger.py` — Secondary control (I'M STRONGER, 981.3 ELO, 2026-06-18) ✅ locked

**Development versions** (current variants):
- `agent.py` — main submission candidate
- `v31_candidate_comet_only.py`, `v31_candidate_sweep_only.py` — isolated feature tests
- `v32_candidate_sweep_comet_hybrid.py` — combined variants
- `v34_candidate_*.py` — later-stage experiments

**Guidelines:**
- Always create a new `v{N}_candidate_<feature>.py` file before experimenting
- Run the candidate gate to isolate the impact of a single feature
- Keep successful baselines in root as `v{N}_baseline.py` for reference
- Document hypothesis in commit messages (see below)

## Documentation Structure

- `docs/README.md` — Master navigation index
- `docs/01_COMPETITION_OVERVIEW.md` — Goals, prizes, deadlines, scoring
- `docs/02_GAME_RULES.md` — Board layout, mechanics, turn order, combat
- `docs/03_AGENT_INTERFACE.md` — Agent function, observation schema, examples
- `docs/04_SUBMISSION_GUIDE.md` — CLI setup, submission formats, workflow
- `docs/05_DATA_STRUCTURES.md` — Named tuples, helper functions
- `docs/06_DATA_UTILITIES.md` — Analysis and logging utilities
- `docs/13_IMPROVEMENT_HYPOTHESIS_BACKLOG.md` — Research ideas and backlog

For operation tracking:
- `docs/operations/BENCHMARK_LOG.md` — Submission and gate results log

For historical research:
- `docs/archive/v30/` — v30 planning and research artifacts

## External Replay Data for Behavioral Cloning

Useful Kaggle discussion/data source for offline learning workflows:
- Main dataset thread: https://www.kaggle.com/competitions/orbit-wars/discussion/697413
- Update/fix thread: https://www.kaggle.com/competitions/orbit-wars/discussion/701894

What it provides:
- Daily replay datasets: `bovard/orbit-wars-top10-episodes-YYYY-MM-DD`
- `episodes.tar.gz` replay JSONs plus `manifest.csv` metadata

Usage guidance:
- Use as a replay corpus for behavioral cloning, imitation learning, and opponent profiling.
- Validate dataset completeness (`manifest.csv` vs files in `episodes.tar.gz`) before training, especially for early-date snapshots.

### Final-week behavioral cloning blueprint (forum signal)

When time is limited, prefer a **per-planet supervised hybrid** over large end-to-end architectures:
- Build training rows from each owned planet's decision point (not full-board monolith states).
- Rebalance no-op skew: keep all launch frames, keep only a small sample of hold frames (~10%).
- Use compact features: local planet state, distance-to-sun, and top-k neighbor context (distance, ETA, owner).
- Train a small dual-head MLP:
  - Launch gate: binary hold/fire
  - Target head: categorical target over top-k candidates
- Keep execution hybrid: learned policy predicts intent; `orbit_lite` remains responsible for intercept angle, ship sizing, and safety constraints.
## Commit Message Convention

When committing agent changes, include a concise hypothesis in the message:

```
v34: Early rush logic refinement

- Lowered EARLY_RUSH_TURN_LIMIT from 32 to 30
- Increased aggressive send ratio in 2P by 0.05
- Hypothesis: Earlier aggression reduces comet race delays
- Test: 24 episodes vs control_producer.py baseline
```

Include:
1. **Version label** (e.g., `v34:`)
2. **What changed** (1–3 lines)
3. **Hypothesis** (brief prediction of impact)
4. **Test method** (gate script, opponent, episodes)

This helps track which experiments led to improvements and why.

## Common Patterns

### Adding a New Configuration Parameter

1. Add to the configuration section at top of `agent.py` (near line ~30–50)
2. Document the purpose inline (see `COMET_SPAWN_BOOST_TURNS` for example)
3. Create a `v{N}_candidate_<feature>.py` copy to test in isolation
4. Run the candidate gate to measure impact
5. If positive, merge into main `agent.py` and increment version

### Fixing a Bug

1. Isolate in `test_agent.py` with a failing test case
2. Fix the logic in `agent.py`
3. Re-run `test_agent.py` to verify the fix
4. Commit with "fix:" prefix and reference the test

### Testing a Hypothesis About Game Mechanics

1. Create a minimal reproduction in `test_agent.py`
2. Run control gate to ensure baseline stability
3. Modify `agent.py` and test candidate gate
4. Document findings in `docs/13_IMPROVEMENT_HYPOTHESIS_BACKLOG.md`

## Board and Fleet Mechanics Reference

- **Board size:** 100×100, sun at (50, 50), sun radius 10.0
- **Sun safety margin:** 1.5 units
- **Max fleet speed:** 6.0 units/turn
- **Orbital mechanics:** Angular velocity 0.03 rad/turn per planet
- **Comet properties:** Radius ~1.0, high production, ~100+ turn lifespan
- **Rotation limit:** 50.0 degrees
- **Total game length:** 500 turns

## Performance Tips

1. **Avoid unnecessary fleets** — Each ungarrisoned planet is vulnerable. Keep home planets defended.
2. **Plan comet interception early** — Pre-position fleets 3 turns before spawn.
3. **Monitor overage time** — Check `observation['remainingOverageTime']` to avoid timeouts.
4. **Predict orbital arrival** — Use horizon-based route search (60–110 turns) to estimate intercepts.
5. **Contested neutrals** — Prioritize planets with 2+ turns of safety over empty ones in early game.

## When to Modify `.github/copilot-instructions.md`

Update this file when:
- A new macro pattern emerges (configuration parameter, testing workflow, etc.)
- Game mechanics understanding deepens or changes
- Version numbering scheme evolves
- New documentation is added or moved
- A recurring development pattern or anti-pattern appears

Do **not** add:
- One-off bug fixes or local tweaks
- Exhaustive lists of all agent parameters (keep those inline in code)
- Generic Python best practices
- Explanations of why certain approaches don't work (focus on what does)

## Latest High-Signal Learnings (2026-06-20)

### 1) Treat ROI failures as score-quality problems, not threshold problems

Deep planner diagnostics on v36-derived candidates showed the dominant rejection mode is `below_roi` with mostly **negative** candidate scores. In this state, lowering `roi_threshold` (e.g., 1.5→1.2) rarely helps because candidates are far below any practical threshold.

**Guideline:** when no-op/low-action behavior appears, instrument planner gates first. If best candidate scores are mostly <= 0, work on score construction / risk modeling / target quality, not threshold tuning.

### 2) Full mixed-pool tournament overrules pairwise wins

Some candidates reached parity in head-to-head vs v36/v37 but dropped back to rank-5 tier in the 10-agent mixed tournament.

**Guideline:** use H2H only as a quick directional filter; promotion decisions must rely on full 10-agent tournament outcomes.

### 3) Reinforcement-risk tuning has a narrow viable band

Reducing `reinforce_size_beta` early can improve passivity symptoms, but aggressive reductions (or combinations with extra permissive knobs) did not produce top-tier tournament gains and degraded live calibration signal.

**Guideline:** keep reinforce-beta experiments conservative and time-bounded; avoid stacking multiple permissive changes before mixed-pool validation.

### 4) Submission bundle rule for wrapper candidates

Wrapper candidates that import another local module will fail Kaggle submission unless all imported files are included.

**Guideline:** for wrapper-based submissions, bundle:
- `main.py` (submission entry point)
- `orbit_lite/`
- every local Python module imported by `main.py` (e.g., `v36_candidate_min_ships.py`)

### 5) Preferred next-step strategy after v53/v59 cycle

Given repeated scalar-ablation plateaus, prioritize **structural planner changes**:
- improve target/score quality,
- reduce false-negative candidate scoring in early game,
- and validate through full mixed-pool tournament before live submission.

