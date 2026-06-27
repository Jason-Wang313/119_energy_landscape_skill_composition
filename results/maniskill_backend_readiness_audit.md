# ManiSkill Reference Backend Readiness Audit

Passed: `true`.
Not evidence: `true`.
Backend module: `external_validation.runner.maniskill_reference_backend`.
Backend contract ready: `true`.
Reference backend collection enabled: `false`.
Official collection ready: `false`.
Strict external evidence ready: `false`.

This audit qualifies the repository's ManiSkill/SAPIEN reference backend against the backend API and method-adapter wiring. It does not provide rollout evidence: official collection still requires accepted fidelity provenance, installed assets, explicit alias unsealing, real MP4 export, JSONL logs, manifests, and strict evidence audits.

## Checks

- `pass` `backend_module_supplied`: external_validation.runner.maniskill_reference_backend
- `pass` `backend_constructs`: Backend
- `pass` `backend_contract_complete`: all required methods are implemented by the backend class
- `pass` `backend_platform_provenance_complete`: {"backend_module_sha256": "0BDF123E0EC4E7EF4513D5269703172A798A3B37AB403840D137B151BA64008E", "collection_enabled_by_default": false, "contact_solver": "operator_verified_by_fidelity_acceptance", "gymnasium_version": "1.2.3", "maniskill_version": "3.0.1", "not_external_evidence": true, "operating_system": "Windows-10-10.0.26200-SP0", "physics_timestep": "operator_verified_by_fidelity_acceptance", "platform_name": "ManiSkill-SAPIEN-reference-backend", "platform_type": "high_fidelity_sim", "platform_version": "3.0.1", "python_version": "3.10.11", "renderer": "operator_default_or_cpu", "sapien_version": "3.0.3", "sensor_modalities": ["state", "camera", "contact_or_force"], "torch_version": "2.10.0"}
- `pass` `backend_loads_all_task_configs`: tasks=4
- `pass` `backend_reports_method_hashes`: methods=12
- `pass` `backend_file_exists`: external_validation/runner/maniskill_reference_backend.py
- `pass` `backend_is_non_template`: TEMPLATE_ONLY=False, BACKEND_NAME='maniskill_sapien_reference_backend_v1'
- `pass` `backend_contract_strict_passes`: strict backend-module contract passed
- `pass` `platform_provenance_marks_non_evidence`: not_external_evidence=True, collection_enabled_by_default=False
- `pass` `delegates_to_reference_adapters`: methods=12, missing=[]
- `pass` `official_collection_fail_closed_without_enable_flag`: ManiSkill reference backend is contract-qualified but fail-closed for official collection; set PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS=1 only inside an accepted external run.
- `pass` `video_export_remains_operator_backend_requirement`: video export is intentionally not implemented in the reference backend; an accepted evidence backend must wrap ManiSkill recording and write real MP4 files.
- `pass` `strict_evidence_remains_false`: backend contract readiness is not rollout evidence, fidelity acceptance, videos, logs, or manifest evidence
