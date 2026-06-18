"""
run_tournament.py — Full round-robin 4-player tournament evaluation.

10 agents compete in all C(10,4) = 210 unique 4-player combinations.
Scoring: 1st=3pts, 2nd=2pts, 3rd=1pt, 4th=0pt (ties split equally).

When fewer agents are available (e.g. torch not installed, Kaggle agents missing),
repeats are automatically increased so the total game count stays at 50+.

Usage:
    python3 run_tournament.py                          # test agent.py vs default pool
    python3 run_tournament.py --agent my_agent.py      # test a specific agent
    python3 run_tournament.py --games 50               # limit to 50 random games
    python3 run_tournament.py --workers 4              # parallel workers
    python3 run_tournament.py --dry-run                # print schedule only

Requirements: Python 3.11+, kaggle-environments>=1.29.0, torch>=2.0
Setup:        bash scripts/setup_tournament_env.sh
Agents:       bash scripts/download_kaggle_agents.sh

See --help for all options.
"""
import argparse
import importlib.util
import json
import math
import multiprocessing
import os
import random
import sys
import time
import traceback
from itertools import combinations
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Placement points
# ---------------------------------------------------------------------------
PLACEMENT_POINTS = [3, 2, 1, 0]  # 1st, 2nd, 3rd, 4th

# Minimum number of games we aim for in the tournament
MIN_GAMES_TARGET = 50


# ---------------------------------------------------------------------------
# Agent loading
# ---------------------------------------------------------------------------

def load_agent(path: str, suffix: str = ""):
    """Dynamically load an agent module and return its agent() callable."""
    name = f"_agent_{suffix}_{random.random()}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # required for dataclasses and relative imports
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        sys.modules.pop(name, None)
        raise RuntimeError(f"Failed to load agent from {path}: {exc}") from exc
    if not hasattr(mod, "agent"):
        sys.modules.pop(name, None)
        raise RuntimeError(f"No agent() function found in {path}")
    return mod.agent


def _can_load_agent(path: str) -> bool:
    """Quick check: try to load the agent module. Returns True if agent() is callable."""
    name = f"_probe_{random.random()}"
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod  # required for dataclasses introspection
        spec.loader.exec_module(mod)
        return hasattr(mod, "agent") and callable(mod.agent)
    except Exception:
        return False
    finally:
        sys.modules.pop(name, None)


def build_agent_pool(test_agent_path: str, root: str) -> list[dict]:
    """
    Returns the ordered list of validated agent descriptors:
      [{"name": str, "path": str}, ...]

    The test agent is always index 0. The pool is filled with:
      - locked local controls + version-history baselines
      - downloaded Kaggle agents from tournament_agents/
    up to 10 agents total. Agents that fail to load are skipped with a warning.
    """
    candidates = [
        # New high-ELO controls (always included — primary and secondary baselines)
        "control_producer.py",   # 1180.2 ELO — PRIMARY control
        "control_stronger.py",   # 981.3 ELO  — secondary control
        # Legacy baselines (kept for historical reference)
        "control_hbx2.py",
        "v29_baseline.py",
        "v28_baseline.py",
        "v27_baseline.py",
        "v26_baseline.py",
        # Kaggle downloads
        "tournament_agents/kaggle_i_the_orbit.py",
        "tournament_agents/kaggle_v2_gru.py",
        "tournament_agents/kaggle_v44_elo.py",
        # Fallback if the locked local Producer control is missing
        "tournament_agents/kaggle_producer.py",
    ]

    pool = [{"name": Path(test_agent_path).name, "path": test_agent_path}]

    for c in candidates:
        full_path = os.path.join(root, c)
        if not os.path.isfile(full_path):
            continue
        if os.path.abspath(full_path) == os.path.abspath(test_agent_path):
            continue
        name = Path(c).stem
        if _can_load_agent(full_path):
            pool.append({"name": name, "path": full_path})
        else:
            print(f"  ⚠  Skipping {name}: failed to load (missing torch or other dependency)")
        if len(pool) >= 10:
            break

    return pool


# ---------------------------------------------------------------------------
# Score extraction
# ---------------------------------------------------------------------------

def final_scores(state, n_agents: int) -> list[float]:
    """Extract planetary + fleet scores for each player from final game state."""
    obs = state[-1][0].observation
    scores = [0.0] * n_agents
    for p in obs.get("planets", []):
        owner = p[1]
        if 0 <= owner < n_agents:
            scores[owner] += p[5]
    for f in obs.get("fleets", []):
        owner = f[1]
        if 0 <= owner < n_agents:
            scores[owner] += f[6]
    return scores


