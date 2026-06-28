# 119 Energy Landscape Skill Composition

Submission-hardening version: v5_expanded

Terminal decision: STRONG_REVISE for an ICLR-main-target robotics submission package.

This rebuild expands the paper into a 30-page, CPU-only, RAM-light submission package about local world/action models for skill seams: predicting whether action/skill composition will fail, diagnosing why, choosing repair/probe/abstain/transition, and writing the outcome back into future planning. The v5 method, `barrier_certified_energy_composer_v5`, instantiates that framing with barrier certification, basin-overlap posterior checks, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, diagnosis, planner-facing failure memory, and a fixed-risk acceptance screen. The independent-validation path now includes a ManiSkill fidelity metadata probe that records simulator timing, backend, controller, observation, and asset metadata for operator review, a ManiSkill render-video preflight with explicit render-backend/shader controls and a renderer-failure classifier that separates render-backed RGB MP4 readiness from diagnostic fallback videos, plus a bounded ManiSkill pilot runtime liveness audit that currently marks the local CPU/render pilot path not ready with a concrete renderer failure summary. The package is stronger and more reviewer-ready than the earlier local scaffold, but it is still not ICLR-main ready because the evidence remains local and synthetic rather than real robot or independently accepted high-fidelity validation.

## Visible Contribution

Paper 119 is a local bridge toward an adaptive physical world/action model for skill seams: it scores whether two embodied skills can compose, explains likely failure modes, selects accept/repair/probe/abstain/transition actions at the seam, and records planner-facing memory for future attempts. Energy landscapes are the implementation vocabulary; the identity of the paper is the bounded skill-seam action model, not a full robot simulator or a low-level controller. The repository now makes that contribution visible through the generated manuscript, bounded claim ledger, mechanism/calibration/holdout/falsification audits, a Planner-edge policy audit for future transition selection, a Local model release card that hash-locks the deterministic v5 seam-model source, method parameters, result artifacts, and reference-adapter hashes while explicitly not being a trained robot policy checkpoint or external evidence, reproducible local experiments, a non-Haonan external validation packet, a guarded config materializer, an External config manifest packet for manifest-declared task-config evidence work orders, an External rollout evidence packet for raw JSONL/video/recompute work orders, an External analysis plan that locks hypotheses and exclusion policy before collection, an External platform probe that records machine/package/GPU/renderer/code/config provenance without counting as evidence, a ManiSkill task binding probe that maps the four task families to concrete public-simulator environment candidates, a ManiSkill env smoke probe showing all four primary bound candidates now construct/reset locally while support candidates explicitly require `oakink-v2` and `ycb` assets, a ManiSkill fidelity metadata probe that pre-fills timing/backend/controller/observation/asset metadata for fidelity review, an External platform onboarding packet for the primary public-simulator route, an External fidelity provenance packet for platform/contact/replay provenance work orders, an External fidelity acceptance draft with a fidelity acceptance promotion checklist that separates machine-prefilled fields from independent operator signoff while keeping acceptance false, a Fidelity acceptance materialization plan that only writes the real acceptance file after explicit independent-operator, real-platform, render-backed-video, real-rollout, manifest, commit, and skill-hash confirmations, an External backend integration packet for the public-simulator backend blocker, a ManiSkill reference backend readiness audit that contract-qualifies an adapter-backed backend candidate and MP4 writer path while proving state-shaped arrays cannot masquerade as render videos and official collection remains fail-closed, explicit render-backend/shader controls, a ManiSkill reference collection preflight audit that shows the explicit backend/config/run-id/alias path now reaches the fidelity-acceptance gate, an External runner backend probe self-test for the real runner path, an External pilot smoke packet for quarantined first-panel backend testing, a ManiSkill render-video preflight with a renderer-failure classifier that records render-backed RGB MP4 readiness separately from diagnostic fallback videos, a ManiSkill pilot runtime liveness audit showing the local reference runner can now write one quarantined schema-valid pilot row/video through a diagnostic non-evidence fallback while render-backed RGB video remains unavailable locally, an External method implementation packet for non-oracle baseline work orders, a reference-adapter provenance catalog that hash-lists every non-oracle interface adapter without counting it as evidence, a strict reference-adapter rejection gate, a manifest assembly checklist that maps every real-manifest field to current file/hash state, operator action, and strict gate, a strict adapter evidence gate that now rejects partial non-oracle manifests, scaffold/reference adapters, unmatched method provenance hashes, and JSONL `policy_or_config_hash` mismatches, a no-go external operator packet that now exposes the tracked ManiSkill reference route with exact commands and the single route-specific fidelity-acceptance blocker, an External collection runbook route-gate audit that carries 41 validation commands, the current ManiSkill route gates, and the actual high-fidelity collection command template in preflight-before-collection order, an audited External operator handoff bundle, a fail-closed real-collection runner harness, and a separate Haonan/Yilun outreach package. The machine readiness audit currently reports `17/21` requirements satisfied; the remaining blockers are external-evidence blockers, not prose or packaging blockers.

