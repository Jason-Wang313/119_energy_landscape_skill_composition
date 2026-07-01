# External Reference Adapter Audit

Passed: `true`.
Not evidence: `true`.
Adapters checked: `12`.
Non-oracle adapters: `11`.

This audit imports and exercises the executable reference adapters against the same callable API shape used by manifest-declared evidence validation. It is an implementation-readiness check only; strict manifest-declared evidence validation rejects these reference-only adapters.

## Checks

- `pass` `common_reference_adapter_exists`: external_validation/baselines/common_reference_adapter.py
- `pass` `reference_adapters_exist`: missing=[]
- `pass` `method_count_ge_12`: methods=12
- `pass` `non_oracle_reference_adapters_ge_11`: non_oracle=11
- `pass` `all_reference_adapters_pass_contract`: failed=[]
- `pass` `reference_adapter_behavior_contract_passes_non_strict`: reference adapters pass the callable API contract only in non-strict mode
- `pass` `audit_not_rollout_evidence`: reference adapters are executable implementation shims, not robot or high-fidelity rollout evidence

## Adapter Results

- `pass` `barrier_certified_energy_composer_v5`: `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py`; ok
- `pass` `behavior_cloned_skill_chain`: `external_validation/baselines/behavior_cloned_skill_chain/adapter.py`; ok
- `pass` `cem_trajectory_composer`: `external_validation/baselines/cem_trajectory_composer/adapter.py`; ok
- `pass` `diffusion_skill_stitcher`: `external_validation/baselines/diffusion_skill_stitcher/adapter.py`; ok
- `pass` `energy_compatibility_heuristic`: `external_validation/baselines/energy_compatibility_heuristic/adapter.py`; ok
- `pass` `greedy_module_sequence`: `external_validation/baselines/greedy_module_sequence/adapter.py`; ok
- `pass` `option_graph_planner`: `external_validation/baselines/option_graph_planner/adapter.py`; ok
- `pass` `oracle_basin_composer`: `external_validation/baselines/oracle_basin_composer/adapter.py`; ok
- `pass` `proposed_energy_landscape_composer_v4_1`: `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py`; ok
- `pass` `residual_rl_composer`: `external_validation/baselines/residual_rl_composer/adapter.py`; ok
- `pass` `stable_dmp_handoff`: `external_validation/baselines/stable_dmp_handoff/adapter.py`; ok
- `pass` `tamp_feasibility_screen`: `external_validation/baselines/tamp_feasibility_screen/adapter.py`; ok
