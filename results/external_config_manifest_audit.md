# External Config Manifest Audit

Passed: `true`.
Not evidence: `true`.
Config manifest packet ready: `true`.
Strict config evidence ready: `false`.
Manifest-declared config ready: `false`.

This audit checks that prepared task configs have a concrete path to manifest-declared config evidence while strict config evidence remains false until a real manifest and rollout artifacts exist.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `materialization_plan_ready_but_not_evidence`: passed=True, write_enabled=False
- `pass` `template_audit_passes`: config_count=4
- `pass` `strict_config_evidence_still_fails_without_manifest`: passed=False, config_count=0
- `pass` `manifest_template_declares_all_collection_tasks`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `prepared_config_files_have_hashes`: hashes=['8D041F5E869F4D81E2352D77A01C85EE585DF2040E45987750DF84B86EA94086', 'EABEA38D21F936A46C69E566D0324F7C42A8693CAA1D441B81C7E87B595FCA0D', '39697F0BA1ECBE013C1790455F26B68C927EEF97415A2BB49C6FD1440DEBEA9C', '15D687A12F9213E1EB410876203CE93F73E667C30E039685E151438017B3D7AD']
- `pass` `work_orders_cover_config_to_manifest_path`: missing=[]
- `pass` `strict_commands_cover_config_manifest_release_and_evidence`: commands=['python scripts\\build_external_config_manifest_packet.py', 'python scripts\\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write', 'python scripts\\build_external_manifest.py --write --check-video-paths', 'python scripts\\validate_external_configs.py --strict', 'python scripts\\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --run-id <specific_run_id> --unsealed-alias-map', 'python scripts\\audit_external_release_package.py --strict', 'python scripts\\audit_external_evidence.py --strict']
- `pass` `collection_readiness_preserves_config_boundary`: collection_ready=False, real_task_configs_ready=True, manifest_exists=False
- `pass` `manifest_template_paths_match_prepared_configs`: manifest_paths=['external_validation/configs/cable_route_insert.json', 'external_validation/configs/door_open_navigation.json', 'external_validation/configs/drawer_to_pick_transfer.json', 'external_validation/configs/peg_place_regrasp.json']
- `pass` `packet_files_written`: packet_json=True, packet_md=True, csv=True
