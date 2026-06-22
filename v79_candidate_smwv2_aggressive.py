from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path

import torch


def _load_private_base() -> object:
    path = Path(__file__).with_name("tournament_agents").joinpath("kaggle_smw_v2.py")
    name = f"{__name__}._smw_v2_base"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base = _load_private_base()


CONFIG_2P = dataclasses.replace(
    base.ProducerLiteConfig(),
    min_ships_to_launch=3.0,
    max_waves_per_turn=7,
    enable_potential_risk=True,
    risk_blend_weight=0.5,
)
CONFIG_4P = dataclasses.replace(
    base.CONFIG_4P,
    horizon=14,
    max_sources_per_lane=7,
    max_waves_per_turn=7,
    min_ships_to_launch=3.0,
    enable_potential_risk=True,
    risk_blend_weight=0.5,
    max_strike_sources=4,
)


def _config_for(player_count: int) -> base.ProducerLiteConfig:
    return CONFIG_4P if int(player_count) >= 4 else CONFIG_2P


base._config_for = _config_for


def agent(obs):
    player = obs.get("player", 0) if isinstance(obs, dict) else obs.player
    player_id = int(player)
    obs_tensors = base.single_obs_to_tensor(obs, player_id=player_id)
    with torch.no_grad():
        sparse_row = base._RUNTIME.tensor_action(obs_tensors)
    return base.sparse_action_row_to_moves(sparse_row, obs, player_id=player_id)
