# Submission Version Log

## Superseded Local Builds

- Earlier archive and local-continuation builds were superseded by the v5 expansion.
- Their useful role is now historical only: they established the paper topic, rough mechanism, and prior proposed baseline.
- Their old page counts, hashes, row counts, and baseline statistics should not be used for the current paper state.

## v5_expanded

- Rebuilt the method as `barrier_certified_energy_composer_v5`.
- Added basin-overlap posterior checks, barrier/descent seam tests, terminal-state sampling, high-energy seam repair, contact/dynamics guards, calibration, fixed-risk acceptance, and repair memory.
- Expanded to 12 methods, 10 paired seeds, 230,400 main cells, 38,400 ablation cells, 161,280 stress cells, 107,520 fixed-risk cells, and 24 failure cases.
- Selected the strongest non-oracle baseline from the hard aggregate; it is `proposed_energy_landscape_composer_v4_1`.
- Reported hard success, hard utility, mechanism diagnostics, ablations, stress endpoints, fixed-risk coverage/breach/gated success, and scope blockers.
- Generated a 29-page ICLR-style PDF with hidden link borders and conference-style citations.
- Updated the manuscript generator to emit a natural skill-seam world/action-interface framing instead of an internal audit abstract.
- Reframed the core claim around predicting handoff failure, diagnosing the failure reason, choosing repair/probe/abstain/transition decisions, updating planner edge beliefs, and feeding those outcomes back into future planning.
- Added a vector-first figure pass with a skill-seam overview diagram and PDF/PNG companion outputs for all main figures.
- Added targeted related-work coverage for CoStream, OAT, SIMPACT, PoCo, Yilun energy-based modeling, and the 2026 robot world-model survey.
- Expanded the related-work boundary with CEP, Diffusion Policy, runtime skill composition, EzSkiROS, latent robot skills, and language/action compositionality, plus `docs/related_work_coverage_matrix.md`.
- Added `docs/independent_validation_protocol.md` as the gate for making the paper independently submission-ready without Haonan.
- Added `docs/haonan_yilun_outreach_package.md` with a CoStream-centered email package and collaboration boundary.
- Added reproducible outreach artifacts: `outreach/paper119_one_page_memo.pdf` and `outreach/paper119_four_page_preview.pdf`.
- Added `scripts/build_outreach_artifacts.ps1` and `scripts/validate_outreach_artifacts.py` for page-count and framing checks.
- Added `external_validation/manifest_template.json`, `external_validation/README.md`, and `scripts/audit_external_evidence.py` so the missing real/high-fidelity validation layer is a machine-checkable submission gate rather than prose.
- Added `scripts/build_external_collection_plan.py` so the independent high-fidelity validation route has a concrete non-evidence schedule before real rollouts are collected.
- Added `scripts/build_external_runbook.py` so the collection schedule becomes a non-evidence operator packet with a runbook, 1,440-row record sheet, task cards, config templates, and audit.
- Added `external_validation/platform_qualification_checklist.md` and `scripts/audit_external_execution_readiness.py` so the independent external-validation packet is checked as executable while still remaining explicitly non-evidence.
- Added `scripts/materialize_external_configs.py` so real task configs can be generated only through a guarded operator command after concrete platform and compute values are supplied.
- Added `scripts/build_external_operator_packet.py` so the independent validation path has a generated go/no-go packet with pre-collection blockers, collection commands, and post-collection strict gates.
- Updated the outreach memo, four-page preview, and Haonan/Yilun package to reflect the operator-packet/no-go stance while keeping Haonan's role framed as scientific fit and falsification advice.
- Added `external_validation/config_schema_v1.json` and `scripts/validate_external_configs.py` so task config templates and future strict evidence configs are machine-checked separately.
- Added `scripts/build_external_baseline_contract.py` so the external package has a non-evidence baseline implementation contract, method matrix, per-method adapter specs, and an audit that still marks independent non-oracle implementations as missing.
- Added `scripts/build_external_adapter_scaffolds.py` so the baseline specs produce executable scaffold templates that strict external validation still rejects as evidence until real implementations replace them.
- Added `scripts/build_external_reference_adapters.py` so every method has an executable reference adapter and a non-evidence contract audit before a real external run.
- Added `scripts/build_external_local_dry_run.py` so the frozen local suite is exported into 1,440 schema-compatible external-style JSONL records for plumbing validation while remaining explicitly non-evidence.
- Added `scripts/self_test_external_adapter_scaffold_guard.py` so scaffold-only adapter detection is itself tested.
- Added `scripts/validate_external_adapters.py` so external baseline adapters must expose the seam-model API, proposal fields, log fields, and policy/config hash reporting; strict mode remains blocked until manifest-declared real implementations replace scaffolds.
- Added `scripts/build_external_manifest.py` so real or high-fidelity rollout logs, videos, configs, checkpoints, hashes, and recomputed metrics can be assembled into `external_validation/manifest.json` without hand-editing evidence.
- Added `external_validation/log_schema_v1.json` and `scripts/validate_external_rollouts.py` so external success/utility margins, paired win rate, fixed-risk coverage, fixed-risk breach, and positive task-family count must be recomputed from raw episode logs.
- Tightened `scripts/audit_external_evidence.py` so a future evidence package is blocked unless manifest metrics agree with recomputed rollout metrics.
- Added `scripts/self_test_external_rollout_validator.py` to test the external rollout validator on temporary synthetic records without treating them as evidence.
- Added `scripts/self_test_external_evidence_pipeline.py` to test the full strict external-evidence path on a temporary synthetic manifest/config/log/video/checkpoint package without creating real repository evidence.
- Fixed strict evidence-audit metric parsing so legitimate zero-valued fixed-risk breach is accepted as a number rather than treated as missing.
- Added `docs/claim_evidence_ledger.json` and `scripts/audit_claim_boundary.py` so the package fails validation if it overclaims beyond the bounded local evidence.
- Added `scripts/audit_submission_readiness_gap.py` so the active objective is tracked as concrete satisfied, missing, and human-polish requirements without falsely declaring the paper complete.
- Added `scripts/audit_visible_contribution.py` so README, final audit, readiness docs, version log, child status, and outreach package must stay synchronized with the current materializer/operator-packet/outreach state.
- Added `scripts/audit_local_falsification.py` and manuscript integration for abstention, cost/search, risk-monotonicity, slice-coverage, and oracle-gap checks over episode-level hard-slice rows.
- Added `scripts/audit_holdout_robustness.py` and manuscript integration for task-family, seam-regime, split, task-regime, and hash-fold withheld-slice local robustness checks.
- Added `scripts/audit_diagnostic_mechanism.py` and manuscript integration for exported diagnostic labels, seam decisions, and planner-edge updates over local rows.
- Added `scripts/audit_decision_quality.py` and manuscript integration for comparative decision quality: accepted-seam coverage, non-abstain quality, recovered predecessor-abstained accepts, and shared-abstention breach changes over local hard rows.
- Added `scripts/audit_seam_prediction_calibration.py` and manuscript integration for local predicted seam-risk calibration against realized breach, including ECE10, max bin gap, monotone risk deciles, and decision relevance.
- Added `scripts/audit_manuscript_numbers.py` so manuscript margins, row counts, generated table values, local falsification numbers, diagnostic mechanism numbers, decision-quality numbers, predictive-calibration numbers, and holdout robustness numbers must match generated result files.
- Added `scripts/audit_related_work.py` so citation coverage, novelty-boundary rows, and outreach/validation boundary wording are machine-checked across 12 required areas.
- Added `scripts/audit_reference_integrity.py` so required BibTeX fields, DOI/arXiv identifiers, recent primary-source metadata, and Haonan/Yilun-adjacent author coverage are machine-checked.
- Added `scripts/audit_manuscript_readability.py` so the agenda framing, novelty boundary, contact-as-testbed positioning, paragraph readability, and stale manual-polish blocker are machine-checked.
- Added `scripts/audit_presentation_quality.py` so the compiled PDF/source/log/figure surface is checked for top-conference presentation hygiene.
- Added `scripts/audit_figure_readability.py` so all seven main figure companions are checked for render resolution, foreground density, contrast, edge margins, color detail, and manuscript references.
- Added `scripts/audit_camera_ready_design.py` so all 29 rendered PDF pages are checked for nonblank content, density, contrast, margins, sparse-page count, canonical PDF parity, and selected text anchors.
- Added `scripts/build_submission_artifacts.ps1` as the single local rebuild command for experiments, manuscript, PDF, audits, and outreach artifacts.
- Terminal decision remains STRONG_REVISE.
- ICLR main readiness remains no pending real robot or accepted high-fidelity validation, released checkpoints/logs, hardware videos, and manifest-declared independent baseline evidence.
