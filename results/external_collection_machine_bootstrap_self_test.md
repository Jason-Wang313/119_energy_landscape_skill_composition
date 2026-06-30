# External Collection Machine Bootstrap Self-Test

Passed: `true`.
Not evidence: `true`.
Strict external evidence ready: `false`.
Temporary fixture ready: `true`.
Missing source rejected: `true`.
Source evidence drift rejected: `true`.
Collection-job go-state rejected: `true`.
Local machine promotion rejected: `true`.
Unsafe command rejected: `true`.
Missing confirmation rejected: `true`.
Install guidance drift rejected: `true`.
Premature outputs rejected: `true`.
Real bootstrap outputs untouched: `true`.

This is a tooling-only mutation test. It rebuilds the collection-machine bootstrap packet in temporary copied workspaces, then proves missing source reports, source non-evidence drift, premature collection-job go-state, local render-machine promotion, unsafe evidence-writing commands, missing explicit confirmation, install-guidance drift, and premature manifest/log/video outputs fail closed without touching the real bootstrap packet.

## Checks

- `pass` `temporary_fixture_builds_current_bootstrap_packet`: status=0, state='READY_TO_BOOTSTRAP_EXTERNAL_MACHINE', steps=7
- `pass` `missing_source_report_rejected`: status=1, error='missing results/external_platform_onboarding_audit.json'
- `pass` `source_non_evidence_drift_rejected`: status=1, source_check=False
- `pass` `collection_job_go_state_rejected`: status=1, job_check=False
- `pass` `local_machine_promotion_rejected`: status=1, local_machine_check=False
- `pass` `unsafe_command_rejected`: status=1, probe_only_check=False
- `pass` `missing_confirmation_rejected`: status=1, confirmation_check=False
- `pass` `install_guidance_drift_rejected`: status=1, install_check=False
- `pass` `premature_outputs_rejected`: status=1, no_outputs_check=False
- `pass` `real_repository_bootstrap_outputs_untouched`: before={'external_validation/collection_machine_bootstrap.json': '4dabfef074b1dfca43723a415300e5ecaf969ba57928496e9928787ddb65edee', 'external_validation/collection_machine_bootstrap.md': '05adb92a7dbd845061f7575cce5ed32412f9afff37574029e6b7e3204af9c848', 'external_validation/collection_machine_bootstrap.ps1': 'b50b58b3a30ae2f73bbd647e844d026e75e1750a0b4e43b55ccc6f99c48e166d', 'external_validation/collection_machine_bootstrap.sh': 'e5046e68d3ad2bc624b74f3cc361ad93d76d1979733abde50911dae704f17268', 'results/external_collection_machine_bootstrap_audit.json': '042037ef9223c6555ff9515d4d51112cfe550111444fab4ef126fccc593de8bf', 'results/external_collection_machine_bootstrap_audit.md': '1cb439e9f005b4fa17fd46288cfc168dac16165e38d3bc6e5b62aec3c48ffab0'}, after={'external_validation/collection_machine_bootstrap.json': '4dabfef074b1dfca43723a415300e5ecaf969ba57928496e9928787ddb65edee', 'external_validation/collection_machine_bootstrap.md': '05adb92a7dbd845061f7575cce5ed32412f9afff37574029e6b7e3204af9c848', 'external_validation/collection_machine_bootstrap.ps1': 'b50b58b3a30ae2f73bbd647e844d026e75e1750a0b4e43b55ccc6f99c48e166d', 'external_validation/collection_machine_bootstrap.sh': 'e5046e68d3ad2bc624b74f3cc361ad93d76d1979733abde50911dae704f17268', 'results/external_collection_machine_bootstrap_audit.json': '042037ef9223c6555ff9515d4d51112cfe550111444fab4ef126fccc593de8bf', 'results/external_collection_machine_bootstrap_audit.md': '1cb439e9f005b4fa17fd46288cfc168dac16165e38d3bc6e5b62aec3c48ffab0'}
