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
Missing Linux command spine rejected: `true`.
Hash gate drift rejected: `true`.
Render self-test drift rejected: `true`.
Real collection job outputs untouched: `true`.

This is a tooling-only mutation test. It rebuilds the collection job packet in temporary copied workspaces, then proves missing sources, source non-evidence drift, premature manifest presence, premature ready-state promotion, unsafe command-spine edits, missing Linux command-spine output, hash-gate drift, and render-machine self-test drift fail closed without touching the real collection job packet.

## Checks

- `pass` `temporary_fixture_builds_current_collection_job_packet`: status=0, job_state='DO_NOT_START_COLLECTION_YET', steps=17
- `pass` `missing_source_payload_rejected`: status=1, error='missing results/external_operator_packet.json'
- `pass` `source_non_evidence_drift_rejected`: status=1, source_check=False
- `pass` `premature_manifest_rejected`: status=1, no_manifest_check=False
- `pass` `premature_ready_state_rejected`: status=1, job_state='READY_FOR_OPERATOR_CONFIRMED_COLLECTION', fail_closed_check=False
- `pass` `unsafe_command_spine_rejected`: status=1, command_guard_check=False
- `pass` `missing_linux_command_spine_rejected`: status=1, error='missing external_validation/collection_job_commands.sh'
- `pass` `hash_gate_drift_rejected`: status=1, hash_gate_check=False
- `pass` `render_self_test_drift_rejected`: status=1, render_self_test_check=False
- `pass` `real_repository_collection_job_outputs_untouched`: before={'external_validation/collection_job_packet.json': '3ffb936bc442b13421393a684e7a2bc80ed29db5fd2b2dbc4429b96821edeb02', 'external_validation/collection_job_packet.md': '8f307ae6f9e06e49c3b7dc6e327d0024d96d7506628068b1d0131614678b0f8c', 'external_validation/collection_job_commands.ps1': '859953b47dae87355d0370d55fa56721af7440388852ba4ba5ff3a2acbf40c41', 'external_validation/collection_job_commands.sh': '707515d35111212bcd150d528adcdba6a8c0f5b0537d33cd0f823dc505de5ab1', 'external_validation/collection_job_checklist.csv': '2acb0609c9240407b17a89b07d968050fcdce0c1e076bc6e00db6b48f09d5388', 'results/external_collection_job_packet_audit.json': '6e836e64823a73acd851e0b1d3773ca46be81b41a7d97b5e38614886676a8108', 'results/external_collection_job_packet_audit.md': '374c5d80df23014da6cbb002f5572d7cc6c1bbd33b6745f4663f527d0f62ca69'}, after={'external_validation/collection_job_packet.json': '3ffb936bc442b13421393a684e7a2bc80ed29db5fd2b2dbc4429b96821edeb02', 'external_validation/collection_job_packet.md': '8f307ae6f9e06e49c3b7dc6e327d0024d96d7506628068b1d0131614678b0f8c', 'external_validation/collection_job_commands.ps1': '859953b47dae87355d0370d55fa56721af7440388852ba4ba5ff3a2acbf40c41', 'external_validation/collection_job_commands.sh': '707515d35111212bcd150d528adcdba6a8c0f5b0537d33cd0f823dc505de5ab1', 'external_validation/collection_job_checklist.csv': '2acb0609c9240407b17a89b07d968050fcdce0c1e076bc6e00db6b48f09d5388', 'results/external_collection_job_packet_audit.json': '6e836e64823a73acd851e0b1d3773ca46be81b41a7d97b5e38614886676a8108', 'results/external_collection_job_packet_audit.md': '374c5d80df23014da6cbb002f5572d7cc6c1bbd33b6745f4663f527d0f62ca69'}
