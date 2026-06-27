# External Pilot Smoke Packet Audit

Passed: `true`.
Not evidence: `true`.
Pilot smoke packet ready: `true`.
Strict evidence ready: `false`.

This audit checks that the pilot-smoke route is available as a quarantined backend smoke test and remains outside official external evidence.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: strict_evidence_ready=False
- `pass` `quarantine_dirs_are_separate_from_official_evidence`: quarantine_root=external_validation/pilot_smoke
- `pass` `runner_backend_probe_already_exercises_actual_runner`: records=2
- `pass` `pilot_commands_preserve_gate_order`: commands=['python scripts\\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\pilot_smoke\\logs --video-dir external_validation\\pilot_smoke\\videos --run-id paper119_pilot_smoke_<platform>_<date> --unsealed-alias-map --force', 'python external_validation\\runner\\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\pilot_smoke\\logs --video-dir external_validation\\pilot_smoke\\videos --run-id paper119_pilot_smoke_<platform>_<date> --unsealed-alias-map --max-rows 12 --force', 'python scripts\\audit_external_pilot_smoke.py --strict --expected-records 12 --check-video-paths', 'Remove or archive external_validation\\pilot_smoke before official collection; pilot logs/videos must never be listed in external_validation\\manifest.json']
- `pass` `pilot_audit_reports_non_evidence_state`: passed=True, records=0
- `pass` `collection_readiness_remains_official_gate`: collection_ready=False
- `pass` `packet_files_written`: json=True, md=True, csv=True
