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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=367, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=369, sha='FFDCF6351660DA172EE7F7B0738A8550E142AACDE6AAC9EEA82EC682D6764B55'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'd2e38d3c7c13d1c0b7bdf9148fd5ac77d036d38637db00102ba0ce28458c94c2', 'results/external_operator_release_bundle_plan.md': '7e6a8bd3e570946bda0030552064c5d299a863aa544d7891487407a4857195a1', 'external_validation/operator_release_bundle_manifest.csv': '89ff992a0b1a34782e21aac03561721b75e36db7c593fcb3b307f857dc17f1a2', 'external_validation/operator_release_bundle_README.md': 'bc23261cb5468b72940c29499a97b0a029e4ffa107b3227bab76025c4dbad8bc', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'd2e38d3c7c13d1c0b7bdf9148fd5ac77d036d38637db00102ba0ce28458c94c2', 'results/external_operator_release_bundle_plan.md': '7e6a8bd3e570946bda0030552064c5d299a863aa544d7891487407a4857195a1', 'external_validation/operator_release_bundle_manifest.csv': '89ff992a0b1a34782e21aac03561721b75e36db7c593fcb3b307f857dc17f1a2', 'external_validation/operator_release_bundle_README.md': 'bc23261cb5468b72940c29499a97b0a029e4ffa107b3227bab76025c4dbad8bc', 'results/paper119_external_operator_release_bundle.zip': None}
