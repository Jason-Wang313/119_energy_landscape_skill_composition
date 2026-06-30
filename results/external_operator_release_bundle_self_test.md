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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=364, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=366, sha='8F90E1296148843A3A7A6E5B7B9A7098101E7F17DF612E7485F4D490DE55587F'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '99fe056a9685f472d3bce8196669bbd9b9dbccdfaad4ea0717566d8a65e596fc', 'results/external_operator_release_bundle_plan.md': 'f887b3ca3a6960fa8851eddd504910664244eece8d4cb1fcf61a9b4398d37c09', 'external_validation/operator_release_bundle_manifest.csv': '045a5ae22dc7c2b5da9f6bedfdd0f065a3a27500e224d2242b94079725511f3c', 'external_validation/operator_release_bundle_README.md': 'a37213dcd33ef3143736d6e8177000393d3edca2a13853570f8a229c20357068', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '99fe056a9685f472d3bce8196669bbd9b9dbccdfaad4ea0717566d8a65e596fc', 'results/external_operator_release_bundle_plan.md': 'f887b3ca3a6960fa8851eddd504910664244eece8d4cb1fcf61a9b4398d37c09', 'external_validation/operator_release_bundle_manifest.csv': '045a5ae22dc7c2b5da9f6bedfdd0f065a3a27500e224d2242b94079725511f3c', 'external_validation/operator_release_bundle_README.md': 'a37213dcd33ef3143736d6e8177000393d3edca2a13853570f8a229c20357068', 'results/paper119_external_operator_release_bundle.zip': None}
