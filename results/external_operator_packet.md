# External Operator Packet

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.
Start state: `DO_NOT_COLLECT_YET`.

This packet is the independent operator entry point for turning the current non-evidence validation plan into real robot or accepted high-fidelity simulator evidence. It does not replace the strict external audits.

## Go / No-Go

- No-go: do not start collection until every pre-collection blocker below is cleared by the strict preflight gate.

## Pre-Collection Blockers

- backend_module_ready: --backend-module is required before actual collection
- fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- alias_unsealing_explicit: unsealed_alias_map=False
- run_id_specific: run_id='paper119_external_validation_run'

## Tracked ManiSkill Reference Route

This tracked public-simulator route is not evidence and does not authorize collection. It shows that, after selecting the repository ManiSkill reference backend, prepared configs, an explicit run id, and unsealed aliases, the pre-collection path reaches the fidelity-acceptance gate.

- Backend module: `external_validation\runner\maniskill_reference_backend.py`
- Run id: `maniskill_sapien_reference_preflight_protocol_v1`
- Reference backend contract ready: `true`
- Collection ready: `false`
- Remaining blockers after reference-route preflight: `1`
- fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'

Reference-route pre-collection gate:

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id maniskill_sapien_reference_preflight_protocol_v1 --unsealed-alias-map
```

Reference-route collection command after fidelity acceptance passes:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id maniskill_sapien_reference_preflight_protocol_v1 --unsealed-alias-map
```

## Fidelity Acceptance Draft

The draft is not evidence and does not satisfy fidelity acceptance. It pre-fills the tracked ManiSkill route's platform, backend, config, and smoke-probe anchors so the independent operator can replace draft fields with accepted provenance before collection.

- Draft JSON: `external_validation/fidelity_acceptance_draft.json`
- Draft notes: `external_validation/fidelity_acceptance_draft.md`
- Draft ready: `true`
- Acceptance ready: `false`
- Remaining operator inputs: `10`
- Machine-prefilled ready: `true`
- Operator signoff ready: `false`
- Operator signoff items: `10`

Draft rebuild command:

```powershell
python scripts\build_external_fidelity_acceptance_draft.py
```

## Fidelity Acceptance Materializer

The materializer is the guarded promotion path from the draft to `external_validation/fidelity_acceptance.json`. The default run writes only a plan; the write path requires independent operator fields, real platform confirmation, render-backed evidence-video readiness, real rollout evidence, and manifest declaration.

- Plan JSON: `results/fidelity_acceptance_materialization_plan.json`
- Plan notes: `results/fidelity_acceptance_materialization_plan.md`
- Source draft: `external_validation/fidelity_acceptance_draft.json`
- Output path: `external_validation/fidelity_acceptance.json`
- Write enabled: `false`
- Acceptance write ready: `false`
- Strict fidelity evidence ready: `false`
- Missing operator text fields: `12`
- Missing confirmation flags: `5`

Dry-run plan command:

```powershell
python scripts\materialize_fidelity_acceptance.py
```

Guarded write command:

```powershell
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write
```

## ManiSkill Fidelity Metadata Probe

This probe is not evidence and does not satisfy fidelity acceptance. It records timing, backend, controller, observation, and asset metadata that the independent operator should verify or replace before promoting the fidelity acceptance file.

- Probe JSON: `results/maniskill_fidelity_metadata_probe.json`
- Probe notes: `results/maniskill_fidelity_metadata_probe.md`
- Metadata probe ready: `true`
- Strict metadata ready: `true`
- Accepted fidelity ready: `false`
- Primary metadata missing: `[]`
- Primary timing summary: `{'agent_uids': ['fetch', 'panda', 'panda_wristcam'], 'control_freq_hz_values': [20.0], 'control_timestep_seconds_values': [0.05], 'controller_types': ['CombinedController'], 'derived_substeps_per_control_step_values': [5.0], 'primary_metadata_env_count': 4, 'scene_backend_types': ['PhysxCpuSystem'], 'scene_timestep_seconds_values': [0.01], 'sim_freq_hz_values': [100.0], 'sim_timestep_seconds_values': [0.01]}`

Probe rebuild command:

```powershell
python scripts\probe_maniskill_fidelity_metadata.py
```

## ManiSkill Render-Video Preflight

This preflight is not evidence and does not satisfy fidelity acceptance. It checks whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before official collection, separating evidence-video readiness from diagnostic fallback videos.

- Audit JSON: `results/maniskill_render_video_preflight_audit.json`
- Audit notes: `results/maniskill_render_video_preflight_audit.md`
- Render video ready: `false`
- Strict external evidence ready: `false`
- Environments probed: `4`
- Render-ready environments: `0`
- Blocking missing: `['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: render preflight exceeded 30 seconds; OpenCabinetDrawer-v1: render preflight exceeded 30 seconds; OpenCabinetDoor-v1: render preflight exceeded 30 seconds; PullCubeTool-v1: render preflight exceeded 30 seconds']`
- Renderer failure classes: `['render_timeout']`
- Operator remediation items: `3`

