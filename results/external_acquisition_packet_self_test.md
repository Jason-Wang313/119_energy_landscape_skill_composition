# External Acquisition Packet Self-Test

Passed: `true`.
Not evidence: `true`.
Temporary fixture ready: `true`.
Missing source rejected: `true`.
Unmapped blocker rejected: `true`.
Premature manifest rejected: `true`.
Collection readiness drift rejected: `true`.
Real acquisition outputs untouched: `true`.

This is a tooling-only mutation test. It runs the acquisition packet builder in temporary copied workspaces, proves the current no-evidence acquisition packet can be rebuilt there, and proves that missing source audits, unmapped blockers, accidental real-manifest presence, and premature collection-readiness promotion fail closed without touching the real repository packet.

## Checks

- `pass` `temporary_fixture_builds_current_acquisition_packet`: status=0, actions=35, blockers=4
- `pass` `missing_source_report_rejected`: status=1, source_check=False, collection_check=False
- `pass` `unmapped_blocker_rejected`: status=1, gap_check=False, mapped_check=False
- `pass` `premature_manifest_rejected`: status=1, no_manifest_check=False
- `pass` `collection_readiness_drift_rejected`: status=1, collection_check=False
- `pass` `real_repository_acquisition_outputs_untouched`: json_before=e979b897017d6ac8e42ec50212331a6bd599af243739889bfc06491b65c367c6, json_after=e979b897017d6ac8e42ec50212331a6bd599af243739889bfc06491b65c367c6, md_before=9bad100eecfc75c195232634de7d7eeb1bf439799b3853aedcc3549352ab9f90, md_after=9bad100eecfc75c195232634de7d7eeb1bf439799b3853aedcc3549352ab9f90
