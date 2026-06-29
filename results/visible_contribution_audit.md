# Visible Contribution Audit

Passed: `true`.
Not evidence: `true`.

This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, the local planner-edge policy audit, the local model release card, guarded external config materialization, the external config manifest packet, the external rollout evidence packet, the strict MP4 video evidence gate, the strict task-config hash gate, the strict policy/config hash gate, the external ablation collection packet, the external evidence intake ledger, the External precollection manifest draft, the locked external analysis plan, the external platform probe, the ManiSkill task binding probe, the ManiSkill env smoke probe, the external platform onboarding packet, the external fidelity provenance packet, the external fidelity acceptance draft, the fidelity acceptance materializer, the external backend integration packet, the ManiSkill reference backend readiness audit with MP4 writer path, state-shaped array video guard, and explicit render-backend/shader controls, the ManiSkill reference collection preflight audit, the external runner backend probe self-test, the official video write guard, the official JSONL write guard, atomic official evidence promotion, the external pilot smoke packet, the ManiSkill render-video preflight, renderer-failure classifier, timeout diagnosis retest, renderer profile matrix, and ManiSkill render machine qualification packet, the ManiSkill pilot runtime liveness audit, the external method implementation packet, the reference-adapter provenance catalog, the strict reference-adapter rejection gate, the manifest assembly checklist, the External manifest builder self-test, the no-go operator packet, the external collection runbook route-gate audit, the no-evidence operator handoff bundle, the reviewer response packet, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.

## Checks

- `pass` `canonical_pdf_metadata_available`: path=C:\Users\wangz\Downloads\119.pdf, sha=317D3156519D8E5062DCB23FF6EE487175ECD3F7B2B81268DB194359F8433B60, size=467426
- `pass` `paper_pdf_matches_canonical`: paper_sha=317D3156519D8E5062DCB23FF6EE487175ECD3F7B2B81268DB194359F8433B60, canonical_sha=317D3156519D8E5062DCB23FF6EE487175ECD3F7B2B81268DB194359F8433B60
- `pass` `readiness_gap_state_visible`: objective_complete=False, satisfied=17, blocking=4
- `pass` `operator_packet_no_go_visible`: start_state='DO_NOT_COLLECT_YET', blocking_missing_count=4
- `pass` `operator_packet_tracked_reference_route_visible`: backend='external_validation\\runner\\maniskill_reference_backend.py', run_id='maniskill_sapien_reference_preflight_protocol_v1', blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `operator_handoff_bundle_visible`: files=278, forbidden=[], start_state='DO_NOT_COLLECT_YET'
- `pass` `external_runbook_route_gates_visible`: validation_command_count=44, route_gates=True, gate_order=True
- `pass` `analysis_plan_visible`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_probe_visible`: primary_route_install_ready=True, missing=[]
- `pass` `maniskill_task_binding_probe_visible`: strict_task_binding_install_ready=True, missing=[]
- `pass` `maniskill_env_smoke_probe_visible`: strict_env_smoke_ready=True, primary_reset_missing=[]
- `pass` `maniskill_fidelity_metadata_probe_visible`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `platform_onboarding_visible`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_provenance_packet_visible`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_draft_visible`: draft_ready=True, remaining_operator_inputs=10, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_visible`: write_enabled=False, acceptance_write_ready=False
- `pass` `backend_integration_packet_visible`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `maniskill_reference_backend_visible`: backend_contract_ready=True, video_writer_ready=True, render_backend='cpu', shader_pack='minimal', official_collection_ready=False, strict_external_evidence_ready=False
- `pass` `maniskill_reference_collection_preflight_visible`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `runner_backend_probe_visible`: records_written=2, schema_errors=[]
- `pass` `official_video_write_guard_visible`: runner refuses diagnostic/non-MP4/undersized/out-of-dir videos before official JSONL writes
- `pass` `official_jsonl_write_guard_visible`: runner refuses schema-invalid rollout records before official JSONL writes
- `pass` `atomic_official_jsonl_promotion_visible`: runner preserves official JSONL logs and videos when a selected batch fails before promotion
- `pass` `pilot_smoke_packet_visible`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_pilot_runtime_liveness_visible`: pilot_runtime_ready=False, runner_io_ready=False, render_video_ready=False, render_backend='cpu', shader_pack='minimal', timed_out=True, records=0, videos=0, diagnostic_fallbacks=0, failure_summary='runner timed out before producing the required pilot record/video'
- `pass` `maniskill_render_video_preflight_visible`: render_video_ready=False, render_backend='cpu', shader_pack='minimal', envs=4, blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: render preflight exceeded 30 seconds; OpenCabinetDrawer-v1: render preflight exceeded 30 seconds; OpenCabinetDoor-v1: render preflight exceeded 30 seconds; PullCubeTool-v1: render preflight exceeded 30 seconds']
- `pass` `renderer_failure_classifier_visible`: classes=['render_timeout'], remediation=3
- `pass` `config_manifest_packet_visible`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_visible`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `strict_video_evidence_gate_visible`: strict rollout validation rejects placeholder/diagnostic/staged/backup/non-MP4 video paths, stale task configs, and manifest method-hash mismatches
- `pass` `release_package_internal_artifact_rejection_visible`: release_package_ready=False, bad_release_package_ready=False
- `pass` `ablation_collection_packet_visible`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `evidence_intake_ledger_visible`: mapped=36/36, strict_external_evidence_ready=False
- `pass` `precollection_manifest_draft_visible`: prepared_configs=4, method_gaps=11, rollout_gaps=8, official_manifest_exists=False
- `pass` `method_implementation_packet_visible`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `strict_reference_adapter_rejection_gate_visible`: reference_adapter_evidence_ready=False, leaky_provenance_ready=False, check=True
- `pass` `materializer_guard_visible`: write_enabled=False, not_external_evidence=True
- `pass` `planner_edge_policy_visible`: frontiers=1680, utility_delta=0.231317169047619, breach_delta=-0.07518194761904762
- `pass` `local_model_release_visible`: release_hash='5CF7C6E592517ECC40371074F6341C489BCAB11E5358E6BA053CB3AD241B5929', local_model_release_ready=True, external_evidence_ready=False
- `pass` `reviewer_response_packet_visible`: entries=12, not_external_evidence=True
- `pass` `ledger_tracks_new_visible_claims`: missing=[]
- `pass` `README_current_visible_contribution_terms`: missing=[]
- `pass` `final_audit_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_decision_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_audit_current_visible_contribution_terms`: missing=[]
- `pass` `version_log_current_visible_contribution_terms`: missing=[]
- `pass` `child_status_current_visible_contribution_terms`: missing=[]
- `pass` `outreach_current_visible_contribution_terms`: missing=[]
- `pass` `reviewer_current_visible_contribution_terms`: missing=[]
- `pass` `public_pdf_metadata_matches_canonical_artifact`: sha=317D3156519D8E5062DCB23FF6EE487175ECD3F7B2B81268DB194359F8433B60, size=467426, missing_sha=[], missing_size=[]
