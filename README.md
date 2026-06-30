# 119 Energy Landscape Skill Composition

Submission-hardening version: v5_expanded

Terminal decision: STRONG_REVISE for an ICLR-main-target robotics submission package.

This rebuild expands the paper into a 30-page, CPU-only, RAM-light submission package about local world/action models for skill seams: predicting whether action/skill composition will fail, diagnosing why, choosing repair/probe/abstain/transition, and writing the outcome back into future planning. The v5 method, `barrier_certified_energy_composer_v5`, instantiates that framing with barrier certification, basin-overlap posterior checks, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, diagnosis, planner-facing failure memory, and a fixed-risk acceptance screen. The independent-validation path now includes a ManiSkill fidelity metadata probe that records simulator timing, backend, controller, observation, and asset metadata for operator review, a ManiSkill render-video preflight with explicit render-backend/shader controls, a renderer-failure classifier, render/pilot progress markers with failure-stage and terminal-stage render diagnostics, a timeout diagnosis retest, a renderer profile matrix over `cpu/minimal`, `gpu/minimal`, and `sapien_cuda/minimal`, and a render resource sweep showing the descriptor-pool failure persists even at `16x16` across the same renderer profiles; these separate render-backed RGB MP4 readiness from diagnostic fallback videos. The path also includes a ManiSkill render machine qualification packet, a ManiSkill render machine qualification self-test (`results/maniskill_render_machine_qualification_self_test.md`) that proves synthetic ready/fail/fallback/missing-env states are classified correctly without touching real reports, and a render failure remediation packet that together keep the exact collection machine fail-closed until platform probing, render-backed MP4 preflight, pilot liveness, and zero diagnostic fallback videos pass, plus a bounded ManiSkill pilot runtime liveness audit and reset-timeout triage sidecar with backend reset substage markers that currently mark the local CPU/render pilot path not ready while explicitly tracking timeout progress, the active row/config/method/env that timed out, the backend substage that was reached, and whether a diagnostic sidecar rejected before JSONL write was stopped by the official video guard. The package is stronger and more reviewer-ready than the earlier local scaffold, but it is still not ICLR-main ready because the evidence remains local and synthetic rather than real robot or independently accepted high-fidelity validation.

## Visible Contribution

