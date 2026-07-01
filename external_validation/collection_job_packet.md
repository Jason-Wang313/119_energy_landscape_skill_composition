# External Collection Job Packet

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Job state: `DO_NOT_START_COLLECTION_YET`.
Collection ready: `false`.
Render machine qualified: `false`.

This packet is the ordered operator job for moving from machine qualification to official collection, hash sealing, manifest promotion, and final strict evidence audits. It is not rollout evidence and cannot satisfy the external-evidence requirement by itself.

Guarded command spine: `external_validation/collection_job_commands.ps1`.
Linux guarded command spine: `external_validation/collection_job_commands.sh`.
Operator checklist: `external_validation/collection_job_checklist.csv`.

## Current No-Go Blockers

- collection_readiness: backend_module_ready: --backend-module is required before actual collection
- collection_readiness: fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- collection_readiness: alias_unsealing_explicit: unsealed_alias_map=False
- collection_readiness: run_id_specific: run_id='paper119_external_validation_run'
- render_machine: render_video_ready is false in results/maniskill_render_video_preflight_audit.json
- render_machine: PegInsertionSide-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- render_machine: PegInsertionSide-v1 did not write a renderer-backed MP4
- render_machine: OpenCabinetDrawer-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- render_machine: OpenCabinetDrawer-v1 did not write a renderer-backed MP4
- render_machine: OpenCabinetDoor-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- render_machine: OpenCabinetDoor-v1 did not write a renderer-backed MP4
- render_machine: PullCubeTool-v1 has no render-backed MP4: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory
- render_machine: PullCubeTool-v1 did not write a renderer-backed MP4
- render_machine: pilot runtime liveness is not ready on the selected machine
- render_machine: pilot runtime used diagnostic fallback video; fallback media cannot count as external evidence
- render_machine: pilot runtime render_video_ready is false

## Ordered Job Steps

### 1. platform_probe

- Phase: `machine_qualification`
- Owner: `independent_operator`
- May run now: `true`
- Boundary: `non_evidence_preflight`
- Blocked until: none
- Acceptance: Exact collection machine provenance, package versions, renderer/GPU state, code commit, and config/backend hashes are recorded.

```powershell
python scripts\probe_external_platform.py
```

### 2. render_profile_matrix

- Phase: `machine_qualification`
- Owner: `independent_operator`
- May run now: `true`
- Boundary: `non_evidence_preflight`
- Blocked until: accepted render backend and shader pack are supplied on the collection machine
- Acceptance: Every primary ManiSkill/SAPIEN task family writes renderer-backed RGB MP4s; diagnostic fallback media remain excluded.

```powershell
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
```

### 3. pilot_runtime_liveness

- Phase: `machine_qualification`
- Owner: `independent_operator`
- May run now: `true`
- Boundary: `non_evidence_preflight`
- Blocked until: render-backed MP4 export works without diagnostic fallback media
- Acceptance: Pilot liveness reports pilot_runtime_ready=true, render_video_ready=true, runner_io_ready=true, records>=1, videos>=1, and zero diagnostic fallbacks.

```powershell
python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180
```

### 4. backend_contract

- Phase: `backend_and_fidelity`
- Owner: `jason_or_independent_operator`
- May run now: `true`
- Boundary: `non_evidence_preflight`
- Blocked until: selected backend module exists and is the one to be used for official collection
- Acceptance: Selected backend satisfies the runner contract, task configs, alias map, video writer, and metadata requirements before collection readiness is trusted.

```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
```

### 5. fidelity_acceptance_materialization

- Phase: `backend_and_fidelity`
- Owner: `independent_operator`
- May run now: `false`
- Boundary: `guarded_acceptance_write`
- Blocked until: all precollection operator fields are real, checkout/hash guards match, and render/liveness gates pass
- Acceptance: Independent operator acceptance is materialized only after real platform, render-backed video readiness, paired replay, commit, and skill-library hash confirmations; rollout logs and manifest declaration are postcollection strict gates.

```powershell
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
```

### 6. strict_collection_readiness

- Phase: `collection_gate`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `non_evidence_go_no_go_gate`
- Blocked until: fidelity acceptance, explicit run id, unsealed aliases, backend module, and render-machine qualification are complete
- Acceptance: Strict collection readiness passes with a specific run id, explicit alias unsealing, accepted fidelity, empty official output dirs, and real backend/config inputs.

```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --run-id <accepted_run_id> --unsealed-alias-map
```

### 7. precollection_freeze_receipt

- Phase: `collection_gate`
- Owner: `independent_operator`
- May run now: `false`
- Boundary: `precollection_hash_lock`
- Blocked until: strict collection readiness passes and operator metadata is real
- Acceptance: Operator sheet, aliases, configs, candidate method-config hashes, method cutover checklist, manifest draft, runner files, and source audits are hash-locked before official collection.

```powershell
python scripts\build_external_precollection_freeze_receipt.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
```

### 8. official_collection_runner

- Phase: `official_collection`
- Owner: `independent_operator`
- May run now: `false`
- Boundary: `writes_official_logs_and_videos`
- Blocked until: ConfirmOfficialCollection switch, no placeholder fields, freeze receipt, and strict readiness pass
- Acceptance: Official JSONL rows and renderer-backed MP4s are produced by the accepted backend under the accepted run id without diagnostic fallback promotion.

