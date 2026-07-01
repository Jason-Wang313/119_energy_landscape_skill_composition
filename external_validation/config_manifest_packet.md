# External Config Manifest Packet

Not evidence: `true`.
Config manifest packet ready: `true`.
Strict config evidence ready: `false`.
Manifest-declared config ready: `false`.

This packet turns prepared task configs into a manifest-declaration checklist. It does not write `external_validation/manifest.json`, does not claim that prepared configs are external evidence, and does not replace raw rollout logs or videos.

## Forbidden Evidence Shortcuts

- treating prepared configs as evidence before external_validation/manifest.json declares them
- changing configs after alias unsealing or after rollout collection starts
- using config_templates directly as manifest-declared configs
- omitting config_hash or letting logs/videos point to a different task definition

## Task Config Records

| Task | Config path | Prepared hash | Strict-ready if manifest-declared | Log | Video dir |
|---|---|---|---|---|---|
| `peg_place_regrasp` | `external_validation/configs/peg_place_regrasp.json` | `021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9` | `true` | `external_validation/logs/peg_place_regrasp.jsonl` | `external_validation/videos/peg_place_regrasp` |
| `drawer_to_pick_transfer` | `external_validation/configs/drawer_to_pick_transfer.json` | `1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471` | `true` | `external_validation/logs/drawer_to_pick_transfer.jsonl` | `external_validation/videos/drawer_to_pick_transfer` |
| `door_open_navigation` | `external_validation/configs/door_open_navigation.json` | `13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61` | `true` | `external_validation/logs/door_open_navigation.jsonl` | `external_validation/videos/door_open_navigation` |
| `cable_route_insert` | `external_validation/configs/cable_route_insert.json` | `8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E` | `true` | `external_validation/logs/cable_route_insert.jsonl` | `external_validation/videos/cable_route_insert` |

## Work Orders

### `lock_real_platform_identity`

- Scope: `all_tasks`
- Operator input: choose the accepted real robot or high-fidelity simulator and freeze platform_name, platform_type, and compute budget before config write
- Required artifacts: `external_validation/fidelity_acceptance.json`, `external_validation/configs/*.json`

### `hash_manifest_config_entries`

- Scope: `all_tasks`
- Operator input: write config_hash for every manifest task entry from the exact config file consumed by the backend
- Required artifacts: `external_validation/manifest.json`, `external_validation/configs/*.json`

### `bind_configs_to_rollout_logs`

- Scope: `all_tasks`
- Operator input: ensure each task's JSONL records were generated with the manifest-declared config and contain matching platform/run identifiers
- Required artifacts: `external_validation/logs/*.jsonl`, `external_validation/videos/<task_family>/`

### `declare_peg_place_regrasp_config`

- Scope: `peg_place_regrasp`
- Operator input: manifest-declare external_validation/configs/peg_place_regrasp.json with sha256 021336396EBF09D9AD0AF7688216E0772E6455A8581C7588BA59258F1498E6B9
- Required artifacts: `external_validation/configs/peg_place_regrasp.json`, `external_validation/logs/peg_place_regrasp.jsonl`, `external_validation/videos/peg_place_regrasp`

### `declare_drawer_to_pick_transfer_config`

- Scope: `drawer_to_pick_transfer`
- Operator input: manifest-declare external_validation/configs/drawer_to_pick_transfer.json with sha256 1288223014CB9D9285E4249B2FA607FFC16EBEE20B6F44E0241B63E88233E471
- Required artifacts: `external_validation/configs/drawer_to_pick_transfer.json`, `external_validation/logs/drawer_to_pick_transfer.jsonl`, `external_validation/videos/drawer_to_pick_transfer`

### `declare_door_open_navigation_config`

- Scope: `door_open_navigation`
- Operator input: manifest-declare external_validation/configs/door_open_navigation.json with sha256 13F285EFD596568ADCCB8AE2255CBB9FDC9F0B9EBC074297883902C1A15B8B61
- Required artifacts: `external_validation/configs/door_open_navigation.json`, `external_validation/logs/door_open_navigation.jsonl`, `external_validation/videos/door_open_navigation`

### `declare_cable_route_insert_config`

- Scope: `cable_route_insert`
- Operator input: manifest-declare external_validation/configs/cable_route_insert.json with sha256 8C6E99766F68CEA04C40D7B54124D4F14A927363D3CF721E68F9C6E523BFF19E
- Required artifacts: `external_validation/configs/cable_route_insert.json`, `external_validation/logs/cable_route_insert.jsonl`, `external_validation/videos/cable_route_insert`

## Strict Acceptance Commands

- `python scripts\build_external_config_manifest_packet.py`
- `python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence.py --strict`
