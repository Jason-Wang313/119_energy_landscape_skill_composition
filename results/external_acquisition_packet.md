# External Evidence Acquisition Packet

Passed: `true`.
Not evidence: `true`.
Strict evidence ready: `false`.

This packet maps the remaining main-conference blockers to concrete operator inputs, artifacts, and strict validation commands. It is not robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for the strict external audits.

## Remaining Submission Blockers

| Requirement | Operator actions |
|---|---|
| `Independent real-robot or accepted high-fidelity external validation evidence` | `platform_fidelity`, `run_collection`, `manifest_and_release` |
| `External rollout metrics recomputed from raw JSONL logs` | `run_collection`, `strict_rollout_recompute` |
| `Manifest-declared real task configs replace non-evidence templates` | `real_task_configs`, `manifest_and_release` |
| `Manifest-declared independent non-oracle baseline evidence and fairness contract` | `real_method_implementations`, `strict_adapter_evidence` |

## Collection Preflight Blockers

- `backend_module_ready`: --backend-module is required before actual collection
- `task_config_dir_exists`: external_validation/configs
- `real_task_configs_ready`: missing config: external_validation/configs/cable_route_insert.json; missing config: external_validation/configs/door_open_navigation.json; missing config: external_validation/configs/drawer_to_pick_transfer.json; missing config: external_validation/configs/peg_place_regrasp.json
- `fidelity_acceptance_ready`: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'
- `alias_unsealing_explicit`: unsealed_alias_map=False
- `run_id_specific`: run_id='paper119_external_validation_run'

## Operator Actions

| ID | Action | Operator input | Key artifacts | Commands |
|---|---|---|---|---|
| `backend_module` | Select a non-template backend module | `--backend-module <module_or_path>` | `external_validation/runner/backends/<real_backend>.py` | `python scripts\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map` |
| `real_task_configs` | Create real manifest-declared task configs | `external_validation/configs/<task_family>.json for each task family` | `external_validation/configs/peg_place_regrasp.json`<br>`external_validation/configs/drawer_to_pick_transfer.json`<br>`external_validation/configs/door_open_navigation.json`<br>`external_validation/configs/cable_route_insert.json` | `python scripts\validate_external_configs.py --strict` |
| `platform_fidelity` | Fill platform fidelity acceptance with real provenance | `accepted simulator or robot evidence, contact/dynamics/camera/state provenance, and task coverage` | `external_validation/fidelity_acceptance.json` | `python scripts\audit_external_fidelity_acceptance.py --strict` |
| `alias_unseal` | Unseal method aliases only after configs, implementations, and run plan are frozen | `--unsealed-alias-map` | `external_validation/method_alias_map.json` | `python scripts\audit_external_collection_readiness.py --strict --unsealed-alias-map` |
| `specific_run_id` | Use a specific immutable external run id | `--run-id <platform>_<date>_<protocol_version>` | `external_validation/logs/*.jsonl` | `python scripts\audit_external_collection_readiness.py --strict --run-id <specific_run_id>` |
| `real_method_implementations` | Replace scaffold-only methods with real non-oracle implementations or wrappers | `implementation_path and checkpoint_or_config_path/hash for every non-oracle method` | `external_validation/adapters/<method>/implementation.py`<br>`external_validation/baselines/<method>/implementation.py`<br>`external_validation/checkpoints_or_configs/<method>.*` | `python scripts\build_external_baseline_contract.py`<br>`python scripts\validate_external_adapters.py --strict` |
| `run_collection` | Collect paired-reset external rollouts | `1,440 JSONL records over 4 tasks x 12 methods x 120 paired resets` | `external_validation/logs/peg_place_regrasp.jsonl`<br>`external_validation/logs/drawer_to_pick_transfer.jsonl`<br>`external_validation/logs/door_open_navigation.jsonl`<br>`external_validation/logs/cable_route_insert.jsonl`<br>`external_validation/videos/<task_family>/*` | `python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map` |
| `manifest_and_release` | Build the real manifest and hash-lock release artifacts | `manifest paths, code commit, skill-library hash, config/log/video/checkpoint hashes` | `external_validation/manifest.json`<br>`results/external_manifest_builder_report.json` | `python scripts\build_external_manifest.py --write --check-video-paths`<br>`python scripts\audit_external_release_package.py --strict` |
| `strict_rollout_recompute` | Recompute external metrics from raw JSONL logs | `strict rollout validator over manifest-declared logs and videos` | `results/external_rollout_metrics.json`<br>`results/external_rollout_metrics.md` | `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict` |
| `strict_adapter_evidence` | Audit independent method evidence after the manifest is real | `manifest-declared non-oracle implementation paths and hashes` | `results/external_baseline_contract_audit.json`<br>`results/external_adapter_contract_evidence_audit.json` | `python scripts\build_external_baseline_contract.py`<br>`python scripts\validate_external_adapters.py --strict` |
| `final_strict_gate` | Run the final strict external-evidence gate | `completed manifest, logs, videos, configs, checkpoints/hashes, adapters, and fidelity acceptance` | `results/external_evidence_audit.json`<br>`results/submission_readiness_gap_audit.json` | `python scripts\audit_external_pairing_integrity.py --strict`<br>`python scripts\audit_external_evidence.py --strict`<br>`python scripts\audit_submission_readiness_gap.py` |

## Strict Collection Command

```powershell
python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map
```

## Post-Collection Strict Gates

- `python scripts\build_external_manifest.py --write --check-video-paths`
- `python scripts\audit_external_release_package.py --strict`
- `python scripts\audit_external_fidelity_acceptance.py --strict`
- `python scripts\validate_external_adapters.py --strict`
- `python scripts\validate_external_configs.py --strict`
- `python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict`
- `python scripts\audit_external_pairing_integrity.py --strict`
- `python scripts\audit_external_evidence.py --strict`

## Checks

- `pass` `source_audits_exist`: results/external_collection_readiness_audit.json, results/external_evidence_preflight.json, results/independent_validation_route_audit.json
- `pass` `gap_audit_has_four_external_blockers`: missing=['Independent real-robot or accepted high-fidelity external validation evidence', 'External rollout metrics recomputed from raw JSONL logs', 'Manifest-declared real task configs replace non-evidence templates', 'Manifest-declared independent non-oracle baseline evidence and fairness contract']
- `pass` `all_missing_requirements_mapped`: unmapped=[]
- `pass` `all_action_ids_exist`: missing_action_ids=[]
- `pass` `collection_preflight_fail_closed`: collection_ready=False, blockers=['alias_unsealing_explicit', 'backend_module_ready', 'fidelity_acceptance_ready', 'real_task_configs_ready', 'run_id_specific', 'task_config_dir_exists']
- `pass` `preflight_operator_actions_present`: operator_next_actions=5, evidence_ready=False
- `pass` `route_independent_of_haonan`: primary_route='maniskill_sapien_primary'
- `pass` `post_collection_strict_commands_cover_all_gates`: missing_command_fragments=[]
- `pass` `no_real_manifest_written`: external_validation/manifest.json absent before real evidence
- `pass` `operator_actions_cover_collection_blockers`: Select a non-template backend module Create real manifest-declared task configs Fill platform fidelity acceptance with real provenance Unseal method aliases only after configs, implementations, and run plan are frozen Use a specific immutable external run id Replace scaffold-only methods with real non-oracle implementations or wrappers Collect paired-reset external rollouts Build the real manifest and hash-lock release artifacts Recompute external metrics from raw JSONL logs Audit independent method evidence after the manifest is real Run the final strict external-evidence gate