Render preflight command:

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4
```

Renderer profile retest commands:

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 30 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```

## ManiSkill Render Machine Qualification

This packet is not evidence. It requires the exact collection machine to pass platform probing, render-backed MP4 preflight, pilot liveness, and zero diagnostic fallback videos before official collection can begin.

- Packet: `external_validation/render_machine_qualification_packet.md`
- Audit JSON: `results/maniskill_render_machine_qualification.json`
- Audit notes: `results/maniskill_render_machine_qualification.md`
- Qualification state: `DO_NOT_COLLECT_RENDER_MACHINE`
- Render machine qualified: `false`
- Strict external evidence ready: `false`
- Blocking missing: `['render_video_ready is false in results/maniskill_render_video_preflight_audit.json', 'PegInsertionSide-v1 has no render-backed MP4: render preflight exceeded 30 seconds', 'PegInsertionSide-v1 did not write a renderer-backed MP4', 'OpenCabinetDrawer-v1 has no render-backed MP4: render preflight exceeded 30 seconds', 'OpenCabinetDrawer-v1 did not write a renderer-backed MP4', 'OpenCabinetDoor-v1 has no render-backed MP4: render preflight exceeded 30 seconds', 'OpenCabinetDoor-v1 did not write a renderer-backed MP4', 'PullCubeTool-v1 has no render-backed MP4: render preflight exceeded 30 seconds', 'PullCubeTool-v1 did not write a renderer-backed MP4', 'pilot runtime liveness is not ready on the selected machine', 'pilot runtime render_video_ready is false']`

Qualification packet command:

```powershell
python scripts\build_maniskill_render_machine_qualification.py
```

## External Ablation Collection

This packet is not evidence. It converts the strict external ablation requirement into five manifest-declared work orders that must use the same accepted configs, skill library, resets, observation interface, and compute budget as the primary method.

- Packet: `external_validation/ablation_collection_packet.md`
- Work orders: `external_validation/ablation_collection_work_orders.csv`
- Audit JSON: `results/external_ablation_collection_audit.json`
- Audit notes: `results/external_ablation_collection_audit.md`
- Expected ablation records: `600`
- Work-order count: `5`
- Manifest ablation evidence ready: `false`
- Strict external evidence ready: `false`
- Blocking missing: `['manifest.ablations.basin_overlap is not true with manifest-declared external ablation evidence', 'manifest.ablations.barrier_height is not true with manifest-declared external ablation evidence', 'manifest.ablations.descent_continuity is not true with manifest-declared external ablation evidence', 'manifest.ablations.risk_calibration is not true with manifest-declared external ablation evidence', 'manifest.ablations.seam_repair is not true with manifest-declared external ablation evidence']`

Ablation packet command:

```powershell
python scripts\build_external_ablation_collection_packet.py
```

## External Evidence Intake Ledger

This ledger is not evidence. It maps every current strict external-evidence failure to the operator artifact, source packet, strict gate, and completion test that would close it.

- Ledger: `external_validation/evidence_intake_ledger.md`
- CSV: `external_validation/evidence_intake_ledger.csv`
- Audit JSON: `results/external_evidence_intake_ledger_audit.json`
- Audit notes: `results/external_evidence_intake_ledger_audit.md`
- Blocking failures mapped: `36/36`
- Closure groups: `8`
- Strict external evidence ready: `false`
- Unmapped failures: `[]`

Ledger rebuild command:

```powershell
python scripts\build_external_evidence_intake_ledger.py
```

## External Precollection Manifest Draft

This draft is not evidence. It pre-fills the task-config hashes and cutover command spine that are safe before collection, while keeping `external_validation/manifest.json` absent and every strict evidence gate false.

- Draft JSON: `external_validation/manifest_precollection_draft.json`
- Draft notes: `external_validation/manifest_precollection_draft.md`
- Audit JSON: `results/external_precollection_manifest_draft_audit.json`
- Audit notes: `results/external_precollection_manifest_draft_audit.md`
- Prepared config hashes: `4`
- Method gaps: `11`
- Rollout log/video gaps: `8`
- Manifest assembly blockers: `28`
- Official manifest exists: `false`
- Strict external evidence ready: `false`

Draft rebuild command:

```powershell
python scripts\build_external_precollection_manifest_draft.py
```

Draft-to-evidence cutover commands:

```powershell
python scripts\build_external_precollection_manifest_draft.py
```
```powershell
python scripts\materialize_fidelity_acceptance.py --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --confirm-code-commit <commit> --confirm-skill-library-hash <sha256> --write
```
```powershell
python scripts\audit_external_fidelity_acceptance.py --strict
```
```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path>
```
```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_manifest.py --write --check-video-paths
```
```powershell
python scripts\validate_external_configs.py --strict
```
```powershell
python scripts\validate_external_adapters.py --strict
```
```powershell
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
```
```powershell
python scripts\audit_external_pairing_integrity.py --strict
```
```powershell
python scripts\audit_external_release_package.py --strict
```
```powershell
python scripts\audit_external_evidence.py --strict
```