Paper 119 is a local bridge toward an adaptive physical world/action model for skill seams: it scores whether two embodied skills can compose, explains likely failure modes, selects accept/repair/probe/abstain/transition actions at the seam, and records planner-facing memory for future attempts. Energy landscapes are the implementation vocabulary; the identity of the paper is the bounded skill-seam action model, not a full robot simulator or a low-level controller. The repository now makes that contribution visible through the generated manuscript, bounded claim ledger, mechanism/calibration/holdout/falsification audits, a Planner-edge policy audit for future transition selection, a Failure-memory adaptation audit for observed-to-held-out planner memory, a Local model release card that hash-locks the deterministic v5 seam-model source, method parameters, result artifacts, and reference-adapter hashes while explicitly not being a trained robot policy checkpoint or external evidence, reproducible local experiments, a non-Haonan external validation packet, a guarded config materializer, an External config manifest packet for manifest-declared task-config evidence work orders, a strict config evidence hash gate for manifest-declared task configs, an External rollout evidence packet for raw JSONL/video/recompute work orders, a strict MP4 video evidence gate for rejecting placeholder, diagnostic, staged, or backup/internal video paths under strict rollout validation, an External ablation collection packet for manifest-declared ablation work orders, an External evidence intake ledger for strict evidence failure closure, an External precollection manifest draft that pre-fills prepared task-config hashes and cutover commands while keeping the official manifest absent, an External precollection freeze receipt that hash-locks the operator sheet, alias map, prepared configs, method cutover checklist, manifest draft, runner files, source audits, current commit, and skill-library hash before official JSONL/video collection while keeping strict external evidence false, an External precollection freeze receipt self-test that exercises a temporary complete freeze and missing-backend/run-id/lock/checkout failures without touching the real receipt, an External analysis plan that locks hypotheses, confidence-gated external rollout statistics, and exclusion policy before collection, an External platform probe that records machine/package/GPU/renderer/code/config provenance without counting as evidence, a ManiSkill task binding probe that maps the four task families to concrete public-simulator environment candidates, a ManiSkill env smoke probe showing all four primary bound candidates now construct/reset locally while support candidates explicitly require `oakink-v2` and `ycb` assets, a ManiSkill fidelity metadata probe that pre-fills timing/backend/controller/observation/asset metadata for fidelity review, an External platform onboarding packet for the primary public-simulator route, an External fidelity provenance packet for platform/contact/replay provenance work orders, an External fidelity acceptance draft with a strict fidelity acceptance provenance gate and a fidelity acceptance promotion checklist that separates machine-prefilled fields from independent operator signoff while keeping acceptance false, a Fidelity acceptance materialization plan that only writes the real acceptance file after explicit independent-operator, real-platform, render-backed-video, real-rollout, manifest, commit, and skill-hash confirmations, an External backend integration packet for the public-simulator backend blocker, a ManiSkill reference backend readiness audit that contract-qualifies an adapter-backed backend candidate and MP4 writer path while proving state-shaped arrays cannot masquerade as render videos and official collection remains fail-closed, explicit render-backend/shader controls, a ManiSkill reference collection preflight audit and collection-readiness tracked reference route that show the explicit backend/config/run-id/alias path now reaches the single fidelity-acceptance gate, an External runner backend probe self-test for the real runner path, an official video write guard that rejects diagnostic fallback, non-MP4-like, undersized, out-of-dir, or unexpected video paths before an official JSONL row is written, an official JSONL write guard that rejects schema-invalid rollout records before append using the same strict rollout validator used after manifest assembly, atomic official evidence promotion that preserves prior official videos/logs if a selected batch fails, an External pilot smoke packet for quarantined first-panel backend testing, a ManiSkill render-video preflight with a renderer-failure classifier, failure-stage diagnostics, timeout diagnosis retest, and renderer profile matrix plus a render resource sweep that records 16x16 descriptor-pool failure persistence separately from diagnostic fallback videos, a ManiSkill render machine qualification packet and render failure remediation packet for the exact collection machine, a ManiSkill pilot runtime liveness audit and reset-timeout triage sidecar with backend reset substage markers that record local timeout progress, the active task/config/method/env at `reset_scene_start`, the last backend substage reached, and whether a diagnostic sidecar rejected before JSONL write was stopped by the official video guard before any complete quarantined pilot row/video is promoted, an External method implementation packet for non-oracle baseline work orders, an External method config materialization plan that writes candidate config artifacts and hashes for all non-oracle methods while keeping them non-evidence until independent implementation provenance, manifest declaration, and raw rollout logs bind to those hashes, a reference-adapter provenance catalog that hash-lists every non-oracle interface adapter without counting it as evidence, a method manifest cutover checklist for the exact `manifest.methods[]` fields and fairness/hash bindings, a strict reference-adapter rejection gate, a strict independent method provenance gate, a strict checkpoint/config artifact gate, a strict fairness-contract binding gate, a manifest assembly checklist and strict manifest promotion gate that map every real-manifest field to current file/hash state before official manifest writing, an External manifest builder self-test that exercises temporary manifest writing from raw JSONL/video/config/method fixtures and rejects partial method manifests, a release-package internal-artifact rejection gate that rejects local-dry-run, template, scaffold, placeholder, staged, backup, diagnostic, fallback, empty-video-directory, and non-MP4-like log/video artifacts from hash-locked release evidence, a strict config evidence self-test that binds prepared task configs in a temporary strict manifest, a strict adapter evidence gate that binds tracked candidate method configs in a temporary strict manifest, rejects partial non-oracle manifests, scaffold/reference adapters, leaky method provenance, implementation-source hashes masquerading as checkpoint/config artifacts, unmatched fairness-contract ids/hashes, unmatched method provenance hashes, and JSONL `policy_or_config_hash` mismatches, a no-go external operator packet that exposes the tracked ManiSkill reference route with exact commands and the single route-specific fidelity-acceptance blocker, an External collection job packet that orders platform/render qualification, guarded fidelity acceptance, strict readiness, official collection, postcollection sealing, manifest promotion, and final strict evidence audits behind Windows/Linux confirmation-guarded command spines, an External collection machine bootstrap that runs only platform/task/env/fidelity-metadata/render/pilot/qualification probes on an independent GPU/Vulkan machine before acceptance or collection, an External collection runbook route-gate audit that carries 47 validation commands, the current ManiSkill route gates, and the actual high-fidelity collection command template in preflight-before-collection order, an audited External operator handoff bundle, an External operator release bundle that recomputes the handoff hashes and can create a deterministic transfer archive only through `--write-archive` while excluding real evidence paths, a fail-closed real-collection runner harness, and a separate Haonan/Yilun outreach package. The machine readiness audit currently reports `17/21` requirements satisfied; the remaining blockers are external-evidence blockers, not prose or packaging blockers.

