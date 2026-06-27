# External Runbook Audit

Passed: `true`.
Not evidence: `true`.
Operator rows: `1440`.
Runbook: `external_validation/collection_runbook.md`.
Operator sheet: `external_validation/operator_record_sheet.csv`.

## Task Cards

- `external_validation/task_cards/peg_place_regrasp.md`
- `external_validation/task_cards/drawer_to_pick_transfer.md`
- `external_validation/task_cards/door_open_navigation.md`
- `external_validation/task_cards/cable_route_insert.md`

## Config Templates

- `external_validation/config_templates/peg_place_regrasp.json`
- `external_validation/config_templates/drawer_to_pick_transfer.json`
- `external_validation/config_templates/door_open_navigation.json`
- `external_validation/config_templates/cable_route_insert.json`

## Checks

- `pass` `not_external_evidence_declared`: runbook and generated sheets are collection scaffolding only
- `pass` `operator_row_count_matches_plan`: rows=1440, required=1440
- `pass` `operator_row_count_ge_1440`: rows=1440
- `pass` `task_cards_match_tasks`: cards=4
- `pass` `config_templates_match_tasks`: templates=4
- `pass` `method_count_ge_12`: method_count=12
- `pass` `required_fields_ge_28`: required_fields=29
- `pass` `strict_commands_present`: strict validation command found
- `pass` `operator_sheet_exists`: external_validation\operator_record_sheet.csv
- `pass` `runbook_exists`: external_validation\collection_runbook.md
