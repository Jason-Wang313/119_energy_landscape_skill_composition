# External Backend Integration Audit

Passed: `true`.
Not evidence: `true`.
Backend integration packet ready: `true`.
Strict backend ready: `false`.
Strict evidence ready: `false`.

This audit checks that the missing backend module has concrete integration work orders while strict backend readiness and strict external evidence remain false.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_backend_ready=False, strict_evidence_ready=False
- `pass` `primary_route_matches_onboarding`: route='maniskill_sapien_primary', platform='ManiSkill/SAPIEN'
- `pass` `backend_contract_harness_ready_but_backend_missing`: actual_backend_ready=False
- `pass` `work_orders_cover_backend_to_manifest_path`: missing=[]
- `pass` `required_hooks_declared`: hooks=['platform_provenance', 'load_task_config', 'reset_scene', 'capture_observation', 'terminal_samples', 'run_method', 'execute_skill_pair', 'record_video', 'policy_or_config_hash']
- `pass` `provenance_fields_declared`: provenance_fields=17
- `pass` `tasks_and_record_budget_preserved`: tasks=['peg_place_regrasp', 'drawer_to_pick_transfer', 'door_open_navigation', 'cable_route_insert'], records=1440
- `pass` `strict_commands_cover_backend_config_fidelity_collection_and_evidence`: commands=['python scripts\\build_external_backend_integration_packet.py', 'python scripts\\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json', 'python scripts\\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write', 'python scripts\\validate_external_configs.py --strict', 'python scripts\\audit_external_fidelity_acceptance.py --strict', 'python scripts\\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --run-id <specific_run_id> --unsealed-alias-map', 'python external_validation\\runner\\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id <specific_run_id> --unsealed-alias-map', 'python scripts\\build_external_manifest.py --write --check-video-paths', 'python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict', 'python scripts\\audit_external_pairing_integrity.py --strict', 'python scripts\\audit_external_release_package.py --strict', 'python scripts\\audit_external_evidence.py --strict']
- `pass` `collection_readiness_still_blocks_backend`: collection_ready=False, blockers=['backend_module_ready: --backend-module is required before actual collection', "fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'", 'alias_unsealing_explicit: unsealed_alias_map=False', "run_id_specific: run_id='paper119_external_validation_run'"]
- `pass` `no_real_backend_files_created`: external_validation/runner/backends is intentionally absent until an independent operator supplies a backend
- `pass` `packet_files_written`: packet_json=True, packet_md=True, csv=True
