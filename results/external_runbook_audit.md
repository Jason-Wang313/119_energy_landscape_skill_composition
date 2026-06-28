# External Runbook Audit

Passed: `true`.
Not evidence: `true`.
Operator rows: `1440`.
Validation commands: `43`.
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
- `pass` `current_maniskill_route_gates_present`: missing=[]
- `pass` `gate_order_preserves_preflight_before_collection_and_evidence`: positions={'audit_external_fidelity_acceptance.py': 403, 'audit_external_backend_contract.py': 623, 'audit_maniskill_reference_collection_preflight.py': 725, 'audit_maniskill_render_video_preflight.py': 1112, 'real_collection_runner.py --backend-module <module_or_path>': 1991, 'build_external_manifest.py --write --check-video-paths': 2241, 'validate_external_rollouts.py --write-results --check-video-paths --strict': 2484, 'audit_external_evidence.py --strict': 2694}
- `pass` `operator_sheet_exists`: external_validation\operator_record_sheet.csv
- `pass` `runbook_exists`: external_validation\collection_runbook.md