def compute_placements(rewards: list[float]) -> list[int]:
    """
    Given a list of rewards (one per player), return placement (0-indexed rank,
    lower is better: 0=1st, 1=2nd ...) for each player. Ties get the same rank.
    """
    order = sorted(range(len(rewards)), key=lambda i: rewards[i], reverse=True)
    ranks = [0] * len(rewards)
    rank = 0
    for pos, idx in enumerate(order):
        if pos > 0 and rewards[idx] < rewards[order[pos - 1]]:
            rank = pos
        ranks[idx] = rank
    return ranks


def placement_points(ranks: list[int]) -> list[float]:
    """Convert rank indices to points, splitting tied ranks equally."""
    n = len(ranks)
    pts = [0.0] * n
    for i in range(n):
        rank = ranks[i]
        # Find all agents with the same rank
        tied = [j for j in range(n) if ranks[j] == rank]
        # Sum of points for tied positions, split equally
        total = sum(PLACEMENT_POINTS[r] for r in range(rank, rank + len(tied)))
        pts[i] = total / len(tied)
    return pts


# ---------------------------------------------------------------------------
# Single game runner (top-level function for multiprocessing)
# ---------------------------------------------------------------------------

def _run_game(args: tuple) -> dict:
    """Run one 4-player game. Called in a worker process."""
    combo, agent_paths, agent_names, steps, act_timeout, seed = args

    # Lazy import inside worker to avoid pickling issues
    import importlib.util
    import random as _rand
    import time as _time
    import traceback as _tb
    from kaggle_environments import make

    def _load(path, sfx):
        name = f"_tw_{sfx}_{_rand.random()}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        import sys as _sys2
        _sys2.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod.agent

    _rand.seed(seed)
    paths = [agent_paths[i] for i in combo]
    names = [agent_names[i] for i in combo]

    t0 = _time.time()
    try:
        env = make(
            "orbit_wars",
            configuration={"episodeSteps": steps, "actTimeout": act_timeout, "seed": seed},
            debug=False,
        )
        agents = [_load(p, f"{idx}_{seed}") for idx, p in enumerate(paths)]
        state = env.run(agents)
        dt = _time.time() - t0

        rewards = [s.reward for s in state[-1]]
        scores = final_scores(state, len(combo))
        # Use final ship-count scores for ranking (rewards are binary win/loss
        # in orbit_wars — all non-winners tie at 0, so 3rd/4th never appear).
        ranks = compute_placements(scores)
        pts = placement_points(ranks)

        return {
            "combo": list(combo),
            "names": names,
            "rewards": rewards,
            "ranks": ranks,
            "points": pts,
            "time_s": round(dt, 2),
            "error": None,
        }
    except Exception as exc:
        return {
            "combo": list(combo),
            "names": names,
            "rewards": [],
            "ranks": [],
            "points": [],
            "time_s": round(_time.time() - t0, 2),
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Tournament runner
# ---------------------------------------------------------------------------

def run_tournament(
    test_agent_path: str,
    root: str,
    n_games: Optional[int],
    steps: int,
    act_timeout: int,
    seed_base: int,
    workers: int,
    dry_run: bool,
    out_path: Optional[str],
    repeats: int = 1,
) -> dict:
    print("Loading agent pool...", flush=True)
    pool = build_agent_pool(test_agent_path, root)

    if len(pool) < 4:
        print(
            f"\nERROR: Only {len(pool)} loadable agents found (need at least 4).\n"
            "Options:\n"
            "  1. Run: bash scripts/download_kaggle_agents.sh\n"
            "  2. Install torch: bash scripts/setup_tournament_env.sh\n"
            "  3. Add more local agent files to the repo root.",
            file=sys.stderr,
        )
        sys.exit(1)

    n_agents = len(pool)
    n_combos = len(list(combinations(range(n_agents), 4)))

    # Auto-increase repeats so we always reach MIN_GAMES_TARGET
    if n_games is None and repeats == 1 and n_combos < MIN_GAMES_TARGET:
        repeats = math.ceil(MIN_GAMES_TARGET / n_combos)
        print(
            f"  ℹ  Only {n_agents} agents → {n_combos} unique combos. "
            f"Auto-setting repeats={repeats} to reach {repeats * n_combos} games (≥{MIN_GAMES_TARGET})."
        )

    all_combos = list(combinations(range(n_agents), 4)) * repeats
    random.seed(seed_base)
    random.shuffle(all_combos)

    if n_games is not None:
        all_combos = all_combos[:n_games]

    print(f"\n{'=' * 60}")
    print(f"ORBIT WARS TOURNAMENT")
    print(f"{'=' * 60}")
    print(f"  Test agent : {pool[0]['name']} ({pool[0]['path']})")
    print(f"  Agents     : {n_agents}/10")
    print(f"  Combos     : {n_combos} unique × {repeats} repeat(s)")
    print(f"  Games      : {len(all_combos)}")
    print(f"  Workers    : {workers}")
    print(f"  Steps/game : {steps}")
    print(f"  Act timeout: {act_timeout}s")
    print(f"\nAgent pool:")
    for i, a in enumerate(pool):
        marker = " ← TEST" if i == 0 else ""
        print(f"  [{i:2d}] {a['name']}{marker}")

    if dry_run:
        print(f"\nDRY RUN — {len(all_combos)} games scheduled:")
        for g, combo in enumerate(all_combos[:20]):
            names = " vs ".join(pool[i]["name"] for i in combo)
            print(f"  g{g+1:3d}: {names}")
        if len(all_combos) > 20:
            print(f"  ... ({len(all_combos) - 20} more)")
        return {}

    # Prepare per-agent accumulators
    stats = {
        i: {"name": pool[i]["name"], "pts": 0.0, "placements": [0, 0, 0, 0], "games": 0, "errors": 0}
        for i in range(n_agents)
    }

    agent_paths = [a["path"] for a in pool]
    agent_names = [a["name"] for a in pool]

    tasks = [
        (combo, agent_paths, agent_names, steps, act_timeout, seed_base + g)
        for g, combo in enumerate(all_combos)
    ]

    game_results = []
    errors = 0
    t_start = time.time()

    print(f"\nRunning {len(tasks)} games with {workers} worker(s)...\n")

    if workers == 1:
        # Single-process for easier debugging
        for i, task in enumerate(tasks):
            result = _run_game(task)
            game_results.append(result)
            _process_result(result, stats, i + 1, len(tasks), t_start)
            if result["error"]:
                errors += 1
    else:
        with multiprocessing.Pool(processes=workers) as mp_pool:
            for i, result in enumerate(mp_pool.imap_unordered(_run_game, tasks)):
                game_results.append(result)
                _process_result(result, stats, i + 1, len(tasks), t_start)
                if result["error"]:
                    errors += 1

    total_time = time.time() - t_start
    print(f"\nAll games done in {total_time:.1f}s  ({errors} errors)")

    leaderboard = _build_leaderboard(stats, n_agents)
    _print_leaderboard(leaderboard, pool[0]["name"])

    output = {
        "test_agent": pool[0]["name"],
        "n_agents": n_agents,
        "n_games": len(game_results),
        "errors": errors,
        "total_time_s": round(total_time, 1),
        "leaderboard": leaderboard,
        "games": game_results,
    }

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to: {out_path}")

    return output


def _process_result(result: dict, stats: dict, game_num: int, total: int, t_start: float):
    """Update stats from one game result and print a progress line."""
    elapsed = time.time() - t_start
    eta = (elapsed / game_num) * (total - game_num) if game_num > 0 else 0

    if result["error"]:
        combo_names = " vs ".join(result["names"])
        print(
            f"  g{game_num:3d}/{total} ERROR  [{combo_names}]  {result['error'][:60]}",
            flush=True,
        )
        # Mark all agents in this combo as errors
        for i, idx in enumerate(result["combo"]):
            stats[idx]["errors"] += 1
        return

    for i, idx in enumerate(result["combo"]):
        rank = result["ranks"][i]
        pts = result["points"][i]
        stats[idx]["pts"] += pts
        stats[idx]["games"] += 1
        if 0 <= rank < 4:
            stats[idx]["placements"][rank] += 1

    # Print progress every 10 games or at start
    if game_num == 1 or game_num % 10 == 0 or game_num == total:
        ranks_str = " ".join(
            f"{result['names'][i]}={result['ranks'][i]+1}st"
            for i in range(len(result["combo"]))
        )
        print(
            f"  g{game_num:3d}/{total}  {ranks_str[:70]:<70}  "
            f"ETA {eta:.0f}s",
            flush=True,
        )


def _build_leaderboard(stats: dict, n_agents: int) -> list[dict]:
    rows = []
    for i in range(n_agents):
        s = stats[i]
        g = s["games"]
        first_pct = (s["placements"][0] / g * 100) if g > 0 else 0.0
        avg_pts = (s["pts"] / g) if g > 0 else 0.0
        rows.append({
            "agent_idx": i,
            "name": s["name"],
            "pts": round(s["pts"], 1),
            "avg_pts": round(avg_pts, 3),
            "games": g,
            "errors": s["errors"],
            "first_pct": round(first_pct, 1),
            "placements": s["placements"],
        })
    rows.sort(key=lambda r: (r["pts"], r["first_pct"]), reverse=True)
    for rank, row in enumerate(rows):
        row["rank"] = rank + 1
    return rows


def _print_leaderboard(leaderboard: list[dict], test_agent_name: str):
    print(f"\n{'=' * 78}")
    print(f"TOURNAMENT LEADERBOARD")
    print(f"{'=' * 78}")
    header = f"{'Rank':<5} {'Agent':<30} {'Pts':>7} {'Avg':>6} {'1st%':>6} {'1st':>5} {'2nd':>5} {'3rd':>5} {'4th':>5} {'Games':>6}"
    print(header)
    print("-" * 78)
    for row in leaderboard:
        marker = " ◄" if row["name"] == test_agent_name else ""
        p = row["placements"]
        line = (
            f"{row['rank']:<5} {row['name'][:29]:<30} {row['pts']:>7.1f} "
            f"{row['avg_pts']:>6.3f} {row['first_pct']:>5.1f}% "
            f"{p[0]:>5} {p[1]:>5} {p[2]:>5} {p[3]:>5} {row['games']:>6}{marker}"
        )
        print(line)
    print("=" * 78)

    # Summary for the test agent
    test_row = next((r for r in leaderboard if r["name"] == test_agent_name), None)
    if test_row:
        print(f"\n📊 Test agent '{test_agent_name}': Rank {test_row['rank']}/{len(leaderboard)}  "
              f"1st={test_row['placements'][0]} ({test_row['first_pct']}%)  "
              f"Pts={test_row['pts']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _auto_detect_root() -> str:
    """Walk up from cwd to find the repo root (contains run_validation.py)."""
    p = Path.cwd()
    for _ in range(5):
        if (p / "run_validation.py").exists():
            return str(p)
        p = p.parent
    return str(Path.cwd())


def main():
    parser = argparse.ArgumentParser(
        description="Run a full round-robin 4-player tournament among 10 agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--agent", default="agent.py",
        help="Path to the test agent (default: agent.py in repo root)"
    )
    parser.add_argument(
        "--games", type=int, default=None,
        help="Limit total games (default: all C(n,4) combinations)"
    )
    parser.add_argument(
        "--repeats", type=int, default=1,
        help="Repeat each combination N times (default: 1)"
    )
    parser.add_argument(
        "--steps", type=int, default=300,
        help="Game steps per episode (default: 300)"
    )
    parser.add_argument(
        "--act-timeout", type=int, default=1,
        help="Per-agent action timeout in seconds (default: 1)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Base random seed (default: 42)"
    )
    parser.add_argument(
        "--workers", type=int,
        default=max(1, (multiprocessing.cpu_count() or 2) // 2),
        help="Parallel worker processes (default: cpu_count // 2)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the game schedule without running any games"
    )
    parser.add_argument(
        "--out", default=None,
        help="Path to save JSON results (default: artifacts/tournament_<timestamp>.json)"
    )
    parser.add_argument(
        "--root", default=None,
        help="Repo root directory (auto-detected by default)"
    )
    args = parser.parse_args()

    root = args.root or _auto_detect_root()

    # Resolve test agent path relative to root if not absolute
    agent_path = args.agent if os.path.isabs(args.agent) else os.path.join(root, args.agent)
    if not os.path.isfile(agent_path):
        print(f"ERROR: test agent not found: {agent_path}", file=sys.stderr)
        sys.exit(1)

    # Default output path
    out_path = args.out
    if out_path is None and not args.dry_run:
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(root, "artifacts", f"tournament_{ts}.json")

    run_tournament(
        test_agent_path=agent_path,
        root=root,
        n_games=args.games,
        steps=args.steps,
        act_timeout=args.act_timeout,
        seed_base=args.seed,
        workers=args.workers,
        dry_run=args.dry_run,
        out_path=out_path,
        repeats=args.repeats,
    )


if __name__ == "__main__":
    main()
