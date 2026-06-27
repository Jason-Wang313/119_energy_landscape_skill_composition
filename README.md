# 119 Energy Landscape Skill Composition

Submission-hardening version: v5_expanded

Terminal decision: STRONG_REVISE for an ICLR-main-target robotics submission package.

This rebuild expands the paper into a 29-page, CPU-only, RAM-light submission package about local world/action models for skill seams: predicting whether action/skill composition will fail, diagnosing why, choosing repair/probe/abstain/transition, and writing the outcome back into future planning. The v5 method, `barrier_certified_energy_composer_v5`, instantiates that framing with barrier certification, basin-overlap posterior checks, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, diagnosis, planner-facing failure memory, and a fixed-risk acceptance screen. The package is stronger and more reviewer-ready than the earlier local scaffold, but it is still not ICLR-main ready because the evidence remains local and synthetic rather than real robot or independently accepted high-fidelity validation.

## Visible Contribution

Paper 119 is a local bridge toward an adaptive physical world/action model for skill seams: it scores whether two embodied skills can compose, explains likely failure modes, selects accept/repair/probe/abstain/transition actions at the seam, and records planner-facing memory for future attempts. Energy landscapes are the implementation vocabulary; the identity of the paper is the bounded skill-seam action model, not a full robot simulator or a low-level controller. The repository now makes that contribution visible through the generated manuscript, bounded claim ledger, mechanism/calibration/holdout/falsification audits, reproducible local experiments, a non-Haonan external validation packet, a guarded config materializer, an External config manifest packet for manifest-declared task-config evidence work orders, an External rollout evidence packet for raw JSONL/video/recompute work orders, an External analysis plan that locks hypotheses and exclusion policy before collection, an External platform probe that records machine/package/GPU/renderer/code/config provenance without counting as evidence, a ManiSkill task binding probe that maps the four task families to concrete public-simulator environment candidates, a ManiSkill env smoke probe that records construction/reset readiness and missing assets, an External platform onboarding packet for the primary public-simulator route, an External fidelity provenance packet for platform/contact/replay provenance work orders, an External backend integration packet for the public-simulator backend blocker, a ManiSkill reference backend readiness audit that contract-qualifies an adapter-backed backend candidate while official collection remains fail-closed, an External runner backend probe self-test for the real runner path, an External pilot smoke packet for quarantined first-panel backend testing, an External method implementation packet for non-oracle baseline work orders, a no-go external operator packet, an audited External operator handoff bundle, a fail-closed real-collection runner harness, and a separate Haonan/Yilun outreach package. The machine readiness audit currently reports `17/21` requirements satisfied; the remaining blockers are external-evidence blockers, not prose or packaging blockers.

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
- Predictive calibration audit: proposed hard-slice ECE10 `0.007207` vs strongest predecessor `0.014790`, max bin gap `0.012758`, risk-breach correlation `0.970670`, and monotone realized breach across 10 risk deciles locally.
- Holdout robustness audit: task-family `6/6`, seam-regime `7/7`, split `4/4`, task-regime `42/42`, and hash-fold `5/5` holdouts have positive local utility margins; worst task-regime success margin `0.021875`, utility margin `0.172559`.
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 documented failure cases.