Reviewer response packet: `docs/reviewer_response_packet.md` maps hostile reviewer objections to exact local evidence, allowed claims, remaining gates, and one-paper Haonan/Yilun outreach guidance while preserving the `STRONG_REVISE` boundary.

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
- Predictive calibration audit: proposed hard-slice ECE10 `0.007207` vs strongest predecessor `0.014790`, max bin gap `0.012758`, risk-breach correlation `0.970670`, and monotone realized breach across 10 risk deciles locally.
- Holdout robustness audit: task-family `6/6`, seam-regime `7/7`, split `4/4`, task-regime `42/42`, and hash-fold `5/5` holdouts have positive local utility margins; worst task-regime success margin `0.021875`, utility margin `0.172559`.
- Evidence coverage: 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 documented failure cases.

## Reproduce

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_submission_artifacts.ps1
```

Use `-InstallDependencies` on the first run if the Python packages are not installed.

Canonical local PDF: `C:/Users/wangz/Downloads/119.pdf`

PDF SHA256: `E38431534F0FAF0F42FAD8534B1E13A9A15EBEF391A09299DF9B778710E73A18`

PDF size: `471840` bytes.

PDF pages: `30`.

Artifact rule: keep the numbered PDF in Downloads only; do not copy it to the visible Desktop.

## Current Strengthening Docs

- Independent validation gate: `docs/independent_validation_protocol.md`
- Claim/evidence ledger: `docs/claim_evidence_ledger.json`
- Claim boundary audit: `results/claim_boundary_audit.md`
- Visible contribution audit: `results/visible_contribution_audit.md`
- Submission readiness gap audit: `results/submission_readiness_gap_audit.md`
- Reviewer response packet: `docs/reviewer_response_packet.md`
- Local falsification audit: `results/local_falsification_audit.md`
- Holdout robustness audit: `results/holdout_robustness_audit.md`
- Diagnostic mechanism audit: `results/diagnostic_mechanism_audit.md`
- Decision-quality audit: `results/decision_quality_audit.md`
- Planner-edge policy audit: `results/planner_edge_policy_audit.md`
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
- External fidelity acceptance draft: `external_validation/fidelity_acceptance_draft.md`
- External fidelity acceptance draft audit: `results/external_fidelity_acceptance_draft_audit.md`
- External backend integration packet: `external_validation/backend_integration_packet.md`
- External backend integration audit: `results/external_backend_integration_audit.md`
- ManiSkill reference backend readiness audit: `results/maniskill_backend_readiness_audit.md`
- ManiSkill reference collection preflight audit: `results/maniskill_reference_collection_preflight_audit.md`
- External runner backend probe self-test: `results/external_runner_backend_self_test.md`
- External pilot smoke packet: `external_validation/pilot_smoke_packet.md`
- External pilot smoke audit: `results/external_pilot_smoke_audit.md`
- ManiSkill render-video preflight: `results/maniskill_render_video_preflight_audit.md`
- ManiSkill pilot runtime liveness audit: `results/maniskill_pilot_runtime_liveness_audit.md`
- External method implementation packet: `external_validation/method_implementation_packet.md`
- External method implementation audit: `results/external_method_implementation_audit.md`
- External method reference provenance: `external_validation/method_reference_provenance.csv`
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
- External manifest assembly checklist: `external_validation/manifest_assembly_checklist.csv`
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
