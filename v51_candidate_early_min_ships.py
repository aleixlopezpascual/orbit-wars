"""v51: phase-aware min_ships_to_launch — lower threshold (8.0→5.0) for steps < 30.

Hypothesis: the early 60% zero-action rate is partly gated by min_ships_to_launch=8.0.
In the opening turns planets haven't yet accumulated 8 ships so the agent stays idle.
Lowering the launch floor early allows small early fleets to grab nearby neutrals
before the enemy does. Reverts to 8.0 after step 30 to preserve late-game efficiency.
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

_EARLY_TURNS = 30
_EARLY_MIN_SHIPS = 5.0   # default is 8.0


class _PhasedRuntime(base.ProducerLiteRuntime):
    def tensor_action(self, obs_tensors: dict):
        mem = self.memory
        if bool((obs_tensors["step"] == 0).all()):
            mem.cached_player_count = None
        if mem.cached_player_count is None:
            mem.cached_player_count = base.largest_initial_player_count(obs_tensors)

        step = int(obs_tensors["step"].item())
        config = base._config_for(int(mem.cached_player_count))
        if step < _EARLY_TURNS:
            config = dataclasses.replace(config, min_ships_to_launch=_EARLY_MIN_SHIPS)

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
