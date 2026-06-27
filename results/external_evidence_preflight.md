# External Evidence Preflight

Passed: `true`.
Not evidence: `true`.
Evidence ready: `false`.
Readiness state: `COLLECT_EXTERNAL_EVIDENCE`.
Manifest source: `external_validation/manifest_template.json`.
Expected records: `1440`.
Observed records: `0`.
Blocking missing items: `60`.

This report is an operator preflight for real external validation artifacts. It is not robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for the strict external audits.

## Task Matrix

| Task | Expected | Observed | Log | Videos | Config | Missing |
|---|---:|---:|---|---:|---|---|
| `peg_place_regrasp` | 360 | 0 | no | 0 | no | platform_name is empty; log_jsonl is missing: external_validation/logs/peg_place_regrasp.jsonl; video_dir is missing: external_validation/videos/peg_place_regrasp; config_path is missing: external_validation/configs/peg_place_regrasp.json; config_hash is empty |
| `drawer_to_pick_transfer` | 360 | 0 | no | 0 | no | platform_name is empty; log_jsonl is missing: external_validation/logs/drawer_to_pick_transfer.jsonl; video_dir is missing: external_validation/videos/drawer_to_pick_transfer; config_path is missing: external_validation/configs/drawer_to_pick_transfer.json; config_hash is empty |
| `door_open_navigation` | 360 | 0 | no | 0 | no | platform_name is empty; log_jsonl is missing: external_validation/logs/door_open_navigation.jsonl; video_dir is missing: external_validation/videos/door_open_navigation; config_path is missing: external_validation/configs/door_open_navigation.json; config_hash is empty |
| `cable_route_insert` | 360 | 0 | no | 0 | no | platform_name is empty; log_jsonl is missing: external_validation/logs/cable_route_insert.jsonl; video_dir is missing: external_validation/videos/cable_route_insert; config_path is missing: external_validation/configs/cable_route_insert.json; config_hash is empty |

## Method Matrix

| Method | Role | Missing |
|---|---|---|
| `greedy_module_sequence` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `behavior_cloned_skill_chain` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `option_graph_planner` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `tamp_feasibility_screen` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `stable_dmp_handoff` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `diffusion_skill_stitcher` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `cem_trajectory_composer` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `residual_rl_composer` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `energy_compatibility_heuristic` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `proposed_energy_landscape_composer_v4_1` | `baseline` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `barrier_certified_energy_composer_v5` | `primary` | implementation missing: implementation path is empty; checkpoint_or_config_path is empty; checkpoint_or_config_hash is empty |
| `oracle_basin_composer` | `oracle` | none |

## Global Blockers

- code_commit is empty
- skill_library_hash is empty
- external_validation/manifest.json has not been written from real evidence
- release_artifacts.configs is empty
- release_artifacts.logs is empty
- release_artifacts.videos is empty
- release_artifacts.checkpoints is empty

## Operator Next Actions

- Collect real-robot or accepted high-fidelity simulator rollouts; do not use local_dry_run logs as evidence.
- Copy manifest_template.json to external_validation/manifest.json only after platform, configs, logs, videos, implementations, and hashes are real.
- Fill platform_name, code_commit, skill_library_hash, task config hashes, method implementation paths, and checkpoint/config hashes.
- Record at least the manifest-declared episodes_per_method for every declared method and task family with paired reset identifiers.
- Run build_external_manifest.py --write --check-video-paths, validate_external_configs.py --strict, validate_external_adapters.py --strict, validate_external_rollouts.py --write-results --check-video-paths --strict, and audit_external_evidence.py --strict.
