# ManiSkill Task Binding Probe

Passed: `true`.
Not evidence: `true`.
Primary route: `maniskill_sapien_primary`.
Registry inspected: `true`.
Strict task-binding install ready: `true`.
Accepted task binding ready: `false`.
Strict external evidence ready: `false`.

This probe binds Paper 119 task families to concrete ManiSkill/SAPIEN environment candidates and, when ManiSkill is installed, checks the local Gymnasium registry. It is not rollout evidence and does not replace operator fidelity acceptance.

## Task Bindings

| Task | Primary env | Support envs | Strength | Available |
|---|---|---|---|---|
| `peg_place_regrasp` | `PegInsertionSide-v1` | `none` | `direct_contact_candidate` | `True` |
| `drawer_to_pick_transfer` | `OpenCabinetDrawer-v1` | `PickCube-v1, PickSingleYCB-v1` | `composite_contact_candidate` | `True` |
| `door_open_navigation` | `OpenCabinetDoor-v1` | `none` | `partial_contact_candidate` | `True` |
| `cable_route_insert` | `PullCubeTool-v1` | `InsertFlower-v1` | `surrogate_contact_candidate` | `True` |

## Checks

- `pass` `probe_is_non_evidence`: not_external_evidence=True
- `pass` `binding_file_ready`: version='maniskill_task_bindings_v1', bindings=4
- `pass` `task_bindings_cover_configs`: missing_task_bindings=[], missing_configs=[]
- `pass` `configs_embed_backend_task_bindings`: missing_or_mismatched=[]
- `pass` `registry_availability_reported`: registry_inspected=True, import_error=''
- `pass` `primary_env_availability_reported`: primary_missing=[]
- `pass` `non_direct_bindings_require_operator_acceptance`: records_needing_acceptance=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `strict_evidence_remains_false`: task binding and registry inspection cannot satisfy fidelity acceptance or rollout evidence
