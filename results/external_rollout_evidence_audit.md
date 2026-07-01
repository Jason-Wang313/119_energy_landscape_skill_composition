# External Rollout Evidence Audit

Passed: `true`.
Not evidence: `true`.
Expected records: `1440`.
Observed records: `0`.

This audit checks that the rollout evidence packet is complete as an operator checklist while strict rollout and external evidence gates remain fail-closed.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `strict_rollout_metrics_still_fail_without_manifest`: passed=False, schema_errors=['missing manifest C:\\Users\\wangz\\robotics_massive_pool_paper_factory\\119_energy_landscape_skill_composition\\external_validation\\manifest.json']
- `pass` `preflight_ready_but_observes_zero_real_records`: expected=1440, observed=0
- `pass` `collection_plan_record_budget_ge_1440`: records=1440, tasks=4, methods=12
- `pass` `task_work_orders_cover_all_planned_tasks`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `strict_commands_cover_collection_manifest_rollout_pairing_release_evidence`: python scripts\build_external_rollout_evidence_packet.py
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
python scripts\audit_external_postcollection_seal_consistency.py
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_evidence.py --strict
- `pass` `strict_gate_audits_remain_fail_closed`: pairing_ready=False, release_package_ready=False, submission_ready=False
- `pass` `no_real_manifest_or_logs_written`: manifest_exists=False, log_files=0, video_dirs=0
- `pass` `packet_files_written`: packet_json=True, packet_md=True, csv=True
