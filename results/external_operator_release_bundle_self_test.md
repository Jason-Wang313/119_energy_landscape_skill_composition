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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=352, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=354, sha='D2DC8BB1EF6FDA07501791141CFE07682FCF043E578339797D1849095BC75964'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '570138aa2549820eb468c45f63630145b21d7a2cbae3d96411407a227627b586', 'results/external_operator_release_bundle_plan.md': '15fb5bb46549246228910abf1b7be53474dd2740d04d21cc324b5dd5070c41f1', 'external_validation/operator_release_bundle_manifest.csv': '94844d09cdea9019f45d37d32b778064420caaa701d72308b5676d4035ccf54b', 'external_validation/operator_release_bundle_README.md': '6985de3a6a253416ad5cdcbb2a82826f27f8358005cccde6fab66b1b1220e403', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '570138aa2549820eb468c45f63630145b21d7a2cbae3d96411407a227627b586', 'results/external_operator_release_bundle_plan.md': '15fb5bb46549246228910abf1b7be53474dd2740d04d21cc324b5dd5070c41f1', 'external_validation/operator_release_bundle_manifest.csv': '94844d09cdea9019f45d37d32b778064420caaa701d72308b5676d4035ccf54b', 'external_validation/operator_release_bundle_README.md': '6985de3a6a253416ad5cdcbb2a82826f27f8358005cccde6fab66b1b1220e403', 'results/paper119_external_operator_release_bundle.zip': None}
