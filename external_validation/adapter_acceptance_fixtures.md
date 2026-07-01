# Adapter Acceptance Fixtures

Not evidence: `true`.
Fixture count: `11`.
Strict adapter evidence ready: `false`.

These fixtures are synthetic pre-rollout smoke tests for independent method implementations. They make the adapter API and log-field expectations concrete, but they do not replace manifest-declared implementations, checkpoint/config hashes, raw rollout logs, render-backed videos, or strict external evidence audits.

Source validator: `scripts/validate_external_adapters.py`.

## Fixtures

### `barrier_certified_energy_composer_v5`

- Fixture ID: `9f068fce6e0dbb71`
- Fixture SHA256: `549a65e96bda998cd160e03330647f8aea10d5dfe105316b38b4879acb46d098`
- Synthetic policy/config hash: `5c799d470f872c005610b60a087d3e692e41db0eac34056312277b79c92c7199`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `behavior_cloned_skill_chain`

- Fixture ID: `c687049fe1e42b8e`
- Fixture SHA256: `d6f7517903c23f2623316817e8e6dfa97e18b170d6fa601a4caa095ef19afbce`
- Synthetic policy/config hash: `36502dc4db709a95739c53b890995e135c4efaf8035794e397c3fbc23b610a9a`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `cem_trajectory_composer`

- Fixture ID: `b304bd717f821f4f`
- Fixture SHA256: `1d1470f584f90fcb2f371cb248ebc77712cdde7ea8bf8e322e61c8697a71793d`
- Synthetic policy/config hash: `d8f8118febac98ba4d6da164ae25a3daf9069cb384753521208e84a23df3bd52`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `diffusion_skill_stitcher`

- Fixture ID: `bf46e7a5a2ec8070`
- Fixture SHA256: `c7470c879eecf7e6777b2c3b7788853c7b380be50c3e6664ebbe358b44675de9`
- Synthetic policy/config hash: `e84371081b26c1396a7b4909e1c10cd5d9acf2069e4600bf84ce9e28a315457d`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `energy_compatibility_heuristic`

- Fixture ID: `dbe9b3013a79b75c`
- Fixture SHA256: `2f0478bcd755bfa6a4351806015e8d88b5b12666e72f5c9dbfb3266d9fec3481`
- Synthetic policy/config hash: `a825621f3d9611a92cf354f602ec7ecd63e4ef5afebaf9490e77ae4d0e9f03e4`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `greedy_module_sequence`

- Fixture ID: `ab38043ad3a079bd`
- Fixture SHA256: `ec7a556b3545a33a07c695965f4d1389d9e81af61309ce42ea6239ffd8812338`
- Synthetic policy/config hash: `e70341dab0fe0c55d9334f24194363d842d7cd47f5bc911dfc468193159bd165`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `option_graph_planner`

- Fixture ID: `695ef6cf59f11a37`
- Fixture SHA256: `410db4e7c6cc110c5a703e3dafa8e96e7307788ffaa4c832e8de4fbcbb01ccd1`
- Synthetic policy/config hash: `74aac2f748ba562a8875c06493033b3f43d3d008cbf36976873b62ec6b493534`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `proposed_energy_landscape_composer_v4_1`

- Fixture ID: `8d47d553b0e71c72`
- Fixture SHA256: `9f095d066d4edeb70f9ab5f215c6b6c37df10691fa41c0c32c196d344936ee69`
- Synthetic policy/config hash: `efae6646486f6f3cb1d8820034d8623df478e93537e8eb57a63555f69317536a`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `residual_rl_composer`

- Fixture ID: `046a1b0e8e104c7c`
- Fixture SHA256: `c471d77e6bdcc21dfbfbf1ebb5f933f6d57ccbec5c26c0ccbacba780955e893c`
- Synthetic policy/config hash: `d0754f7f472b9fafbb9f9c466cffcb67acdf0ec2c42c044150fc3a49cfa67ed8`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `stable_dmp_handoff`

- Fixture ID: `b205384dad3b50bc`
- Fixture SHA256: `849d65c6acfd228726521e74a7aaa4873ba3aa27b50ce53f3cb2c99bc2b44030`
- Synthetic policy/config hash: `70d5ce10dc8723195b17f22941f033cae042ea5658aca46168be50496a8d0784`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

### `tamp_feasibility_screen`

- Fixture ID: `33476b661e28219b`
- Fixture SHA256: `8668882e21de76ce264b282571f8711923eded56e2b44cc8e00ca25c6c26a868`
- Synthetic policy/config hash: `69b7403ed24794ade7449afede0768a417840e1af5e3a5c82a8390073cbb0e4f`
- Required API: `initialize`, `propose`, `log`, `reset`
- Required proposal fields: `decision`, `predicted_seam_risk`, `failure_diagnosis`, `repair_action`
- Required log fields: `decision`, `failure_diagnosis`, `method`, `policy_or_config_hash`, `predicted_seam_risk`, `realized_seam_breach`, `repair_action`, `success`, `utility`
- Synthetic input summary:
  - task_family: `peg_place_regrasp`
  - terminal_samples: `2`
  - fixed_risk_budget: `0.15`

Acceptance assertions:
- adapter imports without side effects
- initialize(config) returns a dict
- propose(observation, terminal_samples, skill_i, skill_j, compute_budget) returns required proposal fields
- predicted_seam_risk is numeric in [0, 1]
- log(episode_context, proposal, outcome) returns required log fields
- log.policy_or_config_hash is a 64-character SHA256 and matches the manifest-declared checkpoint_or_config_hash during strict validation
- reset(reset_context) completes without raising NotImplementedError

Evidence boundary: Passing this synthetic fixture is only a pre-rollout adapter smoke test. Strict evidence still requires external_validation/manifest.json, operator-supplied implementation provenance, checkpoint/config artifact hashes, raw JSONL rollout logs, render-backed videos, pairing/release audits, and audit_external_evidence.py --strict.

