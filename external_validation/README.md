# External Validation Evidence Contract

This directory is reserved for evidence that can make Paper 119 independently submission-ready.

The current paper is not main-conference ready until `scripts/audit_external_evidence.py --strict`, `scripts\validate_external_rollouts.py --strict --write-results`, `scripts\audit_external_pairing_integrity.py --strict`, and `scripts\audit_external_release_package.py --strict` pass against a real `external_validation/manifest.json` and the referenced logs, videos, configs, checkpoints, and baseline implementations. Before spending robot or simulator time, `scripts\audit_external_collection_readiness.py --strict` must also pass with a real backend, real configs, accepted fidelity provenance, explicit alias unsealing, and a specific run id.

Use `manifest_template.json` as the required manifest structure and `log_schema_v1.json` as the required episode-level JSONL schema. A valid evidence package must prove one of:

- at least 3 real-robot composed task families with paired resets;
- at least 4 accepted high-fidelity simulation task families with contact/dynamics fidelity;
- a mixed route with at least 2 real-robot and 2 high-fidelity simulation task families.

Raw episode logs are the source of truth. Tables and figures may be regenerated from them, but cannot replace them.

Task configs must follow `config_schema_v1.json`. Validate non-evidence templates with:

```powershell
python scripts\validate_external_configs.py
```

Validate real manifest-declared configs with:

```powershell
python scripts\validate_external_configs.py --strict
```

Strict config validation currently fails until `external_validation/manifest.json` points to real `external_validation/configs/*.json` files that are not marked as templates. The tracked `external_validation/configs/README.md` file makes the real-config intake directory explicit, but it is not evidence and does not replace the required task JSON files.

Plan guarded materialization of real task configs:

```powershell
python scripts\materialize_external_configs.py
```

This writes `results/external_config_materialization_plan.{json,md}` only. It does not write real configs by default. After an operator has selected a real platform and compute budget, use the guarded write form shown in that report; the command requires `--confirm-real-platform --write` and rejects dry-run/template placeholders.

Build the external config manifest packet:

```powershell
python scripts\build_external_config_manifest_packet.py
```

This writes `external_validation/config_manifest_packet.{json,md}`, `external_validation/config_manifest_work_orders.csv`, and `results/external_config_manifest_audit.{json,md}`. It turns prepared task configs into manifest-declaration and hash-lock work orders. It is not evidence and still reports strict config evidence as missing until a real manifest, rollout logs, videos, and artifact hashes exist.

Build the external rollout evidence packet:

```powershell
python scripts\build_external_rollout_evidence_packet.py
```

This writes `external_validation/rollout_evidence_packet.{json,md}`, `external_validation/rollout_evidence_work_orders.csv`, and `results/external_rollout_evidence_audit.{json,md}`. It turns the missing raw JSONL logs, videos, manifest writing, strict rollout recomputation, pairing, release, and final evidence gates into work orders. It is not evidence and still reports strict rollout and external evidence as missing until real manifest-declared artifacts exist.

Build the external pilot smoke packet:

```powershell
python scripts\audit_external_pilot_smoke.py
python scripts\build_external_pilot_smoke_packet.py
```

This writes `external_validation/pilot_smoke_packet.{json,md}`, `external_validation/pilot_smoke_work_orders.csv`, `results/external_pilot_smoke_audit.{json,md}`, and `results/external_pilot_smoke_packet_audit.{json,md}`. It gives an independent operator a quarantined 12-row first-panel backend smoke test before official collection. Pilot logs and videos must stay under `external_validation/pilot_smoke/` and must never be declared in `external_validation/manifest.json`.

Audit bounded ManiSkill pilot runtime liveness:

```powershell
python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 60 --max-rows 1
```

