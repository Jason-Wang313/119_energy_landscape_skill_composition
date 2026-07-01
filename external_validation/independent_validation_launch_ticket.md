# Independent Validation Launch Ticket

Not evidence: `true`.
Launch state: `DO_NOT_START_COLLECTION_YET`.
Render-machine state: `DO_NOT_COLLECT_RENDER_MACHINE`.
Decision boundary: `STRONG_REVISE`.
Readiness boundary: `17/21` requirements satisfied; `4` strict external-evidence blockers remain.
Agenda identity: Adaptive physical world/action models for embodied agents.

Use this as the copyable issue body for an independent validation operator. Do not create official rollout evidence from this ticket alone; it is a launch/control artifact for the validation run.

## Issue Title

Paper 119 independent external validation run: qualify machine, collect official JSONL/MP4 evidence, seal hashes, and promote manifest

## Start State

- `DO_NOT_START_COLLECTION_YET`: official collection is blocked until render/liveness, fidelity, backend, run-id, alias, and operator metadata gates pass.
- `DO_NOT_COLLECT_RENDER_MACHINE`: the current local machine is not accepted for official evidence collection.
- `QUALIFIED_FOR_RENDER_BACKED_PILOT`: the render-machine qualification ready state required before fidelity acceptance and official collection.
- Haonan is not required for proof, and the launch route is not Haonan-dependent.
- Do not pitch Haonan as responsible for supplying the missing proof.
- Do not mention Yilun as the validation motive; this ticket is for independent evidence collection.

## Before Assignment

- [ ] Independent operator or lab is identified.
- [ ] Accepted real robot or accepted high-fidelity simulator machine is available.
- [ ] Operator has the release bundle README and manifest, plus this launch ticket.
- [ ] Operator has `external_validation/render_host_qualification_brief.md` and understands the current render host state is `RENDER_HOST_NOT_QUALIFIED`.
- [ ] Operator agrees that placeholder fields, diagnostic fallback videos, local dry-run records, and template configs cannot count as evidence.
- [ ] Operator understands that `external_validation/manifest.json` must not exist until postcollection strict gates are ready.

## Attach To Issue

- `external_validation/collection_machine_bootstrap.md`
- `external_validation/collection_machine_bootstrap.ps1`
- `external_validation/collection_machine_bootstrap.sh`
- `external_validation/collection_job_packet.md`
- `external_validation/collection_job_commands.ps1`
- `external_validation/collection_job_commands.sh`
- `docs/external_evidence_closure_brief.md`
- `external_validation/operator_release_bundle_README.md`
- `external_validation/render_host_qualification_brief.md`

## Current Strict Blockers

- `accepted_fidelity_and_manifest`: Independent real-robot or accepted high-fidelity external validation evidence. Completion test: accepted fidelity provenance exists, the official manifest exists, and the final strict external evidence audit no longer reports fidelity or manifest blockers
- `raw_rollouts_videos_and_metrics`: External rollout metrics recomputed from raw JSONL logs. Completion test: strict rollout validation recomputes metrics from raw JSONL logs and the final audit agrees with the manifest metrics
- `manifest_bound_task_configs`: Manifest-declared real task configs replace non-evidence templates. Completion test: strict config evidence passes against manifest-declared config files and hashes rather than template or local-dry-run configs
- `independent_methods_and_fairness_contract`: Manifest-declared independent non-oracle baseline evidence and fairness contract. Completion test: strict adapter evidence passes and the final audit accepts the independent non-oracle method evidence plus fairness contract

## Phase 1: Machine Bootstrap

Run this phase on the independent collection machine. This phase is still non-evidence; it only proves the machine can render, reset, and run the checked path.

Windows:

```powershell
.\external_validation\collection_machine_bootstrap.ps1 -ConfirmBootstrapOnly -InstallManiSkill -AcceptedBackend <accepted_backend> -ShaderPack <accepted_shader_pack>
```

Linux:

```bash
./external_validation/collection_machine_bootstrap.sh --confirm-bootstrap-only --install-maniskill --accepted-backend <accepted_backend> --shader-pack <accepted_shader_pack>
```

