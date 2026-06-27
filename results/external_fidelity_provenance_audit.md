# External Fidelity Provenance Audit

Passed: `true`.
Not evidence: `true`.
Fidelity provenance packet ready: `true`.
Strict fidelity evidence ready: `false`.
Blocking missing items: `14`.

This audit checks that the platform fidelity/provenance packet is complete as an operator checklist while strict fidelity and external evidence gates remain fail-closed.

## Checks

- `pass` `packet_is_non_evidence_and_fail_closed`: not_external_evidence=True, strict_fidelity_evidence_ready=False, strict_external_evidence_ready=False
- `pass` `fidelity_acceptance_contract_ready_but_not_evidence`: acceptance_ready=False, blocking_missing_count=14
- `pass` `platform_onboarding_packet_ready`: platform_onboarding_ready=True, strict_evidence_ready=False
- `pass` `independent_route_and_collection_still_fail_closed`: primary_route='maniskill_sapien_primary', collection_ready=False
- `pass` `template_declares_required_platform_and_gate_fields`: platform_fields=12, qualification_fields=14, gates=5, tasks=4
- `pass` `work_orders_cover_fidelity_blockers`: missing_orders=[]
- `pass` `strict_commands_cover_fidelity_manifest_collection_and_evidence`: python scripts\build_external_fidelity_provenance_packet.py
python scripts\build_external_platform_onboarding.py
python scripts\audit_external_fidelity_acceptance.py --strict
python scripts\build_external_manifest.py --write --check-video-paths
python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map
python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict
python scripts\audit_external_evidence.py --strict
- `pass` `acceptance_template_not_real_evidence`: version='paper119_fidelity_acceptance_template_v1', template_only=True
- `pass` `no_real_acceptance_or_manifest_written`: acceptance_exists=False, manifest_exists=False
- `pass` `packet_files_written`: packet_json=True, packet_md=True, csv=True
