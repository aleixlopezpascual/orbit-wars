# 14) Planet Wars Reference Repo Findings

**Reference repo:** `https://github.com/eonarheim/planet-wars-competition`  
**Purpose:** extract transferable ideas for Orbit Wars without copying code

---

## Executive take

This repo is **not** a strong strategy reference. Its bundled agents are trivial and far weaker than our current `agent.py`.

It is still valuable in three ways:

1. As an **engine semantics oracle** for arrival/combat resolution.
2. As a model for **small, deterministic engine regression tests**.
3. As a reminder to expose **score-over-time telemetry** during validation, not just final outcomes.

The highest-value takeaway is to treat this repo as a **simulation correctness reference**, not a source of gameplay heuristics.

---

## What the repo actually contains

### Useful parts

- `PlanetWars/Server/Game.cs` - authoritative turn phases, movement legality, combat resolution, score tracking
- `PlanetWars.Tests/GameTest.cs` - compact rule tests for colonization, multi-force combat, ETA timing, illegal moves
- `PlanetWars.Shared/StatusResult.cs` - clean status payload with turn and score history
- `readme.md` - short textual description of turn order and combat semantics

### Low-value parts for us

- `PlanetWars/DemoAgent/Agent.cs`
- `CSharpAgent/Agent.cs`

Those agents simply pick a non-owned planet and send roughly half their ships. They do not contain useful opponent modeling, forward planning, comet handling, or search logic.

---

## Priority improvement ideas for Orbit Wars

| Priority | Idea | Why it matters | Adaptation cost | Risk |
|---|---|---|---|---|
| P0 | Audit and correct combat semantics in our forward simulator | A simulator bug can poison reserve estimates, defense timing, and target scoring everywhere | Low-Medium | Retuning after the fix |
| P1 | Add deterministic engine regression tests | Protects combat, ETA, and capture logic from future refactors | Low | Minimal |
| P2 | Add score-over-time telemetry to validation output | Helps distinguish better openings from lucky finishes | Low | Small logging overhead |
| P3 | Build curated tactical scenario fixtures | Faster ablation for comet races, contested neutrals, and sun-risk shots | Medium | Overfitting to hand-picked positions |
| P4 | Gradually separate simulator/policy/entrypoint responsibilities | Makes future ablations safer and easier to verify | Medium-High | Refactor churn during competition |

---

## P0: simulator correctness is the real opportunity

The strongest insight from this repo is the way it resolves arrivals:

1. Start with the current planet owner and garrison as one combatant.
2. Group all arriving fleets by owner.
3. Resolve the contest by comparing total force per owner.
4. Winner keeps `largest - second_largest`; ties can zero the planet.

That matters because our agent depends heavily on projected timelines for:

- `keep_needed`
- `min_owned`
- reserve calculations
- reaction-time logic
- multi-mission planning

If combat semantics are wrong in the simulator, every higher-level heuristic can be miscalibrated.

### Concrete implication for our repo

Before tuning more weights, verify that `resolve_arrival_event` and downstream timeline generation match actual engine behavior in:

- contested neutral captures
- three-way arrivals on the same turn
- simultaneous reinforcement plus enemy arrival
- exact-tie outcomes

---

## P1: copy the testing pattern, not the agent logic

The reference repo's best engineering pattern is its small scenario-based engine tests.

### Tests worth adding here

1. **Contested neutral test** - two players arrive at the same neutral on the same turn.
2. **Three-force arrival test** - owner garrison plus two enemy arrivals.
3. **ETA test** - confirm travel timing against our speed model.
4. **Illegal/degenerate action test** - zero ships, impossible source, or invalid routing assumptions.
5. **Tie test** - confirm whether a tied battle leaves zero ships and what ownership becomes.

### Why this is higher leverage than another heuristic tweak

A single simulator bug can make:

- defensive margins too small
- comet races look safer than they are
- gang-up timing appear profitable when it is not
- recapture logic overestimate future holdings

---

## P2: extend validation output beyond final score

The reference server keeps turn-by-turn score history. We should mirror that idea in our tooling.

### Recommended additions to `run_validation.py`

- per-turn total ships
- per-turn planet count
- per-turn production count if easy to extract
- lead changes
- timing of decisive swings

### Why

This lets us tell the difference between:

- stronger early expansion that later collapses
- stable midgame improvements
- late-game comet-dependent swings
- seat-sensitive opening behavior

Final score alone hides those patterns.

---

## P3: add a tactical scenario suite

Our current benchmark gates are stronger than anything in the reference repo, but full-game evaluation is still slow for certain questions.

Use a small scenario suite for fast checks around:

- comet spawn interception
- comet expiry evacuation
- sun-crossing route rejection
- rotating target arrival drift
- multi-source synchronized capture
- weak-planet finishing attacks
- 4-player kingmaker / third-party cleanup situations

This should supplement, not replace, the control and ablation gates.

---

## P4: treat architecture cleanup as a safety multiplier

The C# repo keeps transport/game-loop code separate from agent decision logic. We do not need that exact structure, but the principle is useful.

A future cleanup path could split our current `agent.py` into logical layers:

- **entrypoint** - Kaggle-facing `agent(observation)`
- **world model** - parsed state, caches, derived facts
- **simulator** - travel and arrival prediction
- **policy** - mission generation and ranking
- **instrumentation** - optional debug and telemetry hooks

This is not the first improvement to ship, but it would lower risk for late-stage experimentation.

---

## What not to copy

Do **not** spend time porting the reference repo's agent heuristics. They are far below our current baseline and omit Orbit Wars-specific essentials such as:

- moving targets on orbital paths
- sun-aware routing
- comet lifecycle handling
- distance-aware fleet sizing
- multi-phase 2P/4P policy adaptation

---

## Recommended follow-up order

1. Verify and, if needed, fix simulator combat semantics.
2. Add golden regression tests for arrivals and ETAs.
3. Add score-curve telemetry to validation artifacts.
4. Add a small scenario fixture suite for fast tactical checks.
5. Consider structural refactoring only after the simulator is trusted.

---

## Bottom line

`eonarheim/planet-wars-competition` is useful because it sharpens our **simulation discipline**.

Its main value is not "here is a better bot." It is "here is a compact engine and test style that can help us trust our own world model more."