This writes `results/maniskill_pilot_runtime_liveness_audit.{json,md}`. It launches the tracked ManiSkill reference runner in quarantined `external_validation/pilot_runtime_guard/` directories with a strict timeout. It is not evidence and does not replace the pilot-smoke packet. The current local default report is fail-closed for official collection: `pilot_runtime_ready=false`, `runner_io_ready=false`, and `render_video_ready=false`, with no promoted pilot row/video. The audit records timeout progress and, when the runner reaches video export, whether a diagnostic sidecar rejected before JSONL write was stopped by the official video guard. Use an accepted GPU/render machine or fix render-backed RGB video before official collection.

The ManiSkill reference path uses explicit render-backend/shader controls. Defaults are `PAPER119_MANISKILL_RENDER_BACKEND=cpu`, `PAPER119_MANISKILL_SHADER_PACK=minimal`, `PAPER119_MANISKILL_RENDER_WIDTH=128`, and `PAPER119_MANISKILL_RENDER_HEIGHT=128`; the render-video preflight and pilot runtime liveness audit record these values so evidence videos are never confused with implicit local renderer defaults.

Build the independent operator packet:

```powershell
python scripts\build_external_operator_packet.py
```

This writes `results/external_operator_packet.{json,md}` with the current go/no-go state, remaining pre-collection blockers, exact collection command, and post-collection strict gates. It is not external evidence; it currently says `DO_NOT_COLLECT_YET` until the strict collection preflight passes with real backend, configs, fidelity acceptance, alias unsealing, and a specific run id.

Build the hash-listed operator handoff bundle:

```powershell
python scripts\build_external_operator_handoff_bundle.py
```

This writes `results/external_operator_handoff_bundle.{json,md}`. The bundle is a non-evidence manifest for the files to hand to an independent validation operator. It hash-lists the operator-facing docs, configs, task cards, runner contracts, baseline specs, adapter references, and strict command sources while excluding rollout logs, videos, checkpoints, local dry-run artifacts, placeholder media, and `external_validation/manifest.json`.

## Manifest Builder Workflow

Before collecting rollouts, generate the non-evidence collection schedule:

```powershell
python scripts\build_external_collection_plan.py
```

This writes `results/external_collection_plan.{json,md}`. It enumerates the paired reset slots, task families, methods, expected JSONL record count, required log fields, and strict validation commands. It is a plan only; it is not evidence and cannot satisfy the external gate.

Before collecting rollouts, lock the non-evidence statistical analysis plan:

```powershell
python scripts\build_external_analysis_plan.py
```

This writes `external_validation/statistical_analysis_plan.{json,md}` and `results/external_analysis_plan_audit.{json,md}`. The plan pre-registers the external primary hypotheses, rollout-schema thresholds, paired-comparison key, exclusion and unblinding policy, strict gates, and required reporting before independent collection starts. It is not evidence and cannot satisfy the external gate.

Generate the non-Haonan independent validation route:

```powershell
python scripts\build_independent_validation_route.py
```

This writes `external_validation/independent_validation_route.md`, `external_validation/independent_validation_route_matrix.csv`, and `results/independent_validation_route_audit.{json,md}`. It names a primary public-simulator route, secondary cross-engine routes, and a third-party robot-lab route for collecting the missing manifest-backed logs, videos, configs, platform provenance, and independent baseline implementations. It is route planning only, not evidence.

Probe the selected external platform machine:

```powershell
python scripts\probe_external_platform.py
```

This writes `results/external_platform_probe.{json,md}` with Python, package, GPU/renderer, code-commit, and config/backend hash provenance for the selected public-simulator route. It is not evidence; rerun it on the actual external GPU workstation and use `--strict` only as an install-readiness gate before collection.

Probe the ManiSkill task-family bindings:

```powershell
python scripts\probe_maniskill_task_bindings.py
```

This writes `results/maniskill_task_binding_probe.{json,md}` from `external_validation/maniskill_task_bindings.json`. It maps the four Paper 119 task families to concrete public-simulator environment candidates and checks the local Gymnasium registry when ManiSkill is installed. It is not evidence; the operator must still accept or replace the bindings in `external_validation/fidelity_acceptance.json` before any rollout can count.

