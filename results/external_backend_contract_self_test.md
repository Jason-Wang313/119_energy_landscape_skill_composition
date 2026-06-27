# External Backend Contract Self-Test

Passed: `true`.
Not evidence: `true`.

This self-test builds temporary backend modules and exercises the strict backend qualification gate. It verifies that a complete synthetic backend passes, incomplete/base-method implementations fail, template backends fail, and the real backend audit report is not overwritten.

## Checks

- `pass` `strict_complete_backend_passes`: passed=True, actual_backend_ready=True
- `pass` `strict_incomplete_backend_fails`: backend_contract_complete: backend uses base NotImplementedError implementation for load_task_config; backend uses base NotImplementedError implementation for reset_scene; backend uses base NotImplementedError implementation for capture_observation; backend uses base NotImplementedError implementation for terminal_samples; backend uses base NotImplementedError implementation for run_method; backend uses base NotImplementedError implementation for execute_skill_pair; backend uses base NotImplemen
- `pass` `strict_template_backend_fails`: backend_contract_complete: backend has TEMPLATE_ONLY=True and cannot collect evidence
backend_platform_provenance_complete: NotImplementedError: real backend must report platform provenance
backend_loads_all_task_configs: cable_route_insert: NotImplementedError: real backend must load task config; door_open_navigation: NotImplementedError: real backend must load task config; drawer_to_pick_transfer: NotImplementedError: real backend must load task config; peg_place_regrasp: NotImplementedError: 
- `pass` `default_missing_backend_remains_nonready`: passed=True, actual_backend_ready=False
- `pass` `real_backend_contract_report_not_overwritten`: self-test calls build_payload only and leaves results/external_backend_contract_audit.json unchanged
