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

- `pass` `temporary_fixture_builds_current_release_plan`: status=0, files=361, archive=False
- `pass` `explicit_archive_fixture_writes_deterministic_transfer_zip`: status=0, entries=363, sha='482BDBEF5D0B11493A7E99FC59C50E841DCA553948C079B1455356D8E9207AE8'
- `pass` `missing_handoff_source_rejected`: status=1, error='missing results/external_operator_handoff_bundle.json'
- `pass` `handoff_no_go_drift_rejected`: status=1, source_check=False
- `pass` `missing_file_rejected`: status=1, hash_check=False
- `pass` `hash_drift_rejected`: status=1, hash_check=False
- `pass` `forbidden_evidence_path_rejected`: status=1, forbidden_check=False
- `pass` `premature_manifest_rejected`: status=1, manifest_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `collection_job_omission_rejected`: status=1, job_check=False
- `pass` `real_repository_release_outputs_untouched`: before={'results/external_operator_release_bundle_plan.json': 'edf1419f5487d9796a7e1de7e3e02c531528b30e4843dfec21100b542fbf4265', 'results/external_operator_release_bundle_plan.md': '9753ed5507489ece0b734575c167c62002371312d073f407d98276ea65e7d27a', 'external_validation/operator_release_bundle_manifest.csv': '95f5d17f904767b6bc440569aadd1f6a28723af1627184b039e01b296e6e690a', 'external_validation/operator_release_bundle_README.md': '0d516c42bec5a1f60cbd92b3c60fe8f71c0802ddae393b3964ce764de1c286d8', 'results/paper119_external_operator_release_bundle.zip': None}, after={'results/external_operator_release_bundle_plan.json': 'edf1419f5487d9796a7e1de7e3e02c531528b30e4843dfec21100b542fbf4265', 'results/external_operator_release_bundle_plan.md': '9753ed5507489ece0b734575c167c62002371312d073f407d98276ea65e7d27a', 'external_validation/operator_release_bundle_manifest.csv': '95f5d17f904767b6bc440569aadd1f6a28723af1627184b039e01b296e6e690a', 'external_validation/operator_release_bundle_README.md': '0d516c42bec5a1f60cbd92b3c60fe8f71c0802ddae393b3964ce764de1c286d8', 'results/paper119_external_operator_release_bundle.zip': None}
