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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=339, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=341, sha='6DD21DD77F97F7C42DDBD75CCF21446A37B15D7A3293A5134D3487D654FAD29E'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '3add8599aaa6381839f25ab8d70b5a7c9c757a972ed0ea9e0f725fb3dd469552', 'results/external_operator_release_bundle_plan.md': '48692ca73322ac27d00bff954e9fe0355b210edda75eb33c6683f56d21952d2c', 'external_validation/operator_release_bundle_manifest.csv': '839536837f68c1005fabdc5243110365ff3802f76856e47b5a2675848441e38c', 'external_validation/operator_release_bundle_README.md': 'e2275d51195fa49dad4ae8afe3401fc300f91e82ae53638906ca8189aa54a488', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '3add8599aaa6381839f25ab8d70b5a7c9c757a972ed0ea9e0f725fb3dd469552', 'results/external_operator_release_bundle_plan.md': '48692ca73322ac27d00bff954e9fe0355b210edda75eb33c6683f56d21952d2c', 'external_validation/operator_release_bundle_manifest.csv': '839536837f68c1005fabdc5243110365ff3802f76856e47b5a2675848441e38c', 'external_validation/operator_release_bundle_README.md': 'e2275d51195fa49dad4ae8afe3401fc300f91e82ae53638906ca8189aa54a488', 'results/paper119_external_operator_release_bundle.zip': None}
