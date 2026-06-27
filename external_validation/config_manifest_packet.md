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

| Task | Config path | Prepared hash | Log | Video dir |
|---|---|---|---|---|
| `peg_place_regrasp` | `external_validation/configs/peg_place_regrasp.json` | `8D041F5E869F4D81E2352D77A01C85EE585DF2040E45987750DF84B86EA94086` | `external_validation/logs/peg_place_regrasp.jsonl` | `external_validation/videos/peg_place_regrasp` |
| `drawer_to_pick_transfer` | `external_validation/configs/drawer_to_pick_transfer.json` | `EABEA38D21F936A46C69E566D0324F7C42A8693CAA1D441B81C7E87B595FCA0D` | `external_validation/logs/drawer_to_pick_transfer.jsonl` | `external_validation/videos/drawer_to_pick_transfer` |
| `door_open_navigation` | `external_validation/configs/door_open_navigation.json` | `39697F0BA1ECBE013C1790455F26B68C927EEF97415A2BB49C6FD1440DEBEA9C` | `external_validation/logs/door_open_navigation.jsonl` | `external_validation/videos/door_open_navigation` |
| `cable_route_insert` | `external_validation/configs/cable_route_insert.json` | `15D687A12F9213E1EB410876203CE93F73E667C30E039685E151438017B3D7AD` | `external_validation/logs/cable_route_insert.jsonl` | `external_validation/videos/cable_route_insert` |

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
- Operator input: manifest-declare external_validation/configs/peg_place_regrasp.json with sha256 8D041F5E869F4D81E2352D77A01C85EE585DF2040E45987750DF84B86EA94086
- Required artifacts: `external_validation/configs/peg_place_regrasp.json`, `external_validation/logs/peg_place_regrasp.jsonl`, `external_validation/videos/peg_place_regrasp`

### `declare_drawer_to_pick_transfer_config`

- Scope: `drawer_to_pick_transfer`
- Operator input: manifest-declare external_validation/configs/drawer_to_pick_transfer.json with sha256 EABEA38D21F936A46C69E566D0324F7C42A8693CAA1D441B81C7E87B595FCA0D
- Required artifacts: `external_validation/configs/drawer_to_pick_transfer.json`, `external_validation/logs/drawer_to_pick_transfer.jsonl`, `external_validation/videos/drawer_to_pick_transfer`

### `declare_door_open_navigation_config`

- Scope: `door_open_navigation`
- Operator input: manifest-declare external_validation/configs/door_open_navigation.json with sha256 39697F0BA1ECBE013C1790455F26B68C927EEF97415A2BB49C6FD1440DEBEA9C
- Required artifacts: `external_validation/configs/door_open_navigation.json`, `external_validation/logs/door_open_navigation.jsonl`, `external_validation/videos/door_open_navigation`

### `declare_cable_route_insert_config`

- Scope: `cable_route_insert`
- Operator input: manifest-declare external_validation/configs/cable_route_insert.json with sha256 15D687A12F9213E1EB410876203CE93F73E667C30E039685E151438017B3D7AD
- Required artifacts: `external_validation/configs/cable_route_insert.json`, `external_validation/logs/cable_route_insert.jsonl`, `external_validation/videos/cable_route_insert`

## Strict Acceptance Commands

- `python scripts\build_external_config_manifest_packet.py`
- `python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence.py --strict`
