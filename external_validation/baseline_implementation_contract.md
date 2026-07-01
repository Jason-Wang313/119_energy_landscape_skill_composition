# External Baseline Implementation Contract

Not external evidence: `true`.

Purpose: make the missing independent baseline layer explicit before any real robot or high-fidelity simulator run is counted as evidence.

A future submission-ready evidence package must provide independent source, config/checkpoint hashes, and episode logs for every non-oracle method below. This contract is a checklist and interface specification only; it does not satisfy the external evidence gate.

## Adapter API

- `initialize`: load method config/checkpoint and declare method_name, version, and hashes.
- `propose`: given shared observation, terminal samples, skill_i, skill_j, and compute budget, return seam decision and optional repair.
- `log`: emit predicted risk, diagnosis, decision, repair action, policy/config hash, and timing for the episode JSONL record.
- `reset`: clear method-local state between paired resets unless the method explicitly models online memory and logs it.

## Fairness Invariants

- same skill library for every non-oracle method.
- same initial state, scene_id, seed, and skill pair for paired comparisons.
- same observation interface and no hidden state except where the platform exposes it to all methods.
- same compute budget or a predeclared budget measured in wall-clock time and simulator queries.
- same logging schema, video requirement, and policy/config hash requirement.
- oracle_basin_composer is reported only as a post hoc upper bound and is excluded from strongest non-oracle selection.

## Method Matrix

- `greedy_module_sequence`: open-loop skill graph baseline; entrypoint `select_next_skill_and_handoff`; adapter `external_validation/baselines/greedy_module_sequence`; status `missing_external_source`.
- `behavior_cloned_skill_chain`: demonstration sequence baseline; entrypoint `predict_demonstrated_handoff`; adapter `external_validation/baselines/behavior_cloned_skill_chain`; status `missing_external_source`.
- `option_graph_planner`: temporal-abstraction planning baseline; entrypoint `plan_over_option_graph`; adapter `external_validation/baselines/option_graph_planner`; status `missing_external_source`.
- `tamp_feasibility_screen`: task-and-motion feasibility baseline; entrypoint `screen_symbolic_geometric_transition`; adapter `external_validation/baselines/tamp_feasibility_screen`; status `missing_external_source`.
- `stable_dmp_handoff`: stable dynamics handoff baseline; entrypoint `generate_stable_handoff`; adapter `external_validation/baselines/stable_dmp_handoff`; status `missing_external_source`.
- `diffusion_skill_stitcher`: generative handoff sampler baseline; entrypoint `sample_handoff_state`; adapter `external_validation/baselines/diffusion_skill_stitcher`; status `missing_external_source`.
- `cem_trajectory_composer`: trajectory-search baseline; entrypoint `optimize_handoff_with_cem`; adapter `external_validation/baselines/cem_trajectory_composer`; status `missing_external_source`.
- `residual_rl_composer`: learned residual repair baseline; entrypoint `apply_residual_repair_policy`; adapter `external_validation/baselines/residual_rl_composer`; status `missing_external_source`.
- `energy_compatibility_heuristic`: non-certified energy heuristic baseline; entrypoint `score_energy_compatibility`; adapter `external_validation/baselines/energy_compatibility_heuristic`; status `missing_external_source`.
- `proposed_energy_landscape_composer_v4_1`: previous proposed method baseline; entrypoint `compose_with_v4_1_rules`; adapter `external_validation/baselines/proposed_energy_landscape_composer_v4_1`; status `missing_external_source`.
- `barrier_certified_energy_composer_v5`: primary method; entrypoint `compose_with_barrier_certified_seam_model`; adapter `external_validation/baselines/barrier_certified_energy_composer_v5`; status `missing_external_source`.
- `oracle_basin_composer`: post hoc upper bound only; entrypoint `evaluate_oracle_upper_bound`; adapter `post_hoc_upper_bound`; status `post_hoc_upper_bound_only`.

## Missing Independent Implementations

- `greedy_module_sequence`
- `behavior_cloned_skill_chain`
- `option_graph_planner`
- `tamp_feasibility_screen`
- `stable_dmp_handoff`
- `diffusion_skill_stitcher`
- `cem_trajectory_composer`
- `residual_rl_composer`
- `energy_compatibility_heuristic`
- `proposed_energy_landscape_composer_v4_1`
- `barrier_certified_energy_composer_v5`

## Generated Spec Files

- `external_validation/baseline_specs/greedy_module_sequence.json`
- `external_validation/baseline_specs/behavior_cloned_skill_chain.json`
- `external_validation/baseline_specs/option_graph_planner.json`
- `external_validation/baseline_specs/tamp_feasibility_screen.json`
- `external_validation/baseline_specs/stable_dmp_handoff.json`
- `external_validation/baseline_specs/diffusion_skill_stitcher.json`
- `external_validation/baseline_specs/cem_trajectory_composer.json`
- `external_validation/baseline_specs/residual_rl_composer.json`
- `external_validation/baseline_specs/energy_compatibility_heuristic.json`
- `external_validation/baseline_specs/proposed_energy_landscape_composer_v4_1.json`
- `external_validation/baseline_specs/barrier_certified_energy_composer_v5.json`
- `external_validation/baseline_specs/oracle_basin_composer.json`
