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
- `pass` `diagnostic_fallback_video_rejected_before_jsonl_write`: returncode=1, records=0, output=backend produced diagnostic fallback video sidecar, which cannot be official evidence: C:\Users\wangz\AppData\Local\Temp\paper119_runner_diagnostic_video_selftest_sibbcsqg\videos\peg_place_regrasp\000_barrier_certified_energy_composer_v5.09
- `pass` `schema_invalid_record_rejected_before_jsonl_write`: returncode=1, records=0, output=runner refused schema-invalid official JSONL record before write: peg_place_regrasp:0:barrier_certified_energy_composer_v5: decision='bad_schema_decision' not in ['accept', 'repair', 'probe', 'abstain', 'transition']
- `pass` `partial_batch_failure_preserves_official_jsonl`: returncode=1, log_preserved=True, output=Traceback (most recent call last): File "C:\Users\wangz\robotics_massive_pool_paper_factory\119_energy_landscape_skill_composition\external_validation\runner\real_collection_runner.py", line 643, in <module> raise SystemExit(main())
- `pass` `partial_batch_failure_preserves_official_videos`: returncode=1, video_preserved=True, staging_leftovers=[]
- `pass` `real_manifest_untouched`: external_validation/manifest.json unchanged or absent
