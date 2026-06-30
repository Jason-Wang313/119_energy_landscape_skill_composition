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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=398, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=400, sha='BFDAD283308D42BA4BE0485951CA80C5E4246B3D4393D0E38FFD3E95362BF640'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'a70453503751709291121e98e6b35bf7fa7298d51e312063405fce1e64de3941', 'results/external_operator_release_bundle_plan.md': '9fee689842d18f56e03c54a2cedd7c48023f04018b3c04a08a1746507231c145', 'external_validation/operator_release_bundle_manifest.csv': '76efc573dcee6795e9e8d6a8ca1be5f71e6d40199c4400f8a867247e4ae6de19', 'external_validation/operator_release_bundle_README.md': '5e188b2ae21e412f1c6fe06b58120f92c708e3d11da7e68e1426a225435f62d6', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'a70453503751709291121e98e6b35bf7fa7298d51e312063405fce1e64de3941', 'results/external_operator_release_bundle_plan.md': '9fee689842d18f56e03c54a2cedd7c48023f04018b3c04a08a1746507231c145', 'external_validation/operator_release_bundle_manifest.csv': '76efc573dcee6795e9e8d6a8ca1be5f71e6d40199c4400f8a867247e4ae6de19', 'external_validation/operator_release_bundle_README.md': '5e188b2ae21e412f1c6fe06b58120f92c708e3d11da7e68e1426a225435f62d6', 'results/paper119_external_operator_release_bundle.zip': None}
