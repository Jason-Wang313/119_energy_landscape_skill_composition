# External Evidence Acquisition Packet

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.

This packet maps the remaining main-conference blockers to concrete operator inputs, artifacts, and strict validation commands. It is not robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for the strict external audits.

## Remaining Submission Blockers

| Requirement | Operator actions |
|---|---|
| `Independent real-robot or accepted high-fidelity external validation evidence` | `platform_probe`, `task_binding_probe`, `env_smoke_probe`, `fidelity_metadata_probe`, `platform_onboarding`, `fidelity_provenance_packet`, `backend_integration_packet`, `maniskill_reference_backend_audit`, `maniskill_reference_collection_preflight`, `fidelity_acceptance_draft`, `fidelity_acceptance_materializer`, `rollout_evidence_packet`, `backend_module`, `platform_fidelity`, `pilot_smoke_packet`, `maniskill_render_video_preflight`, `maniskill_pilot_runtime_liveness`, `maniskill_render_machine_qualification`, `ablation_collection_packet`, `evidence_intake_ledger`, `run_collection`, `manifest_and_release` |
| `External rollout metrics recomputed from raw JSONL logs` | `rollout_evidence_packet`, `ablation_collection_packet`, `evidence_intake_ledger`, `run_collection`, `strict_rollout_recompute` |
| `Manifest-declared real task configs replace non-evidence templates` | `config_manifest_packet`, `evidence_intake_ledger`, `real_task_configs`, `manifest_and_release` |
| `Manifest-declared independent non-oracle baseline evidence and fairness contract` | `method_implementation_packet`, `evidence_intake_ledger`, `real_method_implementations`, `strict_adapter_evidence` |

## Collection Preflight Blockers

- `backend_module_ready`: --backend-module is required before actual collection
- `fidelity_acceptance_ready`: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- `alias_unsealing_explicit`: unsealed_alias_map=False
- `run_id_specific`: run_id='paper119_external_validation_run'

## Operator Actions

