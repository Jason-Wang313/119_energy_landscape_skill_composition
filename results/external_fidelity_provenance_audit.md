# External Fidelity Provenance Audit

Passed: `true`.
Not evidence: `true`.
Fidelity provenance packet ready: `true`.
Strict fidelity evidence ready: `false`.
Blocking missing items: `17`.

This audit checks that the platform fidelity/provenance packet is complete as an operator checklist while strict fidelity and external evidence gates remain fail-closed.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_contract_ready_but_not_evidence`: acceptance_ready=False, blocking_missing_count=17
- `pass` `platform_onboarding_packet_ready`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `external_platform_probe_ready`: primary_route_install_ready=True, missing=[]
- `pass` `independent_route_and_collection_still_fail_closed`: primary_route='maniskill_sapien_primary', collection_ready=False
- `pass` `template_declares_required_platform_and_gate_fields`: platform_fields=12, qualification_fields=14, gates=5, tasks=4
- `pass` `work_orders_cover_fidelity_blockers`: missing_orders=[]
- `pass` `strict_commands_cover_fidelity_manifest_collection_and_evidence`: python scripts\build_external_fidelity_provenance_packet.py
python scripts\build_external_platform_onboarding.py
python scripts\probe_external_platform.py --strict
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
python scripts\audit_external_fidelity_acceptance.py --strict
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_evidence.py --strict
- `pass` `acceptance_template_not_real_evidence`: version='paper119_fidelity_acceptance_template_v1', template_only=True
- `pass` `no_real_acceptance_or_manifest_written`: acceptance_exists=False, manifest_exists=False
- `pass` `packet_files_written`: packet_json=True, packet_md=True, csv=True