Smoke-test bound ManiSkill environments:

```powershell
python scripts\probe_maniskill_env_smoke.py
```

This writes `results/maniskill_env_smoke_probe.{json,md}`. It attempts construction and reset for the bound public-simulator candidates without writing official rollout logs or videos. It is not evidence; use the report to install missing assets, replace weak bindings, and fill fidelity acceptance before backend qualification.

Probe ManiSkill fidelity metadata:

```powershell
python scripts\probe_maniskill_fidelity_metadata.py
```

This writes `results/maniskill_fidelity_metadata_probe.{json,md}`. It records sim/control timestep, SAPIEN backend, controller, observation/info-key, agent, and asset metadata for the bound public-simulator candidates. It is not evidence; use the report to verify or replace fidelity-review fields before promoting `external_validation/fidelity_acceptance.json`.

Build the external platform onboarding packet for the primary public-simulator route:

```powershell
python scripts\build_external_platform_onboarding.py
```

This writes `external_validation/platform_onboarding_packet.{json,md}` and `results/external_platform_onboarding_audit.{json,md}`. It records the official source anchors, install/version-probe command, required simulator provenance, task onboarding files, backend requirements, and strict gate order for the ManiSkill/SAPIEN route. It is not evidence; the operator must still supply real platform versions, accepted fidelity provenance, real configs, backend implementations, logs, videos, manifests, and hashes.

Build the external fidelity provenance packet:

```powershell
python scripts\build_external_fidelity_provenance_packet.py
```

This writes `external_validation/fidelity_provenance_packet.{json,md}`, `external_validation/fidelity_provenance_work_orders.csv`, and `results/external_fidelity_provenance_audit.{json,md}`. It turns platform physics/contact details, paired-reset replay, operator independence, calibration basis, code/skill hashes, manifest declaration, and strict fidelity gating into work orders. It is not evidence and still reports strict fidelity and external evidence as missing until a real acceptance file and manifest-declared artifacts exist.

Build the external fidelity acceptance draft:

```powershell
python scripts\build_external_fidelity_acceptance_draft.py
```

This writes `external_validation/fidelity_acceptance_draft.{json,md}` and `results/external_fidelity_acceptance_draft_audit.{json,md}`. The draft pre-fills the tracked ManiSkill/SAPIEN route with platform/package/backend/config hashes, task bindings, primary environment smoke status, and fidelity metadata, then reports a fidelity acceptance promotion checklist that separates machine-prefilled readiness from independent operator signoff readiness. It remains draft-only non-evidence: `external_validation/fidelity_acceptance.json` and `external_validation/manifest.json` must still be independently filled, promoted, and strict-audited before any collection can count.

Build the fidelity acceptance materialization plan:

```powershell
python scripts\materialize_fidelity_acceptance.py
```

This writes `results/fidelity_acceptance_materialization_plan.{json,md}` without creating `external_validation/fidelity_acceptance.json`. The guarded write command in that report requires independent-operator identity, accepted platform/machine, contact/timestep/replay/calibration/task-binding signoff, render-backed evidence-video readiness, real rollout evidence, manifest declaration, code commit, and skill-library hash before any acceptance file can be materialized. It is not evidence and strict fidelity remains false until the real manifest and strict audits pass.

Build the external backend integration packet:

```powershell
python scripts\build_external_backend_integration_packet.py
```

This writes `external_validation/backend_integration_packet.{json,md}`, `external_validation/backend_integration_work_orders.csv`, and `results/external_backend_integration_audit.{json,md}`. It turns the missing non-template public-simulator backend module into concrete backend-to-manifest work orders. It is not evidence and still reports strict backend readiness as missing until a real independent backend module, real task configs, provenance, logs, videos, manifests, and hashes exist.

