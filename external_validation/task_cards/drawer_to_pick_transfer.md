# Task Card: drawer_to_pick_transfer

Not external evidence: `true`.

Seam under test: drawer contact and terminal handle pose must leave a reachable grasp basin.
Skill pair: `open_drawer_to_clearance` -> `pick_object_from_drawer`.
Platform type: `high_fidelity_sim`.
Required paired resets per method: `30`.
Expected log: `external_validation/logs/drawer_to_pick_transfer.jsonl`.
Expected videos: `external_validation/videos/drawer_to_pick_transfer`.

## Fidelity Checks

- drawer joint friction
- handle contact
- object pose logging

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