| ID | Action | Operator input | Key artifacts | Commands |
|---|---|---|---|---|
| `platform_probe` | Probe the selected external platform machine | `run the non-evidence probe on the GPU workstation or accepted robot/simulator machine before backend qualification` | `results/external_platform_probe.json`<br>`results/external_platform_probe.md` | `python scripts\probe_external_platform.py`<br>`python scripts\probe_external_platform.py --strict` |
| `task_binding_probe` | Probe ManiSkill task-family bindings | `bind each Paper 119 task family to concrete ManiSkill/SAPIEN environment candidates and inspect the local registry when available` | `external_validation/maniskill_task_bindings.json`<br>`results/maniskill_task_binding_probe.json`<br>`results/maniskill_task_binding_probe.md` | `python scripts\probe_maniskill_task_bindings.py`<br>`python scripts\probe_maniskill_task_bindings.py --strict` |
| `env_smoke_probe` | Smoke-test bound ManiSkill environments | `construct and reset the bound public-simulator environment candidates without writing rollout logs or videos` | `results/maniskill_env_smoke_probe.json`<br>`results/maniskill_env_smoke_probe.md` | `python scripts\probe_maniskill_env_smoke.py`<br>`python scripts\probe_maniskill_env_smoke.py --strict` |
| `fidelity_metadata_probe` | Probe ManiSkill/SAPIEN fidelity metadata | `record non-evidence timing, scene/backend, controller, observation, and asset metadata for every bound environment candidate` | `results/maniskill_fidelity_metadata_probe.json`<br>`results/maniskill_fidelity_metadata_probe.md` | `python scripts\probe_maniskill_fidelity_metadata.py`<br>`python scripts\probe_maniskill_fidelity_metadata.py --strict` |
| `platform_onboarding` | Onboard the public simulator platform | `GPU workstation or accepted robot/simulator platform plus recorded version/provenance fields` | `external_validation/platform_onboarding_packet.md`<br>`external_validation/platform_onboarding_packet.json`<br>`results/external_platform_probe.json`<br>`results/maniskill_task_binding_probe.json`<br>`results/maniskill_env_smoke_probe.json`<br>`results/maniskill_fidelity_metadata_probe.json`<br>`results/external_platform_onboarding_audit.json` | `python scripts\probe_external_platform.py`<br>`python scripts\probe_maniskill_task_bindings.py`<br>`python scripts\probe_maniskill_env_smoke.py`<br>`python scripts\probe_maniskill_fidelity_metadata.py`<br>`python scripts\build_external_platform_onboarding.py`<br>`python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json`<br>`python scripts\audit_external_fidelity_acceptance.py --strict` |
| `backend_module` | Select a non-template backend module | `--backend-module <module_or_path>` | `external_validation/runner/backends/<real_backend>.py` | `python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json`<br>`python scripts\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map` |
| `backend_integration_packet` | Use the backend integration packet as the public-simulator backend checklist | `complete the non-template backend work orders with real module, provenance, task binding, hashes, logs, and videos` | `external_validation/backend_integration_packet.md`<br>`external_validation/backend_integration_work_orders.csv`<br>`results/external_backend_integration_audit.json` | `python scripts\build_external_backend_integration_packet.py`<br>`python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json` |
| `maniskill_reference_backend_audit` | Audit the repository ManiSkill/SAPIEN reference backend candidate | `use the tracked reference backend to inspect API/config/adapter wiring before replacing or wrapping it with a real evidence backend` | `external_validation/runner/maniskill_reference_backend.py`<br>`results/maniskill_backend_readiness_audit.json`<br>`results/maniskill_backend_readiness_audit.md` | `python scripts\audit_maniskill_backend_readiness.py` |
| `maniskill_reference_collection_preflight` | Audit explicit reference-backend collection preflight | `use the tracked reference backend with prepared configs, an explicit run id, and unsealed aliases to verify that preflight reaches the fidelity gate` | `results/maniskill_reference_collection_preflight_audit.json`<br>`results/maniskill_reference_collection_preflight_audit.md`<br>`external_validation/runner/maniskill_reference_backend.py` | `python scripts\audit_maniskill_reference_collection_preflight.py` |
| `real_task_configs` | Create real manifest-declared task configs | `external_validation/configs/<task_family>.json for each task family` | `external_validation/configs/peg_place_regrasp.json`<br>`external_validation/configs/drawer_to_pick_transfer.json`<br>`external_validation/configs/door_open_navigation.json`<br>`external_validation/configs/cable_route_insert.json` | `python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`<br>`python scripts\validate_external_configs.py --strict` |
| `config_manifest_packet` | Use the config manifest packet as the task-config evidence checklist | `manifest-declare prepared configs with hashes only after real platform, log, and video artifacts exist` | `external_validation/config_manifest_packet.md`<br>`external_validation/config_manifest_work_orders.csv`<br>`results/external_config_manifest_audit.json` | `python scripts\build_external_config_manifest_packet.py`<br>`python scripts\build_external_manifest.py --write --check-video-paths`<br>`python scripts\validate_external_configs.py --strict` |
| `rollout_evidence_packet` | Use the rollout evidence packet as the raw-log evidence checklist | `complete the rollout work orders with manifest-declared JSONL logs, videos, config hashes, method hashes, and strict recomputation` | `external_validation/rollout_evidence_packet.md`<br>`external_validation/rollout_evidence_work_orders.csv`<br>`results/external_rollout_evidence_audit.json` | `python scripts\build_external_rollout_evidence_packet.py`<br>`python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`<br>`python scripts\audit_external_pairing_integrity.py --strict`<br>`python scripts\audit_external_evidence.py --strict` |
| `ablation_collection_packet` | Collect manifest-declared external ablations | `five required ablated variants on the same accepted task configs, skill library, paired resets, observation interface, and compute budget` | `external_validation/ablation_collection_packet.md`<br>`external_validation/ablation_collection_work_orders.csv`<br>`results/external_ablation_collection_audit.json` | `python scripts\build_external_ablation_collection_packet.py`<br>`python scripts\build_external_manifest.py --write --check-video-paths`<br>`python scripts\audit_external_evidence.py --strict` |
| `evidence_intake_ledger` | Use the evidence intake ledger to close every strict external-evidence failure | `complete the ledger rows for manifest, fidelity, configs, logs/videos, methods, metrics, ablations, pairing, release hashes, and oracle-boundary explanation` | `external_validation/evidence_intake_ledger.md`<br>`external_validation/evidence_intake_ledger.csv`<br>`results/external_evidence_intake_ledger_audit.json` | `python scripts\build_external_evidence_intake_ledger.py`<br>`python scripts\build_external_manifest.py --write --check-video-paths`<br>`python scripts\audit_external_evidence.py --strict` |
| `platform_fidelity` | Fill platform fidelity acceptance with real provenance | `accepted simulator or robot evidence, contact/dynamics/camera/state provenance, and task coverage` | `external_validation/fidelity_acceptance.json` | `python scripts\audit_external_fidelity_acceptance.py --strict` |
| `fidelity_acceptance_draft` | Generate the tracked ManiSkill fidelity acceptance draft | `review the prefilled draft, replace draft-only fields with accepted independent provenance, then promote it only after real platform evidence exists` | `external_validation/fidelity_acceptance_draft.json`<br>`external_validation/fidelity_acceptance_draft.md`<br>`results/external_fidelity_acceptance_draft_audit.json` | `python scripts\build_external_fidelity_acceptance_draft.py`<br>`python scripts\audit_external_fidelity_acceptance.py --strict` |
| `fidelity_acceptance_materializer` | Materialize fidelity acceptance only through the guarded promotion path | `real platform provenance, independent operator signoff, render-backed evidence-video readiness, real rollout evidence, manifest declaration, current clean-checkout code commit, and current skill-library hash` | `scripts/materialize_fidelity_acceptance.py`<br>`results/fidelity_acceptance_materialization_plan.json`<br>`results/fidelity_acceptance_materialization_plan.md`<br>`external_validation/fidelity_acceptance.json` | `python scripts\materialize_fidelity_acceptance.py`<br>`python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <current_clean_checkout_commit_sha> --skill-library-hash <current_baselines_sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write`<br>`python scripts\audit_external_fidelity_acceptance.py --strict` |
| `pilot_smoke_packet` | Run a quarantined first-panel backend smoke test | `real backend, accepted fidelity gate, prepared configs, unsealed aliases, and a pilot-specific run id` | `external_validation/pilot_smoke_packet.md`<br>`external_validation/pilot_smoke_work_orders.csv`<br>`results/external_pilot_smoke_packet_audit.json`<br>`results/external_pilot_smoke_audit.json` | `python scripts\build_external_pilot_smoke_packet.py`<br>`python scripts\audit_external_pilot_smoke.py --strict --expected-records 12 --check-video-paths` |
| `maniskill_pilot_runtime_liveness` | Audit bounded ManiSkill pilot runtime liveness | `tracked reference backend, prepared configs, unsealed aliases, pilot-specific run id, and a bounded timeout on the selected runtime machine` | `scripts/audit_maniskill_pilot_runtime_liveness.py`<br>`results/maniskill_pilot_runtime_liveness_audit.json`<br>`results/maniskill_pilot_runtime_liveness_audit.md` | `python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 60 --max-rows 1` |
| `maniskill_render_video_preflight` | Audit ManiSkill render-backed evidence-video export | `selected ManiSkill/SAPIEN runtime machine with renderer access before full external collection` | `scripts/audit_maniskill_render_video_preflight.py`<br>`results/maniskill_render_video_preflight_audit.json`<br>`results/maniskill_render_video_preflight_audit.md` | `python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4` |
| `maniskill_render_machine_qualification` | Qualify the exact render machine before official collection | `accepted collection machine with platform probe, render-backed MP4 preflight, pilot liveness, and no diagnostic fallback videos` | `external_validation/render_machine_qualification_packet.md`<br>`scripts/build_maniskill_render_machine_qualification.py`<br>`results/maniskill_render_machine_qualification.json`<br>`results/maniskill_render_machine_qualification.md` | `python scripts\build_maniskill_render_machine_qualification.py` |
| `fidelity_provenance_packet` | Use the fidelity provenance packet as the platform acceptance checklist | `complete platform physics/contact, paired-reset replay, operator independence, calibration basis, code commit, skill-library hash, and acceptance gates` | `external_validation/fidelity_provenance_packet.md`<br>`external_validation/fidelity_provenance_work_orders.csv`<br>`results/external_fidelity_provenance_audit.json` | `python scripts\build_external_fidelity_provenance_packet.py`<br>`python scripts\audit_external_fidelity_acceptance.py --strict`<br>`python scripts\build_external_manifest.py --write --check-video-paths` |
| `alias_unseal` | Unseal method aliases only after configs, implementations, and run plan are frozen | `--unsealed-alias-map` | `external_validation/method_alias_map.json` | `python scripts\audit_external_collection_readiness.py --strict --unsealed-alias-map` |
| `specific_run_id` | Use a specific immutable external run id | `--run-id <platform>_<date>_<protocol_version>` | `external_validation/logs/*.jsonl` | `python scripts\audit_external_collection_readiness.py --strict --run-id <specific_run_id>` |
| `real_method_implementations` | Replace scaffold-only methods with real non-oracle implementations or wrappers | `implementation_path and checkpoint_or_config_path/hash for every non-oracle method` | `external_validation/adapters/<method>/implementation.py`<br>`external_validation/baselines/<method>/implementation.py`<br>`external_validation/checkpoints_or_configs/<method>.*` | `python scripts\build_external_baseline_contract.py`<br>`python scripts\validate_external_adapters.py --strict` |
| `method_implementation_packet` | Use the method implementation packet as the non-oracle work-order checklist | `complete every non-oracle method work order with real implementation/config/checkpoint paths and hashes` | `external_validation/method_implementation_packet.md`<br>`external_validation/method_implementation_work_orders.csv`<br>`external_validation/method_reference_provenance.csv`<br>`external_validation/adapter_acceptance_fixtures.json`<br>`external_validation/adapter_acceptance_fixtures.md`<br>`external_validation/adapter_acceptance_fixtures.csv`<br>`results/external_method_implementation_audit.json` | `python scripts\build_external_method_implementation_packet.py`<br>`python scripts\validate_external_adapters.py --strict` |
| `run_collection` | Collect paired-reset external rollouts | `1,440 JSONL records over 4 tasks x 12 methods x 120 paired resets` | `external_validation/logs/peg_place_regrasp.jsonl`<br>`external_validation/logs/drawer_to_pick_transfer.jsonl`<br>`external_validation/logs/door_open_navigation.jsonl`<br>`external_validation/logs/cable_route_insert.jsonl`<br>`external_validation/videos/<task_family>/*` | `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map` |
| `manifest_and_release` | Build the real manifest and hash-lock release artifacts | `manifest paths, code commit, skill-library hash, config/log/video/checkpoint hashes` | `external_validation/manifest.json`<br>`external_validation/manifest_assembly_checklist.csv`<br>`results/external_manifest_builder_report.json` | `python scripts\build_external_manifest.py --write --check-video-paths`<br>`python scripts\audit_external_release_package.py --strict` |
| `strict_rollout_recompute` | Recompute external metrics from raw JSONL logs | `strict rollout validator over manifest-declared logs and videos` | `results/external_rollout_metrics.json`<br>`results/external_rollout_metrics.md` | `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict` |
| `strict_adapter_evidence` | Audit independent method evidence after the manifest is real | `manifest-declared non-oracle implementation paths and hashes` | `results/external_baseline_contract_audit.json`<br>`results/external_adapter_contract_evidence_audit.json` | `python scripts\build_external_baseline_contract.py`<br>`python scripts\validate_external_adapters.py --strict` |
| `final_strict_gate` | Run the final strict external-evidence gate | `completed manifest, logs, videos, configs, checkpoints/hashes, adapters, and fidelity acceptance` | `results/external_evidence_audit.json`<br>`results/submission_readiness_gap_audit.json` | `python scripts\audit_external_pairing_integrity.py --strict`<br>`python scripts\audit_external_evidence.py --strict`<br>`python scripts\audit_submission_readiness_gap.py` |

