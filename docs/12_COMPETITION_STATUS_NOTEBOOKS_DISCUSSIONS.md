# 12) Competition Status: Top Notebooks and Discussions

## Snapshot context

This page summarizes a live Kaggle snapshot collected on **2026-05-30** (leaderboard, notebooks, and discussions).

- Competition: https://www.kaggle.com/competitions/orbit-wars
- Snapshot team count: ~3491 teams
- Snapshot top score: ~1727
- Snapshot team position discussed in this repo context: 1344/3492 with score 743.0

This is a time-slice and will drift as the competition evolves.

---

## 1. Current competitive reality

### Score ladder pressure (snapshot)

- **Current discussed score:** 743.0
- **Top 1000 threshold:** 821.8
- **Top 500 threshold:** 938.2
- **Top 250 threshold:** 1056.1
- **Top 100 threshold:** 1155.9
- **Top 10 threshold:** 1515.2

**Interpretation:** the short-term objective is consistent movement into >=822 territory first; top-100/top-10 requires structural gains, not minor tweaks.

---

## 2. Top notebook patterns (what people are trying)

### High-vote notebook leaders (snapshot)

| Rank | Notebook | Votes | Theme |
|---:|---|---:|---|
| 1 | Getting Started | 1109 | official/starter onboarding |
| 2 | Orbit Wars: Structured Baseline | 235 | rule-based structured baseline |
| 3 | Orbit Wars - Reinforcement Learning Tutorial | 230 | RL training/inference workflow |
| 4 | Agent OW-Proto (Passed 1,000) | 211 | heuristic progression notebook |
| 5 | Orbit Wars 2026 - Starter | 170 | practical baseline implementation |
| 6 | Orbit (Star) Wars \| LB max 1224 | 145 | tuned heuristic/simulation variant |
| 7 | LB-958 Reinforce | 138 | RL/heuristic blend experimentation |
| 8 | hellburner | 121 | strong heuristic lineage |
| 9 | orbitbotnext | 97 | iterative heuristic tuning |
| 10 | train submit v4 ml validator | 80 | hybrid rule-based + ML validator |

### What this says about the meta

1. **Heuristic + simulation/search remains dominant** in publicly successful and widely reused notebooks.
2. **Hybridization is growing** (rule-based policy plus learned validator/value components).
3. **RL is active but not yet the default winning path** in reproducible public pipelines.
4. **Tooling notebooks are influential** (visualizers, replay tools, tournament runners).

---

## 3. Top discussion patterns (what people learned publicly)

### High-signal discussion threads

| Topic | Votes | Why it matters |
|---|---:|---|
| RL lessons so far (ID 697725) | 78 | documents RL instability/cost and practical constraints |
| Local visualizer sharing (ID 694127) | 78 | tooling is a large multiplier for iteration speed |
| 90-degree symmetry proposal/fix (ID 694310) | 73 | environment fairness update changed 4P assumptions |
| Baseline method thread (ID 692800) | 39 | recurring baseline design references |
| Runtime environment specs (ID 700191) | 34 | local-vs-Kaggle runtime mismatches affect outcomes |
| Target evaluation considerations (ID 699003) | 31 | practical value scoring guidance |
| Validation episode failed (ID 692938) | 13 | common submission packaging/runtime failure modes |
| Observation inconsistency report (ID 692695) | 21 | highlights environment-version drift risk |

### Direct links

- https://www.kaggle.com/competitions/orbit-wars/discussion/697725
- https://www.kaggle.com/competitions/orbit-wars/discussion/694127
- https://www.kaggle.com/competitions/orbit-wars/discussion/694310
- https://www.kaggle.com/competitions/orbit-wars/discussion/700191
- https://www.kaggle.com/competitions/orbit-wars/discussion/699003
- https://www.kaggle.com/competitions/orbit-wars/discussion/692938
- https://www.kaggle.com/competitions/orbit-wars/discussion/692695

---

## 4. What appears to work vs. what did not

### What works repeatedly

1. Strong deterministic heuristics with ETA-aware targeting.
2. Lightweight forward simulation and mission scoring.
3. Clear runtime-aware pruning under strict action-time budgets.
4. Replay-driven evaluation loops and local tournament tooling.

### What repeatedly failed or underperformed

1. Uncontrolled RL changes (many architecture changes at once).
2. Assuming local runtime behavior is identical to Kaggle runtime.
3. Complex danger/value models without ablation discipline.
4. Packaging/path mistakes that trigger validation failures.
5. Drawing conclusions from stale pre-fix environment assumptions.

---

## 5. Documentation-only implications

For this documentation phase, the main output is decision clarity:

1. Baseline lineage should be explicitly documented as `hellburner-x2-main.py` -> `control_hbx2.py`.
2. Future implementation should be hypothesis-driven and benchmark-gated.
3. Historical docs should be read as context, while live snapshot docs should drive tactical decisions.
