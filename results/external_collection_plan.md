# External Collection Plan

Passed: `true`.
Not evidence: `true`.
Route: `high_fidelity_sim`.
Task families: `4`.
Methods: `12`.
Paired resets: `120`.
Required JSONL records: `1440`.

This file is a collection schedule only. It does not count as external validation evidence.

## Validation Commands

- `python scripts\build_external_collection_plan.py`
- `python scripts\build_external_analysis_plan.py`
- `python scripts\build_independent_validation_route.py`
- `python scripts\build_external_platform_onboarding.py`
- `python scripts\build_external_fidelity_provenance_packet.py`
- `python scripts\build_external_backend_integration_packet.py`
- `python scripts\build_external_config_manifest_packet.py`
- `python scripts\build_external_rollout_evidence_packet.py`
- `python scripts\audit_external_fidelity_acceptance.py`
- `python scripts\build_external_blind_eval_plan.py`
- `python scripts\audit_external_collection_readiness.py`
- `python scripts\validate_external_configs.py`
- `python scripts\build_external_baseline_contract.py`
- `python scripts\build_external_adapter_scaffolds.py`
- `python scripts\validate_external_adapters.py`
- `python scripts\build_external_method_implementation_packet.py`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_collection_readiness.py --strict`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Invariants

- Every method must run on the same reset/scene/seed/skill pair for paired comparison.
- Every JSONL record must include hashes for the initial state, terminal samples, and method policy/config.
- Videos must be linked per episode and must exist before strict validation.
- Manifest metrics must be recomputed from JSONL logs; hand-entered metrics are not accepted.
- The oracle is a post hoc upper bound and must not be used for deployment decisions.
- The selected robot or high-fidelity simulator must clear the fidelity acceptance audit before rollout evidence is counted.
- The operator should execute the blinded, randomized sheet so method identity and outcome analysis are separated until logs are frozen.

## Tasks

- `peg_place_regrasp` on `high_fidelity_sim`: `30` paired resets x `12` methods = `360` records; log `external_validation/logs/peg_place_regrasp.jsonl`; videos `external_validation/videos/peg_place_regrasp`.
- `drawer_to_pick_transfer` on `high_fidelity_sim`: `30` paired resets x `12` methods = `360` records; log `external_validation/logs/drawer_to_pick_transfer.jsonl`; videos `external_validation/videos/drawer_to_pick_transfer`.
- `door_open_navigation` on `high_fidelity_sim`: `30` paired resets x `12` methods = `360` records; log `external_validation/logs/door_open_navigation.jsonl`; videos `external_validation/videos/door_open_navigation`.
- `cable_route_insert` on `high_fidelity_sim`: `30` paired resets x `12` methods = `360` records; log `external_validation/logs/cable_route_insert.jsonl`; videos `external_validation/videos/cable_route_insert`.

## Checks

- `pass` `route_is_valid`: route=high_fidelity_sim, counts={'real_robot': 0, 'high_fidelity_sim': 4, 'mixed': 4}
- `pass` `shared_skill_library`: value=True
- `pass` `paired_resets`: value=True
- `pass` `same_initial_states`: value=True
- `pass` `same_observation_interface`: value=True
- `pass` `same_compute_budget`: value=True
- `pass` `method_count_ge_12`: method_count=12
- `pass` `task_count_ge_4`: task_count=4
- `pass` `episodes_per_method_ge_30`: weak_tasks=[]
- `pass` `required_fields_complete`: required_field_count=29
- `pass` `paired_key_contains_initial_state`: paired_key=['task_family', 'platform_type', 'scene_id', 'seed', 'skill_i', 'skill_j', 'initial_state_hash']
- `pass` `total_required_records_ge_1440`: total_required_records=1440
