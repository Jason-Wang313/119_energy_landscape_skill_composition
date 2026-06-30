# External Operator Release Bundle Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary fixture ready: `true`.
Explicit archive fixture ready: `true`.
Missing handoff rejected: `true`.
Handoff no-go drift rejected: `true`.
Missing file rejected: `true`.
Hash drift rejected: `true`.
Forbidden evidence path rejected: `true`.
Premature manifest rejected: `true`.
Collection-job go-state rejected: `true`.
Collection-job omission rejected: `true`.
Real release outputs untouched: `true`.

This is a tooling-only mutation test. It rebuilds the operator release bundle plan in temporary copied workspaces, verifies the default no-archive path and explicit archive path, and proves missing handoff sources, no-go drift, missing files, hash drift, forbidden evidence paths, premature manifests, collection-job go-state drift, and collection-job omission fail closed without touching the real release outputs.

## Checks

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=382, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=384, sha='1B512AE9A573F614E4C8640A25E3ED29C8E485125D998D9C52AA02564F79D0B3'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'd4c08eaaf05de0e8e5a7c80f86b7954fa2bc542169e28dadf907d04658db8363', 'results/external_operator_release_bundle_plan.md': '295afd21a1e53fbcd3742e111f03edc9715ac64d552a7a55bc718d75272dab7d', 'external_validation/operator_release_bundle_manifest.csv': 'f82276d4d271dd5d1f836017f4ee01aea6eec841ac66588364f42c94a66a38a8', 'external_validation/operator_release_bundle_README.md': '094f88071327b7b30a79ff27fcca4a9a2baabb9715d297da782b8c4ace7b88e6', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'd4c08eaaf05de0e8e5a7c80f86b7954fa2bc542169e28dadf907d04658db8363', 'results/external_operator_release_bundle_plan.md': '295afd21a1e53fbcd3742e111f03edc9715ac64d552a7a55bc718d75272dab7d', 'external_validation/operator_release_bundle_manifest.csv': 'f82276d4d271dd5d1f836017f4ee01aea6eec841ac66588364f42c94a66a38a8', 'external_validation/operator_release_bundle_README.md': '094f88071327b7b30a79ff27fcca4a9a2baabb9715d297da782b8c4ace7b88e6', 'results/paper119_external_operator_release_bundle.zip': None}
