# External Operator Handoff Bundle Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary fixture ready: `true`.
Missing source rejected: `true`.
No-go drift rejected: `true`.
Acquisition blocker drift rejected: `true`.
Strict evidence drift rejected: `true`.
Missing included file rejected: `true`.
Forbidden evidence path rejected: `true`.
Premature manifest rejected: `true`.
Missing collection job rejected: `true`.
Missing machine bootstrap rejected: `true`.
Real handoff outputs untouched: `true`.

This is a tooling-only mutation test. It rebuilds the operator handoff bundle in temporary copied workspaces and proves the handoff fails closed when source packets are missing, the no-go stance drifts, acquisition blockers disappear prematurely, strict evidence gates flip ready, included files are missing, forbidden evidence paths are inserted, a real manifest appears, or the collection job/bootstrap packets are omitted.

## Checks

- `pass` `temporary_fixture_builds_current_handoff_bundle`: status=0, files=392, start_state='DO_NOT_COLLECT_YET'
- `pass` `missing_source_rejected`: status=1, error='missing results/external_operator_packet.json'
- `pass` `no_go_drift_rejected`: status=1, no_go_check=False
- `pass` `acquisition_blocker_drift_rejected`: status=1, acquisition_check=False
- `pass` `strict_evidence_drift_rejected`: status=1, strict_check=False
- `pass` `missing_included_file_rejected`: status=1, files_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `missing_collection_job_rejected`: status=1, job_check=False
- `pass` `missing_machine_bootstrap_rejected`: status=1, bootstrap_check=False
- `pass` `real_repository_handoff_outputs_untouched`: before={'results/external_operator_handoff_bundle.json': '098a014d1dc2103b2e2f15386ab01ba317dc6916c2cea905839488feef37ac65', 'results/external_operator_handoff_bundle.md': '2b77544edd424b73b4b1eaf4363517d53fe982922ff89486066dcfd0baea7811'}, after={'results/external_operator_handoff_bundle.json': '098a014d1dc2103b2e2f15386ab01ba317dc6916c2cea905839488feef37ac65', 'results/external_operator_handoff_bundle.md': '2b77544edd424b73b4b1eaf4363517d53fe982922ff89486066dcfd0baea7811'}
