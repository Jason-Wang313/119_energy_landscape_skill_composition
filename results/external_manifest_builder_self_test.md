# External Manifest Builder Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic manifest written: `true`.
Synthetic records loaded: `1440`.

This self-test builds a temporary complete manifest fixture with raw JSONL logs, videos, configs, method implementations, checkpoints, and release artifacts. It exercises the external manifest builder's hash, record-loading, metric-recompute, report, and manifest-write path without touching the real `external_validation/manifest.json` or real manifest-builder report.

## Checks

- `pass` `synthetic_manifest_builder_ready`: ready=True, records=1440, schema_errors=0
- `pass` `synthetic_manifest_written_to_temp_output`: exists=True, version='external_validation_v1'
- `pass` `raw_logs_drive_manifest_metrics`: success_margin=0.19999999999999996, utility_margin=0.30999999999999994, paired_win_rate=1.0
- `pass` `release_artifacts_scanned_from_temp_workspace`: counts={'code': 13, 'configs': 4, 'logs': 4, 'videos': 4, 'checkpoints': 12}
- `pass` `config_and_method_hashes_materialized`: tasks=4, methods=12
- `pass` `manifest_report_and_checklist_written_in_temp_workspace`: checklist_rows=35
- `pass` `partial_manifest_with_missing_method_refuses_write`: ready=False, written=False, write_blockers=1
- `pass` `real_manifest_template_remains_fail_closed`: template_status={'ready_to_write_manifest': False, 'records_loaded': 0, 'schema_error_count': 4, 'warning_count': 11, 'manifest_write_blocking_count': 28}
- `pass` `real_manifest_and_reports_not_overwritten`: before={'external_validation/manifest.json': None, 'external_validation/manifest_assembly_checklist.csv': '572827C87C44B677B5897E2215FB3741E38000A40C23AF5141AFBC923D31FAEA', 'results/external_manifest_builder_report.json': 'E42AA95FC6891B19A22EA26DDB1249D711A1D85C7531F906D476F3AF738FE852', 'results/external_manifest_builder_report.md': 'F616DFADCC8944C7029F1EE3D9E3DE0EFB46823580B7E1DB809CAE3F166A58C4'}, after={'external_validation/manifest.json': None, 'external_validation/manifest_assembly_checklist.csv': '572827C87C44B677B5897E2215FB3741E38000A40C23AF5141AFBC923D31FAEA', 'results/external_manifest_builder_report.json': 'E42AA95FC6891B19A22EA26DDB1249D711A1D85C7531F906D476F3AF738FE852', 'results/external_manifest_builder_report.md': 'F616DFADCC8944C7029F1EE3D9E3DE0EFB46823580B7E1DB809CAE3F166A58C4'}