## Reproduce

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_submission_artifacts.ps1
```

Use `-InstallDependencies` on the first run if the Python packages are not installed.

Canonical local PDF: `C:/Users/wangz/Downloads/119.pdf`

PDF SHA256: `92B00B24D439B892D5567ACA2E1D42D13AA15F754A20442D36892A6590D98C80`

PDF size: `467903` bytes.

PDF pages: `29`.

Artifact rule: keep the numbered PDF in Downloads only; do not copy it to the visible Desktop.

## Current Strengthening Docs

- Independent validation gate: `docs/independent_validation_protocol.md`
- Claim/evidence ledger: `docs/claim_evidence_ledger.json`
- Claim boundary audit: `results/claim_boundary_audit.md`
- Visible contribution audit: `results/visible_contribution_audit.md`
- Submission readiness gap audit: `results/submission_readiness_gap_audit.md`
- Local falsification audit: `results/local_falsification_audit.md`
- Holdout robustness audit: `results/holdout_robustness_audit.md`
- Diagnostic mechanism audit: `results/diagnostic_mechanism_audit.md`
- Decision-quality audit: `results/decision_quality_audit.md`
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
- ManiSkill task binding map: `external_validation/maniskill_task_bindings.json`
- External platform onboarding packet: `external_validation/platform_onboarding_packet.md`
- External platform onboarding audit: `results/external_platform_onboarding_audit.md`
- External fidelity provenance packet: `external_validation/fidelity_provenance_packet.md`
- External fidelity provenance audit: `results/external_fidelity_provenance_audit.md`
- External backend integration packet: `external_validation/backend_integration_packet.md`
- External backend integration audit: `results/external_backend_integration_audit.md`
- ManiSkill reference backend readiness audit: `results/maniskill_backend_readiness_audit.md`
- External runner backend probe self-test: `results/external_runner_backend_self_test.md`
- External pilot smoke packet: `external_validation/pilot_smoke_packet.md`
- External pilot smoke audit: `results/external_pilot_smoke_audit.md`
- External method implementation packet: `external_validation/method_implementation_packet.md`
- External method implementation audit: `results/external_method_implementation_audit.md`
- Independent validation route: `external_validation/independent_validation_route.md`
- Independent validation route audit: `results/independent_validation_route_audit.md`
- External fidelity acceptance template: `external_validation/fidelity_acceptance_template.json`
- External fidelity acceptance audit: `results/external_fidelity_acceptance_audit.md`
- External fidelity acceptance self-test: `results/external_fidelity_acceptance_self_test.md`
- External collection runbook: `external_validation/collection_runbook.md`
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
- External collection preflight self-test: `scripts/self_test_external_collection_preflight.py` checks a temporary complete preflight fixture only; it is not evidence.
- External task config schema: `external_validation/config_schema_v1.json`
- External real-config intake directory: `external_validation/configs/README.md`
- External config materialization plan: `results/external_config_materialization_plan.md`
- External config manifest packet: `external_validation/config_manifest_packet.md`
- External config manifest audit: `results/external_config_manifest_audit.md`
- External rollout evidence packet: `external_validation/rollout_evidence_packet.md`
- External rollout evidence audit: `results/external_rollout_evidence_audit.md`
- External config template audit: `results/external_config_template_audit.md`
- External config evidence self-test: `results/external_config_evidence_self_test.md`
- External baseline implementation contract: `external_validation/baseline_implementation_contract.md`
- External baseline implementation audit: `results/external_baseline_contract_audit.md`
- External baseline adapter scaffolds: `external_validation/baseline_adapter_scaffold.md`
- External adapter scaffold audit: `results/external_adapter_scaffold_audit.md`
- External reference adapter report: `external_validation/reference_adapter_report.md`
- External reference adapter audit: `results/external_reference_adapter_audit.md`
- External local dry-run manifest: `external_validation/local_dry_run/manifest.json`
- External local dry-run metrics: `results/external_local_dry_run_metrics.md`
- External adapter scaffold guard self-test: `scripts/self_test_external_adapter_scaffold_guard.py`
- External adapter contract audit: `results/external_adapter_contract_audit.md`
- Strict external adapter evidence audit: `results/external_adapter_contract_evidence_audit.md`
- External adapter evidence self-test: `results/external_adapter_evidence_self_test.md`
- External manifest builder report: `results/external_manifest_builder_report.md`
- External release package audit: `results/external_release_package_audit.md`
- External release package self-test: `results/external_release_package_self_test.md`
- External evidence preflight matrix: `results/external_evidence_preflight.md`
- External evidence acquisition packet: `results/external_acquisition_packet.md`
- External operator packet: `results/external_operator_packet.md`
- External operator handoff bundle: `results/external_operator_handoff_bundle.md`
- External evidence contract: `external_validation/manifest_template.json`
- External rollout log schema: `external_validation/log_schema_v1.json`
- External pairing integrity audit: `results/external_pairing_integrity_audit.md`
- External pairing integrity self-test: `results/external_pairing_integrity_self_test.md`
- External rollout validator self-test: `scripts/self_test_external_rollout_validator.py`
- External collection preflight self-test report: `results/external_collection_preflight_self_test.md`
- External full-pipeline evidence self-test: `scripts/self_test_external_evidence_pipeline.py` checks a temporary synthetic package only; it is not evidence.
- GitHub CI directly runs the backend, fidelity, config, adapter, release-package, pairing-integrity, rollout-validator, collection-preflight, runner-backend, and full-pipeline evidence self-tests.
- External evidence audit: `results/external_evidence_audit.md`
- External rollout metrics audit: `results/external_rollout_metrics.md`
- External execution readiness audit: `results/external_execution_readiness_audit.md`
- External platform qualification checklist: `external_validation/platform_qualification_checklist.md`
- Related-work coverage matrix: `docs/related_work_coverage_matrix.md`
- Haonan/Yilun outreach package: `docs/haonan_yilun_outreach_package.md`
- One-page outreach memo: `outreach/paper119_one_page_memo.pdf`
- Four-page technical preview: `outreach/paper119_four_page_preview.pdf`
- Submission audit: `docs/submission_readiness_audit_v5.md`
- Final audit: `docs/final_audit.md`