## Commands

Materialize real configs after platform selection:

```powershell
python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write
```

Strict backend qualification gate:

```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
```

Strict pre-collection gate:

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```

Actual collection command after the strict gate passes:

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

Official video write guard: the runner refuses diagnostic fallback sidecars, non-MP4-like files, undersized files, out-of-dir paths, or unexpected returned video paths before any official JSONL row is written.
Official JSONL write guard: the runner calls the strict rollout-record validator with video-path checks and refuses schema-invalid records before append.
atomic official evidence promotion: selected-batch videos are staged as `.staging.mp4`, and official videos/logs are replaced together only after the batch succeeds, preserving prior official videos/logs on failure.

Post-collection strict gates:

- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Operator Actions

- `platform_probe`: Probe the selected external platform machine
- `task_binding_probe`: Probe ManiSkill task-family bindings
- `env_smoke_probe`: Smoke-test bound ManiSkill environments
- `fidelity_metadata_probe`: Probe ManiSkill/SAPIEN fidelity metadata
- `platform_onboarding`: Onboard the public simulator platform
- `backend_module`: Select a non-template backend module
- `backend_integration_packet`: Use the backend integration packet as the public-simulator backend checklist
- `maniskill_reference_backend_audit`: Audit the repository ManiSkill/SAPIEN reference backend candidate
- `maniskill_reference_collection_preflight`: Audit explicit reference-backend collection preflight
- `real_task_configs`: Create real manifest-declared task configs
- `config_manifest_packet`: Use the config manifest packet as the task-config evidence checklist
- `rollout_evidence_packet`: Use the rollout evidence packet as the raw-log evidence checklist
- `ablation_collection_packet`: Collect manifest-declared external ablations
- `evidence_intake_ledger`: Use the evidence intake ledger to close every strict external-evidence failure
- `platform_fidelity`: Fill platform fidelity acceptance with real provenance
- `fidelity_acceptance_draft`: Generate the tracked ManiSkill fidelity acceptance draft
- `fidelity_acceptance_materializer`: Materialize fidelity acceptance only through the guarded promotion path
- `pilot_smoke_packet`: Run a quarantined first-panel backend smoke test
- `maniskill_pilot_runtime_liveness`: Audit bounded ManiSkill pilot runtime liveness
- `maniskill_render_video_preflight`: Audit ManiSkill render-backed evidence-video export
- `maniskill_render_machine_qualification`: Qualify the exact render machine before official collection
- `fidelity_provenance_packet`: Use the fidelity provenance packet as the platform acceptance checklist
- `alias_unseal`: Unseal method aliases only after configs, implementations, and run plan are frozen
- `specific_run_id`: Use a specific immutable external run id
- `real_method_implementations`: Replace scaffold-only methods with real non-oracle implementations or wrappers
- `method_implementation_packet`: Use the method implementation packet as the non-oracle work-order checklist
- `run_collection`: Collect paired-reset external rollouts
- `manifest_and_release`: Build the real manifest and hash-lock release artifacts
- `strict_rollout_recompute`: Recompute external metrics from raw JSONL logs
- `strict_adapter_evidence`: Audit independent method evidence after the manifest is real
- `final_strict_gate`: Run the final strict external-evidence gate

## Checks

- `pass` `acquisition_packet_ready`: passed=True, strict_evidence_ready=False
- `pass` `collection_preflight_fail_closed`: collection_ready=False, blocking_missing_count=4
- `pass` `maniskill_reference_preflight_reaches_only_fidelity_gate`: blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `fidelity_acceptance_draft_ready_but_fail_closed`: draft_ready=True, remaining_operator_inputs=10
- `pass` `fidelity_acceptance_materializer_guarded`: write_enabled=False, acceptance_write_ready=False
- `pass` `fidelity_metadata_probe_ready_but_not_evidence`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `render_video_preflight_recorded_but_not_evidence`: render_video_ready=False, envs=4, failure_classes=['render_timeout']
- `pass` `render_machine_qualification_recorded_but_not_evidence`: qualification_state='DO_NOT_COLLECT_RENDER_MACHINE', render_machine_qualified=False, blocking=11
- `pass` `ablation_collection_packet_recorded_but_not_evidence`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `evidence_intake_ledger_recorded_but_not_evidence`: mapped=36/36, groups=8
- `pass` `precollection_manifest_draft_ready_but_not_evidence`: configs=4, method_gaps=11, rollout_gaps=8, official_manifest_exists=False
- `pass` `operator_actions_cover_start_to_finish`: missing=[]
- `pass` `operator_action_titles_present`: missing_titles=[]
- `pass` `config_materializer_is_guarded`: write_enabled=False, task_count=4
- `pass` `backend_contract_gate_is_explicit`: python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
- `pass` `backend_action_runs_contract_before_readiness`: python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
python scripts\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
- `pass` `strict_collection_command_is_explicit`: python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
- `pass` `post_collection_gates_cover_evidence`: commands=8
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `packet_artifacts_exist`: runbook, runner, blinded sheet, alias map, platform checklist, and config schema
