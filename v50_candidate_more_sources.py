"""v50: increase max_sources_per_lane 12→16.

Hypothesis: source utilisation is very low (20-32% of owned planets firing per turn).
Raising max_sources_per_lane allows more owned planets to participate in each
decision cycle, improving fleet coverage and reducing idle production.
"""
from __future__ import annotations

import dataclasses
import os
import sys

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import torch
import v36_candidate_min_ships as base
from orbit_lite.adapter import single_obs_to_tensor, sparse_action_row_to_moves

_CONFIG_2P = dataclasses.replace(base.ProducerLiteConfig(), max_sources_per_lane=16)
_CONFIG_4P = dataclasses.replace(base.CONFIG_4P, max_sources_per_lane=16)


def _config_for(player_count: int):
    return _CONFIG_4P if int(player_count) >= 4 else _CONFIG_2P


class _PhasedRuntime(base.ProducerLiteRuntime):
    def tensor_action(self, obs_tensors: dict):
        mem = self.memory
        if bool((obs_tensors["step"] == 0).all()):
            mem.cached_player_count = None
        if mem.cached_player_count is None:
            mem.cached_player_count = base.largest_initial_player_count(obs_tensors)
        config = _config_for(int(mem.cached_player_count))
        row = base.run_turn(
            obs_tensors, config=config,
            player_count=int(mem.cached_player_count), memory=mem,
        )
        mem.last_sparse_action_row = row
        return row


_RUNTIME = _PhasedRuntime()


def agent(obs):
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    player_id = int(player)
    obs_tensors = single_obs_to_tensor(obs, player_id=player_id)
    with torch.no_grad():
        sparse_row = _RUNTIME.tensor_action(obs_tensors)
    return sparse_action_row_to_moves(sparse_row, obs, player_id=player_id)
