# External Method Implementation Packet

Not evidence: `true`.
Non-oracle method work orders: `11`.
Strict adapter evidence ready: `false`.

This packet converts the missing independent baseline layer into concrete implementation work orders. It does not provide real implementations, checkpoints, configs, logs, videos, or manifest evidence.

## Forbidden Evidence Shortcuts

- using scaffold adapters as manifest-declared implementations
- using reference adapters as rollout evidence without real source/config/checkpoint hashes
- declaring only a subset of non-oracle methods in the strict adapter manifest
- using policy_or_config_hash values in JSONL logs that do not match manifest-declared hashes
- dropping hard methods after viewing method identity or outcomes
- changing compute budgets after seeing paired-reset performance
- hand-entering manifest metrics without raw JSONL logs

## Work Orders

### `barrier_certified_energy_composer_v5`

- Role: primary method
- Spec: `external_validation/baseline_specs/barrier_certified_energy_composer_v5.json`
- Required entrypoint: `compose_with_barrier_certified_seam_model`
- Target adapter directory: `external_validation/baselines/barrier_certified_energy_composer_v5`
- Suggested real implementation path: `external_validation/implementations/barrier_certified_energy_composer_v5/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/barrier_certified_energy_composer_v5/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/barrier_certified_energy_composer_v5/adapter.py",
  "name": "barrier_certified_energy_composer_v5"
}
```

Forbidden advantages:
- post hoc oracle basin truth
- unpaired reset retries

### `behavior_cloned_skill_chain`

- Role: demonstration sequence baseline
- Spec: `external_validation/baseline_specs/behavior_cloned_skill_chain.json`
- Required entrypoint: `predict_demonstrated_handoff`
- Target adapter directory: `external_validation/baselines/behavior_cloned_skill_chain`
- Suggested real implementation path: `external_validation/implementations/behavior_cloned_skill_chain/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/behavior_cloned_skill_chain/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/behavior_cloned_skill_chain/adapter.py",
  "name": "behavior_cloned_skill_chain"
}
```

Forbidden advantages:
- v5 diagnostic labels
- post hoc oracle repair
- unpaired demonstration resets

### `cem_trajectory_composer`

- Role: trajectory-search baseline
- Spec: `external_validation/baseline_specs/cem_trajectory_composer.json`
- Required entrypoint: `optimize_handoff_with_cem`
- Target adapter directory: `external_validation/baselines/cem_trajectory_composer`
- Suggested real implementation path: `external_validation/implementations/cem_trajectory_composer/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/cem_trajectory_composer/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/cem_trajectory_composer/adapter.py",
  "name": "cem_trajectory_composer"
}
```

Forbidden advantages:
- larger compute budget
- extra reset attempts
- oracle basin state

### `diffusion_skill_stitcher`

- Role: generative handoff sampler baseline
- Spec: `external_validation/baseline_specs/diffusion_skill_stitcher.json`
- Required entrypoint: `sample_handoff_state`
- Target adapter directory: `external_validation/baselines/diffusion_skill_stitcher`
- Suggested real implementation path: `external_validation/implementations/diffusion_skill_stitcher/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/diffusion_skill_stitcher/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/diffusion_skill_stitcher/adapter.py",
  "name": "diffusion_skill_stitcher"
}
```

Forbidden advantages:
- v5 accept/reject labels unless explicitly trained on the same data as all baselines

### `energy_compatibility_heuristic`

- Role: non-certified energy heuristic baseline
- Spec: `external_validation/baseline_specs/energy_compatibility_heuristic.json`
- Required entrypoint: `score_energy_compatibility`
- Target adapter directory: `external_validation/baselines/energy_compatibility_heuristic`
- Suggested real implementation path: `external_validation/implementations/energy_compatibility_heuristic/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/energy_compatibility_heuristic/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/energy_compatibility_heuristic/adapter.py",
  "name": "energy_compatibility_heuristic"
}
```

Forbidden advantages:
- fixed-risk calibration gate
- repair memory from proposed v5

### `greedy_module_sequence`

