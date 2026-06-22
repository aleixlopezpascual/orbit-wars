"""v80: focus-fire / multi-source coalition on the v43 base.

Parent: v43_candidate_wavecap5_beta24.py (wave_cap=5, reinforce_beta=2.4).
Hypothesis (GAP=FOCUS_FIRE from V43_LOSS_ANALYSIS.md): winners systematically
out-coordinate v43 via multi-source synchronized captures. v43's single-source
greedy core cannot unlock targets no single planet can take alone.

This enables the existing 2-source coalition feature in v38_feature_suite on top
of v43's proven knobs, at a NEW operating point distinct from the failed H-A5
run (which used the bare v38 base with eta_slack=1.5, max_pairs=2 -> rank 4/10):
  - keep v43's wave_cap=5 + reinforce_beta=2.4
  - tighter arrival synchronization: coalition_eta_slack=1.0 (vs failed 1.5)

Promotion rule (FINAL_DAY_STANDING.md): goes live only if it beats v43 on BOTH
total points and 1st-place rate in the kaggle_latest10 tournament gate.
"""
from __future__ import annotations

import dataclasses

import torch

import v38_feature_suite as base


CONFIG_2P = dataclasses.replace(
    base.ProducerLiteConfig(),
    max_waves_per_turn=5,
    reinforce_size_beta=2.4,
    enable_coalition=True,
    coalition_max_pairs_per_target=2,
    coalition_eta_slack=1.0,
)
CONFIG_4P = dataclasses.replace(
    base.CONFIG_4P,
    max_waves_per_turn=5,
    reinforce_size_beta=2.4,
    enable_coalition=True,
    coalition_max_pairs_per_target=2,
    coalition_eta_slack=1.0,
)


def _config_for(player_count: int) -> base.ProducerLiteConfig:
    return CONFIG_4P if int(player_count) >= 4 else CONFIG_2P


class Runtime:
    def __init__(self, memory: base.ProducerLiteMemory | None = None) -> None:
        self.memory = memory if memory is not None else base.ProducerLiteMemory()

    def tensor_action(self, obs_tensors: dict):
        mem = self.memory
        if bool((obs_tensors["step"] == 0).all()):
            mem.cached_player_count = None
        if mem.cached_player_count is None:
            mem.cached_player_count = base.largest_initial_player_count(obs_tensors)
        row = base.run_turn(
            obs_tensors,
            config=_config_for(mem.cached_player_count),
            player_count=int(mem.cached_player_count),
            memory=mem,
        )
        mem.last_sparse_action_row = row
        return row


_RUNTIME = Runtime()


def agent(obs):
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    player_id = int(player)
    obs_tensors = base.single_obs_to_tensor(obs, player_id=player_id)
    with torch.no_grad():
        sparse_row = _RUNTIME.tensor_action(obs_tensors)
    return base.sparse_action_row_to_moves(sparse_row, obs, player_id=player_id)
