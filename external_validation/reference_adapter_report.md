# External Reference Adapter Report

Not external evidence: `true`.
Evidence status: `implementation_only_not_rollout_evidence`.

These adapters are executable reference implementations for the external validation harness. They can remove adapter engineering ambiguity for an independent operator, but they do not supply real robot or accepted high-fidelity simulator evidence by themselves.

Strict evidence still requires a manifest, raw JSONL logs, videos, task configs, checkpoints or hashes, and recomputed rollout metrics.

## Adapters

- `barrier_certified_energy_composer_v5`: `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py`; metadata `external_validation/baselines/barrier_certified_energy_composer_v5/reference_adapter_metadata.json`.
- `behavior_cloned_skill_chain`: `external_validation/baselines/behavior_cloned_skill_chain/adapter.py`; metadata `external_validation/baselines/behavior_cloned_skill_chain/reference_adapter_metadata.json`.
- `cem_trajectory_composer`: `external_validation/baselines/cem_trajectory_composer/adapter.py`; metadata `external_validation/baselines/cem_trajectory_composer/reference_adapter_metadata.json`.
- `diffusion_skill_stitcher`: `external_validation/baselines/diffusion_skill_stitcher/adapter.py`; metadata `external_validation/baselines/diffusion_skill_stitcher/reference_adapter_metadata.json`.
- `energy_compatibility_heuristic`: `external_validation/baselines/energy_compatibility_heuristic/adapter.py`; metadata `external_validation/baselines/energy_compatibility_heuristic/reference_adapter_metadata.json`.
- `greedy_module_sequence`: `external_validation/baselines/greedy_module_sequence/adapter.py`; metadata `external_validation/baselines/greedy_module_sequence/reference_adapter_metadata.json`.
- `option_graph_planner`: `external_validation/baselines/option_graph_planner/adapter.py`; metadata `external_validation/baselines/option_graph_planner/reference_adapter_metadata.json`.
- `oracle_basin_composer`: `external_validation/baselines/oracle_basin_composer/adapter.py`; metadata `external_validation/baselines/oracle_basin_composer/reference_adapter_metadata.json`.
- `proposed_energy_landscape_composer_v4_1`: `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py`; metadata `external_validation/baselines/proposed_energy_landscape_composer_v4_1/reference_adapter_metadata.json`.
- `residual_rl_composer`: `external_validation/baselines/residual_rl_composer/adapter.py`; metadata `external_validation/baselines/residual_rl_composer/reference_adapter_metadata.json`.
- `stable_dmp_handoff`: `external_validation/baselines/stable_dmp_handoff/adapter.py`; metadata `external_validation/baselines/stable_dmp_handoff/reference_adapter_metadata.json`.
- `tamp_feasibility_screen`: `external_validation/baselines/tamp_feasibility_screen/adapter.py`; metadata `external_validation/baselines/tamp_feasibility_screen/reference_adapter_metadata.json`.
