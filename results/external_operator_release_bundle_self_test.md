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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=370, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=372, sha='7C26C02C51D8601E16453D17F1F2D26F7663D132228F316C21F33B7BA7D39613'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '34e7b4e1804f35657fdc2ac187f833abae16a3a331f8b17fcd7a2bbfb1c279ac', 'results/external_operator_release_bundle_plan.md': '7b3883ac1255eb25cf6be7399f7b84af76eb76fe49d881c4bc2ce8eedc68f50c', 'external_validation/operator_release_bundle_manifest.csv': '3337010d8753ff7e770571e14262c5a2056ae32a226b0f9a9253f6f7cd700de7', 'external_validation/operator_release_bundle_README.md': 'f439d511646c281c63db8006d4dbc8a1d17d3f4c76b28c7de9d4ab3bf98e41f6', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '34e7b4e1804f35657fdc2ac187f833abae16a3a331f8b17fcd7a2bbfb1c279ac', 'results/external_operator_release_bundle_plan.md': '7b3883ac1255eb25cf6be7399f7b84af76eb76fe49d881c4bc2ce8eedc68f50c', 'external_validation/operator_release_bundle_manifest.csv': '3337010d8753ff7e770571e14262c5a2056ae32a226b0f9a9253f6f7cd700de7', 'external_validation/operator_release_bundle_README.md': 'f439d511646c281c63db8006d4dbc8a1d17d3f4c76b28c7de9d4ab3bf98e41f6', 'results/paper119_external_operator_release_bundle.zip': None}