Audit the repository ManiSkill/SAPIEN reference backend candidate:

```powershell
python scripts\audit_maniskill_backend_readiness.py
```

This writes `results/maniskill_backend_readiness_audit.{json,md}`. It contract-qualifies `external_validation/runner/maniskill_reference_backend.py` against the backend API, task configs, platform-provenance fields, all 12 reference adapters, and a synthetic MP4 writer path, while checking that state-shaped arrays cannot masquerade as render videos. It is not evidence: official collection still requires accepted fidelity provenance, installed assets, explicit alias unsealing, a specific run id, renderable per-episode videos, JSONL logs, a manifest, and strict evidence audits.

The readiness audit records explicit render-backend/shader controls in platform provenance: `PAPER119_MANISKILL_RENDER_BACKEND`, `PAPER119_MANISKILL_SHADER_PACK`, `PAPER119_MANISKILL_RENDER_WIDTH`, and `PAPER119_MANISKILL_RENDER_HEIGHT`.

Audit the explicit reference-backend collection preflight:

```powershell
python scripts\audit_maniskill_reference_collection_preflight.py
```

This writes `results/maniskill_reference_collection_preflight_audit.{json,md}`. It runs the tracked reference backend through the strict backend-contract and collection-preflight checks with explicit backend/config/run-id/alias inputs, without writing rollout logs, videos, manifests, or evidence. It currently reaches the fidelity-acceptance gate; official collection and strict external evidence remain false until accepted platform provenance, real logs, videos, manifests, and strict audits exist.

Then audit the platform-fidelity acceptance contract:

```powershell
python scripts\audit_external_fidelity_acceptance.py
python scripts\self_test_external_fidelity_acceptance.py
```

This writes `results/external_fidelity_acceptance_audit.{json,md}` and checks `external_validation/fidelity_acceptance_template.json`. It defines the minimum provenance required before a real robot or high-fidelity simulator route is credible: platform version, physics/contact details, replayable paired resets, state/camera/contact signals, operator independence, real or benchmark calibration basis, code commit, skill-library hash, and acceptance gates. It is not rollout evidence and currently reports `acceptance_ready: false` until `external_validation/fidelity_acceptance.json`, `external_validation/manifest.json`, and the real artifacts exist.

The fidelity acceptance self-test writes `results/external_fidelity_acceptance_self_test.{json,md}`. It uses a temporary synthetic high-fidelity fixture to prove the strict-ready path can pass, verifies the template/default path remains fail-closed, and confirms the real fidelity audit report is not overwritten. It is tooling coverage, not validation evidence.

Generate the blinded randomized collection packet:

```powershell
python scripts\build_external_blind_eval_plan.py
```

This writes `external_validation/blind_evaluation_protocol.md`, `external_validation/blinded_operator_sheet.csv`, `external_validation/method_alias_map.json`, and `results/external_blind_eval_audit.{json,md}`. The blinded sheet contains 1,440 alias-based rows with deterministic per-reset run order; the alias map should stay sealed until logs, videos, configs, checkpoints, implementation hashes, and the skill-library hash are frozen. This is anti-leakage scaffolding only, not evidence.

Then generate the operator-facing, non-evidence collection packet:

```powershell
python scripts\build_external_runbook.py
```

This writes `external_validation/collection_runbook.md`, `external_validation/operator_record_sheet.csv`, task cards under `external_validation/task_cards/`, config templates under `external_validation/config_templates/`, and `results/external_runbook_audit.{json,md}`. These files are collection scaffolding only; they do not replace real JSONL logs, videos, configs, checkpoints, or baseline implementations.

Audit the fail-closed external collection runner:

```powershell
python scripts\audit_external_runner_harness.py
```

This writes `results/external_runner_harness_audit.{json,md}` and checks the executable runner contract under `external_validation/runner/`. The runner can dry-run the blinded packet without writing logs, but actual collection requires a non-template backend module, real task configs, explicit alias unsealing, empty output logs unless `--force` is used, and later strict manifest/log/video validation. It is execution scaffolding only, not rollout evidence.

