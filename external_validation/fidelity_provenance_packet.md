# External Fidelity Provenance Packet

Packet ready: `true`.
Not evidence: `true`.
Strict fidelity evidence ready: `false`.
Strict external evidence ready: `false`.
Platform probe ready: `true`.
Primary route install ready in latest probe: `true`.
Latest probe missing packages: `[]`.
Blocking missing items: `14`.

This packet is a non-evidence work-order layer for platform fidelity and provenance. It exists so an independent operator can fill the real acceptance file before any robot or high-fidelity simulator rollout counts as evidence.

## Work Orders

- `fill_platform_identity_and_physics` (platform): run the external platform probe on the selected machine, then fill platform_name, platform_version, physics engine, contact solver, timestep, substeps, robot model, assets, sensors, and contact/force channels
- `verify_contact_dynamics_and_observability` (task_fidelity): document why each skill seam exposes the contact/dynamics failures needed for Paper 119's diagnosis and risk estimates
- `verify_paired_reset_replay` (collection): prove the selected platform can replay the same scene, seed, skill pair, and initial-state hash across every method panel
- `document_operator_independence_and_calibration_basis` (provenance): record independent operator/lab, date lock, calibration or benchmark basis, known limitations, and no target-collaborator dependency
- `lock_code_skill_and_artifact_hashes` (release): fill code commit, skill-library hash, artifact hash policy, manifest path, and manifest-declared fidelity_acceptance_path
- `run_strict_fidelity_and_external_gates` (final_gate): after platform provenance, logs, videos, configs, implementations, and hashes are real, run strict fidelity and external-evidence gates

## Strict Acceptance Commands

- `python scripts\build_external_fidelity_provenance_packet.py`
- `python scripts\build_external_platform_onboarding.py`
- `python scripts\probe_external_platform.py --strict`
- `python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_evidence.py --strict`

## Forbidden Shortcuts

- treating fidelity_acceptance_template.json as real acceptance evidence
- using a platform without filled physics/contact provenance and accepted limitations
- counting rollouts before paired reset replay is verified
- omitting operator independence, code commit, or skill-library hash
- claiming high-fidelity validation before strict fidelity and external-evidence audits pass
