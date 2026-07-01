# External Collection Runner

Not external evidence: `true`.

This directory defines the fail-closed runner for collecting Paper 119 external validation records on a real robot or accepted high-fidelity simulator. It is an execution harness, not a source of rollout evidence by itself.

## Evidence Command Shape

Dry-run packet check:

```powershell
python external_validation\runner\real_collection_runner.py --dry-run --max-rows 12
```

Backend contract qualification:

```powershell
python scripts\audit_external_backend_contract.py --strict `
  --backend-module my_lab.paper119_maniskill_backend `
  --task-config-dir external_validation\configs `
  --alias-map external_validation\method_alias_map.json
```

Repository ManiSkill/SAPIEN reference backend candidate:

```powershell
python scripts\audit_maniskill_backend_readiness.py
```

This audit checks `external_validation/runner/maniskill_reference_backend.py` against the backend API, task configs, platform-provenance fields, all 12 reference adapters, and a synthetic MP4 writer path. It also checks that state-shaped arrays cannot masquerade as render videos. It is not rollout evidence. The reference backend is fail-closed for official collection by default, and real evidence still requires accepted fidelity provenance, explicit alias unsealing, a specific run id, renderable per-episode videos, JSONL logs, a manifest, and strict evidence audits.

The reference backend records explicit render-backend/shader controls in platform provenance. Defaults are `PAPER119_MANISKILL_RENDER_BACKEND=cpu`, `PAPER119_MANISKILL_SHADER_PACK=minimal`, `PAPER119_MANISKILL_RENDER_WIDTH=128`, and `PAPER119_MANISKILL_RENDER_HEIGHT=128`; change them only as part of an audited external platform qualification.

Explicit reference-backend preflight:

```powershell
python scripts\audit_maniskill_reference_collection_preflight.py
```

This audit checks that the tracked reference backend can pass strict backend-contract qualification and explicit collection preflight up to the fidelity-acceptance gate. It does not write official logs, videos, or manifests, and it does not mark collection ready.

Pre-flight actual collection readiness:

```powershell
python scripts\audit_external_collection_readiness.py --strict `
  --backend-module my_lab.paper119_maniskill_backend `
  --run-id paper119_maniskill_sapien_YYYYMMDD `
  --unsealed-alias-map
```

Actual collection requires all of the following:

- a non-template backend module passed with `--backend-module`;
- real task configs in `external_validation/configs`, not `config_templates`;
- intentional alias unsealing with `--unsealed-alias-map`;
- empty output JSONL logs unless `--force` is explicitly used;
- backend video export to `external_validation/videos`;
- the official video write guard rejecting returned paths that are outside the requested target, non-`.mp4`, undersized, non-MP4-like, or accompanied by a diagnostic fallback sidecar before any JSONL row is written;
- the official JSONL write guard rejecting schema-invalid rollout records with the same strict rollout validator used after manifest assembly;
- atomic official evidence promotion, so videos are written to `.staging.mp4` paths, official videos and JSONL logs are replaced only after the selected batch succeeds, and failed batches preserve previous official videos/logs;
- a passing strict collection-readiness audit before the run starts;
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
