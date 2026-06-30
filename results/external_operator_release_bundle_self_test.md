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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=345, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=347, sha='FE714A3235E9AA9A39FB85A1B88B2CA2EFA7F317AFA82AD2876D9EA6474AB5DA'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': '41547ffce58c28f9eb67d124336d67a28799bdd5490df8070fc4a0c29b7b8264', 'results/external_operator_release_bundle_plan.md': '9f0b3a5eee242c35a44b56b67578cf787df473f7f4e9a5f0f6a5249d54fe1720', 'external_validation/operator_release_bundle_manifest.csv': 'b959b460fcaa248533b71f81cf2af242edc068f4f1b1ac2796b7c191a657ded5', 'external_validation/operator_release_bundle_README.md': 'cc474ac002142e8689f8b464531dc77d4c39449e45317bc9968a9806c3a54bc0', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': '41547ffce58c28f9eb67d124336d67a28799bdd5490df8070fc4a0c29b7b8264', 'results/external_operator_release_bundle_plan.md': '9f0b3a5eee242c35a44b56b67578cf787df473f7f4e9a5f0f6a5249d54fe1720', 'external_validation/operator_release_bundle_manifest.csv': 'b959b460fcaa248533b71f81cf2af242edc068f4f1b1ac2796b7c191a657ded5', 'external_validation/operator_release_bundle_README.md': 'cc474ac002142e8689f8b464531dc77d4c39449e45317bc9968a9806c3a54bc0', 'results/paper119_external_operator_release_bundle.zip': None}
