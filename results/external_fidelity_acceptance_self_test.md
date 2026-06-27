# External Fidelity Acceptance Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic acceptance ready: `true`.

This self-test builds a temporary high-fidelity acceptance fixture and exercises the platform/provenance acceptance gate directly. It proves the strict-ready path can pass for a complete synthetic fixture, that the template/default path remains fail-closed, and that the real fidelity audit report is not overwritten.

## Checks

- `pass` `synthetic_strict_acceptance_ready`: contract_failures=[], evidence_failures=[]
- `pass` `synthetic_route_task_count`: route_has_enough_task_families=True
- `pass` `synthetic_platform_modalities`: modalities=True, contact_channels=True
- `pass` `template_acceptance_fails_strict_evidence`: template_ready=False
- `pass` `real_fidelity_report_not_overwritten`: before=bdcb4a5bb6b441b3426803a5f18eba003528818fbe3a303a324d95b9a20732f0, after=bdcb4a5bb6b441b3426803a5f18eba003528818fbe3a303a324d95b9a20732f0
