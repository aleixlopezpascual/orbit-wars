#!/usr/bin/env python3
"""Batch list submission episodes and download Kaggle replays/logs."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, *, capture_output=True):
    try:
        return subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=capture_output,
        )
    except FileNotFoundError:
        print(
            f"Error: command '{command[0]}' not found. Install Kaggle CLI and ensure it is in PATH.",
            file=sys.stderr,
        )
        sys.exit(1)


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload):
    write_text(path, json.dumps(payload, indent=2) + "\n")


def normalize_header(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def parse_episode_rows(csv_text: str):
    reader = csv.DictReader(csv_text.splitlines())
    rows = list(reader)
    if not rows:
        return []

    header_map = {normalize_header(field): field for field in reader.fieldnames or []}
    episode_field = header_map.get("episodeid")
    if episode_field is None:
        for normalized, original in header_map.items():
            if "episode" in normalized and "id" in normalized:
                episode_field = original
                break
    if episode_field is None:
        raise ValueError("Could not find an episode id column in Kaggle episode output.")

    parsed = []
    for row in rows:
        episode_id = row.get(episode_field)
        if not episode_id:
            continue
        parsed.append(
            {
                "episode_id": str(episode_id).strip(),
                "raw": row,
            }
        )
    return parsed


def list_submission_episodes(kaggle_bin: str, submission_id: int):
    command = [
        kaggle_bin,
        "competitions",
        "episodes",
        str(submission_id),
        "-v",
    ]
    result = run_command(command)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "kaggle episodes failed")
    return result.stdout


def download_replay(kaggle_bin: str, episode_id: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        kaggle_bin,
        "competitions",
        "replay",
        str(episode_id),
        "-p",
        str(out_dir),
    ]
    result = run_command(command)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def download_logs(kaggle_bin: str, episode_id: str, agent_index: int, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        kaggle_bin,
        "competitions",
        "logs",
        str(episode_id),
        str(agent_index),
        "-p",
        str(out_dir),
    ]
    result = run_command(command)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="List submission episodes and batch-download Kaggle replays/logs."
    )
    parser.add_argument("--submission-id", type=int, required=True, help="Kaggle submission id.")
    parser.add_argument("--competition", default="orbit-wars", help="Competition slug.")
    parser.add_argument("--kaggle-bin", default="kaggle", help="Path to kaggle CLI.")
    parser.add_argument("--limit", type=int, default=20, help="Max episodes to process from the submission list.")
    parser.add_argument("--out-dir", required=True, help="Directory for CSV, manifests, replays, and logs.")
    parser.add_argument("--download-replays", action="store_true", help="Download replay JSONs.")
    parser.add_argument("--download-logs", action="store_true", help="Download agent logs.")
    parser.add_argument(
        "--agent-index",
        type=int,
        action="append",
        default=[],
        help="Agent seat index for logs. Repeat to fetch multiple seats.",
    )
    parser.add_argument(
        "--best-effort",
        action="store_true",
        help="Continue when individual replay/log downloads fail.",
    )
    parser.add_argument("--dry-run", action="store_true", help="List episode ids without downloading artifacts.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_text = list_submission_episodes(args.kaggle_bin, args.submission_id)
    write_text(out_dir / "episodes.csv", csv_text)

    parsed_rows = parse_episode_rows(csv_text)
    selected_rows = parsed_rows[: max(0, args.limit)]
    write_json(out_dir / "episodes.json", selected_rows)

    manifest = {
        "submission_id": args.submission_id,
        "competition": args.competition,
        "limit": args.limit,
        "download_replays": args.download_replays,
        "download_logs": args.download_logs,
        "agent_indexes": args.agent_index,
        "selected_episode_ids": [row["episode_id"] for row in selected_rows],
        "generated_at": int(time.time()),
        "downloads": [],
    }

    print(f"Found {len(parsed_rows)} episodes; selected {len(selected_rows)}.", flush=True)
    for row in selected_rows:
        print(f"  episode {row['episode_id']}", flush=True)

    if args.dry_run:
        write_json(out_dir / "manifest.json", manifest)
        return 0

    for row in selected_rows:
        episode_id = row["episode_id"]
        download_entry = {"episode_id": episode_id, "replay": None, "logs": []}

        if args.download_replays:
            replay_result = download_replay(args.kaggle_bin, episode_id, out_dir / "replays")
            download_entry["replay"] = replay_result
            if replay_result["returncode"] != 0 and not args.best_effort:
                write_json(out_dir / "manifest.json", manifest)
                raise SystemExit(
                    f"Replay download failed for episode {episode_id}: {replay_result['stderr'] or replay_result['stdout']}"
                )

        if args.download_logs:
            agent_indexes = args.agent_index or [0]
            for agent_index in agent_indexes:
                log_result = download_logs(
                    args.kaggle_bin,
                    episode_id,
                    agent_index,
                    out_dir / "logs" / f"agent_{agent_index}",
                )
                download_entry["logs"].append({"agent_index": agent_index, **log_result})
                if log_result["returncode"] != 0 and not args.best_effort:
                    write_json(out_dir / "manifest.json", manifest)
                    raise SystemExit(
                        f"Log download failed for episode {episode_id}, agent {agent_index}: "
                        f"{log_result['stderr'] or log_result['stdout']}"
                    )

        manifest["downloads"].append(download_entry)

    write_json(out_dir / "manifest.json", manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
