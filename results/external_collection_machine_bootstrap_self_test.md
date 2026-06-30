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
- `pass` `real_repository_bootstrap_outputs_untouched`: before={'external_validation/collection_machine_bootstrap.json': '5bfaa5dfa12c2693810b0e4546611cdc61bd69861d45d32613e47c4f18f72d85', 'external_validation/collection_machine_bootstrap.md': '89c65b68674f88b4b66392d0d9c96ce5af97cebbe673b558cd8339f9ff7d279e', 'external_validation/collection_machine_bootstrap.ps1': 'b50b58b3a30ae2f73bbd647e844d026e75e1750a0b4e43b55ccc6f99c48e166d', 'results/external_collection_machine_bootstrap_audit.json': 'bef70cc831c395f5fca3b1f2d6838362abde77ec09b1687c27c01d445338eab6', 'results/external_collection_machine_bootstrap_audit.md': '3ae8ef1988c040bdd2ff165d79d8d9b92174317e080c1b9d7ca0db0ea985565a'}, after={'external_validation/collection_machine_bootstrap.json': '5bfaa5dfa12c2693810b0e4546611cdc61bd69861d45d32613e47c4f18f72d85', 'external_validation/collection_machine_bootstrap.md': '89c65b68674f88b4b66392d0d9c96ce5af97cebbe673b558cd8339f9ff7d279e', 'external_validation/collection_machine_bootstrap.ps1': 'b50b58b3a30ae2f73bbd647e844d026e75e1750a0b4e43b55ccc6f99c48e166d', 'results/external_collection_machine_bootstrap_audit.json': 'bef70cc831c395f5fca3b1f2d6838362abde77ec09b1687c27c01d445338eab6', 'results/external_collection_machine_bootstrap_audit.md': '3ae8ef1988c040bdd2ff165d79d8d9b92174317e080c1b9d7ca0db0ea985565a'}