```powershell
python external_validation\runner\real_collection_runner.py --backend-module external_validation\runner\maniskill_reference_backend.py --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <accepted_run_id> --unsealed-alias-map
```

### 9. postcollection_evidence_seal

- Phase: `postcollection_seal`
- Owner: `independent_operator`
- May run now: `false`
- Boundary: `postcollection_hash_seal`
- Blocked until: official collection produced complete logs/videos for the accepted run id
- Acceptance: Raw JSONL logs, rollout videos, prepared configs, precollection receipt, and operator metadata are hash-sealed before manifest promotion.

```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module external_validation\runner\maniskill_reference_backend.py --run-id <accepted_run_id> --operator-id <independent_operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
```

### 10. postcollection_seal_consistency

- Phase: `postcollection_seal`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `postcollection_hash_recompute_gate`
- Blocked until: postcollection evidence seal exists for complete official artifacts
- Acceptance: Sealed raw-log, video, config, precollection, and metadata hashes recompute without drift before manifest promotion.

```powershell
python scripts\audit_external_postcollection_seal_consistency.py
```

### 11. manifest_promotion

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `manifest_write`
- Blocked until: postcollection seal consistency passes
- Acceptance: external_validation/manifest.json is written only from hash-sealed logs, videos, configs, methods, metrics, and release metadata.

```powershell
python scripts\build_external_manifest.py --write --check-video-paths
```

### 12. strict_rollout_recompute

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `strict_rollout_metric_gate`
- Blocked until: manifest contains real logs/videos/configs for the accepted run
- Acceptance: External rollout metrics are recomputed from raw JSONL logs and MP4 paths under strict sample-count, video, pairing, and confidence gates.

```powershell
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
```

### 13. strict_config_evidence

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `strict_config_gate`
- Blocked until: manifest declares real configs and hashes
- Acceptance: Manifest-declared task configs exist, hash-match, and replace non-evidence templates under strict config evidence rules.

```powershell
python scripts\validate_external_configs.py --strict
```

### 14. strict_adapter_evidence

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `strict_method_gate`
- Blocked until: manifest declares independent method evidence for all required baselines
- Acceptance: All non-oracle methods use manifest-declared independent implementations and checkpoint/config hashes rather than scaffolds or reference adapters.

```powershell
python scripts\validate_external_adapters.py --strict
```

### 15. strict_pairing_integrity

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `strict_pairing_gate`
- Blocked until: manifest-declared raw logs pass rollout recomputation
- Acceptance: Paired-reset method panels are complete, unique, and consistent across task/config/method/hash identities.

```powershell
python scripts\audit_external_pairing_integrity.py --strict
```

### 16. strict_release_package

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `strict_release_gate`
- Blocked until: manifest and postcollection hashes are complete
- Acceptance: Release package recomputes manifest hashes and rejects internal, staged, diagnostic, fallback, empty-video, and non-MP4-like artifacts.

```powershell
python scripts\audit_external_release_package.py --strict
```

### 17. final_external_evidence_audit

- Phase: `manifest_and_strict_gates`
- Owner: `jason_or_independent_operator`
- May run now: `false`
- Boundary: `final_external_evidence_gate`
- Blocked until: all previous strict gates pass
- Acceptance: The final strict external evidence audit passes only when real/high-fidelity rollouts, configs, videos, methods, metrics, ablations, pairing, and release hashes satisfy all gates.

```powershell
python scripts\audit_external_evidence.py --strict
```

## Checks

- `pass` `job_packet_is_non_evidence`: writes only packet/audit/checklist/guarded command-spine artifacts
- `pass` `source_payloads_loaded`: operator, collection, render, intake, pre/postcollection, and self-test payloads are loaded
- `pass` `job_state_fail_closed_until_render_and_collection_ready`: job_state=DO_NOT_START_COLLECTION_YET, render_qualified=False, collection_ready=False, start_state='DO_NOT_COLLECT_YET'
- `pass` `command_sequence_covers_full_external_validation_route`: missing=[]
- `pass` `command_order_preserves_preflight_collection_manifest_safety`: positions={'platform_probe': 0, 'render_profile_matrix': 1, 'pilot_runtime_liveness': 2, 'backend_contract': 3, 'fidelity_acceptance_materialization': 4, 'strict_collection_readiness': 5, 'precollection_freeze_receipt': 6, 'official_collection_runner': 7, 'postcollection_evidence_seal': 8, 'postcollection_seal_consistency': 9, 'manifest_promotion': 10, 'strict_rollout_recompute': 11, 'strict_config_evidence': 12, 'strict_adapter_evidence': 13, 'strict_pairing_integrity': 14, 'strict_release_package': 15, 'final_external_evidence_audit': 16}
- `pass` `official_collection_commands_guarded`: PowerShell and Bash job spines require explicit confirmation, placeholder checks, runner, manifest, and final strict evidence gate
- `pass` `linux_command_spine_uses_lf_line_endings`: Bash job spine is generated with LF-only content for Linux collection machines
- `pass` `current_blockers_explicit_and_mapped`: current_blockers=16, submission_blockers=4, mapped=37/37
- `pass` `pre_and_postcollection_hash_gates_present`: manifest_draft=True, freeze_ready=False, seal_ready=False, consistency_ready=False
- `pass` `render_machine_self_test_proves_ready_and_fail_closed_cases`: ready='QUALIFIED_FOR_RENDER_BACKED_PILOT', fail='DO_NOT_COLLECT_RENDER_MACHINE', fallback=True
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
