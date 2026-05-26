"""Ablation candidate A: Hellburner+v30 sweep offense only."""

import v30_agent as base

# Keep sweep offense active, disable added defensive coupling.
base.SWEEP_ENABLED = True
base.SATURATION_ENABLED = False
base.TIE_SAFETY_ENABLED = False

agent = base.agent
