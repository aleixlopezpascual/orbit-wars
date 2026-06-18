"""Local head-to-head validation harness."""
import argparse
import importlib.util
import json
import math
import random
import sys
import time
import traceback
from pathlib import Path
from kaggle_environments import make


def load_agent(path, suffix=""):
    name = f"agent_{suffix}_{random.random()}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # required for @dataclass to resolve cls.__module__
    spec.loader.exec_module(mod)
    return mod.agent


def final_scores(state):
    obs = state[-1][0].observation
    n = len(state[-1])
    scores = [0] * n
    for p in obs.get("planets", []):
        if p[1] != -1:
            scores[p[1]] += p[5]
    for f in obs.get("fleets", []):
        scores[f[1]] += f[6]
    return scores


def step_metrics(step_state):
    obs = step_state[0].observation
    n = len(step_state)
    ships = [0] * n
    planets = [0] * n
    production = [0] * n
    fleet_ships = [0] * n

    for p in obs.get("planets", []):
        owner = p[1]
        if 0 <= owner < n:
            ships[owner] += p[5]
            planets[owner] += 1
            production[owner] += p[6]

    for f in obs.get("fleets", []):
        owner = f[1]
        if 0 <= owner < n:
            ships[owner] += f[6]
            fleet_ships[owner] += f[6]

    return {
        "turn": int(obs.get("step", 0) or 0),
        "ships": ships,
        "planets": planets,
        "production": production,
        "fleet_ships": fleet_ships,
        "scores": ships[:],
    }


def timeline_metrics(state):
    return [step_metrics(step_state) for step_state in state]


def _sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _lead_changes(diff_series):
    prev = None
    changes = 0
    for value in diff_series:
        sign = _sign(value)
        if sign == 0:
            continue
        if prev is not None and sign != prev:
            changes += 1
        prev = sign
    return changes


def _first_nonzero_turn(turns, diff_series):
    for turn, value in zip(turns, diff_series):
        if value != 0:
            return turn
    return None


def _persistent_lead_turn(turns, diff_series):
    signs = [_sign(value) for value in diff_series]
    for idx, sign in enumerate(signs):
        if sign == 0:
            continue
        tail = [value for value in signs[idx:] if value != 0]
        if tail and all(value == sign for value in tail):
            return turns[idx]
    return None


def summarize_timeline(timeline, challenger_seat, baseline_seat):
    turns = [entry["turn"] for entry in timeline]
    score_diff = [entry["scores"][challenger_seat] - entry["scores"][baseline_seat] for entry in timeline]
    ship_diff = [entry["ships"][challenger_seat] - entry["ships"][baseline_seat] for entry in timeline]
    planet_diff = [entry["planets"][challenger_seat] - entry["planets"][baseline_seat] for entry in timeline]
    prod_diff = [entry["production"][challenger_seat] - entry["production"][baseline_seat] for entry in timeline]

    return {
        "score_lead_changes": _lead_changes(score_diff),
        "ship_lead_changes": _lead_changes(ship_diff),
        "planet_lead_changes": _lead_changes(planet_diff),
        "production_lead_changes": _lead_changes(prod_diff),
        "first_score_lead_turn": _first_nonzero_turn(turns, score_diff),
        "persistent_score_lead_turn": _persistent_lead_turn(turns, score_diff),
        "peak_ship_advantage": max(ship_diff) if ship_diff else 0,
        "peak_ship_disadvantage": min(ship_diff) if ship_diff else 0,
        "peak_planet_advantage": max(planet_diff) if planet_diff else 0,
        "peak_planet_disadvantage": min(planet_diff) if planet_diff else 0,
        "final_ship_diff": ship_diff[-1] if ship_diff else 0,
        "final_planet_diff": planet_diff[-1] if planet_diff else 0,
        "final_production_diff": prod_diff[-1] if prod_diff else 0,
    }


def wilson_ci(wins, total, z=1.96):
    if total == 0:
        return 0.0, 100.0
    p = wins / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0, (centre - margin)) * 100, min(1, (centre + margin)) * 100


def write_json(path, payload):
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n")


def h2h(challenger_path, baseline_path, n_games, steps, label, seed_base=42, act_timeout=10, json_out=None):
    print(f"\n=== {label}: {n_games} games × {steps} steps ===", flush=True)
    ch_w = bl_w = ties = 0
    log = []
    for g in range(n_games):
        random.seed(seed_base + g)
        env = make(
            "orbit_wars",
            configuration={"episodeSteps": steps, "actTimeout": act_timeout, "seed": seed_base + g},
            debug=False,
        )
        A = load_agent(challenger_path, f"ch_{g}")
        B = load_agent(baseline_path, f"bl_{g}")
        # Alternate seats
        if g % 2 == 0:
            agents = [A, B]
            ch_seat = 0
        else:
            agents = [B, A]
            ch_seat = 1
        t0 = time.time()
        try:
            state = env.run(agents)
        except Exception as exc:
            print(f"  g{g+1:2d}: ERROR {exc}", flush=True)
            traceback.print_exc()
            continue
        dt = time.time() - t0
        rewards = [s.reward for s in state[-1]]
        scores = final_scores(state)
        timeline = timeline_metrics(state)
        if rewards[0] == rewards[1]:
            ties += 1
            tag = "TIE"
        elif rewards[ch_seat] > rewards[1 - ch_seat]:
            ch_w += 1
            tag = "ch W"
        else:
            bl_w += 1
            tag = "bl W"
        summary = summarize_timeline(timeline, ch_seat, 1 - ch_seat)
        log.append(
            {
                "g": g + 1,
                "ch_seat": ch_seat,
                "result": tag,
                "scores": scores,
                "time_s": dt,
                "timeline_summary": summary,
                "timeline": timeline,
            }
        )
        print(
            "  "
            f"g{g+1:2d}: {tag:5s}  scores={scores}  seat={ch_seat}  t={dt:.1f}s"
            f"  scoreL={summary['score_lead_changes']}  shipL={summary['ship_lead_changes']}"
            f"  lock={summary['persistent_score_lead_turn']}",
            flush=True,
        )

    decisive = ch_w + bl_w
    wr = ch_w / decisive * 100 if decisive else 50.0
    lo, hi = wilson_ci(ch_w, decisive)
    print(
        f"\n  RESULT: {ch_w}W/{bl_w}L/{ties}T  winrate {wr:.1f}%  CI95 [{lo:.0f}–{hi:.0f}]",
        flush=True,
    )
    result = {
        "label": label,
        "challenger_path": challenger_path,
        "baseline_path": baseline_path,
        "n_games": n_games,
        "steps": steps,
        "seed_base": seed_base,
        "act_timeout": act_timeout,
        "wins": ch_w,
        "losses": bl_w,
        "ties": ties,
        "wr": wr,
        "ci": (lo, hi),
        "log": log,
    }
    if json_out:
        write_json(json_out, result)
        print(f"  Telemetry artifact: {json_out}", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ch", default="main.py", help="challenger agent path")
    parser.add_argument("--bl", default="v26.py", help="baseline agent path")
    parser.add_argument("-n", type=int, default=8)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--label", default="ch_vs_bl")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--act-timeout", type=int, default=10)
    parser.add_argument("--json-out", help="Optional path to save per-game telemetry JSON.")
    args = parser.parse_args()

    h2h(
        args.ch,
        args.bl,
        args.n,
        args.steps,
        args.label,
        seed_base=args.seed,
        act_timeout=args.act_timeout,
        json_out=args.json_out,
    )
