# Task Card: cable_route_insert

Not external evidence: `true`.

Seam under test: deformable cable state must remain in the insertion basin after routing.
Skill pair: `route_cable_along_path` -> `insert_cable_endpoint`.
Platform type: `high_fidelity_sim`.
Required paired resets per method: `30`.
Expected log: `external_validation/logs/cable_route_insert.jsonl`.
Expected videos: `external_validation/videos/cable_route_insert`.

## Fidelity Checks

- deformable or contact-rich cable model
- endpoint pose/state logging
- failure video coverage

## Method Checklist

Run every method on the same reset, scene, seed, source skill, target skill, and initial-state hash before moving to the next reset.

- [ ] `greedy_module_sequence`
- [ ] `behavior_cloned_skill_chain`
- [ ] `option_graph_planner`
- [ ] `tamp_feasibility_screen`
- [ ] `stable_dmp_handoff`
- [ ] `diffusion_skill_stitcher`
- [ ] `cem_trajectory_composer`
- [ ] `residual_rl_composer`
- [ ] `energy_compatibility_heuristic`
- [ ] `proposed_energy_landscape_composer_v4_1`
- [ ] `barrier_certified_energy_composer_v5`
- [ ] `oracle_basin_composer`

## Blocking Mistakes

- Do not tune v5 after seeing baseline outcomes on the same reset.
- Do not omit failed, abstained, or damaged episodes.
- Do not replace raw JSONL records with tables.
- Do not cite this task card as evidence.