## ManiSkill Render-Video Preflight

- Render video ready: `false`
- Renderer failure classes: `['vulkan_descriptor_pool_exhaustion']`
- Renderer failure stages: `['initial_render_start']`
- Operator remediation items: `5`
- Blocking missing: `['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done)']`

Renderer profile retest commands:

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend gpu --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 1 --width 64 --height 64 --render-backend sapien_cuda --shader-pack minimal
```
```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4 --width 64 --height 64 --render-backend cpu --shader-pack minimal
```

## External Ablation Collection

- Manifest ablation evidence ready: `false`
- Expected ablation records: `600`
- Work orders: `5`
- Blocking missing: `['manifest.ablations.basin_overlap is not true with manifest-declared external ablation evidence', 'manifest.ablations.barrier_height is not true with manifest-declared external ablation evidence', 'manifest.ablations.descent_continuity is not true with manifest-declared external ablation evidence', 'manifest.ablations.risk_calibration is not true with manifest-declared external ablation evidence', 'manifest.ablations.seam_repair is not true with manifest-declared external ablation evidence']`

## External Evidence Intake Ledger

- Blocking failures mapped: `37/37`
- Closure groups: `8`
- Strict external evidence ready: `false`
- Unmapped failures: `[]`
- Ledger: `external_validation/evidence_intake_ledger.md`
- CSV: `external_validation/evidence_intake_ledger.csv`

## Strict Collection Command

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

## Post-Collection Strict Gates

- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Checks

- `pass` `source_audits_exist`: results/external_collection_readiness_audit.json, results/external_evidence_preflight.json, results/independent_validation_route_audit.json, results/external_platform_probe.json, results/maniskill_task_binding_probe.json, results/maniskill_env_smoke_probe.json, results/external_platform_onboarding_audit.json, results/external_fidelity_provenance_audit.json, results/external_fidelity_acceptance_draft_audit.json, results/fidelity_acceptance_materialization_plan.json, results/external_config_materialization_plan.json, results/external_backend_contract_audit.json, results/external_backend_integration_audit.json, results/maniskill_backend_readiness_audit.json, results/maniskill_reference_collection_preflight_audit.json, results/external_config_manifest_audit.json, results/external_rollout_evidence_audit.json, results/external_ablation_collection_audit.json, results/external_evidence_intake_ledger_audit.json, results/external_method_implementation_audit.json, results/external_pilot_smoke_packet_audit.json, results/maniskill_render_video_preflight_audit.json, results/maniskill_pilot_runtime_liveness_audit.json
- `pass` `gap_audit_has_four_external_blockers`: missing=['Independent real-robot or accepted high-fidelity external validation evidence', 'External rollout metrics recomputed from raw JSONL logs', 'Manifest-declared real task configs replace non-evidence templates', 'Manifest-declared independent non-oracle baseline evidence and fairness contract']
- `pass` `all_missing_requirements_mapped`: unmapped=[]
- `pass` `all_action_ids_exist`: missing_action_ids=[]
- `pass` `collection_preflight_fail_closed`: collection_ready=False, blockers=['alias_unsealing_explicit', 'backend_module_ready', 'fidelity_acceptance_ready', 'run_id_specific']
- `pass` `config_intake_directory_tracked`: task_config_dir_exists=True
- `pass` `config_materializer_ready`: passed=True, write_enabled=False, task_count=4
- `pass` `backend_contract_gate_ready`: harness_ready=True, actual_backend_ready=False
- `pass` `backend_integration_packet_ready`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `maniskill_reference_backend_audit_ready`: backend_contract_ready=True, video_writer_ready=True, official_collection_ready=False
- `pass` `maniskill_reference_collection_preflight_ready`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `config_manifest_packet_ready`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_ready`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `ablation_collection_packet_ready`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `evidence_intake_ledger_ready`: mapped=37/37, groups=8
- `pass` `pilot_smoke_packet_ready`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_render_video_preflight_recorded`: render_video_ready=False, envs=4, failure_classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `maniskill_pilot_runtime_liveness_ready`: pilot_runtime_ready=False, runner_io_ready=False, render_video_ready=False, timed_out=False, records=0, videos=0, diagnostic_fallbacks=1, failure_summary='official video guard rejected diagnostic fallback sidecar before JSONL write after progress stage record_video_start'
- `pass` `maniskill_render_machine_qualification_ready`: qualification_state='DO_NOT_COLLECT_RENDER_MACHINE', render_machine_qualified=False, blocking=12
- `pass` `method_implementation_packet_ready`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `preflight_operator_actions_present`: operator_next_actions=5, evidence_ready=False
- `pass` `route_independent_of_haonan`: primary_route='maniskill_sapien_primary'
- `pass` `platform_probe_ready`: primary_route_install_ready=True, missing=[]
- `pass` `task_binding_probe_ready`: strict_task_binding_install_ready=True, missing=[]
- `pass` `env_smoke_probe_ready`: strict_env_smoke_ready=True, primary_reset_missing=[]
- `pass` `fidelity_metadata_probe_ready`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `platform_onboarding_ready`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_provenance_packet_ready`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_draft_ready`: draft_ready=True, remaining_operator_inputs=10, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_ready`: write_enabled=False, acceptance_write_ready=False
- `pass` `post_collection_strict_commands_cover_all_gates`: missing_command_fragments=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `operator_actions_cover_collection_blockers`: Probe the selected external platform machine Probe ManiSkill task-family bindings Smoke-test bound ManiSkill environments Probe ManiSkill/SAPIEN fidelity metadata Onboard the public simulator platform Select a non-template backend module Use the backend integration packet as the public-simulator backend checklist Audit the repository ManiSkill/SAPIEN reference backend candidate Audit explicit reference-backend collection preflight Create real manifest-declared task configs Use the config manifest packet as the task-config evidence checklist Use the rollout evidence packet as the raw-log evidence checklist Collect manifest-declared external ablations Use the evidence intake ledger to close every strict external-evidence failure Fill platform fidelity acceptance with real provenance Generate the tracked ManiSkill fidelity acceptance draft Materialize fidelity acceptance only through the guarded promotion path Run a quarantined first-panel backend smoke test Audit bounded ManiSkill pilot runtime liveness Audit ManiSkill render-backed evidence-video export Qualify the exact render machine before official collection Use the fidelity provenance packet as the platform acceptance checklist Unseal method aliases only after configs, implementations, and run plan are frozen Use a specific immutable external run id Replace scaffold-only methods with real non-oracle implementations or wrappers Use the method implementation packet as the non-oracle work-order checklist Collect paired-reset external rollouts Build the real manifest and hash-lock release artifacts Recompute external metrics from raw JSONL logs Audit independent method evidence after the manifest is real Run the final strict external-evidence gate
- `pass` `backend_action_runs_contract_before_readiness`: python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json; python scripts\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
