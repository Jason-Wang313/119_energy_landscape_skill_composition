# External Blind Evaluation Audit

Passed: `true`.
Not evidence: `true`.
Rows: `1440`.
Aliases: `12`.
Resets: `120`.
Blinded sheet: `external_validation/blinded_operator_sheet.csv`.
Alias map: `external_validation/method_alias_map.json`.
Protocol: `external_validation/blind_evaluation_protocol.md`.

This audit checks collection blinding and deterministic randomization only. It is not robot or high-fidelity simulator evidence.

## Checks

- `pass` `collection_plan_passed`: passed=True
- `pass` `alias_count_matches_methods`: aliases=12, methods=12
- `pass` `row_count_matches_plan`: rows=1440, expected=1440
- `pass` `blind_artifacts_written`: blinded sheet, alias map, and protocol exist
- `pass` `aliases_unique`: duplicates=[]
- `pass` `aliases_hide_method_names`: aliases do not contain method names
- `pass` `every_reset_has_all_aliases`: bad_resets=[], reset_count=120
- `pass` `run_order_varies_by_reset`: distinct_orders=120
- `pass` `first_order_not_alias_sorted`: first observed order differs from sorted aliases
- `pass` `blinded_sheet_has_no_method_names`: leaked_methods=[]
- `pass` `protocol_contains_anti_leakage_terms`: missing_terms=[]
