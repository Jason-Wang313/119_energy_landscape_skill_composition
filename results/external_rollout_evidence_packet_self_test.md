# External Rollout Evidence Packet Self-Test

Passed: `true`.
Not evidence: `true`.
Strict rollout evidence ready: `false`.
Temporary packet ready: `true`.
Missing task work orders rejected: `true`.
Premature evidence promotion rejected: `true`.
Manifest schema-error drift rejected: `true`.
Observed-record drift rejected: `true`.
Collection-budget shrink rejected: `true`.
Strict command drift rejected: `true`.
Downstream gate promotion rejected: `true`.
Real output write rejected: `true`.
Real rollout packet outputs untouched: `true`.

This self-test rebuilds the rollout evidence packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing task-specific JSONL/video work orders, premature strict-evidence promotion, loss of the missing-manifest rollout-metrics signal, fake observed-record drift, shrunken collection budgets, strict rollout-command drift, downstream gate promotion, and accidental manifest/log/video writes without touching the real rollout packet outputs.

## Checks

- `pass` `temporary_rollout_packet_ready_but_non_evidence`: status=0, passed=True, expected=1440, observed=0
- `pass` `missing_task_work_orders_rejected`: task_order_check=False
- `pass` `premature_evidence_promotion_rejected`: non_evidence_check=False
- `pass` `manifest_schema_error_drift_rejected`: manifest_error_check=False
- `pass` `observed_record_drift_rejected`: observed_record_check=False
- `pass` `collection_budget_shrink_rejected`: budget_check=False
- `pass` `strict_command_drift_rejected`: command_check=False
- `pass` `downstream_gate_promotion_rejected`: downstream_gate_check=False
- `pass` `real_output_write_rejected`: real_output_check=False
- `pass` `real_rollout_packet_outputs_untouched`: changed=[]
