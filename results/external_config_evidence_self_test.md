# External Config Evidence Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic strict config evidence ready: `true`.
Prepared config fixture ready: `true`.

This self-test builds temporary manifest-declared task configs and exercises the strict external-config evidence gate directly. It proves complete synthetic configs can pass, the prepared task configs can bind to a temporary strict manifest with recomputed hashes, missing manifests fail, stale manifest config hashes fail, template configs are rejected as evidence, and the real config evidence audit report is not overwritten.

## Checks

- `pass` `synthetic_strict_configs_pass`: passed=True, config_count=4
- `pass` `synthetic_manifest_entries_cover_tasks`: config_count=4
- `pass` `prepared_task_configs_pass_strict_with_temp_manifest`: passed=True, config_count=4, checks={'config_schema_exists': True, 'config_schema_version': True, 'manifest_exists': True, 'manifest_config_entries_present': True, 'configs_pass_validation': True}
- `pass` `prepared_task_config_methods_match_collection_tasks`: prepared_tasks=4, config_results=4
- `pass` `missing_manifest_fails_strict`: passed=False, checks={'config_schema_exists': True, 'config_schema_version': True, 'manifest_exists': False, 'manifest_config_entries_present': False, 'configs_pass_validation': False}
- `pass` `stale_manifest_config_hash_fails_strict`: passed=False, errors=['manifest config_hash does not match config_path']
- `pass` `template_configs_rejected_as_strict_evidence`: failed_configs=4
- `pass` `real_config_evidence_report_not_overwritten`: before=7396c0d98cf0ec1a9eb5525fbd75b90e9615d4cb923ab480b6bfcafa45624d69, after=7396c0d98cf0ec1a9eb5525fbd75b90e9615d4cb923ab480b6bfcafa45624d69
