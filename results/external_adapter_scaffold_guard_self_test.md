# External Adapter Scaffold Guard Self-Test

Passed: `true`.
Not evidence: `true`.
Scaffold directory detected: `true`.
Scaffold template detected: `true`.
Ordinary adapter falsely rejected: `false`.

This self-test exercises the strict scaffold detector used by the external evidence audit. It proves scaffold-only adapter directories and templates are rejected as evidence while an ordinary replacement adapter file is not falsely rejected. It writes only this receipt and leaves the real scaffold/evidence audit reports untouched.

## Checks

- `pass` `scaffold_directory_detected`: path=external_validation/baselines/barrier_certified_energy_composer_v5
- `pass` `scaffold_template_detected`: path=external_validation/baselines/barrier_certified_energy_composer_v5/adapter_template.py
- `pass` `ordinary_replacement_adapter_not_flagged`: temporary ordinary adapter file was not classified as scaffold-only
- `pass` `temporary_adapter_file_removed`: temporary ordinary adapter file was removed after self-test
- `pass` `real_adapter_reports_untouched`: before={'results/external_adapter_scaffold_audit.json': '92a41ebf2dee4066d5d294c8420492d6e4b934a1f1b601ad4cb8f90390ac2c4a', 'results/external_adapter_scaffold_audit.md': 'f7f2a7e3738a610c9b878a36280bc507ec26d972dc0d0edc01f77d2107681dc0', 'results/external_adapter_contract_evidence_audit.json': 'ae830cd8e98d58b508d5044b140d4ebd84513916d5d6f9faa92a7e8d51bc6609', 'results/external_adapter_contract_evidence_audit.md': 'bdf0f369017209f5b1caa0cdce5c935a3954ec83fca12cad1998a08621b0fd88'}, after={'results/external_adapter_scaffold_audit.json': '92a41ebf2dee4066d5d294c8420492d6e4b934a1f1b601ad4cb8f90390ac2c4a', 'results/external_adapter_scaffold_audit.md': 'f7f2a7e3738a610c9b878a36280bc507ec26d972dc0d0edc01f77d2107681dc0', 'results/external_adapter_contract_evidence_audit.json': 'ae830cd8e98d58b508d5044b140d4ebd84513916d5d6f9faa92a7e8d51bc6609', 'results/external_adapter_contract_evidence_audit.md': 'bdf0f369017209f5b1caa0cdce5c935a3954ec83fca12cad1998a08621b0fd88'}
