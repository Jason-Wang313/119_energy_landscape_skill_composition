# External Fidelity Acceptance Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic acceptance ready: `true`.

This self-test builds a temporary high-fidelity acceptance fixture and exercises the platform/provenance acceptance gate directly. It proves the strict-ready path and strict fidelity acceptance provenance gate can pass for a complete synthetic fixture, that the template/default path remains fail-closed, and that the real fidelity audit report is not overwritten.

## Checks

- `pass` `synthetic_strict_acceptance_ready`: contract_failures=[], evidence_failures=[]
- `pass` `synthetic_route_task_count`: route_has_enough_task_families=True
- `pass` `synthetic_platform_modalities`: modalities=True, contact_channels=True
- `pass` `synthetic_strict_provenance_guards`: ready=True, not_draft=True, strict_external=True, date=True, commit=True, confirmations=True, materialized=True
- `pass` `template_acceptance_fails_strict_evidence`: template_ready=False
- `pass` `template_strict_provenance_guards_fail_closed`: ready=False, strict_external=False, date=False, commit=False, confirmations=False, materialized=False
- `pass` `real_fidelity_report_not_overwritten`: before=116ea1404535839c89a77cae231ac696bc92989ac204a7d2ec9e1d3ec545d9cb, after=116ea1404535839c89a77cae231ac696bc92989ac204a7d2ec9e1d3ec545d9cb
