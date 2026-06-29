# External Method Implementation Packet

Not evidence: `true`.
Non-oracle method work orders: `11`.
Reference adapter provenance records: `11`.
Adapter acceptance fixtures: `11`.
Strict adapter evidence ready: `false`.

This packet converts the missing independent baseline layer into concrete implementation work orders. It does not provide real implementations, checkpoints, configs, logs, videos, or manifest evidence.

## Adapter Acceptance Fixtures (Non-Evidence)

- JSON: `external_validation/adapter_acceptance_fixtures.json`
- Markdown: `external_validation/adapter_acceptance_fixtures.md`
- CSV: `external_validation/adapter_acceptance_fixtures.csv`

The fixture packet gives each independent implementation a synthetic smoke-test input and required adapter/log fields before rollout collection. Passing these fixtures does not count as external evidence; strict evidence still requires manifest-declared implementations, checkpoint/config hashes, raw JSONL logs, render-backed videos, and final strict audits.

## Reference Adapter Provenance (Non-Evidence)

The current reference adapters are executable interface artifacts. They make the proposed adapter API inspectable, but they are not independent rollout evidence, cannot replace operator-supplied implementations, and are blocked by the strict reference-adapter rejection gate.

### `barrier_certified_energy_composer_v5` reference adapter

- Adapter: `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py`
- Adapter SHA256: `DFECC8475DFE638A5F23B7941CEB00C1F8094EF2256BE60F20CA6F817341859B`
- Metadata: `external_validation/baselines/barrier_certified_energy_composer_v5/reference_adapter_metadata.json`
- Metadata SHA256: `43927773BC52B3BA31376C956CEC5269715957DFDFCE8EE3E209DCEEFE8EF092`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `c5b35077de3d070679b8622b66f6fd273ed36f76e5426a8dbd8c75a3fca5801b`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "paper_method_under_test",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": true,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py",
  "interface_reference_adapter_sha256": "DFECC8475DFE638A5F23B7941CEB00C1F8094EF2256BE60F20CA6F817341859B",
  "name": "barrier_certified_energy_composer_v5"
}
```

### `behavior_cloned_skill_chain` reference adapter

- Adapter: `external_validation/baselines/behavior_cloned_skill_chain/adapter.py`
- Adapter SHA256: `9B3548FB33CAB6503F8BF9F6189FEDC2177897E83C3FDF2D657CA6E1019F4890`
- Metadata: `external_validation/baselines/behavior_cloned_skill_chain/reference_adapter_metadata.json`
- Metadata SHA256: `D49DAEFFB6BE02DF858C415B13157FC783CE3864C909A9E144E809439F7E3A3F`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `29f574f25bc81ebbf1a779f80ef703bc20f9782676ce66070affcd86a5db5ff0`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/behavior_cloned_skill_chain/adapter.py",
  "interface_reference_adapter_sha256": "9B3548FB33CAB6503F8BF9F6189FEDC2177897E83C3FDF2D657CA6E1019F4890",
  "name": "behavior_cloned_skill_chain"
}
```

### `cem_trajectory_composer` reference adapter

- Adapter: `external_validation/baselines/cem_trajectory_composer/adapter.py`
- Adapter SHA256: `81B7FFAE412D296A7A5E9D0ADEF0BBE2031FB4D4FB08B65DD6408F1101668FDB`
- Metadata: `external_validation/baselines/cem_trajectory_composer/reference_adapter_metadata.json`
- Metadata SHA256: `517511503ED732E656A3CAE1B8173FB0890DDED96C284CAE30F5428F8A002B08`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `053d72c9cf26900f6d1e050ccfa2f85b806cbb7d019c0112470425b34ac8b121`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/cem_trajectory_composer/adapter.py",
  "interface_reference_adapter_sha256": "81B7FFAE412D296A7A5E9D0ADEF0BBE2031FB4D4FB08B65DD6408F1101668FDB",
  "name": "cem_trajectory_composer"
}
```

### `diffusion_skill_stitcher` reference adapter

- Adapter: `external_validation/baselines/diffusion_skill_stitcher/adapter.py`
- Adapter SHA256: `B16C610BCB5906C72BFD7495792D5635546513E91BC44CAC98C9C5DA3F3177BF`
- Metadata: `external_validation/baselines/diffusion_skill_stitcher/reference_adapter_metadata.json`
- Metadata SHA256: `35EB7CAE4718930995DA80B1F88B059C91BD179E903618C044BF77BD3BBE02C7`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `e2aa37a30871d4db6acc50692895476e4a3fd2570da358a5e21c53a436011428`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/diffusion_skill_stitcher/adapter.py",
  "interface_reference_adapter_sha256": "B16C610BCB5906C72BFD7495792D5635546513E91BC44CAC98C9C5DA3F3177BF",
  "name": "diffusion_skill_stitcher"
}
```

