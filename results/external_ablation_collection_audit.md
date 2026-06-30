# External Ablation Collection Packet

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Manifest ablation evidence ready: `false`.
Expected ablation records: `600`.

This packet turns the strict external ablation requirement into operator work orders. It does not create rollout logs, videos, a real manifest, or ablation evidence.

## Required External Ablations

- `basin_overlap` -> `minus_basin_overlap`: remove basin-overlap posterior.
- `barrier_height` -> `minus_barrier_height`: remove barrier-height term.
- `descent_continuity` -> `minus_descent_continuity`: remove descent-continuity term.
- `risk_calibration` -> `minus_calibration`: remove risk calibration.
- `seam_repair` -> `minus_high_energy_repair`: remove high-energy seam repair.

## Blocking Missing

- manifest.ablations.basin_overlap is not true with manifest-declared external ablation evidence
- manifest.ablations.barrier_height is not true with manifest-declared external ablation evidence
- manifest.ablations.descent_continuity is not true with manifest-declared external ablation evidence
- manifest.ablations.risk_calibration is not true with manifest-declared external ablation evidence
- manifest.ablations.seam_repair is not true with manifest-declared external ablation evidence

## Operator Commands

```powershell
python scripts\build_external_ablation_collection_packet.py
```
```powershell
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```
```powershell
python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>
```
```powershell
python scripts\audit_external_postcollection_seal_consistency.py
```
```powershell
python scripts\build_external_manifest.py --write --check-video-paths
```
```powershell
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
```
```powershell
python scripts\audit_external_evidence.py --strict
```

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_external_evidence_ready=False, manifest_ablation_evidence_ready=False
- `pass` `collection_plan_loaded`: passed=True, not_external_evidence=True
- `pass` `task_and_reset_budget_preserved`: tasks=['peg_place_regrasp', 'drawer_to_pick_transfer', 'door_open_navigation', 'cable_route_insert'], resets_per_task=30, packet_expected=600, recomputed_expected=600
- `pass` `required_ablations_match_strict_audit`: strict_missing=['basin_overlap', 'barrier_height', 'descent_continuity', 'risk_calibration', 'seam_repair'], packet_ablation_ids=['barrier_height', 'basin_overlap', 'descent_continuity', 'risk_calibration', 'seam_repair']
- `pass` `every_required_ablation_has_work_order`: work_orders=5, ids=['barrier_height', 'basin_overlap', 'descent_continuity', 'risk_calibration', 'seam_repair']
- `pass` `work_orders_use_local_reference_variants`: local ablation variants are present in results/ablation_metrics.csv and bound in work orders
- `pass` `work_orders_are_actionable_and_artifact_bound`: each work order binds same configs/resets/interfaces/budget, JSONL/video artifacts, manifest ablation booleans, and strict acceptance commands
- `pass` `manifest_template_declares_ablation_booleans`: manifest_ablation_keys=['barrier_height', 'basin_overlap', 'descent_continuity', 'risk_calibration', 'seam_repair']
- `pass` `operator_commands_cover_collection_manifest_rollout_and_strict_evidence`: strict ablation commands preserve collection-to-manifest gate order
- `pass` `no_real_manifest_written`: external_validation/manifest.json remains absent before real evidence
