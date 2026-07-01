# External Config Materialization Self-Test

Passed: `true`.
Not evidence: `true`.
Strict config evidence ready: `false`.
Temporary plan ready: `true`.
Confirmed write fixture ready: `true`.
Write without confirmation rejected: `true`.
Placeholder platform write rejected: `true`.
Template token write rejected: `true`.
Missing task binding rejected: `true`.
Overwrite without force rejected: `true`.
Real config materialization outputs untouched: `true`.

This self-test exercises the guarded task-config materializer in temporary copied workspaces only. It proves the default plan writes no configs, a confirmed fixture write can materialize schema-valid task configs, and missing confirmation, placeholder platform names, template tokens, missing task bindings, and overwrite attempts fail closed without touching real prepared configs or materialization reports.

## Checks

- `pass` `temporary_config_materialization_plan_ready_but_non_evidence`: status=0, task_count=4, written=0
- `pass` `confirmed_temp_write_materializes_schema_valid_configs`: status=0, files_written=4, temp_files=4
- `pass` `write_without_confirmation_rejected`: status=1, written=0
- `pass` `placeholder_platform_write_rejected`: status=1, written=0
- `pass` `template_token_write_rejected`: status=1, written=0
- `pass` `missing_task_binding_file_rejected`: status=1, task_binding_check=False
- `pass` `overwrite_without_force_rejected`: second confirmed fixture write without --force is rejected
- `pass` `real_config_materialization_outputs_untouched`: tracked=7, changed=[]
