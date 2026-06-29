# External Manifest Builder Report

Manifest written: `false`.
Ready to write manifest: `false`.
Not evidence: `true`.
Template: `C:\Users\wangz\robotics_massive_pool_paper_factory\119_energy_landscape_skill_composition\external_validation\manifest_template.json`.
Output: `C:\Users\wangz\robotics_massive_pool_paper_factory\119_energy_landscape_skill_composition\external_validation\manifest.json`.

## Summary

- Records loaded: `0`.
- Schema errors: `4`.
- Warnings: `11`.
- Manifest assembly checklist: `external_validation/manifest_assembly_checklist.csv`.
- Checklist rows: `35`.
- Checklist blocking rows: `28`.

## Schema Errors

- peg_place_regrasp: missing log file external_validation/logs/peg_place_regrasp.jsonl
- drawer_to_pick_transfer: missing log file external_validation/logs/drawer_to_pick_transfer.jsonl
- door_open_navigation: missing log file external_validation/logs/door_open_navigation.jsonl
- cable_route_insert: missing log file external_validation/logs/cable_route_insert.jsonl

## Warnings

- greedy_module_sequence: no checkpoint_or_config_hash and no hashable implementation/path
- behavior_cloned_skill_chain: no checkpoint_or_config_hash and no hashable implementation/path
- option_graph_planner: no checkpoint_or_config_hash and no hashable implementation/path
- tamp_feasibility_screen: no checkpoint_or_config_hash and no hashable implementation/path
- stable_dmp_handoff: no checkpoint_or_config_hash and no hashable implementation/path
- diffusion_skill_stitcher: no checkpoint_or_config_hash and no hashable implementation/path
- cem_trajectory_composer: no checkpoint_or_config_hash and no hashable implementation/path
- residual_rl_composer: no checkpoint_or_config_hash and no hashable implementation/path
- energy_compatibility_heuristic: no checkpoint_or_config_hash and no hashable implementation/path
- proposed_energy_landscape_composer_v4_1: no checkpoint_or_config_hash and no hashable implementation/path
- barrier_certified_energy_composer_v5: no checkpoint_or_config_hash and no hashable implementation/path

## Manifest Assembly Checklist

- `platform_fidelity` `accepted_fidelity_provenance`: not_accepted_in_current_repo -> promote the fidelity acceptance draft only after independent operator signoff, platform/contact provenance, calibration basis, and replay evidence exist
- `run_identity` `code_commit_and_skill_library_hash`: missing -> record the exact commit and skill-library hash used before collecting external logs
- `task_configs` `peg_place_regrasp_config`: present -> manifest-declare the exact config consumed by the backend and lock config_hash before collection
- `rollout_logs` `peg_place_regrasp_jsonl`: missing -> collect 30 paired-reset episodes per manifest-declared method for this task
- `rollout_videos` `peg_place_regrasp_videos`: missing -> write reviewable videos for manifest-declared rollout records; do not use placeholder media
- `task_configs` `drawer_to_pick_transfer_config`: present -> manifest-declare the exact config consumed by the backend and lock config_hash before collection
- `rollout_logs` `drawer_to_pick_transfer_jsonl`: missing -> collect 30 paired-reset episodes per manifest-declared method for this task
- `rollout_videos` `drawer_to_pick_transfer_videos`: missing -> write reviewable videos for manifest-declared rollout records; do not use placeholder media
- `task_configs` `door_open_navigation_config`: present -> manifest-declare the exact config consumed by the backend and lock config_hash before collection
- `rollout_logs` `door_open_navigation_jsonl`: missing -> collect 30 paired-reset episodes per manifest-declared method for this task
- `rollout_videos` `door_open_navigation_videos`: missing -> write reviewable videos for manifest-declared rollout records; do not use placeholder media
- `task_configs` `cable_route_insert_config`: present -> manifest-declare the exact config consumed by the backend and lock config_hash before collection
- `rollout_logs` `cable_route_insert_jsonl`: missing -> collect 30 paired-reset episodes per manifest-declared method for this task
- `rollout_videos` `cable_route_insert_videos`: missing -> write reviewable videos for manifest-declared rollout records; do not use placeholder media
- `method_implementations` `greedy_module_sequence`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `behavior_cloned_skill_chain`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `option_graph_planner`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `tamp_feasibility_screen`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `stable_dmp_handoff`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `diffusion_skill_stitcher`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `cem_trajectory_composer`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `residual_rl_composer`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `energy_compatibility_heuristic`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `proposed_energy_landscape_composer_v4_1`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `barrier_certified_energy_composer_v5`: implementation=missing_path; checkpoint_or_config=missing_path; manifest_hash=missing; provenance=present -> supply an independent non-oracle implementation or wrapper, lock its source/config hash, declare implementation_provenance signoff, and ensure JSONL policy_or_config_hash matches it
- `method_implementations` `oracle_basin_composer`: oracle_upper_bound_not_independent_method -> keep oracle reported only as a post-hoc upper bound and explain saturation/boundary in the manifest metrics
- `release_artifacts` `code`: entries=7 -> hash-lock real code artifacts into the release package after collection
- `release_artifacts` `configs`: entries=5 -> hash-lock real configs artifacts into the release package after collection
- `release_artifacts` `logs`: entries=0 -> hash-lock real logs artifacts into the release package after collection
- `release_artifacts` `videos`: entries=0 -> hash-lock real videos artifacts into the release package after collection
- `release_artifacts` `checkpoints`: entries=0 -> hash-lock real checkpoints artifacts into the release package after collection
- `rollout_metrics` `schema_valid_records`: records_loaded=0; schema_errors=4 -> load raw JSONL logs with zero schema/video-path errors and recompute metrics from records
- `rollout_metrics` `primary_thresholds`: episodes=0; success_margin=None; utility_margin=None -> do not hand-enter primary metrics; let the manifest builder write metrics after strict raw-log recomputation
- `final_strict_gates` `paired_reset_integrity`: not_ready_without_real_manifest_logs -> pass complete duplicate-free paired-reset panels across all manifest-declared methods
- `final_strict_gates` `final_external_evidence_gate`: warnings=11; schema_errors=4 -> run the final evidence gate only after fidelity, configs, logs, videos, methods, release artifacts, and recomputed metrics are real