Audit actual collection readiness before starting robot or simulator runs:

```powershell
python scripts\audit_external_collection_readiness.py
python scripts\audit_external_collection_readiness.py --strict
```

This writes `results/external_collection_readiness_audit.{json,md}`. The non-strict form is a fail-closed status report; the strict form returns non-zero until the blinded sheet, alias map, non-template backend, real `external_validation/configs/*.json`, accepted fidelity audit, explicit alias unsealing, specific run id, and empty output logs are ready. It is not evidence; it prevents wasting an external run on an incomplete collection setup.

Generate the independent-baseline implementation contract:

```powershell
python scripts\build_external_baseline_contract.py
```

This writes `external_validation/baseline_implementation_contract.md`, `external_validation/baseline_implementation_matrix.csv`, method specs under `external_validation/baseline_specs/`, and `results/external_baseline_contract_audit.{json,md}`. The contract is not evidence; it states the adapter API, fairness invariants, and method-by-method implementation requirements that must be satisfied before strict external validation can pass.

Build the external method implementation packet:

```powershell
python scripts\build_external_method_implementation_packet.py
```

This writes `external_validation/method_implementation_packet.{json,md}`, `external_validation/method_implementation_work_orders.csv`, `external_validation/adapter_acceptance_fixtures.{json,md,csv}`, and `results/external_method_implementation_audit.{json,md}`. It turns every missing non-oracle baseline implementation into a concrete work order with required source/config/checkpoint hashes, log fields, and synthetic adapter acceptance fixtures. It is not evidence and still reports strict adapter evidence as missing until real manifest-declared implementations replace the scaffolds.

Generate executable adapter scaffolds from the method specs:

```powershell
python scripts\build_external_adapter_scaffolds.py
```

This writes `external_validation/baseline_adapter_scaffold.md`, scaffold directories under `external_validation/baselines/`, and `results/external_adapter_scaffold_audit.{json,md}`. These templates intentionally raise `NotImplementedError`; strict external validation treats scaffold-only adapters as missing implementations.

Generate executable reference adapters for the external harness:

```powershell
python scripts\build_external_reference_adapters.py
```

This writes `external_validation/reference_adapter_report.md`, per-method `adapter.py` files under `external_validation/baselines/`, and `results/external_reference_adapter_audit.{json,md}`. These adapters exercise the required API and reduce implementation ambiguity for an independent operator, but they are implementation-only artifacts. They are not rollout evidence and do not replace manifest-declared logs, videos, task configs, checkpoints, or recomputed metrics.

Generate a local dry run of the external JSONL schema:

```powershell
python scripts\build_external_local_dry_run.py
```

This writes `external_validation/local_dry_run/manifest.json`, schema-compatible logs under `external_validation/local_dry_run/logs/`, and `results/external_local_dry_run_metrics.{json,md}`. It converts frozen local CSV rows into the external logging format and recomputes the external-style metrics from those JSONL records. This is a plumbing/reproducibility check only. It is not real robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for `external_validation/manifest.json`.

Validate the adapter contract harness and scaffold structure:

```powershell
python scripts\validate_external_adapters.py
```

This writes `results/external_adapter_contract_audit.{json,md}`. It is not evidence; it checks that every non-oracle method has the required seam-model adapter shape: `initialize`, `propose`, `log`, `reset`, proposal fields for decision/risk/diagnosis/repair, and log fields including the policy or config hash.

Validate real manifest-declared adapter implementations with:

```powershell
python scripts\validate_external_adapters.py --strict
```

Strict adapter validation currently fails until `external_validation/manifest.json` points to real non-oracle implementations that replace the scaffold templates.

Test the strict adapter-evidence gate without creating evidence:

```powershell
python scripts\self_test_external_adapter_evidence.py
```

