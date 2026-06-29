# External Fidelity Acceptance Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic acceptance ready: `true`.

This self-test builds a temporary high-fidelity acceptance fixture and exercises the platform/provenance acceptance gate directly. It proves the strict-ready path and strict fidelity acceptance provenance gate can pass for a complete synthetic fixture, that the template/default path remains fail-closed, and that the real fidelity audit report is not overwritten.

## Checks

- `pass` `synthetic_strict_acceptance_ready`: contract_failures=[], evidence_failures=[]
- `pass` `synthetic_route_task_count`: manifest_task_coverage_when_present=True
- `pass` `synthetic_platform_modalities`: modalities=True, contact_channels=True
- `pass` `synthetic_strict_provenance_guards`: ready=True, not_draft=True, strict_external=True, date=True, commit=True, precollection_confirmations=True, postcollection_deferred=True, materialized=True
- `pass` `template_acceptance_fails_strict_evidence`: template_ready=False
- `pass` `template_strict_provenance_guards_fail_closed`: ready=False, strict_external=False, date=False, commit=False, precollection_confirmations=False, postcollection_deferred=False, materialized=False
- `pass` `real_fidelity_report_not_overwritten`: before=44a74216804348a545706b23acbf66f5f2bb12acdb66c4a98c4101c3c3334582, after=44a74216804348a545706b23acbf66f5f2bb12acdb66c4a98c4101c3c3334582
