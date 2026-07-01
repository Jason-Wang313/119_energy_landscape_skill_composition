"""
Scaffold-only adapter template for Paper 119 external validation.

This file is not external evidence. Replace every NotImplementedError with an
independent implementation before referencing this method in an evidence
manifest.
"""

NOT_EXTERNAL_EVIDENCE = True
SCAFFOLD_ONLY = True
METHOD_NAME = "cem_trajectory_composer"
REQUIRED_ENTRYPOINT = "optimize_handoff_with_cem"


def initialize(config):
    """Load method config/checkpoint and return declared hashes."""
    raise NotImplementedError(f"Replace scaffold for {METHOD_NAME} with an independent implementation.")


def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    """Return seam decision, optional repair action, predicted risk, and diagnosis."""
    raise NotImplementedError(f"Replace scaffold for {METHOD_NAME} with an independent implementation.")


def log(episode_context, proposal, outcome):
    """Return JSONL-ready fields required by external_validation/log_schema_v1.json."""
    raise NotImplementedError(f"Replace scaffold for {METHOD_NAME} with an independent implementation.")


def reset(reset_context):
    """Clear method-local state between paired resets unless online memory is explicitly logged."""
    raise NotImplementedError(f"Replace scaffold for {METHOD_NAME} with an independent implementation.")
