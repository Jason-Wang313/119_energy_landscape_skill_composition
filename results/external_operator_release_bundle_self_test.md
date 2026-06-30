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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=333, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=335, sha='FC97EA0F69B98EF7B12E4BF7B100CE6A20FBE1AC5C45BBDA0E602A02BCC643E9'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'ad6cbc65223bdcbce379056f9664d65a02120003d052a8450a7410e5a6b10d76', 'results/external_operator_release_bundle_plan.md': 'af110bdeec851c1b30fa677c18064d86aa3152ca80f040ba0c0ee9d79e7b9e15', 'external_validation/operator_release_bundle_manifest.csv': 'a92f5ce7c4b9eb813d0cef97e02262b3b589626b66b031f3802c2c8daafb3e8d', 'external_validation/operator_release_bundle_README.md': 'fae3bbe6afe36a7421ed3082b49155c30115480d611444a59de06d93f7c33d4f', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'ad6cbc65223bdcbce379056f9664d65a02120003d052a8450a7410e5a6b10d76', 'results/external_operator_release_bundle_plan.md': 'af110bdeec851c1b30fa677c18064d86aa3152ca80f040ba0c0ee9d79e7b9e15', 'external_validation/operator_release_bundle_manifest.csv': 'a92f5ce7c4b9eb813d0cef97e02262b3b589626b66b031f3802c2c8daafb3e8d', 'external_validation/operator_release_bundle_README.md': 'fae3bbe6afe36a7421ed3082b49155c30115480d611444a59de06d93f7c33d4f', 'results/paper119_external_operator_release_bundle.zip': None}
