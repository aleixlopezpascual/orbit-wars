# Final-Day Medal Push Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Over the final competition day, defend the bronze position and attempt silver by diagnosing the SMW-987 collapse and the v43 loss pattern, then shipping the highest-EV evidence-backed challenger while keeping v43 as a protected floor.

**Architecture:** Four gated phases — (0) establish standing & slot budget, (1) two time-boxed forensics tracks producing evidence verdicts, decision gate, (2) build + locally gate the selected challenger, (3) submit with slot discipline. The only new code component is a tested replay-analysis script; everything else is operational use of existing harnesses.

**Tech Stack:** Python 3.11, `torch` (existing agent runtime), Kaggle CLI, `pytest`, existing repo harnesses (`run_validation.py`, `run_tournament.py`, `scripts/fetch_kaggle_match_artifacts.py`).

## Global Constraints

- Final deadline: **2026-06-23 23:59 UTC**. Treat Phase 1 as time-boxed (~2h total).
- Submissions: **5/day, latest 2 tracked, best-shown wins.** Never let v43 fall out of the tracked pair unless a challenger has passed the local gate.
- Promotion gate (mandatory before any submit): `python run_tournament.py --pool-profile kaggle_latest10 --max-agents 10 --steps 500`. A challenger must beat v43 on **both** total points **and** 1st-place rate. `mixed20` is stress-only.
- Protected floor: `v43_candidate_wavecap5_beta24.py`.
- One hypothesis family per candidate file; each candidate declares its parent.
- Planets in any state are `[id, owner, x, y, radius, ships, production]`; fleets are `[id, owner, x, y, angle, from_planet_id, ships]`. `owner` is `-1` for neutral, `0..3` for players. Planets/fleets lists are global ground truth, identical across all seats' observations.
- Run all commands from the worktree root. Tests follow the repo's root-level `test_*.py` convention (cf. `test_agent.py`).

---

### Task 1: Phase 0 — Baseline & slot map

**Files:**
- Create: `docs/operations/FINAL_DAY_STANDING.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the two Kaggle submission IDs needed downstream — `SMW987_SUBMISSION_ID` and `V43_SUBMISSION_ID` — plus current standing, recorded in `docs/operations/FINAL_DAY_STANDING.md`.

This is an operational task (no test cycle): gather ground truth before spending effort or slots.

- [ ] **Step 1: Confirm Kaggle CLI auth works**

Run: `kaggle competitions submissions orbit-wars`
Expected: a table of your submissions with IDs, scores, and dates. If it errors on auth, fix `~/.kaggle/kaggle.json` before continuing.

- [ ] **Step 2: Record standing and the two submission IDs**

From the submissions table, identify:
- The submission whose score is ~987 (the SMW public-notebook run) → `SMW987_SUBMISSION_ID`.
- The submission corresponding to v43 (the current bronze anchor) → `V43_SUBMISSION_ID`.

Write `docs/operations/FINAL_DAY_STANDING.md` containing:
```markdown
# Final Day Standing (2026-06-22)

- v43 submission id: <V43_SUBMISSION_ID>, score: <score>, current rank: <rank>
- SMW-987 submission id: <SMW987_SUBMISSION_ID>, score: 987
- Silver cutoff (approx, today): <score> / rank <n>  (note: may move on last day)
- Bronze cutoff (approx, today): <score> / rank <n>
- Gap v43 -> silver: <delta>
- Submission slots used today: <k>/5
- Is v43 currently in the latest-2 tracked pair? <yes/no>
```

- [ ] **Step 3: Commit**

```bash
git add docs/operations/FINAL_DAY_STANDING.md
git commit -m "docs: phase 0 final-day standing and slot map"
```

---

### Task 2: Replay analyzer — core data model + focus-fire metric (TDD)

**Files:**
- Create: `scripts/analyze_replays.py`
- Test: `test_analyze_replays.py`

**Interfaces:**
- Consumes: nothing (operates on in-memory replay dicts and JSON files).
- Produces, for downstream tasks:
  - `iter_board_states(replay: dict) -> list[dict]` — returns per-step board states, each `{"planets": list[list], "fleets": list[list]}`.
  - `infer_fleet_target(fleet: list, planets: list[list]) -> int | None` — planet id the fleet is heading toward, or `None`.
  - `detect_launches(states: list[dict]) -> list[dict]` — each launch `{"turn": int, "owner": int, "from_planet_id": int, "target_planet_id": int | None, "ships": int}`.
  - `count_focus_fire_events(launches: list[dict], owner: int, window: int = 2, min_sources: int = 2) -> int` — number of multi-source coordinated strikes by `owner`.
  - `summarize_episode(replay: dict) -> dict` — per-owner `{owner: {"focus_fire_events": int, "launches": int, "final_planets": int}}`.

The board state lists are the documented global format; metric functions are pure and fully unit-testable on synthetic fixtures (no download needed). The replay container shape is confirmed against a real file in Task 3.

- [ ] **Step 1: Write the failing test**

Create `test_analyze_replays.py`:
```python
import math

