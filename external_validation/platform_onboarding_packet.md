# External Platform Onboarding Packet

Not evidence: `true`.
Source check date: `2026-06-27`.
Primary route: `maniskill_sapien_primary`.
Primary platform family: `ManiSkill/SAPIEN`.
Planned records: `1440`.

This packet turns the non-Haonan public-simulator route into an operator onboarding contract. Package and registry probes are non-evidence; this packet does not claim that any simulator task rollout has been run locally. The operator must record actual installed versions, platform provenance, configs, videos, logs, hashes, and backend implementations before any result can count as evidence.

## Official Sources Checked

- ManiSkill installation docs: https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html
- SAPIEN documentation: https://sapien.ucsd.edu/docs/latest/index.html
- `mujoco_robosuite_cross_engine` robosuite installation docs: https://robosuite.ai/docs/installation.html
- `isaac_sim_lab_secondary` Isaac Sim installation docs: https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/index.html
- `isaac_sim_lab_secondary` Isaac Lab local installation docs: https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html

## Primary Install Probe

- Install command from official docs: `python -m pip install --upgrade mani_skill; python -m pip install torch torchvision torchaudio`
- Version capture command: `python -c "import platform, torch, mani_skill, sapien; print(platform.platform()); print(torch.__version__); print(getattr(mani_skill, '__version__', 'unknown')); print(getattr(sapien, '__version__', 'unknown'))"`
- Machine probe command: `python scripts\probe_external_platform.py`
- Strict machine probe command: `python scripts\probe_external_platform.py --strict`
- Task binding probe command: `python scripts\probe_maniskill_task_bindings.py`
- Strict task binding probe command: `python scripts\probe_maniskill_task_bindings.py --strict`
- Env smoke probe command: `python scripts\probe_maniskill_env_smoke.py`
- Strict env smoke probe command: `python scripts\probe_maniskill_env_smoke.py --strict`
- Latest task binding probe report: `results/maniskill_task_binding_probe.json`
- Latest task binding install ready: `true`
- Latest task binding missing env IDs: `[]`
- Latest env smoke probe report: `results/maniskill_env_smoke_probe.json`
- Latest env smoke ready: `true`
- Latest env smoke primary reset missing: `[]`
- Latest env smoke support reset missing: `['InsertFlower-v1', 'PickSingleYCB-v1']`
- Latest env smoke missing asset IDs: `['oakink-v2', 'ycb']`
- Latest env smoke missing asset IDs by env: `{'InsertFlower-v1': ['oakink-v2'], 'PickSingleYCB-v1': ['ycb']}`
- Latest env smoke asset install hint: `python -m mani_skill.utils.download_asset oakink-v2 -y; python -m mani_skill.utils.download_asset ycb -y`
- Latest probe report: `results/external_platform_probe.json`
- Latest probe install ready: `true`
- Latest probe missing packages: `[]`
- Local status: probe is non-evidence; operator must rerun it on the selected GPU workstation and record exact versions in fidelity_acceptance.json

## Required Platform Provenance

- `platform_name`
- `platform_version`
- `maniskill_version`
- `sapien_version`
- `python_version`
- `operating_system`
- `gpu_model`
- `gpu_driver`
- `vulkan_or_renderer_device`
- `physics_timestep`
- `contact_solver`
- `friction_model`
- `compliance_or_contact_regularization`
- `camera_intrinsics_and_resolution`
- `state_observation_keys`
- `contact_signal_keys`
- `asset_sources`
- `task_config_sha256`
- `backend_module_sha256`
- `skill_library_hash`
- `code_commit`

## Task Onboarding

### `peg_place_regrasp`

Backend task binding:
- Primary env ID: `PegInsertionSide-v1`
- Support env IDs: `[]`
- Binding strength: `direct_contact_candidate`
- Primary env available in latest probe: `True`
- Operator fidelity acceptance required: `true`

Required operator files:
- `external_validation/configs/peg_place_regrasp.json`
- `external_validation/logs/peg_place_regrasp.jsonl`
- `external_validation/videos/peg_place_regrasp/`

Must document:
- reset sampler and paired initial-state hash rule
- terminal sample set construction
- camera/state/contact observation channels exposed to every method
- video export path and hash coverage
- task-specific fidelity risks and accepted approximations

### `drawer_to_pick_transfer`

Backend task binding:
- Primary env ID: `OpenCabinetDrawer-v1`
- Support env IDs: `['PickCube-v1', 'PickSingleYCB-v1']`
- Binding strength: `composite_contact_candidate`
- Primary env available in latest probe: `True`
- Operator fidelity acceptance required: `true`

Required operator files:
- `external_validation/configs/drawer_to_pick_transfer.json`
- `external_validation/logs/drawer_to_pick_transfer.jsonl`
- `external_validation/videos/drawer_to_pick_transfer/`

Must document:
- reset sampler and paired initial-state hash rule
- terminal sample set construction
- camera/state/contact observation channels exposed to every method
- video export path and hash coverage
- task-specific fidelity risks and accepted approximations

### `door_open_navigation`

Backend task binding:
- Primary env ID: `OpenCabinetDoor-v1`
- Support env IDs: `[]`
- Binding strength: `partial_contact_candidate`
- Primary env available in latest probe: `True`
- Operator fidelity acceptance required: `true`

Required operator files:
- `external_validation/configs/door_open_navigation.json`
- `external_validation/logs/door_open_navigation.jsonl`
- `external_validation/videos/door_open_navigation/`

Must document:
- reset sampler and paired initial-state hash rule
- terminal sample set construction
- camera/state/contact observation channels exposed to every method
- video export path and hash coverage
- task-specific fidelity risks and accepted approximations

### `cable_route_insert`

Backend task binding:
- Primary env ID: `PullCubeTool-v1`
- Support env IDs: `['InsertFlower-v1']`
- Binding strength: `surrogate_contact_candidate`
- Primary env available in latest probe: `True`
- Operator fidelity acceptance required: `true`

Required operator files:
- `external_validation/configs/cable_route_insert.json`
- `external_validation/logs/cable_route_insert.jsonl`
- `external_validation/videos/cable_route_insert/`

Must document:
- reset sampler and paired initial-state hash rule
- terminal sample set construction
- camera/state/contact observation channels exposed to every method
- video export path and hash coverage
- task-specific fidelity risks and accepted approximations

## Backend Requirements

- implement external_validation.runner.backend_contract.ExternalCollectionBackend
- return non-placeholder platform_provenance with the required provenance fields
- load manifest-declared task configs from external_validation/configs
- preserve paired reset identity for every method panel
- export videos under external_validation/videos and log paths under external_validation/logs
- report policy_or_config_hash for every method execution
- raise rather than silently substituting scaffold/template implementations

## Pilot Sequence

1. Run the dry-run packet check without writing logs or videos.
2. Run strict backend qualification against the non-template backend module.
3. Materialize real task configs only with --confirm-real-platform --write after platform values are known.
4. Fill external_validation/fidelity_acceptance.json with platform, simulator, contact, observation, and task-fidelity provenance.
5. Run strict collection readiness with a specific immutable run id and explicit alias unsealing.
6. Collect the full 1,440-record blinded paired-reset panel only after strict readiness passes.
7. Build the manifest and run strict rollout, pairing, release-package, and evidence audits from raw logs.

## Strict Commands

- `python scripts\build_external_platform_onboarding.py`
- `python scripts\probe_external_platform.py --strict`
- `python scripts\probe_maniskill_task_bindings.py --strict`
- `python scripts\probe_maniskill_env_smoke.py --strict`
- `python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json`
- `python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map`
- `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map`
- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_evidence.py --strict`
