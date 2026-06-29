# External Postcollection Seal Consistency Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic consistency ready: `true`.
Drift rejected: `true`.
Unsealed official artifact rejected: `true`.

This self-test builds a temporary postcollection seal fixture and exercises the consistency gate directly. It proves the ready path can pass for a complete sealed raw-log/video/config set, hash drift fails, unsealed official artifacts fail, and the real consistency report is not overwritten.

## Checks

- `pass` `synthetic_ready_seal_consistency_passes`: passed=True, ready=True, records=3, videos=3, matched=7
- `pass` `synthetic_ready_checks_cover_hashes_counts_and_order`: ready_checks={'postcollection_seal_artifacts_loaded': True, 'consistency_gate_is_non_evidence_and_fail_closed': True, 'sealed_hashes_recompute_without_drift': True, 'no_unsealed_official_artifacts_before_manifest_promotion': True, 'manifest_promotion_requires_ready_seal_and_consistency': True, 'current_counts_match_default_or_ready_state': True, 'no_real_manifest_written_before_seal_consistency': True, 'strict_sequence_places_consistency_after_seal_before_manifest': True, 'consistency_gate_references_rollout_pairing_release_final_gates': True}
- `pass` `hash_drift_rejected`: passed=False, mismatches=[{'path': 'external_validation/configs/peg_place_regrasp.json', 'expected': '0086D12A1265FAFCE70D25BB84157EC30F0A355F696E7CE571AE228877AB4C0E', 'actual': '22A98161257BACB5F81EA0016990A2CB56E3EB6246A9E436171E14FCE54557EE'}]
- `pass` `hash_drift_fails_recompute_and_promotion_checks`: drift_checks={'postcollection_seal_artifacts_loaded': True, 'consistency_gate_is_non_evidence_and_fail_closed': False, 'sealed_hashes_recompute_without_drift': False, 'no_unsealed_official_artifacts_before_manifest_promotion': True, 'manifest_promotion_requires_ready_seal_and_consistency': False, 'current_counts_match_default_or_ready_state': True, 'no_real_manifest_written_before_seal_consistency': True, 'strict_sequence_places_consistency_after_seal_before_manifest': True, 'consistency_gate_references_rollout_pairing_release_final_gates': True}
- `pass` `unsealed_official_artifact_rejected`: passed=False, extra=['external_validation/videos/peg_place_regrasp/unsealed_extra.mp4']
- `pass` `unsealed_artifact_fails_official_artifact_check`: extra_checks={'postcollection_seal_artifacts_loaded': True, 'consistency_gate_is_non_evidence_and_fail_closed': False, 'sealed_hashes_recompute_without_drift': True, 'no_unsealed_official_artifacts_before_manifest_promotion': False, 'manifest_promotion_requires_ready_seal_and_consistency': False, 'current_counts_match_default_or_ready_state': True, 'no_real_manifest_written_before_seal_consistency': True, 'strict_sequence_places_consistency_after_seal_before_manifest': True, 'consistency_gate_references_rollout_pairing_release_final_gates': True}
- `pass` `real_consistency_report_not_overwritten`: before=91d1c2818f2f135d642077a778c1dda98565224068060732b86d08a998c99789, after=91d1c2818f2f135d642077a778c1dda98565224068060732b86d08a998c99789
