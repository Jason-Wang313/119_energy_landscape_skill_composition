# External Backend Integration Packet Self-Test

Passed: `true`.
Not evidence: `true`.
Strict backend ready: `false`.
Temporary packet ready: `true`.
Missing work orders rejected: `true`.
Work-order artifact/command drift rejected: `true`.
Premature backend/evidence promotion rejected: `true`.
Route independence drift rejected: `true`.
Actual-backend promotion rejected: `true`.
Hook contract drift rejected: `true`.
Provenance field drift rejected: `true`.
Task-budget shrink rejected: `true`.
Strict command drift rejected: `true`.
Collection-ready promotion rejected: `true`.
Real backend file write rejected: `true`.
Packet file deletion rejected: `true`.
Real backend-integration outputs untouched: `true`.

This self-test rebuilds the backend integration packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing or vague backend work orders, premature backend/evidence readiness, Haonan-dependence drift, false actual-backend readiness, missing hooks/provenance, shrunken task budgets, strict-command drift, premature collection readiness, accidental real backend files, and missing packet files without touching real backend-integration outputs.

## Checks

- `pass` `temporary_backend_integration_packet_ready_but_non_evidence`: status=0, passed=True, records=1440, orders=5
- `pass` `missing_work_orders_rejected`: work_order_check=False
- `pass` `work_order_artifact_command_drift_rejected`: actionable_check=False
- `pass` `premature_backend_evidence_promotion_rejected`: non_evidence_check=False
- `pass` `route_independence_drift_rejected`: route_check=False
- `pass` `actual_backend_promotion_rejected`: backend_check=False
- `pass` `hook_contract_drift_rejected`: hook_check=False
- `pass` `provenance_field_drift_rejected`: provenance_check=False
- `pass` `task_budget_shrink_rejected`: budget_check=False
- `pass` `strict_command_drift_rejected`: command_check=False
- `pass` `collection_ready_promotion_rejected`: collection_check=False
- `pass` `real_backend_file_write_rejected`: backend_file_check=False
- `pass` `packet_file_deletion_rejected`: packet_file_check=False
- `pass` `real_backend_integration_outputs_untouched`: changed=[]
