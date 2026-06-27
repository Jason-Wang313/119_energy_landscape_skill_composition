# External Collection Runner

Not external evidence: `true`.

This directory defines the fail-closed runner for collecting Paper 119 external validation records on a real robot or accepted high-fidelity simulator. It is an execution harness, not a source of rollout evidence by itself.

## Evidence Command Shape

Dry-run packet check:

```powershell
python external_validation\runner\real_collection_runner.py --dry-run --max-rows 12
```

Actual collection requires all of the following:

- a non-template backend module passed with `--backend-module`;
- real task configs in `external_validation/configs`, not `config_templates`;
- intentional alias unsealing with `--unsealed-alias-map`;
- empty output JSONL logs unless `--force` is explicitly used;
- backend video export to `external_validation/videos`;
- a later manifest build plus strict `validate_external_rollouts.py --strict --check-video-paths` and `audit_external_evidence.py --strict`.

Example actual command after a real backend exists:

```powershell
python external_validation\runner\real_collection_runner.py `
  --backend-module my_lab.paper119_maniskill_backend `
  --task-config-dir external_validation\configs `
  --output-log-dir external_validation\logs `
  --video-dir external_validation\videos `
  --run-id paper119_maniskill_sapien_YYYYMMDD `
  --unsealed-alias-map
```

## Backend Contract

Backends must implement:

- `platform_provenance`
- `load_task_config`
- `reset_scene`
- `capture_observation`
- `terminal_samples`
- `run_method`
- `execute_skill_pair`
- `record_video`
- `policy_or_config_hash`

Template backends under `backend_templates/` keep `TEMPLATE_ONLY = True` and deliberately raise `NotImplementedError` through the shared base class. The runner refuses those templates for actual collection.

## Blinding Boundary

The operator sheet stays blinded. The runner only resolves `method_alias` through `method_alias_map.json` when `--unsealed-alias-map` is supplied, making alias access explicit in the execution command. Do not unseal aliases until configs, implementation hashes, logs, and videos are frozen.

