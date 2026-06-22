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


def find_seat_by_name(replay: dict, name: str) -> int | None:
    """Seat index whose TeamName matches `name`, else None."""
    names = replay.get("info", {}).get("TeamNames", []) or []
    for seat, team in enumerate(names):
        if team == name:
            return seat
    return None


def episode_report(replay: dict, our_name: str) -> dict:
    """Per-episode summary from our seat's perspective.

    Returns our seat, win/loss (via top-level rewards), focus-fire counts for us
    and the winner, player count, and per-seat focus-fire events.
    """
    states = iter_board_states(replay)
    launches = detect_launches(states)
    rewards = replay.get("rewards", []) or []
    seats = list(range(len(rewards))) if rewards else sorted(
        {l["owner"] for l in launches if l["owner"] >= 0}
    )
    ff = {s: count_focus_fire_events(launches, s) for s in seats}
    our_seat = find_seat_by_name(replay, our_name)
    winner_seat = None
    if rewards:
        max_r = max(rewards)
        winners = [s for s, r in enumerate(rewards) if r == max_r]
        winner_seat = winners[0] if len(winners) == 1 else None
    our_reward = rewards[our_seat] if (our_seat is not None and our_seat < len(rewards)) else None
    our_won = None
    if our_reward is not None and rewards:
        our_won = our_reward == max(rewards) and len([r for r in rewards if r == max(rewards)]) == 1
    return {
        "player_count": len(seats),
        "our_seat": our_seat,
        "our_reward": our_reward,
        "our_won": our_won,
        "our_focus_fire": ff.get(our_seat, 0) if our_seat is not None else None,
        "our_launches": sum(1 for l in launches if l["owner"] == our_seat),
        "winner_seat": winner_seat,
        "winner_focus_fire": ff.get(winner_seat, 0) if winner_seat is not None else None,
        "focus_fire_by_seat": ff,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Orbit Wars replay JSON files.")
    ap.add_argument("paths", nargs="+", help="Replay JSON file(s).")
    ap.add_argument("--our-name", default=None,
                    help="Team name to treat as 'us' for win/loss + focus-fire gap aggregation.")
    args = ap.parse_args()
    if args.our_name:
        reports = []
        for path in args.paths:
            replay = json.loads(Path(path).read_text())
            reports.append((path, episode_report(replay, args.our_name)))
        losses = [r for _, r in reports if r["our_won"] is False]
        wins = [r for _, r in reports if r["our_won"] is True]
        for path, r in reports:
            tag = "WIN " if r["our_won"] else ("LOSS" if r["our_won"] is False else "??? ")
            print(f"{tag} {Path(path).name} | {r['player_count']}P | "
                  f"our_ff={r['our_focus_fire']} winner_ff={r['winner_focus_fire']} "
                  f"our_launches={r['our_launches']}")
        def avg(vals):
            vals = [v for v in vals if v is not None]
            return round(sum(vals) / len(vals), 2) if vals else None
        print("\n=== AGGREGATE ===")
        print(f"games: {len(reports)} | wins: {len(wins)} | losses: {len(losses)}")
        print(f"avg our focus-fire (losses): {avg([r['our_focus_fire'] for r in losses])}")
        print(f"avg winner focus-fire (losses): {avg([r['winner_focus_fire'] for r in losses])}")
        print(f"avg our focus-fire (wins): {avg([r['our_focus_fire'] for r in wins])}")
        return 0
    for path in args.paths:
        replay = json.loads(Path(path).read_text())
        print(f"== {path} ==")
        print(json.dumps(summarize_episode(replay), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