Phase 1 acceptance:

- [ ] `results/maniskill_render_machine_qualification.json` reports `qualification_state=QUALIFIED_FOR_RENDER_BACKED_PILOT` and `render_machine_qualified=true` on the independent machine, replacing the current `DO_NOT_COLLECT_RENDER_MACHINE` state.
- [ ] Render-backed MP4 export passes for the primary ManiSkill/SAPIEN task families with no diagnostic fallback promotion.
- [ ] Pilot runtime liveness passes with official-video and JSONL write guards intact.

## Phase 2: Official Collection

Do not start this phase while any placeholder value remains. The scripts intentionally require explicit confirmation and real operator/platform fields.

Windows:

```powershell
.\external_validation\collection_job_commands.ps1 -ConfirmOfficialCollection -AcceptedBackend <accepted_backend> -ShaderPack <accepted_shader_pack> -RunId <accepted_run_id> -OperatorNameOrLab <independent_operator_or_lab> -OperatorId <independent_operator_or_lab> -CollectionMachine <machine_or_robot_platform> -ContactSolverAndFrictionModel <solver_friction_contact_model> -TimestepAndSubstepsPerControlStep <sim_dt_control_dt_substeps> -PairedResetReplayTest <paired_reset_replay_result> -CalibrationBasis <calibration_basis> -TaskBindingDecision <accepted_or_replaced_task_bindings> -AcceptanceGateSignoff <gate_signoff_summary> -KnownLimitations <known_limitations> -DateLocked <YYYY-MM-DD> -DateSealed <YYYY-MM-DD> -CodeCommit <commit_sha> -SkillLibraryHash <sha256>
```

Linux:

```bash
./external_validation/collection_job_commands.sh --confirm-official-collection --accepted-backend <accepted_backend> --shader-pack <accepted_shader_pack> --run-id <accepted_run_id> --operator-name-or-lab <independent_operator_or_lab> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --date-sealed <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256>
```

Phase 2 acceptance:

- [ ] `official_collection_runner`: Official JSONL rows and renderer-backed MP4s are produced by the accepted backend under the accepted run id without diagnostic fallback promotion.
- [ ] `postcollection_evidence_seal`: Raw JSONL logs, rollout videos, prepared configs, precollection receipt, and operator metadata are hash-sealed before manifest promotion.
- [ ] `postcollection_seal_consistency`: Sealed raw-log, video, config, precollection, and metadata hashes recompute without drift before manifest promotion.

## Evidence Upload Contract

- [ ] `external_validation/logs/*.jsonl` raw official logs.
- [ ] `external_validation/videos/<task_family>/*.mp4` render-backed videos.
- [ ] `external_validation/fidelity_acceptance.json` with independent operator signoff.
- [ ] `external_validation/precollection_freeze_receipt.*` and `external_validation/postcollection_evidence_seal.*`.
- [ ] `external_validation/manifest.json` only after postcollection seal consistency and manifest promotion gates pass.
- [ ] Real method config/checkpoint artifacts for all independent non-oracle baselines, with hashes bound in logs and manifest.

## Close Criteria

- [ ] `python scripts\audit_external_evidence.py --strict` passes.
- [ ] `python scripts\audit_submission_readiness_gap.py` no longer reports the four strict external-evidence blockers.
- [ ] Raw JSONL rollout metrics recompute from official logs and match the manifest.
- [ ] Manifest-declared task configs replace template/non-evidence configs.
- [ ] Independent non-oracle baseline evidence and fairness contract are manifest-bound.
- [ ] Claim boundary remains honest: no strict evidence is claimed before all above checks pass.

## Source Packet Status

- Collection job packet: `DO_NOT_START_COLLECTION_YET`, `17` ordered steps.
- Bootstrap packet: `READY_TO_BOOTSTRAP_EXTERNAL_MACHINE`.
- Execution packet: ready=`true`, strict evidence ready=`false`.
- Closure route: `maniskill_sapien_primary`, Haonan dependency=`false`.