This writes `results/external_adapter_evidence_self_test.{json,md}`. It uses temporary manifest-declared adapters to prove the strict gate can pass when real-style implementations exist, and verifies missing manifests and scaffold templates remain fail-closed.

Use the manifest builder before strict validation. It does not fabricate evidence; in report-only mode it only scans the declared logs, videos, configs, and checkpoints and writes a readiness report:

```powershell
python scripts\build_external_collection_plan.py
python scripts\build_external_analysis_plan.py
python scripts\build_independent_validation_route.py
python scripts\build_external_platform_onboarding.py
python scripts\build_external_backend_integration_packet.py
python scripts\build_external_config_manifest_packet.py
python scripts\audit_external_fidelity_acceptance.py
python scripts\build_external_blind_eval_plan.py
python scripts\build_external_runbook.py
python scripts\audit_external_runner_harness.py
python scripts\audit_external_collection_readiness.py
python scripts\validate_external_configs.py
python scripts\self_test_external_config_evidence.py
python scripts\build_external_baseline_contract.py
python scripts\build_external_adapter_scaffolds.py
python scripts\build_external_reference_adapters.py
python scripts\build_external_local_dry_run.py
python scripts\validate_external_adapters.py
python scripts\build_external_method_implementation_packet.py
python scripts\self_test_external_adapter_evidence.py
python scripts\build_external_manifest.py --allow-missing
python scripts\audit_external_evidence_preflight.py
python scripts\audit_external_pairing_integrity.py
python scripts\build_external_blind_eval_plan.py
```

The preflight audit writes `results/external_evidence_preflight.{json,md}`. It is an operator-facing missing-evidence matrix over task logs, videos, configs, method implementations, checkpoint/config hashes, and expected JSONL record counts. It deliberately remains `not_external_evidence: true` and currently reports `evidence_ready: false` until a real `external_validation/manifest.json` and manifest-declared artifacts exist.

Audit the manifest-declared release package:

```powershell
python scripts\audit_external_release_package.py
```

This writes `results/external_release_package_audit.{json,md}`. It verifies that manifest-declared code, config, log, video, and checkpoint artifacts exist and match their SHA256 hashes, and it rejects local dry-run, template, scaffold, or placeholder artifacts. It remains `release_package_ready: false` until a real manifest exists.

Test the release-package hash gate without creating evidence:

```powershell
python scripts\self_test_external_release_package.py
```

This writes `results/external_release_package_self_test.{json,md}`. It creates temporary complete artifacts to prove the hash gate can pass, then checks that missing manifests and local-dry-run/template/scaffold/placeholder artifacts remain fail-closed.

Audit paired-reset and method-panel integrity:

```powershell
python scripts\audit_external_pairing_integrity.py
```

This writes `results/external_pairing_integrity_audit.{json,md}`. Before real evidence exists, it reports `pairing_ready: false` and is not evidence. With a real manifest, the strict form requires every paired reset to have a complete, duplicate-free panel over all declared methods, equal per-method counts, and consistent terminal samples, platform, and fixed-risk budget within each panel.

Test the paired-reset fairness gate without creating evidence:

```powershell
python scripts\self_test_external_pairing_integrity.py
```

This writes `results/external_pairing_integrity_self_test.{json,md}`. It creates temporary complete 1,440-record method panels to prove the gate can pass, then checks missing manifests, duplicate method rows, incomplete panels, and terminal-sample mismatches stay fail-closed.

After real or accepted high-fidelity artifacts exist, run:

```powershell
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\audit_external_collection_readiness.py --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_fidelity_acceptance.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_evidence.py --strict
```

The builder fills hashes for `config_path`, `checkpoint_or_config_path`, and scanned release artifacts under `external_validation/configs`, `external_validation/logs`, `external_validation/videos`, and `external_validation/checkpoints`. It also fills manifest metrics from raw JSONL logs when the logs are schema-valid. The output still must pass the rollout validator and evidence audit; a builder report is not evidence.

