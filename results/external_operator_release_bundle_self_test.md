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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=355, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=357, sha='074AC7BFB5C468E4FF98EB7A762E5D1B1921CF28D1C2FDED79DD11EADEEB15CD'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'e9bba20ede8dd836cddf5338b336108fc2fbe11289c869364030ce460d907ae5', 'results/external_operator_release_bundle_plan.md': 'ccac49fc6b01fb659a1d5149dc36995f53506ad6457e3c1e772f8207ed8541f8', 'external_validation/operator_release_bundle_manifest.csv': 'e1f3f5e080dd3c6db706a00b5722f0fbdd36a92848ca8a5dde66dd440ae58d68', 'external_validation/operator_release_bundle_README.md': '9904d8f63dd08bc6e5ced94eeb6415c48c91590c708852e15774be58736d236b', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'e9bba20ede8dd836cddf5338b336108fc2fbe11289c869364030ce460d907ae5', 'results/external_operator_release_bundle_plan.md': 'ccac49fc6b01fb659a1d5149dc36995f53506ad6457e3c1e772f8207ed8541f8', 'external_validation/operator_release_bundle_manifest.csv': 'e1f3f5e080dd3c6db706a00b5722f0fbdd36a92848ca8a5dde66dd440ae58d68', 'external_validation/operator_release_bundle_README.md': '9904d8f63dd08bc6e5ced94eeb6415c48c91590c708852e15774be58736d236b', 'results/paper119_external_operator_release_bundle.zip': None}
