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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=358, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=360, sha='3AB51E90527EB8FA4EA84AE74F086AD0859E004AA1073B25E93FE3F9DF57887D'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'a1f35c8b83fb9ff8d14b76f5309c195fc3ad805988eccbe4dde58a1fd80e7e25', 'results/external_operator_release_bundle_plan.md': 'acbef8662bcca485c4f9e40beae41f18d5b8d951286a2874477d829c5499f17b', 'external_validation/operator_release_bundle_manifest.csv': '163ba5373fda8c5695c14db1b70972d28a01dbd392cea96b91ddaa2e6a577082', 'external_validation/operator_release_bundle_README.md': '29af3c6d1bfaab1b97a79d6dd07b18efd084ee8635e5827ec7cac46b5e4e6f74', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'a1f35c8b83fb9ff8d14b76f5309c195fc3ad805988eccbe4dde58a1fd80e7e25', 'results/external_operator_release_bundle_plan.md': 'acbef8662bcca485c4f9e40beae41f18d5b8d951286a2874477d829c5499f17b', 'external_validation/operator_release_bundle_manifest.csv': '163ba5373fda8c5695c14db1b70972d28a01dbd392cea96b91ddaa2e6a577082', 'external_validation/operator_release_bundle_README.md': '29af3c6d1bfaab1b97a79d6dd07b18efd084ee8635e5827ec7cac46b5e4e6f74', 'results/paper119_external_operator_release_bundle.zip': None}