### `energy_compatibility_heuristic` reference adapter

- Adapter: `external_validation/baselines/energy_compatibility_heuristic/adapter.py`
- Adapter SHA256: `C59B9E9BA7621A12731D0228488B990593915A23A884FC2042842D550637FC59`
- Metadata: `external_validation/baselines/energy_compatibility_heuristic/reference_adapter_metadata.json`
- Metadata SHA256: `18D60A2A2F1687319F36DA9BCE9B119B8B8128F1BE4942240E77F05E241692C9`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `7663d39aa3d4336989a346b9fed49eb14645f4bbaeecfbf81c9321af1797a2d9`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/energy_compatibility_heuristic/adapter.py",
  "interface_reference_adapter_sha256": "C59B9E9BA7621A12731D0228488B990593915A23A884FC2042842D550637FC59",
  "name": "energy_compatibility_heuristic"
}
```

### `greedy_module_sequence` reference adapter

- Adapter: `external_validation/baselines/greedy_module_sequence/adapter.py`
- Adapter SHA256: `8C9F465960077E3B8A67DC398B236C2C1C0E4F253E51366A56EA77E5ED5CC963`
- Metadata: `external_validation/baselines/greedy_module_sequence/reference_adapter_metadata.json`
- Metadata SHA256: `DCCBF2DD75F13658266157E0AD797AFCE6E9DA96B92EAA7A3387A8BDCE090407`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `1156058db6d821bfcff6e8f68394ddf1c99964a96bbf39984c1c02db91593d09`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/greedy_module_sequence/adapter.py",
  "interface_reference_adapter_sha256": "8C9F465960077E3B8A67DC398B236C2C1C0E4F253E51366A56EA77E5ED5CC963",
  "name": "greedy_module_sequence"
}
```

### `option_graph_planner` reference adapter

- Adapter: `external_validation/baselines/option_graph_planner/adapter.py`
- Adapter SHA256: `BA19AC254B64D5F79600E44EE88A748FC237D3910BA592014D732E632535B22D`
- Metadata: `external_validation/baselines/option_graph_planner/reference_adapter_metadata.json`
- Metadata SHA256: `4FCA52468D2B02DDFCEAA9B2A89381E9723CF910F89DC33AB995E6A11368F02D`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `97728765a959db7ed443cd6eb726e58bcbcc36878395200a2f14bdc9a083fdfe`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/option_graph_planner/adapter.py",
  "interface_reference_adapter_sha256": "BA19AC254B64D5F79600E44EE88A748FC237D3910BA592014D732E632535B22D",
  "name": "option_graph_planner"
}
```

### `proposed_energy_landscape_composer_v4_1` reference adapter

- Adapter: `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py`
- Adapter SHA256: `ADE2084726B6A6DE7B2F90DFA6A1C4F5D2614551079E978AF9B849A794C6A540`
- Metadata: `external_validation/baselines/proposed_energy_landscape_composer_v4_1/reference_adapter_metadata.json`
- Metadata SHA256: `3D0F0E9C90265776C4B7A18D0E11FC5AE1EF03CCF32862F7EB30D0B6543C2E97`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `ca89dded1eb2bf14fc273965ccac560b69f5ca0527accdca85162dcaffacc8bf`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "paper_predecessor_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": true,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py",
  "interface_reference_adapter_sha256": "ADE2084726B6A6DE7B2F90DFA6A1C4F5D2614551079E978AF9B849A794C6A540",
  "name": "proposed_energy_landscape_composer_v4_1"
}
```

### `residual_rl_composer` reference adapter

- Adapter: `external_validation/baselines/residual_rl_composer/adapter.py`
- Adapter SHA256: `5B72C98DC049FC0476451EE9E89A0F94D2E50DC1B20AF7CB327D6A60404919FF`
- Metadata: `external_validation/baselines/residual_rl_composer/reference_adapter_metadata.json`
- Metadata SHA256: `834E64EE4A38F2B90C5D7D15E8711C05B670DA42794D8AF70C992D7017601CA1`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `4a99e07c959388c4a66d68b31dd8f184d33f6dab32dc1e1c52e2773b595567f2`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/residual_rl_composer/adapter.py",
  "interface_reference_adapter_sha256": "5B72C98DC049FC0476451EE9E89A0F94D2E50DC1B20AF7CB327D6A60404919FF",
  "name": "residual_rl_composer"
}
```

### `stable_dmp_handoff` reference adapter

- Adapter: `external_validation/baselines/stable_dmp_handoff/adapter.py`
- Adapter SHA256: `3C16F0F4178F4F9A6FA6EEB88CF0CC7EB5A78890351C0EB2DDCFBCF6BC031F89`
- Metadata: `external_validation/baselines/stable_dmp_handoff/reference_adapter_metadata.json`
- Metadata SHA256: `1F13C312604CABE911505F547A790EF6E04404FA1B07A401E542831B78AF7018`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `eb50e1f9e2b168d6150d0cb4b87464746f8eca7a5174e1ab39303ff0e0dfc96b`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/stable_dmp_handoff/adapter.py",
  "interface_reference_adapter_sha256": "3C16F0F4178F4F9A6FA6EEB88CF0CC7EB5A78890351C0EB2DDCFBCF6BC031F89",
  "name": "stable_dmp_handoff"
}
```

