# External Collection Job Packet Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary fixture ready: `true`.
Missing source rejected: `true`.
Source evidence drift rejected: `true`.
Premature manifest rejected: `true`.
Premature ready state rejected: `true`.
Unsafe command spine rejected: `true`.
Hash gate drift rejected: `true`.
Render self-test drift rejected: `true`.
Real collection job outputs untouched: `true`.

This is a tooling-only mutation test. It rebuilds the collection job packet in temporary copied workspaces, then proves missing sources, source non-evidence drift, premature manifest presence, premature ready-state promotion, unsafe command-spine edits, hash-gate drift, and render-machine self-test drift fail closed without touching the real collection job packet.

## Checks

- `pass` `temporary_fixture_builds_current_collection_job_packet`: status=0, job_state='DO_NOT_START_COLLECTION_YET', steps=17
- `pass` `missing_source_payload_rejected`: status=1, error='missing results/external_operator_packet.json'
- `pass` `source_non_evidence_drift_rejected`: status=1, source_check=False
- `pass` `premature_manifest_rejected`: status=1, no_manifest_check=False
- `pass` `premature_ready_state_rejected`: status=1, job_state='READY_FOR_OPERATOR_CONFIRMED_COLLECTION', fail_closed_check=False
- `pass` `unsafe_command_spine_rejected`: status=1, command_guard_check=False
- `pass` `hash_gate_drift_rejected`: status=1, hash_gate_check=False
- `pass` `render_self_test_drift_rejected`: status=1, render_self_test_check=False
- `pass` `real_repository_collection_job_outputs_untouched`: before={'external_validation/collection_job_packet.json': 'b74b08b146454a8ae9bc94aeb1059eaf355f509573cbd18c54e65d0aa70e2ead', 'external_validation/collection_job_packet.md': 'f4860ef625547478173c792f5fc93d1b1c27baf4cf7301ca030b476ed3e96a11', 'external_validation/collection_job_commands.ps1': '859953b47dae87355d0370d55fa56721af7440388852ba4ba5ff3a2acbf40c41', 'external_validation/collection_job_checklist.csv': '2acb0609c9240407b17a89b07d968050fcdce0c1e076bc6e00db6b48f09d5388', 'results/external_collection_job_packet_audit.json': '9d02c547036cf06e3fff3b4ed33994fcdb031255ce6e890b86373dc3f5b2f28d', 'results/external_collection_job_packet_audit.md': 'a6ae1d5685e70291378d58638e2529c4588d5090d2193bd1e74e96220510ab28'}, after={'external_validation/collection_job_packet.json': 'b74b08b146454a8ae9bc94aeb1059eaf355f509573cbd18c54e65d0aa70e2ead', 'external_validation/collection_job_packet.md': 'f4860ef625547478173c792f5fc93d1b1c27baf4cf7301ca030b476ed3e96a11', 'external_validation/collection_job_commands.ps1': '859953b47dae87355d0370d55fa56721af7440388852ba4ba5ff3a2acbf40c41', 'external_validation/collection_job_checklist.csv': '2acb0609c9240407b17a89b07d968050fcdce0c1e076bc6e00db6b48f09d5388', 'results/external_collection_job_packet_audit.json': '9d02c547036cf06e3fff3b4ed33994fcdb031255ce6e890b86373dc3f5b2f28d', 'results/external_collection_job_packet_audit.md': 'a6ae1d5685e70291378d58638e2529c4588d5090d2193bd1e74e96220510ab28'}
