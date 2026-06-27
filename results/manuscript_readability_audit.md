# Manuscript Readability Audit

Passed: `true`.
Not evidence: `true`.
Abstract words: `256`.
World/action phrase count: `9`.
Contact-rich phrase count: `1`.

This audit checks that the generated manuscript is naturally framed around a bounded skill-seam world/action model, keeps contact-rich manipulation as a testbed rather than the identity, and has machine-audited related-work/reference coverage. It is not external robot evidence.

## Checks

- `pass` `abstract_exists`: words=256
- `pass` `abstract_length_conference_reasonable`: words=256
- `pass` `required_sections_present`: positions=[2352, 6345, 9788, 11815, 12689, 14223, 23304, 27952]
- `pass` `required_sections_in_order`: positions=[2352, 6345, 9788, 11815, 12689, 14223, 23304, 27952]
- `pass` `core_frame_term_local world/action-modeling prob`: local world/action-modeling problem
- `pass` `core_frame_term_compact predictive interface bet`: compact predictive interface between a skill library and a planner
- `pass` `core_frame_term_action-conditioned physical inte`: action-conditioned physical interface between a skill library and a planner
- `pass` `core_frame_term_world/action-model view at a del`: world/action-model view at a deliberately local scale
- `pass` `core_frame_term_prediction-action-update loop`: prediction-action-update loop
- `pass` `core_frame_term_accept, repair, probe, abstain`: accept, repair, probe, abstain
- `pass` `core_frame_term_choose a different transition`: choose a different transition
- `pass` `core_frame_term_planner-edge updates for future `: planner-edge updates for future planning
- `pass` `core_frame_term_planner's edge beliefs`: planner's edge beliefs
- `pass` `boundary_term_not a universal world model`: not a universal world model
- `pass` `boundary_term_rather than a new low-level cont`: rather than a new low-level controller
- `pass` `boundary_term_bounded claim`: bounded claim
- `pass` `boundary_term_local study`: local study
- `pass` `boundary_term_external robot or high-fidelity `: external robot or high-fidelity validation
- `pass` `boundary_term_deployment-level claims`: deployment-level claims
- `pass` `matrix_term_Composable Energy Policies`: Composable Energy Policies
- `pass` `matrix_term_Runtime Skill Composition`: Runtime Skill Composition
- `pass` `matrix_term_World/action models and hierarch`: World/action models and hierarchical world models
- `pass` `matrix_term_Closest outreach works`: Closest outreach works
- `pass` `matrix_term_External Validation Boundary`: External Validation Boundary
- `pass` `identity_phrase_not_forced`: count=0
- `pass` `world_action_framing_not_overdone`: count=9
- `pass` `contact_rich_is_not_the_identity`: contact-rich count=1
- `pass` `contact_positioning_is_testbed`: contact-rich examples are positioned as a testbed
- `pass` `no_stale_internal_or_manual_polish_terms`: hits=[]
- `pass` `summary_scope_blockers_are_external_only`: missing_scope_evidence=['no_real_robot_rollouts', 'no_accepted_high_fidelity_skill_composition_simulation', 'no_released_skill_energy_or_policy_checkpoint', 'no_calibrated_contact_force_camera_or_state_logs', 'no_hardware_rollout_videos', 'no_independent_baseline_implementations']
- `pass` `all_citations_have_bib_entries`: missing=[]
- `pass` `bibliography_has_enough_entries`: entries=26
- `pass` `related_work_audit_passed`: results/related_work_audit.json
- `pass` `reference_integrity_audit_passed`: results/reference_integrity_audit.json
- `pass` `number_audit_passed`: results/manuscript_number_audit.json
- `pass` `main_body_paragraphs_not_overlong`: long=[]
- `pass` `abstract_is_bounded`: current evidence supports a bounded claim
- `pass` `scope_section_demands_external_evidence`: scope section has evidence contract
