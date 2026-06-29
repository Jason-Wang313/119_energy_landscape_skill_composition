# External Adapter Evidence Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic strict adapter evidence ready: `true`.

This self-test builds temporary manifest-declared adapter implementations and exercises the strict external-adapter evidence gate directly. It proves complete synthetic adapters can pass, missing manifests fail, scaffold templates and reference adapters are rejected as evidence, implementation-source hashes cannot replace checkpoint/config artifacts, and the real adapter evidence audit report is not overwritten.

## Checks

- `pass` `synthetic_strict_adapters_pass`: passed=True, adapter_count=11
- `pass` `synthetic_manifest_entries_cover_non_oracle_methods`: methods=11
- `pass` `missing_manifest_fails_strict`: passed=False, checks={'baseline_specs_present': True, 'contract_self_test_passed': True, 'log_schema_exists': True, 'manifest_exists': False, 'manifest_implementation_entries_present': False, 'manifest_declares_all_required_non_oracle_methods': False, 'manifest_has_no_duplicate_or_malformed_non_oracle_methods': True, 'manifest_implementation_entries_cover_required_non_oracle_methods': False, 'manifest_checkpoint_or_config_artifacts_declared': False, 'manifest_required_hashes_match_artifacts': False, 'manifest_independent_provenance_declared': False, 'adapter_results_passed': False}
- `pass` `leaky_or_reference_provenance_fails_strict`: passed=False, checks={'baseline_specs_present': True, 'contract_self_test_passed': True, 'log_schema_exists': True, 'manifest_exists': True, 'manifest_implementation_entries_present': True, 'manifest_declares_all_required_non_oracle_methods': True, 'manifest_has_no_duplicate_or_malformed_non_oracle_methods': True, 'manifest_implementation_entries_cover_required_non_oracle_methods': True, 'manifest_checkpoint_or_config_artifacts_declared': True, 'manifest_required_hashes_match_artifacts': True, 'manifest_independent_provenance_declared': False, 'adapter_results_passed': True}
- `pass` `implementation_hash_cannot_replace_checkpoint_or_config`: passed=False, checks={'baseline_specs_present': True, 'contract_self_test_passed': True, 'log_schema_exists': True, 'manifest_exists': True, 'manifest_implementation_entries_present': True, 'manifest_declares_all_required_non_oracle_methods': True, 'manifest_has_no_duplicate_or_malformed_non_oracle_methods': True, 'manifest_implementation_entries_cover_required_non_oracle_methods': True, 'manifest_checkpoint_or_config_artifacts_declared': False, 'manifest_required_hashes_match_artifacts': False, 'manifest_independent_provenance_declared': True, 'adapter_results_passed': True}
- `pass` `scaffold_adapters_rejected_as_strict_evidence`: failed_adapters=11
- `pass` `reference_adapters_rejected_as_strict_evidence`: failed_adapters=11
- `pass` `real_adapter_evidence_report_not_overwritten`: before=76bcad615bc07c1a68227015d77c9f52b0e5c66a1d31bf1c0fe6f3b320da36d1, after=76bcad615bc07c1a68227015d77c9f52b0e5c66a1d31bf1c0fe6f3b320da36d1
