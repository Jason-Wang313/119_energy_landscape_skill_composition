# Method Manifest Cutover Checklist

Not evidence: `true`.
Strict adapter evidence ready: `false`.
Method rows: `11`.

This checklist is the operator-facing bridge from non-evidence method work orders to real `manifest.methods[]` entries. It does not provide implementations, checkpoints, configs, rollout logs, videos, or adapter evidence. It exists so the independent operator cannot half-declare a method before strict adapter validation.

## Required Cutover Fields

- `name`
- `implementation`
- `checkpoint_or_config_path`
- `checkpoint_or_config_hash`
- `implementation_provenance`
- `implementation_sha256_or_commit`
- fairness-contract ids/hashes for skill library, observation interface, compute budget, and paired-reset protocol
- JSONL `policy_or_config_hash` values matching `checkpoint_or_config_hash`

## Method Rows

| Method | Role | Manifest key | Fixture | Reference interface | Strict gate |
|---|---|---|---|---|---|
| `barrier_certified_energy_composer_v5` | `paper_method_under_test` | `methods[barrier_certified_energy_composer_v5]` | `9f068fce6e0dbb71` | `external_validation/baselines/barrier_certified_energy_composer_v5/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `behavior_cloned_skill_chain` | `independent_non_oracle_method` | `methods[behavior_cloned_skill_chain]` | `c687049fe1e42b8e` | `external_validation/baselines/behavior_cloned_skill_chain/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `cem_trajectory_composer` | `independent_non_oracle_method` | `methods[cem_trajectory_composer]` | `b304bd717f821f4f` | `external_validation/baselines/cem_trajectory_composer/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `diffusion_skill_stitcher` | `independent_non_oracle_method` | `methods[diffusion_skill_stitcher]` | `bf46e7a5a2ec8070` | `external_validation/baselines/diffusion_skill_stitcher/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `energy_compatibility_heuristic` | `independent_non_oracle_method` | `methods[energy_compatibility_heuristic]` | `dbe9b3013a79b75c` | `external_validation/baselines/energy_compatibility_heuristic/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `greedy_module_sequence` | `independent_non_oracle_method` | `methods[greedy_module_sequence]` | `ab38043ad3a079bd` | `external_validation/baselines/greedy_module_sequence/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `option_graph_planner` | `independent_non_oracle_method` | `methods[option_graph_planner]` | `695ef6cf59f11a37` | `external_validation/baselines/option_graph_planner/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `proposed_energy_landscape_composer_v4_1` | `paper_predecessor_method` | `methods[proposed_energy_landscape_composer_v4_1]` | `8d47d553b0e71c72` | `external_validation/baselines/proposed_energy_landscape_composer_v4_1/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `residual_rl_composer` | `independent_non_oracle_method` | `methods[residual_rl_composer]` | `046a1b0e8e104c7c` | `external_validation/baselines/residual_rl_composer/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `stable_dmp_handoff` | `independent_non_oracle_method` | `methods[stable_dmp_handoff]` | `b205384dad3b50bc` | `external_validation/baselines/stable_dmp_handoff/adapter.py` | `python scripts\validate_external_adapters.py --strict` |
| `tamp_feasibility_screen` | `independent_non_oracle_method` | `methods[tamp_feasibility_screen]` | `33476b661e28219b` | `external_validation/baselines/tamp_feasibility_screen/adapter.py` | `python scripts\validate_external_adapters.py --strict` |

## Evidence Boundary

- Reference adapters and scaffold templates are interface aids only; they are forbidden as strict external evidence.
- `checkpoint_or_config_hash` must hash the declared checkpoint/config artifact, not merely the implementation source.
- Every method provenance block must bind to the same manifest fairness contract before rollout logs count.
- This checklist remains blocking until real operator-supplied implementations and manifest-declared hashes pass `python scripts\validate_external_adapters.py --strict`.

