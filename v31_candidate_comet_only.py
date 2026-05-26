"""Ablation candidate B: Hellburner comet behavior only (no v30 sweep stack)."""

import v30_agent as base

# Disable v30 sweep stack; keep comet behavior from baseline lineage.
base.SWEEP_ENABLED = False
base.SATURATION_ENABLED = False
base.TIE_SAFETY_ENABLED = False

agent = base.agent
