from __future__ import annotations

import dataclasses

import torch

import v38_feature_suite as base


CONFIG_2P = dataclasses.replace(
    base.ProducerLiteConfig(),
    enable_coalition=True,
    coalition_max_pairs_per_target=2,
    coalition_eta_slack=1.5,
)
CONFIG_4P = dataclasses.replace(
    base.CONFIG_4P,
    enable_coalition=True,
    coalition_max_pairs_per_target=2,
    coalition_eta_slack=1.5,
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