import analyze_replays_helper as ar  # see Step 3 note on import path


def _planet(pid, owner, x, y, ships, prod=3, radius=2.0):
    return [pid, owner, x, y, radius, ships, prod]


def _fleet(fid, owner, x, y, angle, frm, ships):
    return [fid, owner, x, y, angle, frm, ships]


def test_iter_board_states_extracts_planets_and_fleets():
    replay = {
        "steps": [
            [{"observation": {"planets": [_planet(0, 0, 10, 50, 20)], "fleets": []}}],
            [{"observation": {"planets": [_planet(0, 0, 10, 50, 18)],
                              "fleets": [_fleet(5, 0, 12, 50, 0.0, 0, 7)]}}],
        ]
    }
    states = ar.iter_board_states(replay)
    assert len(states) == 2
    assert states[1]["fleets"][0][0] == 5


def test_infer_fleet_target_picks_planet_along_heading():
    # Fleet launched from planet 0 at (10,50) heading angle 0 (east) toward planet 1 at (90,50)
    planets = [_planet(0, 0, 10, 50, 5), _planet(1, -1, 90, 50, 3),
               _planet(2, -1, 10, 90, 3)]
    fleet = _fleet(5, 0, 11, 50, 0.0, 0, 4)
    assert ar.infer_fleet_target(fleet, planets) == 1


def test_detect_launches_flags_new_fleets_only():
    s0 = {"planets": [_planet(0, 0, 10, 50, 20), _planet(1, -1, 90, 50, 3)],
          "fleets": []}
    s1 = {"planets": [_planet(0, 0, 10, 50, 16), _planet(1, -1, 90, 50, 3)],
          "fleets": [_fleet(5, 0, 12, 50, 0.0, 0, 4)]}
    s2 = {"planets": [_planet(0, 0, 10, 50, 16), _planet(1, -1, 90, 50, 3)],
          "fleets": [_fleet(5, 0, 30, 50, 0.0, 0, 4)]}  # same fleet moved, not new
    launches = ar.detect_launches([s0, s1, s2])
    assert len(launches) == 1
    assert launches[0]["turn"] == 1
    assert launches[0]["owner"] == 0
    assert launches[0]["from_planet_id"] == 0
    assert launches[0]["target_planet_id"] == 1


