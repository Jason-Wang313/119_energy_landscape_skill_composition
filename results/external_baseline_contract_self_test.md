# External Baseline Contract Self-Test

Passed: `true`.
Not evidence: `true`.
Implementations ready: `false`.
Temporary contract ready: `true`.
Missing required method rejected: `true`.
Premature implementation promotion rejected: `true`.
Independent-source drift rejected: `true`.
Oracle-boundary drift rejected: `true`.
Fairness invariant shrink rejected: `true`.
Adapter API drift rejected: `true`.
Spec method-binding drift rejected: `true`.
Release-evidence spec drift rejected: `true`.
Policy/config log-field drift rejected: `true`.
Contract-file deletion rejected: `true`.
Real baseline-contract outputs untouched: `true`.

This tooling-only self-test rebuilds the baseline implementation contract in temporary copied workspaces. It proves the contract remains non-evidence and rejects missing required methods, premature implementation readiness, independent-source drift, oracle-boundary drift, weakened fairness invariants, adapter API drift, spec method-binding drift, missing release-evidence requirements, missing `policy_or_config_hash` log requirements, and deleted contract files without touching real baseline-contract outputs.

## Checks

- `pass` `temporary_baseline_contract_ready_but_non_evidence`: status=0, passed=True, methods=12
- `pass` `missing_required_method_rejected`: method_check=False
- `pass` `premature_implementation_promotion_rejected`: implementation_check=False
- `pass` `independent_source_drift_rejected`: source_check=False
- `pass` `oracle_boundary_drift_rejected`: oracle_check=False
- `pass` `fairness_invariant_shrink_rejected`: fairness_check=False
- `pass` `adapter_api_drift_rejected`: adapter_api_check=False
- `pass` `spec_method_binding_drift_rejected`: spec_binding_check=False
- `pass` `release_evidence_spec_drift_rejected`: release_evidence_check=False
- `pass` `policy_config_log_field_drift_rejected`: policy_hash_check=False
- `pass` `contract_file_deletion_rejected`: contract_file_check=False
- `pass` `real_baseline_contract_outputs_untouched`: changed=[]
