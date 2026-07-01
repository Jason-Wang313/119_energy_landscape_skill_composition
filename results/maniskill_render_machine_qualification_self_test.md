# ManiSkill Render Machine Qualification Self-Test

Passed: `true`.
Not evidence: `true`.
Synthetic ready state: `QUALIFIED_FOR_RENDER_BACKED_PILOT`.
Synthetic fail-closed state: `DO_NOT_COLLECT_RENDER_MACHINE`.
Missing environment rejected: `true`.
Diagnostic fallback rejected: `true`.

This self-test exercises the render-machine qualification classifier and remediation work-order builder on synthetic payloads only. It proves a complete render-backed/liveness fixture can qualify, while render failure, missing environment records, and diagnostic fallback media fail closed before official collection. It does not run ManiSkill, does not write the real render-machine qualification reports, and is not external evidence.

## Checks

- `pass` `synthetic_ready_machine_qualifies`: state=QUALIFIED_FOR_RENDER_BACKED_PILOT, blockers=[]
- `pass` `synthetic_ready_remediation_is_ready`: state=RENDER_REMEDIATION_READY, work_orders=['collection_readiness_gate', 'diagnostic_fallback_exclusion', 'fidelity_acceptance_after_render_ready', 'pilot_liveness_retest', 'render_profile_matrix_retest', 'renderer_platform_probe']
- `pass` `render_failure_fails_closed`: state=DO_NOT_COLLECT_RENDER_MACHINE, blockers=12
- `pass` `failure_remediation_work_orders_cover_gate_sequence`: state=RENDER_REMEDIATION_REQUIRED, work_orders=['collection_readiness_gate', 'diagnostic_fallback_exclusion', 'fidelity_acceptance_after_render_ready', 'pilot_liveness_retest', 'render_profile_matrix_retest', 'renderer_platform_probe']
- `pass` `missing_environment_record_fails_closed`: blockers=['missing render preflight record for PullCubeTool-v1']
- `pass` `diagnostic_fallback_blocks_qualification`: blockers=['pilot runtime used diagnostic fallback video; fallback media cannot count as external evidence']
- `pass` `real_render_machine_reports_not_overwritten`: before={'results/maniskill_render_machine_qualification.json': '0fb486ce9aaff6b8765562d3108666ca37c0797835db062bcba77af22d153694', 'results/maniskill_render_machine_qualification.md': '93be7c5c7679ff96a46c66e8a15d2b9cf5d39e6b2f75f4c67124e2c82f0d17da', 'external_validation/render_machine_qualification_packet.md': '93be7c5c7679ff96a46c66e8a15d2b9cf5d39e6b2f75f4c67124e2c82f0d17da', 'results/maniskill_render_failure_remediation.json': 'cf66a7c0cefbcf8fe6c670b17e987419c2c8172fde900e16c2ac1a95b47953c1', 'results/maniskill_render_failure_remediation.md': '09c15b11c23c66a6feb199a6b15d7d4431d104be7bb99721a25055b554e6408b', 'external_validation/render_failure_remediation_work_orders.csv': 'a24c287ad901962080b1bb4b5d5615f62f507cf36cceb7f1fa4877a274a7d7c7'}, after={'results/maniskill_render_machine_qualification.json': '0fb486ce9aaff6b8765562d3108666ca37c0797835db062bcba77af22d153694', 'results/maniskill_render_machine_qualification.md': '93be7c5c7679ff96a46c66e8a15d2b9cf5d39e6b2f75f4c67124e2c82f0d17da', 'external_validation/render_machine_qualification_packet.md': '93be7c5c7679ff96a46c66e8a15d2b9cf5d39e6b2f75f4c67124e2c82f0d17da', 'results/maniskill_render_failure_remediation.json': 'cf66a7c0cefbcf8fe6c670b17e987419c2c8172fde900e16c2ac1a95b47953c1', 'results/maniskill_render_failure_remediation.md': '09c15b11c23c66a6feb199a6b15d7d4431d104be7bb99721a25055b554e6408b', 'external_validation/render_failure_remediation_work_orders.csv': 'a24c287ad901962080b1bb4b5d5615f62f507cf36cceb7f1fa4877a274a7d7c7'}
