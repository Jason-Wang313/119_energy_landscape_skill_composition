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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=373, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=375, sha='223E171F76060FB4F6A3EF948B16AEACBC11860F605B97225CE7CD2404CEFB67'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '2bc62c828ab63a15c00640a49a44408dcc305012ae0c26064c406149764c6335', 'results/external_operator_release_bundle_plan.md': '3a0ac3736bf8dc768d495564e15d285cfb2d2d3a38907c7ab7e75b8421b6fd1e', 'external_validation/operator_release_bundle_manifest.csv': 'fe74ea9e980072158b2ef6f4e3c7a899e992b254b185b2de9b9b08bfa2485022', 'external_validation/operator_release_bundle_README.md': '79a2ce37b7cfbc894af533ea87981cfd21ca11d3ba6bcdfcbbecbca566da5c1d', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '2bc62c828ab63a15c00640a49a44408dcc305012ae0c26064c406149764c6335', 'results/external_operator_release_bundle_plan.md': '3a0ac3736bf8dc768d495564e15d285cfb2d2d3a38907c7ab7e75b8421b6fd1e', 'external_validation/operator_release_bundle_manifest.csv': 'fe74ea9e980072158b2ef6f4e3c7a899e992b254b185b2de9b9b08bfa2485022', 'external_validation/operator_release_bundle_README.md': '79a2ce37b7cfbc894af533ea87981cfd21ca11d3ba6bcdfcbbecbca566da5c1d', 'results/paper119_external_operator_release_bundle.zip': None}
