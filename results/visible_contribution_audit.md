# Visible Contribution Audit

Passed: `true`.
Not evidence: `true`.

This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, the local planner-edge policy audit, the failure-memory adaptation audit, the local model release card, guarded external config materialization, the External config materialization self-test, the external config manifest packet, the External config manifest packet self-test, the external rollout evidence packet, the External rollout evidence packet self-test, the External evidence preflight self-test, the External execution readiness self-test, the strict MP4 video evidence gate, the strict full-method coverage gate, the strict rollout sample-count gate, the strict paired-panel gate, the strict rollout uniqueness gate, confidence-gated external rollout statistics, the final rollout confidence summary gate, the strict task-config hash gate, the strict policy/config hash gate, the external ablation collection packet, the External ablation collection packet self-test, the external evidence intake ledger, the External evidence intake ledger self-test, the External precollection manifest draft, the External precollection manifest draft self-test, the External precollection freeze receipt, the External precollection freeze receipt self-test, the External postcollection evidence seal, the External postcollection evidence seal self-test, the External postcollection seal consistency gate, the External postcollection seal consistency self-test, the locked external analysis plan, the external platform probe, the ManiSkill task binding probe, the ManiSkill env smoke probe, the external platform onboarding packet, the external fidelity provenance packet, the external fidelity acceptance draft, the strict fidelity acceptance provenance gate, the fidelity acceptance materializer, the external backend integration packet, the external backend integration packet self-test, the ManiSkill reference backend readiness audit with MP4 writer path, state-shaped array video guard, and explicit render-backend/shader controls, the ManiSkill reference collection preflight audit, the External collection preflight self-test with tracked reference-route readiness after accepted fidelity, the external runner backend probe self-test, the official video write guard, the official JSONL write guard, diagnostic sidecar rejected before JSONL write tracking, atomic official evidence promotion, the external pilot smoke packet, the ManiSkill render-video preflight, renderer-failure classifier, timeout diagnosis retest, renderer profile matrix, render resource sweep, render host qualification brief, ManiSkill render machine qualification packet, ManiSkill render machine qualification self-test, render failure remediation packet, ManiSkill pilot runtime liveness audit, reset-timeout triage sidecar, and backend reset substage markers, the external method implementation packet, the External method implementation packet self-test, the External baseline contract self-test, External method config materialization, External method config materialization self-test, prepared task-config binding in the config evidence self-test, tracked candidate method-config binding in the adapter evidence self-test, adapter acceptance fixtures, the reference-adapter provenance catalog, the method manifest cutover checklist, the External adapter scaffold guard self-test, the strict reference-adapter rejection gate, the strict independent method provenance gate, the strict checkpoint/config artifact gate, the strict fairness-contract binding gate, the manifest assembly checklist, the External manifest builder self-test, the External rollout validator self-test, the External full-pipeline evidence self-test, the External evidence closure brief, the External evidence closure brief self-test, the no-go operator packet, the External collection job packet, the External collection job packet self-test, the External collection machine bootstrap, the External collection machine bootstrap self-test, the Independent validation launch ticket, the external collection runbook route-gate audit, the no-evidence operator handoff bundle, the External operator handoff bundle self-test, the External operator release bundle, the External operator release bundle self-test, the reviewer response packet, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.
The External full-pipeline evidence self-test also documents prepared task-config and tracked candidate method-config binding inside the temporary fixture.
The External acquisition packet self-test documents acquisition-packet fail-closed behavior for missing source audits, unmapped blockers, premature manifests, and premature collection readiness.
The External evidence closure brief self-test documents compact-closure fail-closed behavior for fifth-blocker drift, premature manifests, missing Linux command spines, Haonan-dependent route drift, and missing source packets.
The External evidence preflight self-test documents preflight fail-closed behavior for the current no-manifest route, incomplete logs, placeholder videos, template configs, scaffold implementations, and real-output overwrite attempts while proving a temporary complete 1,440-record package can reach strict-audit handoff.
The External execution readiness self-test documents top-level execution-packet fail-closed behavior for missing operator packets, missing required packet files, premature manifests, accidental strict-evidence promotion, and Haonan-dependence drift.
The External collection job packet self-test documents collection-job fail-closed behavior for missing sources, source evidence drift, premature manifests, premature ready states, unsafe command-spine edits, missing Linux command output, hash-gate drift, and render self-test drift.
The External collection machine bootstrap self-test documents bootstrap fail-closed behavior for missing source reports, source evidence drift, premature collection go-states, local-machine promotion, unsafe commands, missing confirmation, install-guidance drift, and premature manifest/log/video outputs.
The External operator handoff bundle self-test documents no-evidence handoff fail-closed behavior for no-go drift, missing files, forbidden evidence paths, premature manifests, missing collection-job/bootstrap packets, and premature strict-evidence readiness.
The External operator release bundle self-test documents transfer-package fail-closed behavior for the default no-archive path, explicit archive creation, source handoff drift, hash drift, forbidden evidence paths, premature manifests, and collection-job drift.

