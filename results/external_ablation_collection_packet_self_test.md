# External Ablation Collection Packet Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary packet ready: `true`.
Missing work order rejected: `true`.
Premature evidence promotion rejected: `true`.
Collection-budget shrink rejected: `true`.
Strict missing-ablation drift rejected: `true`.
Local reference variant drift rejected: `true`.
Manifest ablation boolean omission rejected: `true`.
Work-order artifact/command drift rejected: `true`.
Strict command drift rejected: `true`.
Real manifest write rejected: `true`.
Packet file deletion rejected: `true`.
Real ablation packet outputs untouched: `true`.

This self-test rebuilds the ablation collection packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing ablation work orders, premature strict-evidence promotion, shrunken ablation budgets, drift from the strict external-ablation blocker, local-reference variant drift, missing manifest ablation booleans, vague work-order artifacts or commands, strict command drift, accidental real manifest writes, and missing packet files without touching real ablation-packet outputs.

## Checks

- `pass` `temporary_ablation_collection_packet_ready_but_non_evidence`: status=0, passed=True, expected_records=600
- `pass` `missing_ablation_work_order_rejected`: check=False
- `pass` `premature_evidence_promotion_rejected`: check=False
- `pass` `collection_budget_shrink_rejected`: check=False
- `pass` `strict_missing_ablation_drift_rejected`: check=False
- `pass` `local_reference_variant_drift_rejected`: check=False
- `pass` `manifest_ablation_boolean_omission_rejected`: check=False
- `pass` `work_order_artifact_command_drift_rejected`: check=False
- `pass` `strict_command_drift_rejected`: check=False
- `pass` `real_manifest_write_rejected`: check=False
- `pass` `packet_file_deletion_rejected`: required temporary packet output check detects deleted ablation work-order CSV
- `pass` `real_ablation_packet_outputs_untouched`: before={'external_validation/ablation_collection_packet.json': '5b7814ef0c0555b0148b40b2d5e2b9db1069c9bc1e1686c96e1411b1fa36d94e', 'external_validation/ablation_collection_packet.md': 'ce3703f13541aafb56ea072107d224e585dbfcb3025b97c9940a6dcea536d545', 'external_validation/ablation_collection_work_orders.csv': 'b441b51baa4da00dec488c05e11ef8d381df1b2d742024936691a12b16cbb1b7', 'results/external_ablation_collection_audit.json': '586e5a58d35a79eab496934c9fd2c09421b364cac09f05c722fd0552a841a885', 'results/external_ablation_collection_audit.md': 'ce3703f13541aafb56ea072107d224e585dbfcb3025b97c9940a6dcea536d545', 'external_validation/manifest.json': None}, after={'external_validation/ablation_collection_packet.json': '5b7814ef0c0555b0148b40b2d5e2b9db1069c9bc1e1686c96e1411b1fa36d94e', 'external_validation/ablation_collection_packet.md': 'ce3703f13541aafb56ea072107d224e585dbfcb3025b97c9940a6dcea536d545', 'external_validation/ablation_collection_work_orders.csv': 'b441b51baa4da00dec488c05e11ef8d381df1b2d742024936691a12b16cbb1b7', 'results/external_ablation_collection_audit.json': '586e5a58d35a79eab496934c9fd2c09421b364cac09f05c722fd0552a841a885', 'results/external_ablation_collection_audit.md': 'ce3703f13541aafb56ea072107d224e585dbfcb3025b97c9940a6dcea536d545', 'external_validation/manifest.json': None}
