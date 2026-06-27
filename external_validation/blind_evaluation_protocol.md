# External Blind Evaluation Protocol

Not external evidence: `true`.

Purpose: reduce method-order, operator-expectation, and post-hoc tuning leakage before collecting real robot or accepted high-fidelity simulator evidence for Paper 119.

## Artifacts

- Blinded operator sheet: `external_validation/blinded_operator_sheet.csv`.
- Sealed method alias map: `external_validation/method_alias_map.json`.
- Source collection plan: `results/external_collection_plan.json`.

## Rules

- Execute rows from the blinded operator sheet in `run_order_within_reset` order.
- The operator sees `method_alias`, not method names.
- The alias map remains sealed until JSONL logs, videos, configs, checkpoints, and implementation hashes are frozen.
- Do not tune fixed-risk budget, thresholds, skill library, observation interface, or method hyperparameters after alias assignment.
- Include failed, abstained, repaired, damaged, and oracle-gap episodes in the raw JSONL logs.
- Recompute metrics from JSONL records before unblinding aggregate conclusions.

## Locked Analysis Gates

- External success margin over strongest non-oracle baseline >= `0.05`.
- External utility margin over strongest non-oracle baseline >= `0.08`.
- Paired win rate >= `0.70`.
- Fixed-risk coverage >= `0.55` and breach <= `0.02` at budget `0.15`.
- At least 3 of 4 task families must show positive margins.

## Scale

- Required JSONL records: `1440`.
- Methods: `12`.
- Task families: `4`.