Reviewer response packet: `docs/reviewer_response_packet.md` maps hostile reviewer objections to exact local evidence, allowed claims, remaining gates, and one-paper Haonan/Yilun outreach guidance while preserving the `STRONG_REVISE` boundary.

External evidence closure brief: `docs/external_evidence_closure_brief.md` and `results/external_evidence_closure_brief.md` compress the four remaining blockers into a minimum independent proof package plus chronological strict command spine; the External evidence closure brief self-test keeps it fail-closed against fifth-blocker drift, premature manifests, missing Linux command spines, Haonan-dependent route drift, and missing source packets.

Latest evidence-integrity hardening: the strict fidelity acceptance provenance gate now rejects real acceptance files that skip guarded materialization, omit `acceptance_ready=true`, use non-SHA collection commits, omit ISO-like lock dates, or lack operator confirmation booleans, while still keeping strict fidelity/external evidence false until real manifest/log/video gates pass; the fidelity materializer checkout self-test now verifies the temporary clean-checkout write path plus stale-commit, mismatched-hash, dirty-checkout, cache-file, and real-acceptance-untouched guards; the fidelity acceptance materializer requires the operator-supplied collection commit and cache-independent skill-library hash to match the current clean checkout before writing the real acceptance file, the strict full-method coverage gate rejects manifests that omit required external methods, the strict rollout sample-count gate rejects underdeclared episode counts or per-task/per-method record-count mismatches, the strict paired-panel gate rejects duplicate or incomplete method panels within paired resets, the strict rollout uniqueness gate rejects duplicate episode identities or reused rollout videos, the confidence-gated external rollout statistics gate requires 95% bootstrap confidence bounds for primary external metrics to clear the predeclared thresholds, the final rollout confidence summary gate makes the final external evidence audit reject passed rollout metrics unless the embedded `external_statistical_confidence_v1` summary clears all primary confidence gates, the strict config evidence hash gate rejects manifest-declared task configs when `config_hash` is missing, malformed, or mismatched with `config_path`, the strict checkpoint/config artifact gate rejects method manifests whose `checkpoint_or_config_hash` is backed only by implementation source rather than a real `checkpoint_or_config_path`, the strict fairness-contract binding gate rejects manifests whose per-method provenance does not match the manifest-declared skill-library, observation-interface, compute-budget, and paired-reset contract ids/hashes, and the strict task-config hash gate and strict policy/config hash gate reject raw JSONL rollout rows whose task fields disagree with the manifest-declared config hash or whose `policy_or_config_hash` disagrees with the manifest-declared method `checkpoint_or_config_hash`.

final rollout confidence summary gate: the final external evidence audit now requires the strict rollout validator's embedded confidence summary, including all five primary metric gates and the positive-task-family gate, so a stale or edited `results/external_rollout_metrics.json` cannot pass by setting `passed=true` alone.

final release artifact hash recomputation gate: the final external evidence audit now recomputes SHA256 values for manifest-declared code, config, log, video, and checkpoint release artifacts, so a stale release artifact hash cannot pass even if it is SHA-shaped.

## Evidence Snapshot