def test_count_focus_fire_events_needs_two_distinct_sources_same_target():
    # Two launches by owner 0 from planets 0 and 2, both targeting planet 1, within window.
    launches = [
        {"turn": 5, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
        {"turn": 6, "owner": 0, "from_planet_id": 2, "target_planet_id": 1, "ships": 4},
        {"turn": 5, "owner": 1, "from_planet_id": 9, "target_planet_id": 7, "ships": 4},
    ]
    assert ar.count_focus_fire_events(launches, owner=0, window=2, min_sources=2) == 1
    assert ar.count_focus_fire_events(launches, owner=1, window=2, min_sources=2) == 0


def test_count_focus_fire_ignores_same_source_repeat():
    launches = [
        {"turn": 5, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
        {"turn": 6, "owner": 0, "from_planet_id": 0, "target_planet_id": 1, "ships": 4},
    ]
    assert ar.count_focus_fire_events(launches, owner=0, window=2, min_sources=2) == 0
```

Note: tests import `analyze_replays_helper`; we expose the logic in `scripts/analyze_replays.py` and add a thin root shim so the test imports cleanly (Step 3).

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest test_analyze_replays.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'analyze_replays_helper'`.

- [ ] **Step 3: Write the minimal implementation**

Create `scripts/analyze_replays.py`:
```python
#!/usr/bin/env python3
"""Parse Orbit Wars replay JSON and compute behavioral metrics.

Board state lists use the documented global format:
  planet = [id, owner, x, y, radius, ships, production]
  fleet  = [id, owner, x, y, angle, from_planet_id, ships]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

P_ID, P_OWNER, P_X, P_Y, P_R, P_SHIPS, P_PROD = range(7)
F_ID, F_OWNER, F_X, F_Y, F_ANGLE, F_FROM, F_SHIPS = range(7)


def iter_board_states(replay: dict) -> list[dict]:
    """Return per-step {"planets":..., "fleets":...} from a kaggle replay dict.

    Planets/fleets are global, so seat 0's observation is sufficient.
    """
    states = []
    for step in replay.get("steps", []):
        obs = step[0].get("observation", {}) if step else {}
        states.append({
            "planets": obs.get("planets", []) or [],
            "fleets": obs.get("fleets", []) or [],
        })
    return states


def infer_fleet_target(fleet: list, planets: list) -> int | None:
    """Planet id whose direction best matches the fleet heading (tie: nearest)."""
    fx, fy, ang = fleet[F_X], fleet[F_Y], fleet[F_ANGLE]
    hx, hy = math.cos(ang), math.sin(ang)
    best_id, best_key = None, None
    for p in planets:
        if p[P_ID] == fleet[F_FROM]:
            continue
        dx, dy = p[P_X] - fx, p[P_Y] - fy
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        align = (dx * hx + dy * hy) / dist  # cos of angle between heading and bearing
        if align <= 0:
            continue  # planet is behind the fleet
        key = (-align, dist)  # most-aligned first, nearest as tiebreak
        if best_key is None or key < best_key:
            best_key, best_id = key, p[P_ID]
    return best_id


def detect_launches(states: list[dict]) -> list[dict]:
    """A launch = a fleet id appearing at turn t that was absent at t-1."""
    launches = []
    seen: set = set()
    for turn, st in enumerate(states):
        for f in st["fleets"]:
            fid = f[F_ID]
            if fid in seen:
                continue
            seen.add(fid)
            if turn == 0:
                continue  # cannot attribute a launch turn for pre-existing fleets
            launches.append({
                "turn": turn,
                "owner": f[F_OWNER],
                "from_planet_id": f[F_FROM],
                "target_planet_id": infer_fleet_target(f, st["planets"]),
                "ships": f[F_SHIPS],
            })
    return launches


def count_focus_fire_events(launches: list[dict], owner: int,
                            window: int = 2, min_sources: int = 2) -> int:
    """Count coordinated strikes: >=min_sources distinct source planets by `owner`
    targeting the same planet within `window` turns of each other."""
    mine = [l for l in launches if l["owner"] == owner and l["target_planet_id"] is not None]
    by_target: dict[int, list[dict]] = {}
    for l in mine:
        by_target.setdefault(l["target_planet_id"], []).append(l)
    events = 0
    for target, group in by_target.items():
        group.sort(key=lambda l: l["turn"])
        used = [False] * len(group)
        for i, anchor in enumerate(group):
            if used[i]:
                continue
            sources = {anchor["from_planet_id"]}
            members = [i]
            for j in range(i + 1, len(group)):
                if used[j]:
                    continue
                if group[j]["turn"] - anchor["turn"] <= window:
                    sources.add(group[j]["from_planet_id"])
                    members.append(j)
            if len(sources) >= min_sources:
                events += 1
                for m in members:
                    used[m] = True
    return events


def summarize_episode(replay: dict) -> dict:
    states = iter_board_states(replay)
    launches = detect_launches(states)
    final = states[-1]["planets"] if states else []
    owners = set(l["owner"] for l in launches) | {p[P_OWNER] for p in final if p[P_OWNER] >= 0}
    summary = {}
    for owner in sorted(owners):
        summary[owner] = {
            "focus_fire_events": count_focus_fire_events(launches, owner),
            "launches": sum(1 for l in launches if l["owner"] == owner),
            "final_planets": sum(1 for p in final if p[P_OWNER] == owner),
        }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Orbit Wars replay JSON files.")
    ap.add_argument("paths", nargs="+", help="Replay JSON file(s).")
    args = ap.parse_args()
    for path in args.paths:
        replay = json.loads(Path(path).read_text())
        print(f"== {path} ==")
        print(json.dumps(summarize_episode(replay), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Then create the root shim `analyze_replays_helper.py` so tests and ad-hoc use import without packaging:
```python
from scripts.analyze_replays import (  # noqa: F401
    iter_board_states,
    infer_fleet_target,
    detect_launches,
    count_focus_fire_events,
    summarize_episode,
)
```
If `from scripts.analyze_replays import ...` fails because `scripts/` lacks `__init__.py`, create an empty `scripts/__init__.py`.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest test_analyze_replays.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/analyze_replays.py analyze_replays_helper.py test_analyze_replays.py
git add scripts/__init__.py 2>/dev/null || true
git commit -m "feat: replay analyzer with focus-fire detection (TDD)"
```

---

### Task 3: Validate analyzer against one real replay (schema confirmation)

**Files:**
- Modify (only if schema differs): `scripts/analyze_replays.py:iter_board_states`
- Create: `artifacts/kaggle/schema_probe/` (downloaded sample)

**Interfaces:**
- Consumes: `V43_SUBMISSION_ID` from Task 1, `iter_board_states` from Task 2.
- Produces: confirmation that `iter_board_states` matches the real Kaggle replay container, or a corrected version of it.

The synthetic tests assume the standard kaggle_environments shape (`replay["steps"][t][seat]["observation"]["planets"]`). This task confirms that against a real download and fixes the loader if orbit-wars differs.

- [ ] **Step 1: Download one real replay**

Run:
```bash
python scripts/fetch_kaggle_match_artifacts.py \
  --submission-id <V43_SUBMISSION_ID> --limit 1 \
  --download-replays --out-dir artifacts/kaggle/schema_probe
```
Expected: `artifacts/kaggle/schema_probe/replays/<episode>.json` exists.

- [ ] **Step 2: Probe the structure**

Run:
```bash
python -c "import json,glob; r=json.load(open(glob.glob('artifacts/kaggle/schema_probe/replays/*.json')[0])); print(list(r.keys())); print(type(r['steps']), len(r['steps'])); print(json.dumps(r['steps'][1][0].get('observation',{}).get('planets',[])[:2], indent=2))"
```
Expected: top-level keys include `steps`; `steps[1][0]["observation"]["planets"]` prints planet arrays of length 7.

- [ ] **Step 3: Run the analyzer end-to-end on the real file**

Run: `python scripts/analyze_replays.py artifacts/kaggle/schema_probe/replays/*.json`
Expected: a per-owner JSON summary with non-zero `launches` and `final_planets` for at least one owner.

- [ ] **Step 4: If the structure differs, fix `iter_board_states` and re-run tests**

If Step 2 shows planets nested elsewhere (e.g. `observation` only on the active seat, or a `state` wrapper), update `iter_board_states` to read the correct path, then:
Run: `python -m pytest test_analyze_replays.py -v` → expected PASS (synthetic shape still supported), and re-run Step 3 → expected non-zero summary.

- [ ] **Step 5: Commit (only if loader changed)**

```bash
git add scripts/analyze_replays.py
git commit -m "fix: align replay loader with real Kaggle episode schema"
```

---

### Task 4: Track F — SMW-987 autopsy

**Files:**
- Create: `docs/operations/SMW987_AUTOPSY.md`
- Create: `artifacts/kaggle/smw987/` (downloaded logs + replays)

**Interfaces:**
- Consumes: `SMW987_SUBMISSION_ID` from Task 1.
- Produces: a verdict token recorded in `SMW987_AUTOPSY.md` — one of `RUNTIME_BUG`, `4P_WEAKNESS`, `GENUINELY_WEAK_HERE`, `INCONCLUSIVE`.

Operational task. Goal: explain the ~300-point gap between SMW's reputation and its 987.

- [ ] **Step 1: Download logs (all 4 seats) and replays**

Run:
```bash
python scripts/fetch_kaggle_match_artifacts.py \
  --submission-id <SMW987_SUBMISSION_ID> --limit 15 \
  --download-replays --download-logs \
  --agent-index 0 --agent-index 1 --agent-index 2 --agent-index 3 \
  --best-effort --out-dir artifacts/kaggle/smw987
```
Expected: `artifacts/kaggle/smw987/logs/agent_*/` and `.../replays/` populated; `manifest.json` written.

- [ ] **Step 2: Scan logs for runtime failure signatures**

Run:
```bash
grep -riE "traceback|error|exception|timed? ?out|overage|exceeded|killed|invalid|failed" artifacts/kaggle/smw987/logs | sort | uniq -c | sort -rn | head -40
```
Expected: either clear error/timeout lines (→ runtime bug) or none (→ look at strategy/4P).

- [ ] **Step 3: Split performance by player count (2P vs 4P)**

Run: `python scripts/analyze_replays.py artifacts/kaggle/smw987/replays/*.json`
For each episode, note player count (number of distinct non-neutral owners in the final state) and whether the SMW seat finished 1st. Tally 2P vs 4P placement.

- [ ] **Step 4: Write the verdict**

Write `docs/operations/SMW987_AUTOPSY.md`:
```markdown
# SMW-987 Autopsy (2026-06-22)

- Submission id: <SMW987_SUBMISSION_ID>, episodes analyzed: <n>
- Log failure signatures: <none | list with counts>
- Per-turn time near limit: <yes/no, evidence>
- 2P placement: <wins/total>; 4P placement: <wins/total>
- VERDICT: <RUNTIME_BUG | 4P_WEAKNESS | GENUINELY_WEAK_HERE | INCONCLUSIVE>
- If RUNTIME_BUG: root cause = <timeout/import/version/...>; proposed fix = <...>
```

- [ ] **Step 5: Commit**

```bash
git add docs/operations/SMW987_AUTOPSY.md
git commit -m "docs: track F SMW-987 autopsy verdict"
```

---

### Task 5: Track L — v43 loss analysis

**Files:**
- Create: `docs/operations/V43_LOSS_ANALYSIS.md`
- Create: `artifacts/kaggle/v43_losses/`, `artifacts/kaggle/top_players/`

**Interfaces:**
- Consumes: `V43_SUBMISSION_ID` from Task 1; `summarize_episode` / `count_focus_fire_events` from Task 2.
- Produces: a verdict token in `V43_LOSS_ANALYSIS.md` — one of `GAP=FOCUS_FIRE`, `GAP=SNIPE/ELIM`, `GAP=OTHER`, `NO_CLEAR_GAP`.

Operational task. The quantified decision driver is focus-fire; snipe/elimination are assessed qualitatively from a few replays (the analyzer is extended only if focus-fire comes back negative — see Decision Gate).

- [ ] **Step 1: Download v43 episodes (replays, all seats' logs optional)**

Run:
```bash
python scripts/fetch_kaggle_match_artifacts.py \
  --submission-id <V43_SUBMISSION_ID> --limit 25 \
  --download-replays --best-effort --out-dir artifacts/kaggle/v43_losses
```

- [ ] **Step 2: Download a few top-player public episodes**

Identify 1-2 top leaderboard submission IDs (from the public leaderboard / episode browser). For each:
```bash
python scripts/fetch_kaggle_match_artifacts.py \
  --submission-id <TOP_SUBMISSION_ID> --limit 10 \
  --download-replays --best-effort --out-dir artifacts/kaggle/top_players
```

- [ ] **Step 3: Quantify the focus-fire gap**

Run:
```bash
python scripts/analyze_replays.py artifacts/kaggle/v43_losses/replays/*.json
python scripts/analyze_replays.py artifacts/kaggle/top_players/replays/*.json
```
For v43's losing episodes, identify v43's seat (the owner whose `final_planets` is low / who lost) and compare its `focus_fire_events` per game against the winner's. Compute the average `focus_fire_events` for winners vs for v43 across the losing set.

- [ ] **Step 4: Qualitative pass for snipe/elimination (3-5 replays)**

Open 3-5 of v43's clearest losses (inspect the replay JSON final states / step progression, or the Kaggle web replay viewer) and note whether winners repeatedly: (a) time arrivals to a neutral exactly as an enemy fleet contests it (snipe), or (b) pile onto a nearly-eliminated player. Record qualitative frequency.

- [ ] **Step 5: Write the verdict**

Write `docs/operations/V43_LOSS_ANALYSIS.md`:
```markdown
# v43 Loss Analysis (2026-06-22)

- v43 losing episodes analyzed: <n>; top-player episodes: <n>
- Avg focus_fire_events: winners <x.x> vs v43 <y.y>  (delta <...>)
- Snipe pattern frequency (qualitative): <low/med/high>
- Elimination pile-on frequency (qualitative): <low/med/high>
- VERDICT: <GAP=FOCUS_FIRE | GAP=SNIPE/ELIM | GAP=OTHER | NO_CLEAR_GAP>
- Evidence summary: <2-3 sentences>
```

- [ ] **Step 6: Commit**

```bash
git add docs/operations/V43_LOSS_ANALYSIS.md
git commit -m "docs: track L v43 loss analysis verdict"
```

---

### Task 6: Decision gate

**Files:**
- Modify: `docs/operations/FINAL_DAY_STANDING.md` (append decision)

**Interfaces:**
- Consumes: verdicts from `SMW987_AUTOPSY.md` (Task 4) and `V43_LOSS_ANALYSIS.md` (Task 5).
- Produces: the selected Phase-2 branch — one of `BRANCH=FIX_SMW`, `BRANCH=FOCUS_FIRE`, `BRANCH=MISSION_TYPE`, `BRANCH=FALLBACK`.

- [ ] **Step 1: Apply the deterministic priority**

Pick the first that fires:
1. Track F verdict = `RUNTIME_BUG` → `BRANCH=FIX_SMW` (do Task 7a). If time remains after, also pursue `BRANCH=FOCUS_FIRE` as a second challenger.
2. Track L verdict = `GAP=FOCUS_FIRE` → `BRANCH=FOCUS_FIRE` (do Task 7b).
3. Track L verdict = `GAP=SNIPE/ELIM` → `BRANCH=MISSION_TYPE` (do Task 7c).
4. Otherwise → `BRANCH=FALLBACK` (do Task 7c with the single most-supported narrow heuristic, accepting low EV).

- [ ] **Step 2: Record the decision and commit**

Append to `docs/operations/FINAL_DAY_STANDING.md`:
```markdown
## Decision Gate (2026-06-22)
- Track F: <verdict>; Track L: <verdict>
- SELECTED BRANCH: <BRANCH=...>
- Rationale: <1-2 sentences>
```
```bash
git add docs/operations/FINAL_DAY_STANDING.md
git commit -m "docs: decision gate -> selected phase 2 branch"
```

---

### Task 7a: Build branch FIX_SMW (only if selected)

**Files:**
- Create: `submission_smw_fixed/` bundle (or corrected `tournament_agents/kaggle_smw_v2.py`-derived `main.py`)

**Interfaces:**
- Consumes: root cause from `SMW987_AUTOPSY.md`.
- Produces: a gated, submittable SMW-derived bundle.

- [ ] **Step 1: Apply the identified fix**

Apply the exact root-cause fix from the autopsy. Common cases and concrete fixes:
- **Per-turn timeout** → in the agent's config, lower the cost knobs that drive runtime (e.g. `max_sources_per_lane`, `horizon`, `max_strike_sources`) and/or add an early time-budget guard that returns the best partial move set when `obs["remainingOverageTime"]` is low.
- **Import/version mismatch** → pin the exact import path the live env expects; remove any dependency not present in the Kaggle image.
- **Wrong/older notebook version** → replace with the current `tournament_agents/kaggle_smw_v2.py` content as the submission entrypoint.

- [ ] **Step 2: Local runtime + strength gate**

Run:
```bash
python run_validation.py --ch tournament_agents/kaggle_smw_v2.py --bl v43_candidate_wavecap5_beta24.py -n 24 --seed 42
python run_tournament.py --pool-profile kaggle_latest10 --max-agents 10 --steps 500
```
Expected: no per-turn timeouts in output; beats v43 on points **and** 1st-rate. If it still times out locally, the live timeout is reproduced — iterate Step 1.

- [ ] **Step 3: Validate bundle and commit**

Run: `python scripts/validate_submission_bundle.py <bundle path>`
Expected: PASS.
```bash
git add -A && git commit -m "feat: fixed SMW submission bundle (root cause: <...>)"
```

---

### Task 7b: Build branch FOCUS_FIRE (only if selected)

**Files:**
- Read: `tournament_agents/kaggle_smw_v2.py` (strike-package builder), `v36_candidate_min_ships.py` (our `ProducerLiteConfig` + `run_turn` mission generator)
- Create: `vNN_candidate_focus_fire.py` (declares parent `v43_candidate_wavecap5_beta24.py`)

**Interfaces:**
- Consumes: `GAP=FOCUS_FIRE` evidence; the v43 config pattern (thin `dataclasses.replace` over `v36` base).
- Produces: a gated focus-fire candidate.

Exact line edits depend on whether our `ProducerLiteConfig` already exposes a focus-fire flag; this is determined by reading the code first.

- [ ] **Step 1: Locate the config field and the mission generator**

Run:
```bash
grep -nE "focus_fire|max_strike_sources|track_fleets|enable_potential_risk" tournament_agents/kaggle_smw_v2.py | head
grep -nE "class ProducerLiteConfig|max_sources_per_lane|def run_turn|def .*candidate|single.source|strike" v36_candidate_min_ships.py | head -40
```
Decide: does our config already support multi-source strikes (a flag/field), or must the multi-source candidate generator be ported?

- [ ] **Step 2a: If a flag exists — create the candidate via config override**

Create `vNN_candidate_focus_fire.py` mirroring `v43_candidate_wavecap5_beta24.py`'s structure, adding the focus-fire fields to both `CONFIG_2P` and `CONFIG_4P` (e.g. `enable_focus_fire=True, max_strike_sources=4`), keeping `max_waves_per_turn=5, reinforce_size_beta=2.4`.

- [ ] **Step 2b: If no flag exists — port the multi-source generator**

In a copy of the base mission generator, add a candidate-generation pass that, for each target a single source cannot meet alone, selects up to `max_strike_sources` nearest owned planets whose combined arriving ships exceed the capture floor with synchronized arrival (match the SMW V2 logic read in Step 1), behind a new `enable_focus_fire` config flag defaulting to `True` in the candidate. Keep the existing single-source path as fallback.

- [ ] **Step 3: Sanity — agent loads and acts**

Run: `python -c "import vNN_candidate_focus_fire as a; print(hasattr(a, 'agent'))"`
Expected: `True`. (Rename `vNN` to the actual next version number.)

- [ ] **Step 4: Local strength + runtime gate**

Run:
```bash
python run_validation.py --ch vNN_candidate_focus_fire.py --bl v43_candidate_wavecap5_beta24.py -n 24 --seed 42
python run_tournament.py --pool-profile kaggle_latest10 --max-agents 10 --steps 500
```
Expected: n=24 does not regress vs v43; tournament beats v43 on points **and** 1st-rate; no per-turn timeout. If n=24 regresses, do not proceed — record the negative result and fall back to defending v43.

- [ ] **Step 5: Commit**

```bash
git add vNN_candidate_focus_fire.py
git commit -m "feat: vNN focus-fire multi-source candidate (parent v43)"
```

---

### Task 7c: Build branch MISSION_TYPE / FALLBACK (only if selected)

**Files:**
- Read: `v36_candidate_min_ships.py` (mission generation + scoring)
- Create: `vNN_candidate_<mission>.py` (declares parent `v43_candidate_wavecap5_beta24.py`)

**Interfaces:**
- Consumes: the single most-supported gap from `V43_LOSS_ANALYSIS.md` (snipe or elimination), or the single narrowest heuristic if fallback.
- Produces: a gated narrow-heuristic candidate.

- [ ] **Step 1: Implement exactly one mission/heuristic the data supports**

Mirror `v43_candidate_wavecap5_beta24.py`'s thin-config structure and add the one change:
- **Snipe (H-D3):** add a candidate that, when an enemy fleet is inbound to a neutral, generates a launch timed to arrive within +/-1 turn of the enemy arrival from the nearest owned planet that can meet the post-contest floor.
- **Elimination (H-D1):** add a `+bonus` to target score for attacking an opponent whose total ships < 20% of ours, gated to fire only when capture is affordable.
Implement only one.

- [ ] **Step 2: Local strength + runtime gate**

Run:
```bash
python run_validation.py --ch vNN_candidate_<mission>.py --bl v43_candidate_wavecap5_beta24.py -n 24 --seed 42
python run_tournament.py --pool-profile kaggle_latest10 --max-agents 10 --steps 500
```
Expected: n=24 no regression; tournament beats v43 on points **and** 1st-rate. If not, record negative and fall back to defending v43 (skip to Task 8 with no challenger).

- [ ] **Step 3: Commit**

```bash
git add vNN_candidate_<mission>.py
git commit -m "feat: vNN <mission> candidate (parent v43)"
```

---

### Task 8: Phase 3 — Submission with slot discipline

**Files:**
- Modify: `docs/operations/FINAL_DAY_STANDING.md` (append submission log)

**Interfaces:**
- Consumes: the gated challenger(s) from Task 7a/7b/7c; slot state from Task 1.
- Produces: the final tracked submission pair {v43 floor, best gated challenger}, recorded.

- [ ] **Step 1: Pre-submission gate (mandatory)**

Run: `bash scripts/pre_submission_tournament_gate.sh <challenger file>`
Expected: PASS (beats v43 on points + 1st-rate). If FAIL: do not submit; ensure v43 remains tracked and stop here (bronze defended).

- [ ] **Step 2: Protect the floor**

If v43 is NOT currently in the latest-2 tracked pair (per Task 1 / current state), submit v43 first so it stays tracked:
```bash
# package and submit v43 per scripts/validate_submission_bundle.py + kaggle submit flow
```
Verify in `kaggle competitions submissions orbit-wars` that v43 is present and tracked.

- [ ] **Step 3: Submit the gated challenger**

Submit the challenger that passed Step 1, respecting the 5/day budget recorded in Task 1. After submission, confirm the tracked pair is {v43, challenger}.

- [ ] **Step 4: Watch early validation/score**

Run: `kaggle competitions submissions orbit-wars`
Expected: challenger passes validation (not "Error"). If it errors, the floor (v43) protects bronze; investigate logs only if time remains.

- [ ] **Step 5: Append final submission log and commit**

Append to `docs/operations/FINAL_DAY_STANDING.md`:
```markdown
## Submission Log (2026-06-22/23)
- Submitted v43 (floor): <yes/no>, status <...>
- Submitted challenger <file>: status <...>, early score <...>
- Tracked pair at deadline: {v43, <challenger>}
```
```bash
git add docs/operations/FINAL_DAY_STANDING.md
git commit -m "docs: final submission log and tracked pair"
```

---

## Self-Review Notes

- **Spec coverage:** Phase 0 → Task 1; replay tooling → Tasks 2-3; Track F → Task 4; Track L → Task 5; decision gate → Task 6; Phase 2 branches (fix-SMW / focus-fire / mission-type / fallback) → Tasks 7a/7b/7c; Phase 3 slot discipline + rollback + gate → Task 8. All spec sections mapped.
- **Conditional honesty:** Phase 2 is genuinely branch-dependent; Tasks 7a/7b/7c are mutually exclusive and selected by Task 6. Exact line edits for the focus-fire port depend on reading the code (Task 7b Step 1) because our config may or may not already expose the flag — this is stated, not hidden behind a placeholder.
- **Scope guard:** snipe/elimination quantification is intentionally qualitative unless focus-fire fails the gate, keeping the analyzer focused (the decision driver is focus-fire).
- **Type consistency:** analyzer function names/signatures in the Interfaces blocks match the implementation in Task 2 Step 3 and the tests in Task 2 Step 1.
