# External Config Materialization Plan

Passed: `true`.
Not evidence: `true`.
Write enabled: `false`.
Strict config evidence ready: `false`.

This report checks that real task configs can be materialized from the non-evidence templates once an operator supplies a real platform and compute budget. The default report does not write configs and does not satisfy strict config evidence.

## Operator Write Command

```powershell
python scripts\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write
```

## Materialized Config Targets

| Task | Template | Output | Status |
|---|---|---|---|
| `cable_route_insert` | `external_validation/config_templates/cable_route_insert.json` | `external_validation/configs/cable_route_insert.json` | `pass` |
| `door_open_navigation` | `external_validation/config_templates/door_open_navigation.json` | `external_validation/configs/door_open_navigation.json` | `pass` |
| `drawer_to_pick_transfer` | `external_validation/config_templates/drawer_to_pick_transfer.json` | `external_validation/configs/drawer_to_pick_transfer.json` | `pass` |
| `peg_place_regrasp` | `external_validation/config_templates/peg_place_regrasp.json` | `external_validation/configs/peg_place_regrasp.json` | `pass` |

## Checks

- `pass` `schema_exists`: external_validation/config_schema_v1.json
- `pass` `schema_version`: version='external_config_schema_v1'
- `pass` `template_dir_exists`: external_validation/config_templates
- `pass` `template_count_ge_4`: templates=4
- `pass` `output_dir_exists`: external_validation/configs
- `pass` `write_requires_explicit_flag`: write=False, confirm_real_platform=False
- `pass` `materialized_payloads_validate`: failed=[]
