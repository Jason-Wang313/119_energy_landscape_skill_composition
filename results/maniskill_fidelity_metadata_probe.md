# ManiSkill Fidelity Metadata Probe

Passed: `true`.
Not evidence: `true`.
Metadata probe ready: `true`.
Strict metadata ready: `true`.
Accepted fidelity ready: `false`.
Strict external evidence ready: `false`.

This probe records platform timing, scene/backend, observation, controller, and asset metadata for the bound ManiSkill/SAPIEN task candidates. It is not rollout evidence and does not replace independent operator fidelity acceptance.

## Primary Timing Summary

- sim_freq_hz_values: `[100.0]`
- control_freq_hz_values: `[20.0]`
- sim_timestep_seconds_values: `[0.01]`
- control_timestep_seconds_values: `[0.05]`
- derived_substeps_per_control_step_values: `[5.0]`
- scene_backend_types: `['PhysxCpuSystem']`

## Environment Records

| Env ID | Primary for | Support for | Reset | sim dt | control dt | substeps | backend | agent | info keys | Missing assets |
|---|---|---|---|---|---|---|---|---|---|---|
| `InsertFlower-v1` | `none` | `cable_route_insert` | `False` | `` | `` | `` | `` | `` | `none` | `oakink-v2` |
| `OpenCabinetDoor-v1` | `door_open_navigation` | `none` | `True` | `0.01` | `0.05` | `5.0` | `PhysxCpuSystem` | `fetch` | `elapsed_steps, handle_link_pos, open_enough, reconfigure, success` | `none` |
| `OpenCabinetDrawer-v1` | `drawer_to_pick_transfer` | `none` | `True` | `0.01` | `0.05` | `5.0` | `PhysxCpuSystem` | `fetch` | `elapsed_steps, handle_link_pos, open_enough, reconfigure, success` | `none` |
| `PegInsertionSide-v1` | `peg_place_regrasp` | `none` | `True` | `0.01` | `0.05` | `5.0` | `PhysxCpuSystem` | `panda_wristcam` | `elapsed_steps, peg_head_pos_at_hole, reconfigure, success` | `none` |
| `PickCube-v1` | `none` | `drawer_to_pick_transfer` | `True` | `0.01` | `0.05` | `5.0` | `PhysxCpuSystem` | `panda` | `elapsed_steps, is_grasped, is_obj_placed, is_robot_static, reconfigure, success` | `none` |
| `PickSingleYCB-v1` | `none` | `drawer_to_pick_transfer` | `False` | `` | `` | `` | `` | `` | `none` | `ycb` |
| `PullCubeTool-v1` | `cable_route_insert` | `none` | `True` | `0.01` | `0.05` | `5.0` | `PhysxCpuSystem` | `panda` | `cube_distance, cube_progress, elapsed_steps, reconfigure, reward, success, success_at_end, success_once` | `none` |

## Checks

- `pass` `probe_is_non_evidence`: not_external_evidence=True
- `pass` `binding_file_ready`: version='maniskill_task_bindings_v1', bindings=4
- `pass` `metadata_attempted_all_bound_envs`: attempted=7, expected=7
- `pass` `primary_metadata_readiness_reported`: primary_metadata_missing=[]
- `pass` `timing_summary_reported`: {"agent_uids": ["fetch", "panda", "panda_wristcam"], "control_freq_hz_values": [20.0], "control_timestep_seconds_values": [0.05], "controller_types": ["CombinedController"], "derived_substeps_per_control_step_values": [5.0], "primary_metadata_env_count": 4, "scene_backend_types": ["PhysxCpuSystem"], "scene_timestep_seconds_values": [0.01], "sim_freq_hz_values": [100.0], "sim_timestep_seconds_values": [0.01]}
- `pass` `asset_requirements_reported`: missing_asset_ids=['oakink-v2', 'ycb']
- `pass` `strict_evidence_remains_false`: metadata probing cannot satisfy fidelity acceptance, rollout logs, videos, or manifest evidence
