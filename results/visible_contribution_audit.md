# Visible Contribution Audit

Passed: `true`.
Not evidence: `true`.

This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, the local planner-edge policy audit, guarded external config materialization, the external config manifest packet, the external rollout evidence packet, the locked external analysis plan, the external platform probe, the ManiSkill task binding probe, the ManiSkill env smoke probe, the external platform onboarding packet, the external fidelity provenance packet, the external fidelity acceptance draft, the external backend integration packet, the ManiSkill reference backend readiness audit with MP4 writer path, the ManiSkill reference collection preflight audit, the external runner backend probe self-test, the external pilot smoke packet, the ManiSkill pilot runtime liveness audit, the external method implementation packet, the no-go operator packet, the no-evidence operator handoff bundle, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.

## Checks

- `pass` `readiness_gap_state_visible`: objective_complete=False, satisfied=17, blocking=4
- `pass` `operator_packet_no_go_visible`: start_state='DO_NOT_COLLECT_YET', blocking_missing_count=4
- `pass` `operator_packet_tracked_reference_route_visible`: backend='external_validation\\runner\\maniskill_reference_backend.py', run_id='maniskill_sapien_reference_preflight_protocol_v1', blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `operator_handoff_bundle_visible`: files=246, forbidden=[], start_state='DO_NOT_COLLECT_YET'
- `pass` `analysis_plan_visible`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_probe_visible`: primary_route_install_ready=True, missing=[]
- `pass` `maniskill_task_binding_probe_visible`: strict_task_binding_install_ready=True, missing=[]
- `pass` `maniskill_env_smoke_probe_visible`: strict_env_smoke_ready=True, primary_reset_missing=[]
- `pass` `maniskill_fidelity_metadata_probe_visible`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `platform_onboarding_visible`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_provenance_packet_visible`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_draft_visible`: draft_ready=True, remaining_operator_inputs=10, acceptance_ready=False
- `pass` `backend_integration_packet_visible`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `maniskill_reference_backend_visible`: backend_contract_ready=True, video_writer_ready=True, official_collection_ready=False, strict_external_evidence_ready=False
- `pass` `maniskill_reference_collection_preflight_visible`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `runner_backend_probe_visible`: records_written=2, schema_errors=[]
- `pass` `pilot_smoke_packet_visible`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_pilot_runtime_liveness_visible`: pilot_runtime_ready=False, runner_io_ready=True, render_video_ready=False, timed_out=False, records=1, videos=1, diagnostic_fallbacks=1, failure_summary='runner wrote quarantined schema-valid row/video using diagnostic non-evidence video fallback; render-backed video remains unavailable'
- `pass` `config_manifest_packet_visible`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `rollout_evidence_packet_visible`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `method_implementation_packet_visible`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `materializer_guard_visible`: write_enabled=False, not_external_evidence=True
- `pass` `planner_edge_policy_visible`: frontiers=1680, utility_delta=0.231317169047619, breach_delta=-0.07518194761904762
- `pass` `ledger_tracks_new_visible_claims`: missing=[]
- `pass` `README_current_visible_contribution_terms`: missing=[]
- `pass` `final_audit_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_decision_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_audit_current_visible_contribution_terms`: missing=[]
- `pass` `version_log_current_visible_contribution_terms`: missing=[]
- `pass` `child_status_current_visible_contribution_terms`: missing=[]
- `pass` `outreach_current_visible_contribution_terms`: missing=[]
