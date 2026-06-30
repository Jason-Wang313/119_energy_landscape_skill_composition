# External Evidence Closure Brief

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Current decision: `STRONG_REVISE`.
Current readiness: `17/21` requirements satisfied.
Blocking missing requirements: `4`.
Haonan dependency: `false`.

This is the compact closure recipe for the remaining proof layer. It does not create robot evidence, simulator evidence, rollout logs, videos, checkpoints, or `external_validation/manifest.json`. Its job is to make the final validation layer unambiguous: an independent operator must close all four external-evidence blockers through the strict gates below.

## Minimum Proof Package

### accepted_fidelity_and_manifest

- Requirement: `Independent real-robot or accepted high-fidelity external validation evidence`
- Current blocker: strict external evidence audit is NOT_READY; real manifest/log/video/checkpoint evidence and accepted robot/simulator fidelity provenance are missing
- Evidence ready now: `false`
- Proof artifacts:
  - `external_validation/fidelity_acceptance.json`
  - `external_validation/manifest.json`
  - `external_validation/platform_onboarding_packet.json`
  - `external_validation/precollection_freeze_receipt.json`
  - `external_validation/postcollection_evidence_seal.json`
- Operator inputs:
  - independent operator or lab identity
  - accepted robot or high-fidelity simulator machine
  - contact solver, friction model, timing, observation, controller, and asset provenance
  - render-backed video readiness and paired-reset replay acceptance
  - current clean code commit and skill-library hash
- Strict gates:
  - `python scripts\materialize_fidelity_acceptance.py ... --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write`
  - `python scripts\audit_external_fidelity_acceptance.py --strict`
  - `python scripts\build_external_manifest.py --write --check-video-paths`
  - `python scripts\audit_external_evidence.py --strict`
- Completion test: accepted fidelity provenance exists, the official manifest exists, and the final strict external evidence audit no longer reports fidelity or manifest blockers

### raw_rollouts_videos_and_metrics

- Requirement: `External rollout metrics recomputed from raw JSONL logs`
- Current blocker: strict rollout validation does not pass because external_validation/manifest.json and raw logs are missing
- Evidence ready now: `false`
- Proof artifacts:
  - `external_validation/logs/*.jsonl`
  - `external_validation/videos/<task_family>/*.mp4`
  - `results/external_rollout_metrics.json`
  - `results/external_rollout_metrics.md`
- Operator inputs:
  - paired resets for every task/method panel
  - official JSONL rows written only by the checked runner path
  - render-backed MP4 videos for success and failure evidence
  - manifest-declared task, method, config, and policy/config hashes
- Strict gates:
  - `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map`
  - `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
  - `python scripts\audit_external_pairing_integrity.py --strict`
  - `python scripts\audit_external_evidence.py --strict`
- Completion test: strict rollout validation recomputes metrics from raw JSONL logs and the final audit agrees with the manifest metrics

### manifest_bound_task_configs

- Requirement: `Manifest-declared real task configs replace non-evidence templates`
- Current blocker: strict config evidence audit has no real manifest-declared configs
- Evidence ready now: `false`
- Proof artifacts:
  - `external_validation/configs/peg_place_regrasp.json`
  - `external_validation/configs/drawer_to_pick_transfer.json`
  - `external_validation/configs/door_open_navigation.json`
  - `external_validation/configs/cable_route_insert.json`
  - `external_validation/manifest.json`
- Operator inputs:
  - accepted backend task binding for each task family
  - real platform timing and query-budget fields
  - manifest config_path/config_hash fields matching the collected logs
- Strict gates:
  - `python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
  - `python scripts\validate_external_configs.py --strict`
  - `python scripts\build_external_manifest.py --write --check-video-paths`
  - `python scripts\audit_external_evidence.py --strict`
- Completion test: strict config evidence passes against manifest-declared config files and hashes rather than template or local-dry-run configs

### independent_methods_and_fairness_contract

- Requirement: `Manifest-declared independent non-oracle baseline evidence and fairness contract`
- Current blocker: baseline contract still reports manifest-declared independent non-oracle evidence as missing; strict adapter contract evidence audit has no passing manifest-declared real implementations
- Evidence ready now: `false`
- Proof artifacts:
  - `external_validation/method_implementation_work_orders.csv`
  - `external_validation/method_manifest_cutover_checklist.csv`
  - `external_validation/method_config_candidates.csv`
  - `external_validation/manifest.json`
  - `external_validation/checkpoints_or_configs/<method>.*`
- Operator inputs:
  - real non-oracle implementation/config/checkpoint path for every required method
  - checkpoint_or_config_hash values backed by real artifacts, not implementation source
  - matching JSONL policy_or_config_hash values
  - shared skill library, observation interface, compute budget, and paired-reset contract hashes
- Strict gates:
  - `python scripts\build_external_baseline_contract.py`
  - `python scripts\validate_external_adapters.py --strict`
  - `python scripts\audit_external_release_package.py --strict`
  - `python scripts\audit_external_evidence.py --strict`
- Completion test: strict adapter evidence passes and the final audit accepts the independent non-oracle method evidence plus fairness contract

## Chronological Command Spine

These commands are placeholders until an independent operator supplies real platform identifiers, backend module, run id, signoff fields, and collection-machine details. They are listed to preserve order: probe, qualify, accept fidelity, freeze, collect, seal, manifest, recompute, then audit.

```powershell
python scripts\probe_external_platform.py --strict
python scripts\probe_maniskill_task_bindings.py --strict
python scripts\probe_maniskill_env_smoke.py --strict
python scripts\probe_maniskill_fidelity_metadata.py --strict
python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <current_clean_checkout_commit_sha> --skill-library-hash <current_baselines_sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
python scripts\audit_external_postcollection_seal_consistency.py
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_evidence.py --strict
python scripts\audit_submission_readiness_gap.py
```

## Outreach Boundary

Use this brief as the private answer to what remains. Do not pitch Haonan as responsible for supplying the missing proof. The collaboration ask should be about whether the seam-certification layer is scientifically useful in a behavior-composition stack and what would falsify it cleanly.

## Checks

- `pass` `brief_is_non_evidence_and_currently_incomplete`: objective_complete=False, decision='STRONG_REVISE', strict=False
- `pass` `exact_four_submission_blockers_mapped`: missing=['Independent real-robot or accepted high-fidelity external validation evidence', 'External rollout metrics recomputed from raw JSONL logs', 'Manifest-declared real task configs replace non-evidence templates', 'Manifest-declared independent non-oracle baseline evidence and fairness contract']
- `pass` `closure_items_are_concrete`: items=4
- `pass` `command_spine_covers_all_strict_gates`: missing=[]
- `pass` `independent_route_not_haonan_dependent`: route_check=True
- `pass` `source_packets_ready_but_not_evidence`: acquisition=True, execution=True, intake=37/37, release='READY_TO_SEND_OPERATOR_PACKAGE'
- `pass` `collection_spines_exist_for_windows_and_linux`: job=True, bootstrap=True
- `pass` `no_real_manifest_written_before_external_evidence`: external_validation/manifest.json absent before real evidence
