# Paper 119 External Validation Runbook

Not external evidence: `true`.

This runbook turns the independent validation protocol into operator-facing collection steps. It does not satisfy the external-evidence gate until real or accepted high-fidelity logs, videos, configs, checkpoints, and manifest-declared independent baseline evidence are collected and validated.

## Collection Scale

- Route: `high_fidelity_sim`.
- Task families: `4`.
- Methods: `12`.
- Paired resets: `120`.
- Required JSONL records: `1440`.
- Operator sheet: `external_validation/operator_record_sheet.csv`.
- Blinded operator sheet: `external_validation/blinded_operator_sheet.csv`.
- Method alias map: `external_validation/method_alias_map.json`.

## Operator Sequence

1. Select the robot or accepted high-fidelity simulator and fill `platform_name` in the task config template.
2. Generate and use the blinded operator sheet; keep `method_alias_map.json` sealed until logs, videos, configs, checkpoints, and implementation hashes are frozen.
3. For each task card, instantiate all paired resets before running any method-specific tuning.
4. Run all declared aliases on the same reset in `run_order_within_reset` order before changing the scene.
5. Write one JSONL record per episode using the schema fields below.
6. Save representative videos for successes, failures, abstentions, repairs, and oracle-gap cases.
7. Run the strict validators and do not edit manifest metrics by hand.

## Required JSONL Fields

- `barrier_score`
- `barrier_violation`
- `basin_estimate`
- `composition_cost`
- `damage_or_intervention`
- `decision`
- `descent_continuity_score`
- `episode_index`
- `failure_diagnosis`
- `fixed_risk_budget`
- `initial_state_hash`
- `method`
- `platform_name`
- `platform_type`
- `policy_or_config_hash`
- `predicted_seam_risk`
- `realized_seam_breach`
- `repair_action`
- `run_id`
- `scene_id`
- `seam_failure`
- `seed`
- `skill_i`
- `skill_j`
- `success`
- `task_family`
- `terminal_sample_set_hash`
- `utility`
- `video_path`

## Strict Validation Commands

- `python scripts\build_external_collection_plan.py`
- `python scripts\build_external_analysis_plan.py`
- `python scripts\build_independent_validation_route.py`
- `python scripts\probe_external_platform.py`
- `python scripts\probe_maniskill_task_bindings.py`
- `python scripts\probe_maniskill_env_smoke.py`
- `python scripts\probe_maniskill_fidelity_metadata.py`
- `python scripts\build_external_platform_onboarding.py`
- `python scripts\audit_external_fidelity_acceptance.py`
- `python scripts\build_external_fidelity_provenance_packet.py`
- `python scripts\build_external_fidelity_acceptance_draft.py`
- `python scripts\audit_external_runner_harness.py`
- `python scripts\audit_external_backend_contract.py`
- `python scripts\audit_maniskill_backend_readiness.py`
- `python scripts\audit_maniskill_reference_collection_preflight.py`
- `python scripts\build_external_backend_integration_packet.py`
- `python scripts\self_test_external_runner_backend.py`
- `python scripts\build_external_config_manifest_packet.py`
- `python scripts\build_external_rollout_evidence_packet.py`
- `python scripts\audit_external_pilot_smoke.py`
- `python scripts\build_external_pilot_smoke_packet.py`
- `python scripts\audit_maniskill_render_video_preflight.py`
- `python scripts\audit_maniskill_pilot_runtime_liveness.py`
- `python scripts\build_maniskill_render_machine_qualification.py`
- `python scripts\build_external_blind_eval_plan.py`
- `python scripts\audit_external_collection_readiness.py`
- `python scripts\validate_external_configs.py`
- `python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
- `python scripts\build_external_baseline_contract.py`
- `python scripts\build_external_adapter_scaffolds.py`
- `python scripts\validate_external_adapters.py`
- `python scripts\build_external_method_implementation_packet.py`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_collection_readiness.py --strict`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence_preflight.py`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\build_external_ablation_collection_packet.py`
- `python scripts\build_external_evidence_intake_ledger.py`
- `python scripts\audit_external_evidence.py --strict`

## Task Cards

- `external_validation/task_cards/peg_place_regrasp.md`
- `external_validation/task_cards/drawer_to_pick_transfer.md`
- `external_validation/task_cards/door_open_navigation.md`
- `external_validation/task_cards/cable_route_insert.md`
