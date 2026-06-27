# ManiSkill Environment Smoke Probe

Passed: `true`.
Not evidence: `true`.
Environment smoke probe ready: `true`.
Strict env smoke ready: `true`.
Accepted fidelity ready: `false`.
Strict external evidence ready: `false`.

This probe attempts construction and reset for the ManiSkill/SAPIEN environment candidates bound to Paper 119 task families. It is not rollout evidence and does not replace backend qualification, operator fidelity acceptance, videos, logs, manifests, or strict evidence audits.

Asset install hint: `python -m mani_skill.utils.download_asset partnet_mobility_cabinet`

## Environment Records

| Env ID | Primary for | Support for | Made | Reset | Error |
|---|---|---|---|---|---|
| `InsertFlower-v1` | `none` | `cable_route_insert` | `False` | `False` | EOF when reading a line |
| `OpenCabinetDoor-v1` | `door_open_navigation` | `none` | `True` | `True` |  |
| `OpenCabinetDrawer-v1` | `drawer_to_pick_transfer` | `none` | `True` | `True` |  |
| `PegInsertionSide-v1` | `peg_place_regrasp` | `none` | `True` | `True` |  |
| `PickCube-v1` | `none` | `drawer_to_pick_transfer` | `True` | `True` |  |
| `PickSingleYCB-v1` | `none` | `drawer_to_pick_transfer` | `False` | `False` | EOF when reading a line |
| `PullCubeTool-v1` | `cable_route_insert` | `none` | `True` | `True` |  |

## Checks

- `pass` `probe_is_non_evidence`: not_external_evidence=True
- `pass` `binding_file_ready`: version='maniskill_task_bindings_v1', bindings=4
- `pass` `smoke_attempted_all_bound_envs`: attempted=7, expected=7
- `pass` `primary_reset_readiness_reported`: primary_reset_missing=[]
- `pass` `asset_failures_reported`: asset_related_failures=['InsertFlower-v1', 'PickSingleYCB-v1']
- `pass` `strict_evidence_remains_false`: environment construction/reset smoke tests are not rollout evidence
