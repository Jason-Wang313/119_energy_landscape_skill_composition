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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=392, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=394, sha='22BAB6074B629077A13D17D3175DD8F3B84955A7DDFBA2829DB272215EFBE23A'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '52a207cb94f910346d08b8160de63efd6667519bc9512fd45fd3fcc1dd97f03e', 'results/external_operator_release_bundle_plan.md': '9bcdeb9122b9e36c3a0fd1b6909b3cb438efb79b168005ae96ebb225064284ba', 'external_validation/operator_release_bundle_manifest.csv': '273ed2e932370ce5d882b248cae0cee94479e5094533bfc13596bb57431687f3', 'external_validation/operator_release_bundle_README.md': 'e94aced88b863f4ccf5b90435c40347e4d3da6deb1767dc7c4e0dde3838a92d6', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '52a207cb94f910346d08b8160de63efd6667519bc9512fd45fd3fcc1dd97f03e', 'results/external_operator_release_bundle_plan.md': '9bcdeb9122b9e36c3a0fd1b6909b3cb438efb79b168005ae96ebb225064284ba', 'external_validation/operator_release_bundle_manifest.csv': '273ed2e932370ce5d882b248cae0cee94479e5094533bfc13596bb57431687f3', 'external_validation/operator_release_bundle_README.md': 'e94aced88b863f4ccf5b90435c40347e4d3da6deb1767dc7c4e0dde3838a92d6', 'results/paper119_external_operator_release_bundle.zip': None}
