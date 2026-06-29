# External Release Package Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic release package ready: `true`.

This self-test builds temporary manifest-declared release artifacts and exercises the external release-package hash gate directly. It proves complete synthetic artifacts can pass, missing manifests fail, local-dry-run/template/scaffold/placeholder artifacts plus staged/backup/diagnostic/fallback log-video artifacts, empty video directories, and non-MP4-like video artifacts are rejected as evidence, and the real release-package audit report is not overwritten.

## Checks

- `pass` `synthetic_release_package_passes`: ready=True, counts={'code': 1, 'configs': 1, 'logs': 1, 'videos': 1, 'checkpoints': 1}
- `pass` `missing_manifest_fails_release_readiness`: ready=False, blockers=['external_validation/manifest.json has not been written from real evidence']
- `pass` `bad_artifacts_rejected_as_release_evidence`: blocking_fragments_present=True, blockers=20
- `pass` `release_hashes_are_recomputed`: entries=5
- `pass` `real_release_package_report_not_overwritten`: before=d760b589bd12aa51882d2c99b501475a6103fcabafcf86a6e1744f9235e91278, after=d760b589bd12aa51882d2c99b501475a6103fcabafcf86a6e1744f9235e91278
