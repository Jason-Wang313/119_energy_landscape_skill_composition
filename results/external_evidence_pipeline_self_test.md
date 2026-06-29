# External Evidence Pipeline Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic submission ready: `true`.
Synthetic records: `1440`.
Synthetic tasks: `4`.
Synthetic methods: `12`.
Confidence gates passed: `true`.
Tampered rollout confidence rejected: `true`.
Tampered release hash rejected: `true`.
Real manifest untouched: `true`.
Real reports untouched: `true`.

This is a tooling-only self-test. It creates a temporary manifest/config/log/video/checkpoint package, proves the final strict external-evidence audit can reach ready on that temporary package with confidence-gated rollout statistics, proves tampered rollout confidence summaries and release hashes fail, and confirms the real repository evidence state is not promoted or overwritten.

## Checks

- `pass` `synthetic_complete_package_reaches_final_external_ready`: submission_ready=True, blocking=0
- `pass` `synthetic_records_cover_tasks_methods_and_confidence`: records=1440, tasks=4, methods=12, confidence=True
- `pass` `synthetic_component_gates_pass`: config=True, adapter=True, fidelity=True, pairing=True, release=True
- `pass` `tampered_rollout_confidence_summary_rejected`: failures=['external_rollout_confidence_gates_passed']
- `pass` `tampered_release_artifact_hash_rejected`: release_code_failure="entries=11, malformed=[], missing_paths=[], missing_sha256=[], hash_mismatches=['external_validation/implementations/greedy_module_sequence/adapter.py: declared=000000000000..., actual=74A31F94C452...'], hash_errors=[]"
- `pass` `real_repository_evidence_state_untouched`: manifest_before=None, manifest_after=None, external_audit_before=95549a716a35845863d28aaec7bc61f0029e767b6e57f7618d39e07b524fbbd5, external_audit_after=95549a716a35845863d28aaec7bc61f0029e767b6e57f7618d39e07b524fbbd5, rollout_before=d5cbdf671f96ddc7f79fda887f889d216d8db388b3a06bec98b0191deb141c2a, rollout_after=d5cbdf671f96ddc7f79fda887f889d216d8db388b3a06bec98b0191deb141c2a
