# External Platform Onboarding Audit

Passed: `true`.
Not evidence: `true`.
Platform onboarding ready: `true`.
Strict evidence ready: `false`.

This audit checks that the public-simulator onboarding packet is specific enough for an independent operator while still remaining non-evidence.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_evidence_ready=False
- `pass` `primary_route_matches_independent_plan`: primary_route='maniskill_sapien_primary'
- `pass` `task_onboarding_covers_collection_plan`: tasks=['cable_route_insert', 'door_open_navigation', 'drawer_to_pick_transfer', 'peg_place_regrasp']
- `pass` `record_budget_preserved`: planned_records=1440
- `pass` `all_remaining_blockers_addressed`: addressed=['manifest_backed_external_evidence', 'raw_jsonl_metric_recompute', 'real_task_configs', 'independent_non_oracle_baselines']
- `pass` `official_sources_are_primary_and_currently_checked`: source_urls=['https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html', 'https://sapien.ucsd.edu/docs/latest/index.html', 'https://robosuite.ai/docs/installation.html', 'https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/index.html', 'https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html']
- `pass` `platform_provenance_fields_cover_fidelity_hashes_and_observations`: missing=[]
- `pass` `platform_probe_report_ready`: primary_route_install_ready=True, missing=[]
- `pass` `primary_install_probe_has_machine_probe_command`: install_probe={'install_command_from_official_docs': 'python -m pip install --upgrade mani_skill; python -m pip install torch torchvision torchaudio', 'version_capture_command': 'python -c "import platform, torch, mani_skill, sapien; print(platform.platform()); print(torch.__version__); print(getattr(mani_skill, \'__version__\', \'unknown\')); print(getattr(sapien, \'__version__\', \'unknown\'))"', 'machine_probe_command': 'python scripts\\probe_external_platform.py', 'strict_machine_probe_command': 'python scripts\\probe_external_platform.py --strict', 'task_binding_probe_command': 'python scripts\\probe_maniskill_task_bindings.py', 'strict_task_binding_probe_command': 'python scripts\\probe_maniskill_task_bindings.py --strict', 'latest_task_binding_probe_report': 'results/maniskill_task_binding_probe.json', 'latest_task_binding_install_ready': True, 'latest_task_binding_missing_env_ids': [], 'latest_probe_report': 'results/external_platform_probe.json', 'latest_probe_install_ready': True, 'latest_probe_missing_packages': [], 'local_status': 'probe is non-evidence; operator must rerun it on the selected GPU workstation and record exact versions in fidelity_acceptance.json'}
- `pass` `task_binding_probe_report_ready`: strict_task_binding_install_ready=True, missing=[]
- `pass` `strict_command_includes_build_external_platform_onboarding`: build_external_platform_onboarding.py
- `pass` `strict_command_includes_probe_external_platform`: probe_external_platform.py --strict
- `pass` `strict_command_includes_probe_maniskill_task_bindings`: probe_maniskill_task_bindings.py --strict
- `pass` `strict_command_includes_audit_external_backend_contract`: audit_external_backend_contract.py --strict
- `pass` `strict_command_includes_materialize_external_configs`: materialize_external_configs.py
- `pass` `strict_command_includes_validate_external_configs`: validate_external_configs.py --strict
- `pass` `strict_command_includes_audit_external_fidelity_acceptance`: audit_external_fidelity_acceptance.py --strict
- `pass` `strict_command_includes_audit_external_collection_readiness`: audit_external_collection_readiness.py --strict
- `pass` `strict_command_includes_real_collection_runner`: real_collection_runner.py
- `pass` `strict_command_includes_build_external_manifest`: build_external_manifest.py --write --check-video-paths
- `pass` `strict_command_includes_validate_external_rollouts`: validate_external_rollouts.py
- `pass` `strict_command_includes_audit_external_pairing_integrity`: audit_external_pairing_integrity.py --strict
- `pass` `strict_command_includes_audit_external_release_package`: audit_external_release_package.py --strict
- `pass` `strict_command_includes_audit_external_evidence`: audit_external_evidence.py --strict
- `pass` `pilot_sequence_preserves_gate_order`: pilot_sequence=['Run the dry-run packet check without writing logs or videos.', 'Run strict backend qualification against the non-template backend module.', 'Materialize real task configs only with --confirm-real-platform --write after platform values are known.', 'Fill external_validation/fidelity_acceptance.json with platform, simulator, contact, observation, and task-fidelity provenance.', 'Run strict collection readiness with a specific immutable run id and explicit alias unsealing.', 'Collect the full 1,440-record blinded paired-reset panel only after strict readiness passes.', 'Build the manifest and run strict rollout, pairing, release-package, and evidence audits from raw logs.']
- `pass` `packet_files_written`: packet_json=True, packet_md=True
