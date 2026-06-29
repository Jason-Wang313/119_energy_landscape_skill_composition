# Fidelity Acceptance Materialization Plan

Passed: `true`.
Not evidence: `true`.
Write enabled: `false`.
Acceptance write ready: `false`.
Strict fidelity evidence ready: `false`.

This report turns the draft fidelity acceptance file into a guarded operator write path. The default run writes only this plan; it does not create `external_validation/fidelity_acceptance.json`, does not create a manifest, and does not satisfy strict fidelity evidence.

## Operator Write Command

```powershell
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <current_clean_checkout_commit_sha> --skill-library-hash <current_baselines_sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write
```

## Plan-Generation Checkout Guard

- Plan-generation code commit: `d7a4310a3a4ea9fd70a4b0b9912a9d141ddf2014`
- Plan-generation skill-library hash: `62EA64D1C80D67F5EB7EC63A88A581AE2D89B4230873F11D46799658541411F1`
- Plan-generation checkout clean: `false`
- Plan-generation dirty status lines: `2`

These values are a dry-run snapshot. The write path recomputes the checkout at runtime and requires the supplied `--code-commit` and `--skill-library-hash` to match that clean checkout before writing `external_validation/fidelity_acceptance.json`.

## Missing Operator Inputs In This Run

- `independent operator/lab identity`
- `accepted robot/simulator machine identity`
- `contact solver, friction model, and dynamics justification`
- `sim/control timestep and substeps per control step`
- `paired-reset replay verification`
- `real or benchmark calibration basis`
- `accepted or replaced task-binding decision`
- `operator acceptance-gate signoff`
- `known limitations for the accepted route`
- `date on which platform acceptance was locked`
- `code commit used for collection`
- `SHA256 hash for the skill/baseline library`

## Missing Confirmations In This Run

- `confirm_real_platform`
- `confirm_independent_operator`
- `confirm_render_backed_videos`
- `confirm_real_rollout_evidence`
- `confirm_manifest_declaration`

## Checks

- `pass` `draft_exists_and_is_draft_version`: path=external_validation/fidelity_acceptance_draft.json, version='paper119_fidelity_acceptance_draft_v1', draft_only=True
- `pass` `materialized_payload_has_contract_shape`: version='paper119_fidelity_acceptance_v1', gates=5
- `pass` `operator_text_required_before_write`: write=False, missing_text=['independent operator/lab identity', 'accepted robot/simulator machine identity', 'contact solver, friction model, and dynamics justification', 'sim/control timestep and substeps per control step', 'paired-reset replay verification', 'real or benchmark calibration basis', 'accepted or replaced task-binding decision', 'operator acceptance-gate signoff', 'known limitations for the accepted route', 'date on which platform acceptance was locked', 'code commit used for collection', 'SHA256 hash for the skill/baseline library']
- `pass` `confirmation_flags_required_before_write`: write=False, missing_confirmations=['confirm_real_platform', 'confirm_independent_operator', 'confirm_render_backed_videos', 'confirm_real_rollout_evidence', 'confirm_manifest_declaration']
- `pass` `write_requires_complete_operator_signoff`: write=False, acceptance_write_ready=False
- `pass` `current_checkout_hashes_recorded`: current_commit='d7a4310a3a4ea9fd70a4b0b9912a9d141ddf2014', current_skill_library_hash='62EA64D1C80D67F5EB7EC63A88A581AE2D89B4230873F11D46799658541411F1'
- `pass` `write_requires_clean_checkout`: write=False, dirty_status_count=2
- `pass` `write_requires_current_code_commit_and_skill_hash`: write=False, supplied_commit='', current_commit='d7a4310a3a4ea9fd70a4b0b9912a9d141ddf2014', supplied_skill_hash='', current_skill_hash='62EA64D1C80D67F5EB7EC63A88A581AE2D89B4230873F11D46799658541411F1'
- `pass` `default_run_does_not_write_real_acceptance_or_manifest`: write=False, acceptance_exists=False, manifest_exists=False
- `pass` `gates_accepted_only_after_confirmations`: acceptance_write_ready=False, gate_statuses=['operator_unaccepted', 'operator_unaccepted', 'operator_unaccepted', 'operator_unaccepted', 'operator_unaccepted']
- `pass` `strict_evidence_remains_external_to_materializer`: materializer can write provenance, but strict audits and manifest evidence still decide readiness
- `pass` `operator_write_command_is_guarded`: python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <current_clean_checkout_commit_sha> --skill-library-hash <current_baselines_sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write
