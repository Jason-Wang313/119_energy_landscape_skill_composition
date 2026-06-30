# External Precollection Manifest Draft Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary draft ready: `true`.
Premature evidence promotion rejected: `true`.
Missing prepared-config hash rejected: `true`.
Task config path drift rejected: `true`.
Candidate method-config hash drift rejected: `true`.
Method blocker omission rejected: `true`.
Rollout gap omission rejected: `true`.
Source report drift rejected: `true`.
Cutover command drift rejected: `true`.
Real manifest write rejected: `true`.
Draft file deletion rejected: `true`.
Real precollection-manifest outputs untouched: `true`.

This self-test rebuilds the precollection manifest draft in temporary copied workspaces and mutates only those fixtures. It proves the draft remains non-evidence and rejects premature strict-evidence promotion, missing prepared task-config hashes, task-config path drift, candidate method-config hash drift, omitted independent-method blockers, omitted rollout gaps, stale source reports, cutover-command drift, accidental official manifest writes, and missing draft files without touching real precollection-manifest outputs.

## Checks

- `pass` `temporary_precollection_manifest_draft_ready_but_non_evidence`: status=0, configs=4, methods=11
- `pass` `premature_evidence_promotion_rejected`: check=False
- `pass` `missing_prepared_config_hash_rejected`: check=False
- `pass` `task_config_path_drift_rejected`: check=False
- `pass` `candidate_method_config_hash_drift_rejected`: check=False
- `pass` `method_blocker_omission_rejected`: check=False
- `pass` `rollout_gap_omission_rejected`: check=False
- `pass` `source_report_drift_rejected`: check=False
- `pass` `cutover_command_drift_rejected`: check=False
- `pass` `real_manifest_write_rejected`: check=False
- `pass` `draft_file_deletion_rejected`: required temporary draft output check detects deleted precollection manifest markdown
- `pass` `real_precollection_manifest_outputs_untouched`: before={'external_validation/manifest_precollection_draft.json': '2efde6f059def0dc03a12baffdcd3e39973ecab4424ca5bcb6b5bc29263fbdb8', 'external_validation/manifest_precollection_draft.md': '0db9bb55d0e70b38e9c96321298309a9c54977e6b137258ef6fa2c0df8879b43', 'results/external_precollection_manifest_draft_audit.json': '5ea5219c264b754dcdeb65b3dc107c99fcf834e6909bf707082abcb537a548bf', 'results/external_precollection_manifest_draft_audit.md': '04d1e0d920d763eaabcbf93fd3378ba2b261c7dcef43ee0e6e2125c6b5cd89e5', 'external_validation/manifest.json': None}, after={'external_validation/manifest_precollection_draft.json': '2efde6f059def0dc03a12baffdcd3e39973ecab4424ca5bcb6b5bc29263fbdb8', 'external_validation/manifest_precollection_draft.md': '0db9bb55d0e70b38e9c96321298309a9c54977e6b137258ef6fa2c0df8879b43', 'results/external_precollection_manifest_draft_audit.json': '5ea5219c264b754dcdeb65b3dc107c99fcf834e6909bf707082abcb537a548bf', 'results/external_precollection_manifest_draft_audit.md': '04d1e0d920d763eaabcbf93fd3378ba2b261c7dcef43ee0e6e2125c6b5cd89e5', 'external_validation/manifest.json': None}
