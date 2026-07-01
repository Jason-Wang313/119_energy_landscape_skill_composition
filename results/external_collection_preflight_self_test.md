# External Collection Preflight Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic collection ready: `true`.
Reference route ready after synthetic fidelity: `true`.
Synthetic row count: `1440`.

This self-test builds a temporary complete collection-preflight fixture and calls the collection readiness audit without writing the real readiness report. It proves the strict preflight gate can turn green when backend, configs, fidelity acceptance, aliases, logs, video directory, and run id are complete. It is not external validation evidence.

## Checks

- `pass` `synthetic_preflight_collection_ready`: collection_ready=True, blockers=[]
- `pass` `synthetic_row_budget`: row_count=1440
- `pass` `synthetic_backend_module_ready`: backend_module_ready=True
- `pass` `synthetic_real_task_configs_ready`: real_task_configs_ready=True
- `pass` `synthetic_fidelity_acceptance_ready`: fidelity_acceptance_ready=True
- `pass` `synthetic_alias_unsealing_explicit`: alias_unsealing_explicit=True
- `pass` `synthetic_run_id_specific`: run_id_specific=True
- `pass` `synthetic_output_logs_empty_or_force`: output_logs_empty_or_force=True
- `pass` `real_readiness_report_not_overwritten`: self-test uses build_payload only and leaves results/external_collection_readiness_audit.json unchanged
- `pass` `reference_route_collection_ready_after_synthetic_fidelity_acceptance`: collection_ready=True, blockers=[]
- `pass` `reference_route_core_checks_pass_after_synthetic_fidelity_acceptance`: reference_checks={'runner_exists': True, 'schema_exists': True, 'operator_sheet_exists': True, 'operator_sheet_columns': True, 'operator_sheet_row_budget': True, 'alias_map_exists': True, 'alias_map_complete': True, 'backend_module_ready': True, 'task_config_dir_exists': True, 'real_task_configs_ready': True, 'fidelity_acceptance_ready': True, 'alias_unsealing_explicit': True, 'run_id_specific': True, 'output_logs_empty_or_force': True, 'video_dir_parent_exists': True}