- Role: open-loop skill graph baseline
- Spec: `external_validation/baseline_specs/greedy_module_sequence.json`
- Required entrypoint: `select_next_skill_and_handoff`
- Target adapter directory: `external_validation/baselines/greedy_module_sequence`
- Suggested real implementation path: `external_validation/implementations/greedy_module_sequence/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/greedy_module_sequence/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/greedy_module_sequence/adapter.py",
  "name": "greedy_module_sequence"
}
```

Forbidden advantages:
- energy seam labels
- post hoc basin truth
- extra reset attempts

### `option_graph_planner`

- Role: temporal-abstraction planning baseline
- Spec: `external_validation/baseline_specs/option_graph_planner.json`
- Required entrypoint: `plan_over_option_graph`
- Target adapter directory: `external_validation/baselines/option_graph_planner`
- Suggested real implementation path: `external_validation/implementations/option_graph_planner/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/option_graph_planner/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/option_graph_planner/adapter.py",
  "name": "option_graph_planner"
}
```

Forbidden advantages:
- hidden basin classifier
- privileged barrier score

### `proposed_energy_landscape_composer_v4_1`

- Role: previous proposed method baseline
- Spec: `external_validation/baseline_specs/proposed_energy_landscape_composer_v4_1.json`
- Required entrypoint: `compose_with_v4_1_rules`
- Target adapter directory: `external_validation/baselines/proposed_energy_landscape_composer_v4_1`
- Suggested real implementation path: `external_validation/implementations/proposed_energy_landscape_composer_v4_1/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/proposed_energy_landscape_composer_v4_1/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/proposed_energy_landscape_composer_v4_1/adapter.py",
  "name": "proposed_energy_landscape_composer_v4_1"
}
```

Forbidden advantages:
- v5-only repair memory
- v5 fixed-risk calibration updates

### `residual_rl_composer`

- Role: learned residual repair baseline
- Spec: `external_validation/baseline_specs/residual_rl_composer.json`
- Required entrypoint: `apply_residual_repair_policy`
- Target adapter directory: `external_validation/baselines/residual_rl_composer`
- Suggested real implementation path: `external_validation/implementations/residual_rl_composer/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/residual_rl_composer/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/residual_rl_composer/adapter.py",
  "name": "residual_rl_composer"
}
```

Forbidden advantages:
- training on evaluation resets
- post hoc barrier labels

### `stable_dmp_handoff`

- Role: stable dynamics handoff baseline
- Spec: `external_validation/baseline_specs/stable_dmp_handoff.json`
- Required entrypoint: `generate_stable_handoff`
- Target adapter directory: `external_validation/baselines/stable_dmp_handoff`
- Suggested real implementation path: `external_validation/implementations/stable_dmp_handoff/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/stable_dmp_handoff/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/stable_dmp_handoff/adapter.py",
  "name": "stable_dmp_handoff"
}
```

Forbidden advantages:
- oracle basin membership
- future failure labels

### `tamp_feasibility_screen`

- Role: task-and-motion feasibility baseline
- Spec: `external_validation/baseline_specs/tamp_feasibility_screen.json`
- Required entrypoint: `screen_symbolic_geometric_transition`
- Target adapter directory: `external_validation/baselines/tamp_feasibility_screen`
- Suggested real implementation path: `external_validation/implementations/tamp_feasibility_screen/implementation.py`
- Evidence status: `missing_manifest_declared_implementation`
- Independent implementation required: `true`
- Scaffold allowed as evidence: `false`
- Reference adapter allowed as evidence: `false`
- Policy/config hash required in logs: `true`
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path or implementation>",
  "checkpoint_or_config_path": "external_validation/implementations/tamp_feasibility_screen/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/tamp_feasibility_screen/adapter.py",
  "name": "tamp_feasibility_screen"
}
```

Forbidden advantages:
- energy descent continuity
- post hoc contact outcome

## Strict Acceptance Commands

- `python scripts\build_external_method_implementation_packet.py`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\build_external_baseline_contract.py`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`
