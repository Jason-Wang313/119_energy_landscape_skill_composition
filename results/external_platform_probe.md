# External Platform Probe

Passed: `true`.
Not evidence: `true`.
Primary route: `maniskill_sapien_primary`.
Primary route install ready: `true`.
Strict fidelity evidence ready: `false`.
Strict external evidence ready: `false`.

This probe records operator-machine environment facts for the independent public-simulator route. It is not rollout evidence and cannot make the paper submission-ready by itself.

## Primary Package Status

- `gymnasium`: module_available=`true`, version=`1.2.3`
- `mani_skill`: module_available=`true`, version=`3.0.1`
- `sapien`: module_available=`true`, version=`3.0.3`
- `torch`: module_available=`true`, version=`2.10.0`

## Environment

- `python_executable`: `C:\Users\wangz\AppData\Local\Programs\Python\Python310\python.exe`
- `python_version`: `3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]`
- `platform`: `Windows-10-10.0.26200-SP0`
- `machine`: `AMD64`

## GPU/Renderer Commands

- `nvidia_smi`: available=`false`, returncode=`None`
- `vulkaninfo_summary`: available=`true`, returncode=`0`

## Operator Next Steps

- Run this probe on the selected external GPU workstation.
- If primary_route_install_ready is false, install/repair ManiSkill, SAPIEN, Torch, and Gymnasium before backend qualification.
- Copy exact package, GPU, renderer, code commit, config hash, and backend hash values into external_validation/fidelity_acceptance.json.
- Then run python scripts\audit_external_fidelity_acceptance.py --strict and python scripts\audit_external_collection_readiness.py --strict with the real backend.

## Checks

- `pass` `probe_is_non_evidence`: not_external_evidence=True
- `pass` `primary_route_declared`: maniskill_sapien_primary
- `pass` `primary_packages_checked`: checked=['gymnasium', 'isaaclab', 'isaacsim', 'mani_skill', 'mujoco', 'robosuite', 'sapien', 'torch']
- `pass` `primary_install_readiness_reported`: primary_missing=[]
- `pass` `repo_commit_reported`: commit='ee132b3031cc8dedf8219ff6e23bd448047da4a8'
- `pass` `required_hashes_recorded`: missing=[]
- `pass` `gpu_renderer_commands_attempted`: commands=['nvidia_smi', 'vulkaninfo_summary']
- `pass` `strict_evidence_remains_false`: probe cannot satisfy external fidelity or rollout evidence
