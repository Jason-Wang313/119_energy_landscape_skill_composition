# External Operator Release Bundle Plan

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Bundle state: `READY_TO_SEND_OPERATOR_PACKAGE`.
Included handoff files: `333`.
Payload bytes: `4618356`.
Archive written: `false`.
Archive path: `results/paper119_external_operator_release_bundle.zip`.
Manifest CSV: `external_validation/operator_release_bundle_manifest.csv`.
Release README: `external_validation/operator_release_bundle_README.md`.

This is a transfer package plan for the independent operator. It does not contain real rollout evidence and does not write `external_validation/manifest.json`.

## Archive Command

```powershell
python scripts\build_external_operator_release_bundle.py --write-archive
```

## Category Counts

- `baseline_spec`: `12`
- `config_template`: `4`
- `generated_non_evidence_report`: `102`
- `method_config_candidate`: `11`
- `operator_command_source`: `45`
- `operator_facing_input`: `86`
- `prepared_config_input`: `4`
- `reference_adapter`: `60`
- `runner_backend_template`: `5`
- `task_card`: `4`

## Checks

- `pass` `release_bundle_is_non_evidence`: release bundle is a transfer package only
- `pass` `source_handoff_bundle_ready`: passed=True, start_state='DO_NOT_COLLECT_YET', strict=False
- `pass` `collection_job_packet_present_in_handoff`: job_state='DO_NOT_START_COLLECTION_YET', packet_in_paths=True
- `pass` `handoff_hashes_recomputed`: missing=[], mismatched=[]
- `pass` `forbidden_evidence_paths_excluded`: forbidden=[]
- `pass` `release_manifest_covers_all_handoff_files`: records=333, handoff_count=333
- `pass` `archive_writer_is_explicit_and_optional`: default mode writes only plan files; archive writing requires --write-archive
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `archive_not_written_by_default`: use --write-archive to create the transfer zip
