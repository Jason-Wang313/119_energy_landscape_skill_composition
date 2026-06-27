# External Backend Contract Audit

Passed: `true`.
Strict: `false`.
Not evidence: `true`.
Backend contract harness ready: `true`.
Actual backend ready: `false`.

This audit checks the backend module contract before any real robot or high-fidelity simulator collection starts. It is not rollout evidence and does not replace fidelity acceptance, JSONL logs, videos, manifests, or strict external-evidence audits.

## Strict Command

```powershell
python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json
```

## Blocking Missing

- backend_module_supplied: --backend-module not supplied

## Checks

- `pass` `backend_contract_file_exists`: external_validation/runner/backend_contract.py
- `pass` `backend_contract_mentions_required_backend_api`: REQUIRED_BACKEND_API
- `pass` `backend_contract_mentions_base_class`: ExternalCollectionBackend
- `pass` `backend_contract_mentions_validator`: validate_backend_object
- `pass` `backend_contract_mentions_base_implementation_rejection`: backend uses base NotImplementedError implementation
- `pass` `backend_templates_fail_closed`: templates=4, errors=[]
- `pass` `runner_readme_declares_backend_audit`: README documents backend qualification audit
- `pass` `contract_accepts_complete_synthetic_backend`: complete backend passed
- `pass` `contract_rejects_incomplete_synthetic_backend`: backend uses base NotImplementedError implementation for load_task_config; backend uses base NotImplementedError implementation for reset_scene; backend uses base NotImplementedError implementation for capture_observation; backend uses base NotImplementedError implementation for terminal_samples; backend uses base NotImplementedError implementation for run_method; backend uses base NotImplementedError implementation for execute_skill_pair; backend uses base NotImplementedError implementation for record_video; backend uses base NotImplementedError implementation for policy_or_config_hash
- `fail` `backend_module_supplied`: --backend-module not supplied