Required validation commands:

```powershell
python scripts\build_external_collection_plan.py
python scripts\build_external_analysis_plan.py
python scripts\build_external_platform_onboarding.py
python scripts\build_external_manifest.py --allow-missing
python scripts\build_independent_validation_route.py
python scripts\build_external_baseline_contract.py
python scripts\build_external_adapter_scaffolds.py
python scripts\build_external_reference_adapters.py
python scripts\build_external_local_dry_run.py
python scripts\audit_external_fidelity_acceptance.py
python scripts\build_external_blind_eval_plan.py
python scripts\audit_external_runner_harness.py
python scripts\audit_external_backend_contract.py
python scripts\build_external_backend_integration_packet.py
python scripts\build_external_config_manifest_packet.py
python scripts\audit_external_collection_readiness.py
python scripts\audit_external_release_package.py
python scripts\self_test_external_release_package.py
python scripts\audit_external_evidence_preflight.py
python scripts\audit_external_pairing_integrity.py
python scripts\self_test_external_pairing_integrity.py
python scripts\validate_external_adapters.py
python scripts\build_external_method_implementation_packet.py
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\self_test_external_backend_contract.py
python scripts\self_test_external_config_evidence.py
python scripts\self_test_external_adapter_evidence.py
python scripts\self_test_external_fidelity_acceptance.py
python scripts\self_test_external_release_package.py
python scripts\self_test_external_pairing_integrity.py
python scripts\self_test_external_rollout_validator.py
python scripts\self_test_external_evidence_pipeline.py
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_evidence.py --strict
```

The self-test uses temporary synthetic records only. It verifies the validator's metric recomputation and schema failure path, but it is not external evidence and must not be cited as validation.

The full-pipeline self-test also uses a temporary synthetic package only. It verifies that a complete manifest/config/log/video/checkpoint/implementation package can drive the strict audit to READY, then deletes the fixture and confirms the real repository evidence state is untouched. It is tooling coverage, not validation evidence.

The backend contract self-test uses temporary backend modules only. It verifies that strict backend qualification accepts a complete synthetic backend, rejects incomplete/template backends, and leaves the real backend audit report untouched. It is tooling coverage, not validation evidence.

The config evidence self-test uses temporary manifest-declared task configs only. It verifies that strict config evidence can become ready when all real-style config fields are supplied, rejects missing manifests and template configs, and leaves the real config evidence audit report untouched. It is tooling coverage, not validation evidence.

The fidelity acceptance self-test uses a temporary acceptance file and synthetic manifest data only. It verifies that strict platform/fidelity acceptance can become ready when all provenance fields are supplied, rejects the template/default path, and leaves the real fidelity audit report untouched. It is tooling coverage, not validation evidence.

The rollout validator recomputes the external success margin, utility margin, paired win rate, fixed-risk coverage, fixed-risk breach, and positive task-family count from raw JSONL records. The manifest metrics are therefore not accepted as evidence unless they are backed by episode logs with the seam prediction, diagnosis, decision, outcome, utility, video, and config/checkpoint hashes required by `log_schema_v1.json`. The evidence audit also blocks if manifest metrics disagree with the recomputed rollout metrics.

The pairing integrity audit is a separate fairness gate over the same raw logs. It blocks incomplete paired reset panels, duplicate method records, undeclared methods, unequal method counts, and within-reset mismatches in terminal samples, platform, or fixed-risk budget.

The release package audit is the hash-lock gate. It blocks stale or missing release artifacts, hash mismatches, local dry-run logs/videos, config templates, adapter scaffolds, and placeholder videos before any strict evidence claim can pass.

The collection readiness audit is the last pre-run gate. It blocks actual collection until the operator supplies a non-template backend, real task configs, accepted platform provenance, explicit alias unsealing, a specific run id, and empty output logs.