- Design: 6 task families x 8 seam regimes x 5 deployment splits x 12 methods x 10 paired seeds, with 230,400 main episode cells.
- Strongest non-oracle baseline: `proposed_energy_landscape_composer_v4_1`.
- Hard aggregate success: proposed `0.801711` vs strongest baseline `0.717113`; margin `0.084598`, with `10/10` paired-seed wins.
- Hard aggregate utility: proposed `0.888270` vs strongest baseline `0.653100`; margin `0.235170`, with `10/10` paired-seed wins.
- Mechanism deltas vs strongest baseline: seam failure `-0.049123`, barrier violation `-0.040869`, basin alignment `+0.080008`, descent continuity `+0.078090`.
- Risk/cost deltas: damage `-0.005790`, composition cost `-0.045838`, energy-model error `-0.014417`, risk calibration error `-0.010549`, realized seam breach `-0.075646`.
- Best ablation gaps: success `0.028125`, utility `0.043490`.
- Stress endpoint margins: success `0.103125`, utility `0.264045`.
- Fixed-risk audit at risk budget `0.15`: coverage `0.863021`, breach `0.000302`, gated success `0.760108`, utility margin `1.787443`.
- Diagnostic mechanism audit: zero label, decision, and planner-update mismatches over 230,400 local rows; all five failure labels and all five seam decisions appear in 13,440 proposed hard rows.
- Decision-quality audit: accept coverage `0.404` vs `0.000`; accepted-seam breach above the `0.15` budget rate `0.000`; 3,850 recovered accepts improve utility by `0.243`, success by `0.091`, and realized breach by `-0.077` locally.
- Planner-edge policy audit: across 1,680 local hard-slice planning frontiers, selected-edge utility improves by `+0.231`, success by `+0.080`, realized breach by `-0.075`, and executable-edge coverage by `+0.502` versus the strongest predecessor; this is still non-external evidence.
- Failure-memory adaptation audit: 2,210 observed-to-held-out signature pairs over 1,667 local hard-slice frontiers show early seam memory predicts later breach with correlation `0.957`, high-memory-risk signatures have held-out breach `0.120` vs `0.074`, and v5 lowers predecessor high-memory-risk future breach by `0.083`; this is still non-external evidence.
- Predictive calibration audit: proposed hard-slice ECE10 `0.007207` vs strongest predecessor `0.014790`, max bin gap `0.012758`, risk-breach correlation `0.970670`, and monotone realized breach across 10 risk deciles locally.
- Holdout robustness audit: task-family `6/6`, seam-regime `7/7`, split `4/4`, task-regime `42/42`, and hash-fold `5/5` holdouts have positive local utility margins; worst task-regime success margin `0.021875`, utility margin `0.172559`.
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 documented failure cases.

