# External Method Config Materialization Self-Test

Passed: `true`.
Not evidence: `true`.
Strict adapter evidence ready: `false`.
Temporary materialization ready: `true`.
Premature evidence promotion rejected: `true`.
Missing candidate record rejected: `true`.
Oracle candidate rejected: `true`.
Candidate file hash drift rejected: `true`.
Manifest stub hash drift rejected: `true`.
Candidate evidence-content drift rejected: `true`.
Source method packet drift rejected: `true`.
Adapter evidence promotion rejected: `true`.
Baseline spec hash drift rejected: `true`.
Candidate CSV drift rejected: `true`.
Real manifest write rejected: `true`.
Materialization file deletion rejected: `true`.
Real method-config materialization outputs untouched: `true`.

This self-test rebuilds method-config materialization in temporary copied workspaces and mutates only those fixtures. It proves candidate method configs remain non-evidence and rejects missing or oracle candidates, stale candidate file hashes, manifest-stub hash drift, candidate config content promoted to evidence, source packet drift, adapter evidence promotion, baseline spec drift, CSV drift, accidental real manifest writes, and deleted materialization files without touching real method-config outputs.

## Checks

- `pass` `temporary_method_config_materialization_ready_but_non_evidence`: status=0, candidate_config_count=11
- `pass` `premature_evidence_promotion_rejected`: check=False
- `pass` `missing_candidate_record_rejected`: check=False
- `pass` `oracle_candidate_rejected`: check=False
- `pass` `candidate_file_hash_drift_rejected`: check=False
- `pass` `manifest_stub_hash_drift_rejected`: check=False
- `pass` `candidate_evidence_content_drift_rejected`: check=False
- `pass` `source_method_packet_drift_rejected`: check=False
- `pass` `adapter_evidence_promotion_rejected`: check=False
- `pass` `baseline_spec_hash_drift_rejected`: check=False
- `pass` `candidate_csv_drift_rejected`: check=False
- `pass` `real_manifest_write_rejected`: check=False
- `pass` `materialization_file_deletion_rejected`: required temporary materialization output check detects deleted candidate CSV
- `pass` `real_method_config_materialization_outputs_untouched`: tracked=17, changed=[]
