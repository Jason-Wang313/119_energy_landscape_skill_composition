# External Runner Backend Self-Test

Passed: `true`.
Not evidence: `true`.
Records written in temporary fixture: `2`.
Schema errors: `0`.

This self-test exercises the actual collection runner with a temporary synthetic non-template backend. It proves the backend API, runner JSONL writer, video export path, and rollout-record schema path can work end to end without touching the real external manifest or claiming validation evidence.

## Checks

- `pass` `runner_actual_path_exits_zero`: External collection runner wrote 2 JSONL records. Not validated until manifest and strict audits pass.

- `pass` `temporary_records_written`: records=2
- `pass` `temporary_records_schema_valid`: errors=[]
- `pass` `temporary_videos_written`: videos=2
- `pass` `real_manifest_untouched`: external_validation/manifest.json unchanged or absent
