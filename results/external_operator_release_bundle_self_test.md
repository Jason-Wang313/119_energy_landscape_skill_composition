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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=374, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=376, sha='2A63E5350EE250FB7E766A1818FA3630B8B5E55461383D811C2EFF8803FAB1FE'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'c4fc61cef5dde77b780afcca7ddeeb7573a8973ecd9ae03fc4c5e03298485af8', 'results/external_operator_release_bundle_plan.md': 'b4af16c9a55082e2d00a42d002cfb4e92e11e74c4a63a501d27f0cc4b57e2bf3', 'external_validation/operator_release_bundle_manifest.csv': 'b6e1575f15899f331de2a93c59111cb5ff2a1e494f9c4d88e99a2c55f91f752b', 'external_validation/operator_release_bundle_README.md': '4096e0c16828e8381eaed7a140868f46156b91f585964688b227af8a0d650efc', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'c4fc61cef5dde77b780afcca7ddeeb7573a8973ecd9ae03fc4c5e03298485af8', 'results/external_operator_release_bundle_plan.md': 'b4af16c9a55082e2d00a42d002cfb4e92e11e74c4a63a501d27f0cc4b57e2bf3', 'external_validation/operator_release_bundle_manifest.csv': 'b6e1575f15899f331de2a93c59111cb5ff2a1e494f9c4d88e99a2c55f91f752b', 'external_validation/operator_release_bundle_README.md': '4096e0c16828e8381eaed7a140868f46156b91f585964688b227af8a0d650efc', 'results/paper119_external_operator_release_bundle.zip': None}