## Reproduce

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_submission_artifacts.ps1
```

Use `-InstallDependencies` on the first run if the Python packages are not installed.

Canonical local PDF: `C:/Users/wangz/Downloads/119.pdf`

PDF SHA256: `AE310705B235339B73987C6E2DBD31439C50F78ADD364D5593302A9733D83A5B`

PDF size: `469674` bytes.

PDF pages: `30`.

Artifact rule: keep the numbered PDF in Downloads only; do not copy it to the visible Desktop.

## Current Strengthening Docs

- Independent validation gate: `docs/independent_validation_protocol.md`
- Claim/evidence ledger: `docs/claim_evidence_ledger.json`
- Claim boundary audit: `results/claim_boundary_audit.md`
- Visible contribution audit: `results/visible_contribution_audit.md`
- Submission readiness gap audit: `results/submission_readiness_gap_audit.md`
- Reviewer response packet: `docs/reviewer_response_packet.md`
- External evidence closure brief: `docs/external_evidence_closure_brief.md`
- External evidence closure brief self-test: `results/external_evidence_closure_brief_self_test.md`
- Local falsification audit: `results/local_falsification_audit.md`
- Holdout robustness audit: `results/holdout_robustness_audit.md`
- Diagnostic mechanism audit: `results/diagnostic_mechanism_audit.md`
- Decision-quality audit: `results/decision_quality_audit.md`
- Planner-edge policy audit: `results/planner_edge_policy_audit.md`
- Failure-memory adaptation audit: `results/failure_memory_adaptation_audit.md`
- Local model release card: `docs/local_model_release.md`
- Local model release audit: `results/local_model_release_audit.md`
- Predictive calibration audit: `results/seam_prediction_calibration_audit.md`
- Manuscript number audit: `results/manuscript_number_audit.md`
- Related-work audit: `results/related_work_audit.md`
- Reference integrity audit: `results/reference_integrity_audit.md`
- Manuscript readability/framing audit: `results/manuscript_readability_audit.md`
- Presentation quality audit: `results/presentation_quality_audit.md`
- Figure readability audit: `results/figure_readability_audit.md`
- Camera-ready design audit: `results/camera_ready_design_audit.md`
- Full local build script: `scripts/build_submission_artifacts.ps1`
- GitHub validation workflow: `.github/workflows/paper119-validation.yml`
- External collection plan: `results/external_collection_plan.md`
- External analysis plan: `external_validation/statistical_analysis_plan.md`
- External analysis plan audit: `results/external_analysis_plan_audit.md`
- External platform probe: `results/external_platform_probe.md`
- ManiSkill task binding probe: `results/maniskill_task_binding_probe.md`
- ManiSkill env smoke probe: `results/maniskill_env_smoke_probe.md`
- ManiSkill fidelity metadata probe: `results/maniskill_fidelity_metadata_probe.md`
- ManiSkill task binding map: `external_validation/maniskill_task_bindings.json`
- External platform onboarding packet: `external_validation/platform_onboarding_packet.md`
- External platform onboarding audit: `results/external_platform_onboarding_audit.md`
- External fidelity provenance packet: `external_validation/fidelity_provenance_packet.md`
- External fidelity provenance audit: `results/external_fidelity_provenance_audit.md`
- External fidelity provenance packet self-test: `results/external_fidelity_provenance_packet_self_test.md`
- External fidelity acceptance draft: `external_validation/fidelity_acceptance_draft.md`
- External fidelity acceptance draft audit: `results/external_fidelity_acceptance_draft_audit.md`
- Fidelity acceptance materialization plan: `results/fidelity_acceptance_materialization_plan.md`
- fidelity materializer checkout self-test: `results/fidelity_acceptance_materializer_self_test.md`
- External backend integration packet: `external_validation/backend_integration_packet.md`
- External backend integration audit: `results/external_backend_integration_audit.md`
- External backend integration packet self-test: `results/external_backend_integration_packet_self_test.md`
- ManiSkill reference backend readiness audit: `results/maniskill_backend_readiness_audit.md`
- ManiSkill reference collection preflight audit: `results/maniskill_reference_collection_preflight_audit.md`
- External runner backend probe self-test: `results/external_runner_backend_self_test.md`
- External pilot smoke packet: `external_validation/pilot_smoke_packet.md`
- External pilot smoke audit: `results/external_pilot_smoke_audit.md`
- ManiSkill render-video preflight: `results/maniskill_render_video_preflight_audit.md`
- ManiSkill render resource sweep: `results/maniskill_render_resource_sweep.md`
- ManiSkill render machine qualification packet: `results/maniskill_render_machine_qualification.md`
- ManiSkill render machine qualification self-test: `results/maniskill_render_machine_qualification_self_test.md`
- ManiSkill render failure remediation packet: `results/maniskill_render_failure_remediation.md`
- ManiSkill pilot runtime liveness audit: `results/maniskill_pilot_runtime_liveness_audit.md`
- ManiSkill pilot reset-timeout triage sidecar: `results/maniskill_pilot_reset_timeout_triage.md`
- External method implementation packet: `external_validation/method_implementation_packet.md`
- External method config materialization plan: `external_validation/method_config_materialization_plan.md`
- External method config candidates: `external_validation/method_config_candidates.csv`
- Adapter acceptance fixtures: `external_validation/adapter_acceptance_fixtures.md`
- External method implementation audit: `results/external_method_implementation_audit.md`
- External method implementation packet self-test: `results/external_method_implementation_packet_self_test.md`
- External method config materialization audit: `results/external_method_config_materialization_audit.md`
- External method config materialization self-test: `results/external_method_config_materialization_self_test.md`
- External method reference provenance: `external_validation/method_reference_provenance.csv`
- Method manifest cutover checklist: `external_validation/method_manifest_cutover_checklist.md`
- Independent validation route: `external_validation/independent_validation_route.md`
- Independent validation route audit: `results/independent_validation_route_audit.md`
- External fidelity acceptance template: `external_validation/fidelity_acceptance_template.json`
- External fidelity acceptance audit: `results/external_fidelity_acceptance_audit.md`
- External fidelity acceptance self-test: `results/external_fidelity_acceptance_self_test.md`
- External collection runbook: `external_validation/collection_runbook.md`
- External collection runbook command count: 47 validation commands
- External operator record sheet: `external_validation/operator_record_sheet.csv`
- External blinded evaluation protocol: `external_validation/blind_evaluation_protocol.md`
- External blinded operator sheet: `external_validation/blinded_operator_sheet.csv`
- External blind evaluation audit: `results/external_blind_eval_audit.md`
- External runbook audit: `results/external_runbook_audit.md`
- External collection runner harness: `external_validation/runner/README.md`
- External runner harness audit: `results/external_runner_harness_audit.md`
- External backend contract audit: `results/external_backend_contract_audit.md`
- External backend contract self-test: `results/external_backend_contract_self_test.md`
- External collection readiness audit: `results/external_collection_readiness_audit.md`
- External collection preflight self-test: `scripts/self_test_external_collection_preflight.py` checks a temporary complete preflight fixture and proves the tracked ManiSkill reference route becomes collection-ready once a temporary accepted-fidelity audit is supplied; it is not evidence.
- External task config schema: `external_validation/config_schema_v1.json`
- External real-config intake directory: `external_validation/configs/README.md`
- External config materialization plan: `results/external_config_materialization_plan.md`
- External config materialization self-test: `results/external_config_materialization_self_test.md`
- External config manifest packet: `external_validation/config_manifest_packet.md`
- External config manifest audit: `results/external_config_manifest_audit.md`
- External config manifest packet self-test: `results/external_config_manifest_packet_self_test.md`
- External rollout evidence packet: `external_validation/rollout_evidence_packet.md`
- External rollout evidence audit: `results/external_rollout_evidence_audit.md`
- External rollout evidence packet self-test: `results/external_rollout_evidence_packet_self_test.md`
- Strict MP4 video evidence gate: `scripts/validate_external_rollouts.py`
- External ablation collection packet: `external_validation/ablation_collection_packet.md`
- External ablation collection audit: `results/external_ablation_collection_audit.md`
- External ablation collection packet self-test: `results/external_ablation_collection_packet_self_test.md`
- External evidence intake ledger: `external_validation/evidence_intake_ledger.md`
- External evidence intake audit: `results/external_evidence_intake_ledger_audit.md`
- External evidence intake ledger self-test: `results/external_evidence_intake_ledger_self_test.md`
- External precollection manifest draft: `external_validation/manifest_precollection_draft.md`
- External precollection manifest draft candidate method-config hash bindings: `external_validation/manifest_precollection_draft.md`
- External precollection manifest draft audit: `results/external_precollection_manifest_draft_audit.md`
- External precollection manifest draft self-test: `results/external_precollection_manifest_draft_self_test.md`
- External precollection freeze receipt: `external_validation/precollection_freeze_receipt.md`
- External precollection freeze receipt audit: `results/external_precollection_freeze_receipt_audit.md`
- External precollection freeze receipt candidate method-config hash locks: `external_validation/precollection_freeze_receipt.csv` now includes all 11 non-oracle candidate method-config JSON hashes while keeping them non-evidence.
- External precollection freeze receipt self-test: `results/external_precollection_freeze_receipt_self_test.md`
- External postcollection evidence seal: `external_validation/postcollection_evidence_seal.md`
- External postcollection evidence seal audit: `results/external_postcollection_evidence_seal_audit.md`
- External postcollection evidence seal self-test: `results/external_postcollection_evidence_seal_self_test.md`
- External postcollection seal consistency gate: `results/external_postcollection_seal_consistency_audit.md`
- External postcollection seal consistency self-test: `results/external_postcollection_seal_consistency_self_test.md`
- External config template audit: `results/external_config_template_audit.md`
- External config evidence self-test: `results/external_config_evidence_self_test.md`
- External baseline implementation contract: `external_validation/baseline_implementation_contract.md`
- External baseline implementation audit: `results/external_baseline_contract_audit.md`
- External baseline contract self-test: `results/external_baseline_contract_self_test.md`
- External baseline adapter scaffolds: `external_validation/baseline_adapter_scaffold.md`
- External adapter scaffold audit: `results/external_adapter_scaffold_audit.md`
- External reference adapter report: `external_validation/reference_adapter_report.md`
- External reference adapter audit: `results/external_reference_adapter_audit.md`
- External local dry-run manifest: `external_validation/local_dry_run/manifest.json`
- External local dry-run metrics: `results/external_local_dry_run_metrics.md`
- External adapter scaffold guard self-test: `results/external_adapter_scaffold_guard_self_test.md` proves scaffold-only adapter directories/templates are rejected while ordinary replacement adapter files are not falsely rejected; it is not evidence.
- External adapter contract audit: `results/external_adapter_contract_audit.md`
- Strict external adapter evidence audit: `results/external_adapter_contract_evidence_audit.md`
- External adapter evidence self-test: `results/external_adapter_evidence_self_test.md`
- External manifest builder report: `results/external_manifest_builder_report.md`
- External manifest assembly checklist: `external_validation/manifest_assembly_checklist.csv`
- External manifest builder self-test: `results/external_manifest_builder_self_test.md`
- External release package audit: `results/external_release_package_audit.md`
- External release package self-test: `results/external_release_package_self_test.md`
- External evidence preflight matrix: `results/external_evidence_preflight.md`
- External evidence preflight self-test: `results/external_evidence_preflight_self_test.md`
- External evidence acquisition packet: `results/external_acquisition_packet.md`
- External acquisition packet self-test: `results/external_acquisition_packet_self_test.md`
- External operator packet: `results/external_operator_packet.md`
- External collection job packet: `external_validation/collection_job_packet.md`
- External collection job command spines: `external_validation/collection_job_commands.ps1`, `external_validation/collection_job_commands.sh`
- External collection job packet audit: `results/external_collection_job_packet_audit.md`
- External collection job packet self-test: `results/external_collection_job_packet_self_test.md`
- External collection machine bootstrap: `external_validation/collection_machine_bootstrap.md` (`collection_machine_bootstrap.ps1` and `collection_machine_bootstrap.sh`)
- External collection machine bootstrap audit: `results/external_collection_machine_bootstrap_audit.md`
- External collection machine bootstrap self-test: `results/external_collection_machine_bootstrap_self_test.md`
- External operator handoff bundle: `results/external_operator_handoff_bundle.md`
- External operator handoff bundle self-test: `results/external_operator_handoff_bundle_self_test.md`
- External operator release bundle: `results/external_operator_release_bundle_plan.md`
- External operator release bundle self-test: `results/external_operator_release_bundle_self_test.md`
- External operator release manifest: `external_validation/operator_release_bundle_manifest.csv`
- External evidence contract: `external_validation/manifest_template.json`
- External rollout log schema: `external_validation/log_schema_v1.json`
- External pairing integrity audit: `results/external_pairing_integrity_audit.md`
- External pairing integrity self-test: `results/external_pairing_integrity_self_test.md`
- External rollout validator self-test: `results/external_rollout_validator_self_test.md` proves the strict raw-log metric, confidence, paired-panel, task-config, method-hash, and MP4 evidence gates on temporary fixtures only; it is not evidence.
- External collection preflight self-test report: `results/external_collection_preflight_self_test.md`
- External full-pipeline evidence self-test: `results/external_evidence_pipeline_self_test.md` checks a temporary complete package only, binds the prepared task configs and tracked candidate method configs into that package, and verifies tampered rollout confidence-summary and release-hash rejection; it is not evidence.
- GitHub CI directly runs the backend, fidelity, precollection freeze receipt, postcollection evidence seal, postcollection seal consistency, config, adapter, release-package, pairing-integrity, rollout-validator, collection-preflight, runner-backend, and full-pipeline evidence self-tests.
- External evidence audit: `results/external_evidence_audit.md`
- External rollout metrics audit: `results/external_rollout_metrics.md`
- External execution readiness audit: `results/external_execution_readiness_audit.md`
- External execution readiness self-test: `results/external_execution_readiness_self_test.md`
- External platform qualification checklist: `external_validation/platform_qualification_checklist.md`
- Related-work coverage matrix: `docs/related_work_coverage_matrix.md`
- Haonan/Yilun outreach package: `docs/haonan_yilun_outreach_package.md`
- One-page outreach memo: `outreach/paper119_one_page_memo.pdf`
- Four-page technical preview: `outreach/paper119_four_page_preview.pdf`
- Submission audit: `docs/submission_readiness_audit_v5.md`
- Final audit: `docs/final_audit.md`
