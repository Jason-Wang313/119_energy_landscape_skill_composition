# External Rollout Evidence Packet

Packet ready: `true`.
Not evidence: `true`.
Strict rollout evidence ready: `false`.
Strict external evidence ready: `false`.
Expected records: `1440`.
Observed records: `0`.

This packet is a non-evidence work-order layer for the raw external rollout logs. It exists to keep the validation plan precise: collection, manifest writing, rollout metric recomputation, pairing integrity, release hash-locking, and final evidence gates must all pass before any external-validation claim is made.

## Work Orders

- `freeze_rollout_manifest_contract` (all_tasks): freeze platform identity, method aliases, task configs, backend module, run id, and paired reset schedule before collecting logs
- `collect_manifest_declared_rollout_logs` (all_tasks): run the non-template backend to produce one manifest-declared JSONL record for each task-method-reset episode
- `bind_videos_configs_and_method_hashes` (all_tasks): ensure every JSONL record points to an existing video, manifest-declared config hash, and method policy/config hash
- `recompute_rollout_metrics_from_raw_jsonl` (all_tasks): recompute external metrics from the raw JSONL logs with video-path checks enabled; do not hand-enter metrics
- `run_pairing_release_and_final_evidence_gates` (all_tasks): only after logs/videos/configs/method hashes are real, run the paired-reset, release-package, and final evidence gates
- `collect_peg_place_regrasp_jsonl_and_videos` (peg_place_regrasp): collect 360 paired-reset records for peg_place_regrasp with videos under external_validation/videos/peg_place_regrasp
- `collect_drawer_to_pick_transfer_jsonl_and_videos` (drawer_to_pick_transfer): collect 360 paired-reset records for drawer_to_pick_transfer with videos under external_validation/videos/drawer_to_pick_transfer
- `collect_door_open_navigation_jsonl_and_videos` (door_open_navigation): collect 360 paired-reset records for door_open_navigation with videos under external_validation/videos/door_open_navigation
- `collect_cable_route_insert_jsonl_and_videos` (cable_route_insert): collect 360 paired-reset records for cable_route_insert with videos under external_validation/videos/cable_route_insert

## Task Record Budget

- `peg_place_regrasp`: expected `360`, observed `0`, log `external_validation/logs/peg_place_regrasp.jsonl`, video dir `external_validation/videos/peg_place_regrasp`
- `drawer_to_pick_transfer`: expected `360`, observed `0`, log `external_validation/logs/drawer_to_pick_transfer.jsonl`, video dir `external_validation/videos/drawer_to_pick_transfer`
- `door_open_navigation`: expected `360`, observed `0`, log `external_validation/logs/door_open_navigation.jsonl`, video dir `external_validation/videos/door_open_navigation`
- `cable_route_insert`: expected `360`, observed `0`, log `external_validation/logs/cable_route_insert.jsonl`, video dir `external_validation/videos/cable_route_insert`

## Strict Acceptance Commands

- `python scripts\build_external_rollout_evidence_packet.py`
- `python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Forbidden Shortcuts

- treating external_validation/local_dry_run logs as external evidence
- hand-entering manifest metrics without recomputing from JSONL logs
- using rollout rows that do not have manifest-declared configs, videos, and method hashes
- unsealing aliases before configs, implementations, and run id are frozen
- counting logs without paired-reset method panels across the declared methods
