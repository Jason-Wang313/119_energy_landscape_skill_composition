from __future__ import annotations

import sys
from pathlib import Path


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common_reference_adapter import make_adapter


METHOD_NAME = "proposed_energy_landscape_composer_v4_1"
REFERENCE_IMPLEMENTATION = True
ADAPTER_VERSION = "paper119_reference_adapter_v1"

_ADAPTER = make_adapter(METHOD_NAME)


def initialize(config):
    return _ADAPTER.initialize(config)


def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    return _ADAPTER.propose(observation, terminal_samples, skill_i, skill_j, compute_budget)


def log(episode_context, proposal, outcome):
    return _ADAPTER.log(episode_context, proposal, outcome)


def reset(reset_context):
    return _ADAPTER.reset(reset_context)
