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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=348, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=350, sha='7C276551404FAB87F5B750FA2FDFEC5B4199B4C1895836F9384318D799113354'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '31d392ffe24b15d7e4886d0b350991e0496588b829cb61a171c87558ab08dc99', 'results/external_operator_release_bundle_plan.md': '6a168a53266acb3e7ac8e8e4b58f56bb8ae66e8fcf82faae6c7351d27668f350', 'external_validation/operator_release_bundle_manifest.csv': '3deccffaf399c44d103f22a41c9e6aaddc04d61dd7d9b57a4b736d7d62bfd126', 'external_validation/operator_release_bundle_README.md': '241e68bf979b513c5201b31fd963e37d7fd6228efb2c280c5f59ba94309f4a45', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '31d392ffe24b15d7e4886d0b350991e0496588b829cb61a171c87558ab08dc99', 'results/external_operator_release_bundle_plan.md': '6a168a53266acb3e7ac8e8e4b58f56bb8ae66e8fcf82faae6c7351d27668f350', 'external_validation/operator_release_bundle_manifest.csv': '3deccffaf399c44d103f22a41c9e6aaddc04d61dd7d9b57a4b736d7d62bfd126', 'external_validation/operator_release_bundle_README.md': '241e68bf979b513c5201b31fd963e37d7fd6228efb2c280c5f59ba94309f4a45', 'results/paper119_external_operator_release_bundle.zip': None}
