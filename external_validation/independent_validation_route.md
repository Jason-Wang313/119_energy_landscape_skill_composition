# Independent Validation Route

Not external evidence: `true`.

Purpose: make Paper 119's external validation path executable without relying on Haonan. This document is a route plan, not validation evidence. It becomes evidence only after a real manifest declares accepted platform provenance, hash-locked configs, raw JSONL rollout logs, videos, checkpoints or config hashes, and independent non-oracle baseline implementations.

## Primary Route

- Route: `maniskill_sapien_primary`.
- Execute the blinded operator sheet before unblinding method names.
- Fill `external_validation/fidelity_acceptance.json` before counting simulator results as accepted high-fidelity evidence.
- Replace config templates with manifest-declared real configs under `external_validation/configs/`.
- Replace adapter scaffolds with manifest-declared real implementations or wrappers for every non-oracle method.
- Run strict validators from raw logs; do not hand-enter metrics into the manifest.

## Strict Commands

- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_evidence.py --strict`

## Routes

### 1. ManiSkill/SAPIEN

- Route id: `maniskill_sapien_primary`.
- Role: primary independent high-fidelity simulator route.
- Platform type: `high_fidelity_sim`.
- Independent of Haonan: `true`.
- Requires GPU: `true`.
- Expected owner: Jason or any external operator with a GPU workstation.
- Task coverage: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`, `cable_route_insert`.
- Closes blockers when executed: `manifest_backed_external_evidence`, `raw_jsonl_metric_recompute`, `real_task_configs`, `independent_non_oracle_baselines`.
- Why: Open-source manipulation simulator route for collecting paired state, camera, contact, action, and video evidence without needing Haonan's lab access.
- Fidelity risk: Must document contact solver, friction, compliance, sensor rendering, and any deformable or cable proxy before the route can count as accepted high-fidelity evidence.
- Official sources:
  - https://maniskill.readthedocs.io/en/latest/user_guide/index.html
  - https://sapien.ucsd.edu/

### 2. MuJoCo/robosuite

- Route id: `mujoco_robosuite_cross_engine`.
- Role: cross-engine replication route.
- Platform type: `high_fidelity_sim`.
- Independent of Haonan: `true`.
- Requires GPU: `false`.
- Expected owner: Jason or an independent replication operator.
- Task coverage: `peg_place_regrasp`, `drawer_to_pick_transfer`, `tool_use_handover`.
- Closes blockers when executed: `raw_jsonl_metric_recompute`, `real_task_configs`, `independent_non_oracle_baselines`.
- Why: Useful for a second physics-engine check and CPU-friendlier manipulation replication, especially for tabletop handoff tasks.
- Fidelity risk: Likely insufficient alone for the full four-task high-fidelity route unless door/cable tasks are implemented and accepted with contact/dynamics provenance.
- Official sources:
  - https://mujoco.readthedocs.io/
  - https://robosuite.ai/

### 3. Isaac Sim/Isaac Lab

- Route id: `isaac_sim_lab_secondary`.
- Role: sensor-realistic secondary simulator route.
- Platform type: `high_fidelity_sim`.
- Independent of Haonan: `true`.
- Requires GPU: `true`.
- Expected owner: external operator with NVIDIA GPU and Isaac stack.
- Task coverage: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`, `cable_route_insert`.
- Closes blockers when executed: `manifest_backed_external_evidence`, `raw_jsonl_metric_recompute`, `real_task_configs`, `independent_non_oracle_baselines`.
- Why: Useful if the paper needs more realistic rendering, sensor logs, and PhysX-based robot-environment interaction as an independent validation route.
- Fidelity risk: Installation and GPU requirements are heavier; accepted evidence still needs a filled fidelity acceptance file, hash-locked configs, raw JSONL logs, and videos.
- Official sources:
  - https://docs.isaacsim.omniverse.nvidia.com/
  - https://isaac-sim.github.io/IsaacLab/

### 4. independent robot lab

- Route id: `third_party_robot_lab`.
- Role: physical robot confirmation route.
- Platform type: `real_robot`.
- Independent of Haonan: `true`.
- Requires GPU: `false`.
- Expected owner: any independent lab with a manipulation platform.
- Task coverage: `peg_place_regrasp`, `drawer_to_pick_transfer`, `door_open_navigation`.
- Closes blockers when executed: `manifest_backed_external_evidence`, `raw_jsonl_metric_recompute`, `real_task_configs`, `independent_non_oracle_baselines`.
- Why: Best evidence if available: real robot paired resets, calibrated camera/force/state logs, videos, and method implementations run through the same blinded protocol.
- Fidelity risk: Requires external collaborator time and hardware access, but is not Haonan-specific.

## Blocker Closure Map

- `manifest_backed_external_evidence`: create `external_validation/manifest.json` from real logs/videos/configs/checkpoints with `scripts/build_external_manifest.py --write --check-video-paths`.
- `raw_jsonl_metric_recompute`: collect task JSONL logs and run `scripts/validate_external_rollouts.py --write-results --check-video-paths --strict`.
- `real_task_configs`: replace templates with hash-locked configs and pass `scripts/validate_external_configs.py --strict`.
- `independent_non_oracle_baselines`: replace scaffolds/reference adapters with manifest-declared independent implementations and pass `scripts/validate_external_adapters.py --strict`.

## Audit

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
