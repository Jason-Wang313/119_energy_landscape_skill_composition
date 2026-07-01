# External Pairing Integrity Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic pairing ready: `true`.

This self-test builds temporary manifest-declared JSONL logs and exercises the paired-reset fairness gate directly. It proves complete method panels can pass, missing manifests fail, duplicate method rows fail, incomplete panels fail, terminal-sample mismatches fail, and the real pairing audit report is not overwritten.

## Checks

- `pass` `synthetic_pairing_integrity_passes`: ready=True, records=1440/1440
- `pass` `missing_manifest_fails_pairing_readiness`: ready=False, blockers=['external_validation/manifest.json has not been written from real evidence']
- `pass` `duplicate_method_rows_fail_pairing`: ready=False, blockers=2
- `pass` `missing_method_panel_fails_pairing`: ready=False, blockers=2
- `pass` `terminal_sample_mismatch_fails_pairing`: ready=False, blockers=1
- `pass` `real_pairing_integrity_report_not_overwritten`: before=d4abaa9c2083d8b5932139dfee0b1d79b4c7c97acb9088c2e55245b26f624148, after=d4abaa9c2083d8b5932139dfee0b1d79b4c7c97acb9088c2e55245b26f624148
