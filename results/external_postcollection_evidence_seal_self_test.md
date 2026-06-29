# External Postcollection Evidence Seal Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic seal ready: `true`.
Missing operator metadata rejected: `true`.
Incomplete video set rejected: `true`.
Manifest-present promotion rejected: `true`.

This self-test builds temporary postcollection seal fixtures and exercises the seal builder directly. It proves a complete sealed raw-log/video/config fixture can reach manifest-promotion readiness, while missing operator metadata, incomplete official videos, and a pre-existing manifest remain fail-closed without overwriting the real seal or audit.

## Checks

- `pass` `synthetic_complete_seal_reaches_manifest_promotion`: seal_ready=True, promotion=True, records=3, videos=3, artifacts=12
- `pass` `synthetic_ready_checks_cover_order_inventory_and_boundary`: ready_checks={'seal_is_non_evidence_and_fail_closed': True, 'precollection_freeze_loaded_but_not_real_ready': True, 'raw_logs_and_videos_absent_before_collection': True, 'operator_metadata_still_required': True, 'hash_inventory_written_for_precollection_inputs': True, 'strict_sequence_places_seal_after_collection_before_manifest': True, 'seal_references_consistency_gate_before_manifest': True, 'seal_references_rollout_pairing_release_final_gates': True, 'strict_evidence_gates_still_false': True, 'no_real_manifest_written': True}
- `pass` `missing_operator_metadata_rejected`: seal_ready=False, operator_check=False
- `pass` `incomplete_video_set_rejected`: seal_ready=False, records=3, videos=2
- `pass` `manifest_present_rejected_before_promotion`: seal_ready=False, manifest_exists=True
- `pass` `real_postcollection_seal_reports_not_overwritten`: seal_before=8438c9260339d4a63051f3cdc0afdc918ee091f70cb77cde53f2a84164a954cd, seal_after=8438c9260339d4a63051f3cdc0afdc918ee091f70cb77cde53f2a84164a954cd, audit_before=d0f4d0ed189b831f0477cc0d61fa7a7e3c541b711852b25fcd12ca7fd721cfa7, audit_after=d0f4d0ed189b831f0477cc0d61fa7a7e3c541b711852b25fcd12ca7fd721cfa7