### `tamp_feasibility_screen` reference adapter

- Adapter: `external_validation/baselines/tamp_feasibility_screen/adapter.py`
- Adapter SHA256: `1664C0DB0B62CAAE96F3BB2DDE13956797A82FC00BFA11D12C8F2E06C51C6AA9`
- Metadata: `external_validation/baselines/tamp_feasibility_screen/reference_adapter_metadata.json`
- Metadata SHA256: `DA8DBB10C331A0FE572D5ADF7BBDACABDE29664E78BEFADA1BFC7CEA377F0987`
- Shared adapter SHA256: `9FC13A8FFA1120279C68CAA335C8095D128AA5AA1E04D25355A64AA7C32C140A`
- Reference policy hash: `36ab281a79d427ee2aa5766a8fcc89cdbca905efb50d46bb95d7c3f08b129350`
- Evidence status: `implementation_only_not_rollout_evidence`
- Manifest declaration stub:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "<operator-supplied real config/checkpoint path>",
  "implementation": "<operator-supplied independent implementation path, not the current reference adapter>",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
  "interface_reference_adapter": "external_validation/baselines/tamp_feasibility_screen/adapter.py",
  "interface_reference_adapter_sha256": "1664C0DB0B62CAAE96F3BB2DDE13956797A82FC00BFA11D12C8F2E06C51C6AA9",
  "name": "tamp_feasibility_screen"
}
```

## Forbidden Evidence Shortcuts

- using scaffold adapters as manifest-declared implementations
- using reference adapters as rollout evidence without real source/config/checkpoint hashes
- using reference adapters to bypass the strict reference-adapter rejection gate
- using implementation-source hashes as checkpoint_or_config_hash without a matching checkpoint_or_config_path artifact
- declaring only a subset of non-oracle methods in the strict adapter manifest
- using policy_or_config_hash values in JSONL logs that do not match manifest-declared hashes
- omitting implementation_provenance or using provenance that permits oracle access, scaffold/reference adapters, proposed-code leakage for independent baselines, or post-outcome tuning
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/barrier_certified_energy_composer_v5/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/barrier_certified_energy_composer_v5/adapter.py",
  "implementation_provenance": {
    "evidence_role": "paper_method_under_test",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": true,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/behavior_cloned_skill_chain/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/behavior_cloned_skill_chain/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/cem_trajectory_composer/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/cem_trajectory_composer/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/diffusion_skill_stitcher/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/diffusion_skill_stitcher/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/energy_compatibility_heuristic/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/energy_compatibility_heuristic/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/greedy_module_sequence/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/greedy_module_sequence/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/option_graph_planner/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/option_graph_planner/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/proposed_energy_landscape_composer_v4_1/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/proposed_energy_landscape_composer_v4_1/adapter.py",
  "implementation_provenance": {
    "evidence_role": "paper_predecessor_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": true,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/residual_rl_composer/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/residual_rl_composer/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/stable_dmp_handoff/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/stable_dmp_handoff/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
- Required artifact fields: `implementation_path_or_repository`, `implementation_sha256_or_commit`, `checkpoint_or_config_path`, `checkpoint_or_config_hash`, `implementation_provenance`, `adapter_path`, `manifest_method_entry`, `policy_or_config_hash_in_logs`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `success`, `utility`
- Manifest method entry template:
```json
{
  "checkpoint_or_config_hash": "<64-character SHA256 matching checkpoint_or_config_path>",
  "checkpoint_or_config_path": "external_validation/implementations/tamp_feasibility_screen/config_or_checkpoint.json",
  "implementation": "external_validation/implementations/tamp_feasibility_screen/adapter.py",
  "implementation_provenance": {
    "evidence_role": "independent_non_oracle_method",
    "implementation_origin": "<operator/lab/repository source for this implementation>",
    "independent_operator_or_lab": "<independent operator or lab name>",
    "operator_signoff_id": "<signoff id or dated note>",
    "oracle_access": false,
    "policy_or_config_hash_locked": true,
    "same_compute_budget": true,
    "same_observation_interface": true,
    "same_skill_library": true,
    "uses_eval_outcome_tuning": false,
    "uses_proposed_method_code": false,
    "uses_reference_adapter": false,
    "uses_scaffold_template": false,
    "uses_unblinded_method_identity_during_collection": false
  },
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
