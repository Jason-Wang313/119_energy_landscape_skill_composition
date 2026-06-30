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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=336, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=338, sha='D8BC9C40F37151532D4DD98F9FDF2A8D7470536A8F7E562F1E4CBCB9E2C29559'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '7652109711cc73148817cbb1a00acd6b6c53a0049a5c82264e7da1dcf6871ef7', 'results/external_operator_release_bundle_plan.md': 'dea49f139013a4356aeffe166c2b8ebfad72e94d7bdd7db366c384ee7bb1dfef', 'external_validation/operator_release_bundle_manifest.csv': 'f2ba116c63af30f272d147f987d0e24c9cfb4d57cac46ca3e6bc104546932647', 'external_validation/operator_release_bundle_README.md': 'c24abd3e6cc7cf841ae8fc76b86a79b7d2dcdc3eff9083d246432ffa20f5e502', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '7652109711cc73148817cbb1a00acd6b6c53a0049a5c82264e7da1dcf6871ef7', 'results/external_operator_release_bundle_plan.md': 'dea49f139013a4356aeffe166c2b8ebfad72e94d7bdd7db366c384ee7bb1dfef', 'external_validation/operator_release_bundle_manifest.csv': 'f2ba116c63af30f272d147f987d0e24c9cfb4d57cac46ca3e6bc104546932647', 'external_validation/operator_release_bundle_README.md': 'c24abd3e6cc7cf841ae8fc76b86a79b7d2dcdc3eff9083d246432ffa20f5e502', 'results/paper119_external_operator_release_bundle.zip': None}
