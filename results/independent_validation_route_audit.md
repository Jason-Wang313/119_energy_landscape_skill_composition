# Independent Validation Route Audit

Passed: `true`.
Not evidence: `true`.
Primary route: `maniskill_sapien_primary`.
Planned tasks: `4`.
Routes: `4`.

This audit checks that the non-Haonan validation route covers the external-evidence blockers. It does not count as robot or high-fidelity simulator evidence.

## Checks

- `pass` `collection_plan_passed`: passed=True
- `pass` `collection_plan_scale_preserved`: total_required_records=1440
- `pass` `route_count_ge_4`: routes=4
- `pass` `primary_route_independent_of_haonan`: route_id=maniskill_sapien_primary, owner='Jason or any external operator with a GPU workstation'
- `pass` `primary_route_covers_collection_tasks`: planned=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp'], primary_coverage=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `all_readiness_blockers_have_route_closure`: closed=['independent_non_oracle_baselines', 'manifest_backed_external_evidence', 'raw_jsonl_metric_recompute', 'real_task_configs']
- `pass` `public_sim_routes_have_official_sources`: high-fidelity simulator routes include official source URLs
- `pass` `strict_commands_cover_manifest_rollout_config_adapter_audits`: commands=['python scripts\\validate_external_configs.py --strict', 'python scripts\\validate_external_adapters.py --strict', 'python scripts\\build_external_manifest.py --write --check-video-paths', 'python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict', 'python scripts\\audit_external_evidence.py --strict']
- `pass` `route_matrix_written`: external_validation/independent_validation_route_matrix.csv
- `pass` `route_marked_not_evidence`: route artifacts are execution planning only
