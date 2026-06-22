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
