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

Build the independent operator packet:

```powershell
python scripts\build_external_operator_packet.py
```

This writes `results/external_operator_packet.{json,md}` with the current go/no-go state, remaining pre-collection blockers, exact collection command, and post-collection strict gates. It is not external evidence; it currently says `DO_NOT_COLLECT_YET` until the strict collection preflight passes with real backend, configs, fidelity acceptance, alias unsealing, and a specific run id.

## Manifest Builder Workflow

Before collecting rollouts, generate the non-evidence collection schedule:

```powershell
python scripts\build_external_collection_plan.py
```

This writes `results/external_collection_plan.{json,md}`. It enumerates the paired reset slots, task families, methods, expected JSONL record count, required log fields, and strict validation commands. It is a plan only; it is not evidence and cannot satisfy the external gate.

Generate the non-Haonan independent validation route:

```powershell
python scripts\build_independent_validation_route.py
```

This writes `external_validation/independent_validation_route.md`, `external_validation/independent_validation_route_matrix.csv`, and `results/independent_validation_route_audit.{json,md}`. It names a primary public-simulator route, secondary cross-engine routes, and a third-party robot-lab route for collecting the missing manifest-backed logs, videos, configs, platform provenance, and independent baseline implementations. It is route planning only, not evidence.

Then audit the platform-fidelity acceptance contract:

```powershell
python scripts\audit_external_fidelity_acceptance.py
```

This writes `results/external_fidelity_acceptance_audit.{json,md}` and checks `external_validation/fidelity_acceptance_template.json`. It defines the minimum provenance required before a real robot or high-fidelity simulator route is credible: platform version, physics/contact details, replayable paired resets, state/camera/contact signals, operator independence, real or benchmark calibration basis, code commit, skill-library hash, and acceptance gates. It is not rollout evidence and currently reports `acceptance_ready: false` until `external_validation/fidelity_acceptance.json`, `external_validation/manifest.json`, and the real artifacts exist.

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

Use the manifest builder before strict validation. It does not fabricate evidence; in report-only mode it only scans the declared logs, videos, configs, and checkpoints and writes a readiness report:

```powershell
python scripts\build_external_collection_plan.py
python scripts\build_independent_validation_route.py
python scripts\audit_external_fidelity_acceptance.py
python scripts\build_external_blind_eval_plan.py
python scripts\build_external_runbook.py
python scripts\audit_external_runner_harness.py
python scripts\audit_external_collection_readiness.py
python scripts\validate_external_configs.py
python scripts\build_external_baseline_contract.py
python scripts\build_external_adapter_scaffolds.py
python scripts\build_external_reference_adapters.py
python scripts\build_external_local_dry_run.py
python scripts\validate_external_adapters.py
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

Audit paired-reset and method-panel integrity:

```powershell
python scripts\audit_external_pairing_integrity.py
```

This writes `results/external_pairing_integrity_audit.{json,md}`. Before real evidence exists, it reports `pairing_ready: false` and is not evidence. With a real manifest, the strict form requires every paired reset to have a complete, duplicate-free panel over all declared methods, equal per-method counts, and consistent terminal samples, platform, and fixed-risk budget within each panel.

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
python scripts\build_external_manifest.py --allow-missing
python scripts\build_independent_validation_route.py
python scripts\build_external_baseline_contract.py
python scripts\build_external_adapter_scaffolds.py
python scripts\build_external_reference_adapters.py
python scripts\build_external_local_dry_run.py
python scripts\audit_external_fidelity_acceptance.py
python scripts\build_external_blind_eval_plan.py
python scripts\audit_external_runner_harness.py
python scripts\audit_external_collection_readiness.py
python scripts\audit_external_release_package.py
python scripts\audit_external_evidence_preflight.py
python scripts\audit_external_pairing_integrity.py
python scripts\validate_external_adapters.py
python scripts\validate_external_configs.py --strict
python scripts\validate_external_adapters.py --strict
python scripts\self_test_external_rollout_validator.py
python scripts\self_test_external_evidence_pipeline.py
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_release_package.py --strict
python scripts\audit_external_pairing_integrity.py --strict
python scripts\audit_external_evidence.py --strict
```

The self-test uses temporary synthetic records only. It verifies the validator's metric recomputation and schema failure path, but it is not external evidence and must not be cited as validation.

The full-pipeline self-test also uses a temporary synthetic package only. It verifies that a complete manifest/config/log/video/checkpoint/implementation package can drive the strict audit to READY, then deletes the fixture and confirms the real repository evidence state is untouched. It is tooling coverage, not validation evidence.

The rollout validator recomputes the external success margin, utility margin, paired win rate, fixed-risk coverage, fixed-risk breach, and positive task-family count from raw JSONL records. The manifest metrics are therefore not accepted as evidence unless they are backed by episode logs with the seam prediction, diagnosis, decision, outcome, utility, video, and config/checkpoint hashes required by `log_schema_v1.json`. The evidence audit also blocks if manifest metrics disagree with the recomputed rollout metrics.

The pairing integrity audit is a separate fairness gate over the same raw logs. It blocks incomplete paired reset panels, duplicate method records, undeclared methods, unequal method counts, and within-reset mismatches in terminal samples, platform, or fixed-risk budget.

The release package audit is the hash-lock gate. It blocks stale or missing release artifacts, hash mismatches, local dry-run logs/videos, config templates, adapter scaffolds, and placeholder videos before any strict evidence claim can pass.

The collection readiness audit is the last pre-run gate. It blocks actual collection until the operator supplies a non-template backend, real task configs, accepted platform provenance, explicit alias unsealing, a specific run id, and empty output logs.
