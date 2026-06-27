# External Backend Integration Packet

Not evidence: `true`.
Primary route: `maniskill_sapien_primary`.
Primary platform family: `ManiSkill/SAPIEN`.
Strict backend ready: `false`.
Strict evidence ready: `false`.

This packet converts the missing non-template backend module into concrete integration work orders for the independent public-simulator route. It does not provide a backend, rollout logs, videos, manifest, or accepted high-fidelity evidence.

## Forbidden Evidence Shortcuts

- using backend_templates as real backends
- using local_dry_run logs or placeholder videos as external evidence
- collecting before strict backend qualification and collection readiness pass
- changing task configs or method identities after alias unsealing
- omitting policy/config hashes or platform provenance from logs and manifest inputs

## Required Backend Hooks

- `platform_provenance`
- `load_task_config`
- `reset_scene`
- `capture_observation`
- `terminal_samples`
- `run_method`
- `execute_skill_pair`
- `record_video`
- `policy_or_config_hash`

## Required Platform Provenance Fields

- `platform_name`
- `platform_version`
- `maniskill_version`
- `sapien_version`
- `python_version`
- `operating_system`
- `gpu_model`
- `gpu_driver`
- `vulkan_or_renderer_device`
- `physics_timestep`
- `contact_solver`
- `friction_model`
- `camera_intrinsics_and_resolution`
- `state_observation_keys`
- `contact_signal_keys`
- `backend_module_sha256`
- `code_commit`

## Work Orders

### `create_non_template_backend_module`

- Route: `maniskill_sapien_primary`
- Platform family: `ManiSkill/SAPIEN`
- Operator input: implement create_backend() or Backend using ExternalCollectionBackend without TEMPLATE_ONLY
- Required artifacts: `external_validation/runner/backends/<real_backend>.py`, `external_validation/fidelity_acceptance.json`

- Required hooks: `platform_provenance`, `load_task_config`, `reset_scene`, `capture_observation`, `terminal_samples`, `run_method`, `execute_skill_pair`, `record_video`, `policy_or_config_hash`

### `bind_task_configs_to_backend`

- Route: `maniskill_sapien_primary`
- Platform family: `ManiSkill/SAPIEN`
- Operator input: load every prepared task config and record the exact accepted platform values
- Required artifacts: `external_validation/configs/*.json`, `external_validation/config_schema_v1.json`

- Required tasks: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`, `cable_route_insert`

### `preserve_paired_reset_execution`

- Route: `maniskill_sapien_primary`
- Platform family: `ManiSkill/SAPIEN`
- Operator input: make reset_scene preserve scene_id, seed, skill_i, skill_j, and initial_state_hash across the full method panel
- Required artifacts: `external_validation/blinded_operator_sheet.csv`, `external_validation/method_alias_map.json`

- Required tasks: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`, `cable_route_insert`

### `bridge_method_adapters_and_hashes`

- Route: `maniskill_sapien_primary`
- Platform family: `ManiSkill/SAPIEN`
- Operator input: route run_method through real manifest-declared method implementations and emit policy_or_config_hash
- Required artifacts: `external_validation/method_implementation_packet.md`, `external_validation/method_implementation_work_orders.csv`

- Required hooks: `run_method`, `policy_or_config_hash`, `terminal_samples`

### `export_logs_videos_and_manifest_inputs`

- Route: `maniskill_sapien_primary`
- Platform family: `ManiSkill/SAPIEN`
- Operator input: write JSONL records and videos from the real backend, then hash-lock them into the manifest
- Required artifacts: `external_validation/logs/*.jsonl`, `external_validation/videos/<task_family>/`

- Required tasks: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`, `cable_route_insert`

## Strict Acceptance Commands

- `python scripts\build_external_backend_integration_packet.py`
- `python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json`
- `python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence.py --strict`
