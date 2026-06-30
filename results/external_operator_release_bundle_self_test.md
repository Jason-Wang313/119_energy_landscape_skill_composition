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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=375, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=377, sha='65023A2B8951F8CF2720642A2A8BE98592B182E749445F1DF612D592EE362E4B'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '322eabb2bb7ee171c08c0e2b8c7887ad3cdf383e5e14d90c69931ca2f1701abe', 'results/external_operator_release_bundle_plan.md': '786b353c8f27b81265cbf9334ee60a5e605f9f77e3ee4ef8e373f89e1ddce87c', 'external_validation/operator_release_bundle_manifest.csv': '92d3f2ca7f8b363dc97f8e3c0b79faf4bc8a9b028b4824702104a5eefb427e74', 'external_validation/operator_release_bundle_README.md': '7278d7f2d73ed0cd769c88343d9255e8a633053b7f0d3529fc74c2c8710cd8e1', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '322eabb2bb7ee171c08c0e2b8c7887ad3cdf383e5e14d90c69931ca2f1701abe', 'results/external_operator_release_bundle_plan.md': '786b353c8f27b81265cbf9334ee60a5e605f9f77e3ee4ef8e373f89e1ddce87c', 'external_validation/operator_release_bundle_manifest.csv': '92d3f2ca7f8b363dc97f8e3c0b79faf4bc8a9b028b4824702104a5eefb427e74', 'external_validation/operator_release_bundle_README.md': '7278d7f2d73ed0cd769c88343d9255e8a633053b7f0d3529fc74c2c8710cd8e1', 'results/paper119_external_operator_release_bundle.zip': None}