## Checks

- `pass` `canonical_pdf_metadata_available`: path=C:\Users\wangz\Downloads\119.pdf, sha=AE310705B235339B73987C6E2DBD31439C50F78ADD364D5593302A9733D83A5B, size=469674
- `pass` `paper_pdf_matches_canonical`: paper_sha=AE310705B235339B73987C6E2DBD31439C50F78ADD364D5593302A9733D83A5B, canonical_sha=AE310705B235339B73987C6E2DBD31439C50F78ADD364D5593302A9733D83A5B
- `pass` `readiness_gap_state_visible`: objective_complete=False, satisfied=17, blocking=4
- `pass` `operator_packet_no_go_visible`: start_state='DO_NOT_COLLECT_YET', blocking_missing_count=4
- `pass` `collection_readiness_tracked_reference_route_visible`: backend='external_validation\\runner\\maniskill_reference_backend.py', run_id='maniskill_sapien_reference_preflight_protocol_v1', blocking=["reference_fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `operator_packet_tracked_reference_route_visible`: backend='external_validation\\runner\\maniskill_reference_backend.py', run_id='maniskill_sapien_reference_preflight_protocol_v1', blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `operator_handoff_bundle_visible`: files=398, forbidden=[], start_state='DO_NOT_COLLECT_YET'
- `pass` `external_operator_handoff_bundle_self_test_visible`: fixture_ready=True, no_go_drift_rejected=True, strict_drift_rejected=True, forbidden_rejected=True
- `pass` `external_acquisition_packet_self_test_visible`: fixture_ready=True, missing_source_rejected=True, unmapped_blocker_rejected=True, manifest_rejected=True, collection_drift_rejected=True
- `pass` `external_evidence_closure_brief_visible`: blockers=4, items=4, haonan_dependency=False
- `pass` `external_evidence_closure_brief_self_test_visible`: fixture_ready=True, unmapped_rejected=True, haonan_rejected=True
- `pass` `external_collection_job_packet_visible`: job_state='DO_NOT_START_COLLECTION_YET', steps=17, blockers=4
- `pass` `external_collection_job_packet_self_test_visible`: fixture_ready=True, missing_source_rejected=True, source_drift_rejected=True, manifest_rejected=True, ready_state_rejected=True, unsafe_command_rejected=True
- `pass` `external_collection_machine_bootstrap_visible`: bootstrap_state='READY_TO_BOOTSTRAP_EXTERNAL_MACHINE', command='external_validation/collection_machine_bootstrap.ps1'
- `pass` `external_collection_machine_bootstrap_self_test_visible`: fixture_ready=True, missing_source_rejected=True, job_go_rejected=True, local_promotion_rejected=True, unsafe_command_rejected=True
- `pass` `independent_validation_launch_ticket_visible`: launch_state='DO_NOT_START_COLLECTION_YET', render_state='DO_NOT_COLLECT_RENDER_MACHINE', haonan_dependency=False
- `pass` `external_operator_release_bundle_visible`: bundle_state='READY_TO_SEND_OPERATOR_PACKAGE', files=398, archive_written=False
- `pass` `external_operator_release_bundle_self_test_visible`: fixture_ready=True, archive_ready=True, forbidden_rejected=True, real_untouched=True
- `pass` `external_runbook_route_gates_visible`: validation_command_count=47, route_gates=True, gate_order=True
- `pass` `analysis_plan_visible`: analysis_plan_ready=True, strict_evidence_ready=False
- `pass` `platform_probe_visible`: primary_route_install_ready=True, missing=[]
- `pass` `maniskill_task_binding_probe_visible`: strict_task_binding_install_ready=True, missing=[]
- `pass` `maniskill_env_smoke_probe_visible`: strict_env_smoke_ready=True, primary_reset_missing=[]
- `pass` `maniskill_fidelity_metadata_probe_visible`: strict_metadata_ready=True, primary_metadata_missing=[]
- `pass` `platform_onboarding_visible`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `fidelity_provenance_packet_visible`: fidelity_provenance_packet_ready=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_provenance_packet_self_test_visible`: temporary_ready=True, strict_command_drift_rejected=True, real_untouched=True
- `pass` `fidelity_acceptance_draft_visible`: draft_ready=True, remaining_operator_inputs=9, acceptance_ready=False
- `pass` `fidelity_acceptance_materializer_visible`: write_enabled=False, acceptance_write_ready=False, commit='8242a93661319da5e1eec86a74e6a6c09cc629a4', skill_hash='62EA64D1C80D67F5EB7EC63A88A581AE2D89B4230873F11D46799658541411F1', clean=True, dirty_count=0
- `pass` `fidelity_acceptance_materializer_self_test_visible`: checks={'matching_clean_checkout_writes_temp_acceptance': True, 'stale_commit_rejected_without_temp_write': True, 'mismatched_skill_hash_rejected_without_temp_write': True, 'dirty_checkout_rejected_without_temp_write': True, 'pycache_excluded_from_skill_library_hash': True, 'real_acceptance_file_not_touched': True}
- `pass` `backend_integration_packet_visible`: backend_integration_packet_ready=True, strict_backend_ready=False
- `pass` `backend_integration_packet_self_test_visible`: temporary_ready=True, strict_command_drift_rejected=True, real_untouched=True
- `pass` `maniskill_reference_backend_visible`: backend_contract_ready=True, video_writer_ready=True, render_backend='cpu', shader_pack='minimal', official_collection_ready=False, strict_external_evidence_ready=False
- `pass` `maniskill_reference_collection_preflight_visible`: contract_ready=True, collection_ready=False, blocking=["fidelity_acceptance_ready: acceptance_ready=False, readiness_state='COLLECT_PLATFORM_PROVENANCE'"]
- `pass` `external_collection_preflight_self_test_visible`: synthetic_ready=True, reference_ready=True, blockers=[]
- `pass` `external_evidence_preflight_self_test_visible`: temporary_complete_fixture_ready=True, incomplete_log_rejected=True, placeholder_video_rejected=True, template_config_rejected=True, scaffold_implementation_rejected=True
- `pass` `external_execution_readiness_self_test_visible`: temporary_fixture_execution_ready=True, missing_linux_bootstrap_rejected=True, strict_evidence_promotion_rejected=True, haonan_dependence_drift_rejected=True
- `pass` `runner_backend_probe_visible`: records_written=2, schema_errors=[]
- `pass` `official_video_write_guard_visible`: runner refuses diagnostic/non-MP4/undersized/out-of-dir videos before official JSONL writes
- `pass` `official_jsonl_write_guard_visible`: runner refuses schema-invalid rollout records before official JSONL writes
- `pass` `atomic_official_jsonl_promotion_visible`: runner preserves official JSONL logs and videos when a selected batch fails before promotion
- `pass` `pilot_smoke_packet_visible`: pilot_smoke_packet_ready=True, strict_evidence_ready=False
- `pass` `maniskill_pilot_runtime_liveness_visible`: pilot_runtime_ready=False, runner_io_ready=False, render_video_ready=False, render_backend='cpu', shader_pack='minimal', timed_out=False, records=0, videos=0, diagnostic_fallbacks=1, diagnostic_rejected=True, last_stage='record_video_start', last_backend_stage='reset_scene_return', reset_triage_status='RESET_SCENE_TIMEOUT_TRIAGE_NOT_APPLICABLE', failure_summary='official video guard rejected diagnostic fallback sidecar before JSONL write after progress stage record_video_start'
- `pass` `maniskill_render_video_preflight_visible`: render_video_ready=False, render_backend='cpu', shader_pack='minimal', failure_stages=['initial_render_start', 'initial_render_start', 'initial_render_start', 'initial_render_start'], terminal_stages=['close_done', 'close_done', 'close_done', 'close_done'], envs=4, blocking=['render-backed MP4 preflight is not ready on this machine; PegInsertionSide-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDrawer-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); OpenCabinetDoor-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done); PullCubeTool-v1: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory (failure stage: initial_render_start, terminal stage: close_done)']
- `pass` `renderer_failure_classifier_visible`: classes=['vulkan_descriptor_pool_exhaustion'], remediation=5
- `pass` `render_resource_sweep_visible`: any_ready=False, records=3, classes=['vulkan_descriptor_pool_exhaustion']
- `pass` `render_failure_remediation_packet_visible`: state='RENDER_REMEDIATION_REQUIRED', errors=['RuntimeError: vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory'], work_orders=['collection_readiness_gate', 'diagnostic_fallback_exclusion', 'fidelity_acceptance_after_render_ready', 'pilot_liveness_retest', 'render_profile_matrix_retest', 'renderer_platform_probe']
- `pass` `maniskill_render_host_qualification_brief_visible`: host_state='RENDER_HOST_NOT_QUALIFIED', collection_state='DO_NOT_COLLECT_RENDER_MACHINE', sources=['https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html', 'https://sapien.ucsd.edu/docs/latest/index.html', 'https://registry.khronos.org/vulkan/specs/latest/man/html/vkAllocateDescriptorSets.html']
- `pass` `render_machine_qualification_self_test_visible`: ready='QUALIFIED_FOR_RENDER_BACKED_PILOT', fail_closed='DO_NOT_COLLECT_RENDER_MACHINE', fallback_rejected=True, real_untouched=True
- `pass` `external_config_materialization_self_test_visible`: temporary_plan_ready=True, confirmed_write_fixture_ready=True, real_outputs_untouched=True
- `pass` `config_manifest_packet_visible`: config_manifest_packet_ready=True, strict_config_evidence_ready=False, manifest_declared_config_ready=False
- `pass` `config_manifest_packet_self_test_visible`: temporary_ready=True, manifest_omission_rejected=True, real_untouched=True
- `pass` `strict_config_evidence_hash_gate_visible`: strict config validation recomputes manifest-declared task-config hashes and rejects stale config_path/config_hash pairs
- `pass` `rollout_evidence_packet_visible`: rollout_evidence_packet_ready=True, strict_rollout_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `rollout_evidence_packet_self_test_visible`: temporary_ready=True, tasks_rejected=True, real_untouched=True
- `pass` `strict_video_evidence_gate_visible`: strict rollout validation rejects placeholder/diagnostic/staged/backup/non-MP4 video paths, incomplete method sets, duplicate rows/videos, weak sample counts, mispaired method panels, stale task configs, manifest method-hash mismatches, weak confidence bounds, and missing final confidence summaries
- `pass` `external_rollout_validator_self_test_visible`: records=1440, confidence=True, weak_rejected=True, real_untouched=True
- `pass` `external_evidence_pipeline_self_test_visible`: synthetic_ready=True, records=1440, prepared_configs=True, candidate_configs=True, confidence_rejected=True, release_rejected=True, real_untouched=True/True
- `pass` `release_package_internal_artifact_rejection_visible`: release_package_ready=False, bad_release_package_ready=False
- `pass` `ablation_collection_packet_visible`: work_order_count=5, expected_ablation_records=600, manifest_ablation_evidence_ready=False
- `pass` `ablation_collection_packet_self_test_visible`: temporary_packet_ready=True, work_order_artifact_command_drift_rejected=True, real_outputs_untouched=True
- `pass` `evidence_intake_ledger_visible`: mapped=37/37, strict_external_evidence_ready=False
- `pass` `evidence_intake_ledger_self_test_visible`: temporary_ledger_ready=True, unmapped_failure_rejected=True, real_outputs_untouched=True
- `pass` `external_operator_return_package_contract_visible`: items=28, expected_records=1440, missing=56
- `pass` `precollection_manifest_draft_visible`: prepared_configs=4, method_configs=11, method_gaps=11, rollout_gaps=8, official_manifest_exists=False
- `pass` `precollection_manifest_draft_self_test_visible`: temporary_draft_ready=True, candidate_hash_drift=True, source_report_drift=True
- `pass` `precollection_freeze_receipt_visible`: locked_artifacts=42, candidate_method_configs=11, freeze_receipt_ready=False, strict_external_evidence_ready=False
- `pass` `precollection_freeze_receipt_self_test_visible`: synthetic_ready=True, missing_backend=True, placeholder_run=True, missing_lock=True, dirty_checkout=True
- `pass` `postcollection_evidence_seal_visible`: sealed_artifacts=11, records=0, videos=0, seal_ready=False, manifest_promotion=False
- `pass` `postcollection_evidence_seal_self_test_visible`: synthetic_ready=True, metadata_rejected=True, videos_rejected=True, manifest_rejected=True
- `pass` `postcollection_seal_consistency_gate_visible`: matched=11, records=0, videos=0, consistency_ready=False
- `pass` `postcollection_seal_consistency_self_test_visible`: synthetic_ready=True, drift_rejected=True, extra_rejected=True
- `pass` `method_implementation_packet_visible`: method_implementation_packet_ready=True, strict_adapter_evidence_ready=False
- `pass` `method_implementation_packet_self_test_visible`: temporary_ready=True, missing_rejected=True, oracle_rejected=True, real_untouched=True
- `pass` `baseline_contract_self_test_visible`: implementations_ready=False, release_evidence=True, self_test=True
- `pass` `external_method_config_materialization_visible`: candidate_configs=11, strict_adapter_evidence_ready=False, oracle_excluded=True
- `pass` `external_method_config_materialization_self_test_visible`: temporary_materialization_ready=True, candidate_hash_drift=True, real_outputs_untouched=True
- `pass` `adapter_scaffold_guard_self_test_visible`: scaffold_dir=True, scaffold_template=True, ordinary_false_positive=False, real_untouched=True
- `pass` `strict_reference_adapter_rejection_gate_visible`: tracked_candidate_config_fixture_ready=True, reference_adapter_evidence_ready=False, leaky_provenance_ready=False, implementation_hash_only_ready=False, fairness_mismatch_ready=False, check=True
- `pass` `materializer_guard_visible`: write_enabled=False, not_external_evidence=True
- `pass` `planner_edge_policy_visible`: frontiers=1680, utility_delta=0.231317169047619, breach_delta=-0.07518194761904762
- `pass` `failure_memory_adaptation_visible`: signatures=2210, frontiers=1667, corr=0.9574193753223077, breach_delta=-0.08288240682870371
- `pass` `local_model_release_visible`: release_hash='546D8DA38D310FBB51EBFC15C41DFD7A9058EC1631EA60019501378FD487A57D', local_model_release_ready=True, external_evidence_ready=False
- `pass` `reviewer_response_packet_visible`: entries=12, not_external_evidence=True
- `pass` `haonan_yilun_send_ready_outreach_visible`: words=189, primary='CoStream', secondary='none'
- `pass` `ledger_tracks_new_visible_claims`: missing=[]
- `pass` `README_current_visible_contribution_terms`: missing=[]
- `pass` `final_audit_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_decision_current_visible_contribution_terms`: missing=[]
- `pass` `readiness_audit_current_visible_contribution_terms`: missing=[]
- `pass` `version_log_current_visible_contribution_terms`: missing=[]
- `pass` `child_status_current_visible_contribution_terms`: missing=[]
- `pass` `outreach_current_visible_contribution_terms`: missing=[]
- `pass` `reviewer_current_visible_contribution_terms`: missing=[]
- `pass` `send_ready_outreach_current_visible_contribution_terms`: missing=[]
- `pass` `public_pdf_metadata_matches_canonical_artifact`: sha=AE310705B235339B73987C6E2DBD31439C50F78ADD364D5593302A9733D83A5B, size=469674, missing_sha=[], missing_size=[]
