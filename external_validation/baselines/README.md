# External Baseline Adapter Scaffolds

Not external evidence: `true`.

These directories provide executable templates for plugging independent baselines into the external validation protocol. They intentionally raise `NotImplementedError` and must not be cited as independent implementations.

## Required Adapter API

- `initialize`
- `propose`
- `log`
- `reset`

## Scaffolds

- `barrier_certified_energy_composer_v5`: `external_validation/baselines/barrier_certified_energy_composer_v5/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `behavior_cloned_skill_chain`: `external_validation/baselines/behavior_cloned_skill_chain/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `cem_trajectory_composer`: `external_validation/baselines/cem_trajectory_composer/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `diffusion_skill_stitcher`: `external_validation/baselines/diffusion_skill_stitcher/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `energy_compatibility_heuristic`: `external_validation/baselines/energy_compatibility_heuristic/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `greedy_module_sequence`: `external_validation/baselines/greedy_module_sequence/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `option_graph_planner`: `external_validation/baselines/option_graph_planner/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `oracle_basin_composer`: `external_validation/baselines/oracle_basin_composer/adapter_template.py`; status `post_hoc_upper_bound_only`.
- `proposed_energy_landscape_composer_v4_1`: `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `residual_rl_composer`: `external_validation/baselines/residual_rl_composer/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `stable_dmp_handoff`: `external_validation/baselines/stable_dmp_handoff/adapter_template.py`; status `scaffold_only_missing_external_source`.
- `tamp_feasibility_screen`: `external_validation/baselines/tamp_feasibility_screen/adapter_template.py`; status `scaffold_only_missing_external_source`.
