from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_PACKET_JSON = EXTERNAL / "collection_machine_bootstrap.json"
OUT_PACKET_MD = EXTERNAL / "collection_machine_bootstrap.md"
OUT_COMMANDS = EXTERNAL / "collection_machine_bootstrap.ps1"
OUT_AUDIT_JSON = RESULTS / "external_collection_machine_bootstrap_audit.json"
OUT_AUDIT_MD = RESULTS / "external_collection_machine_bootstrap_audit.md"

VERSION = "external_collection_machine_bootstrap_v1"
AUDIT_VERSION = "external_collection_machine_bootstrap_audit_v1"

BOOTSTRAP_COMMANDS = [
    r"python scripts\probe_external_platform.py --strict",
    r"python scripts\probe_maniskill_task_bindings.py --strict",
    r"python scripts\probe_maniskill_env_smoke.py --strict",
    r"python scripts\probe_maniskill_fidelity_metadata.py --strict",
    (
        r"python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 "
        r"--width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> "
        r"--profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 "
        r"--timeout-diagnosis-width 64 --timeout-diagnosis-height 64"
    ),
    (
        r"python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180 "
        r"--render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --render-width 128 --render-height 128"
    ),
    r"python scripts\build_maniskill_render_machine_qualification.py",
]

PROBE_ONLY_FORBIDDEN_FRAGMENTS = [
    "real_collection_runner.py",
    "materialize_fidelity_acceptance.py",
    "build_external_manifest.py --write",
    "build_external_postcollection_evidence_seal.py",
    "external_validation\\logs",
    "external_validation\\videos",
    "--write",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def require_payload(path: Path, version: str) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_command_file() -> str:
    text = r"""[CmdletBinding()]
param(
    [switch]$ConfirmBootstrapOnly,
    [switch]$InstallManiSkill,
    [string]$AcceptedBackend = "sapien_cuda",
    [string]$ShaderPack = "minimal",
    [ValidateRange(30, 1800)][int]$RenderPreflightTimeoutSeconds = 120,
    [ValidateRange(30, 1800)][int]$PilotTimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

if (-not $ConfirmBootstrapOnly) {
    throw "Refusing to bootstrap silently. Re-run with -ConfirmBootstrapOnly on the independent collection machine. This script does not collect official evidence."
}

if ($InstallManiSkill) {
    Invoke-Native python -m pip install --upgrade pip
    Invoke-Native python -m pip install numpy matplotlib imageio imageio-ffmpeg
    Invoke-Native python -m pip install --upgrade mani_skill
    Invoke-Native python -m pip install torch torchvision torchaudio
}

Invoke-Native python scripts\probe_external_platform.py --strict
Invoke-Native python scripts\probe_maniskill_task_bindings.py --strict
Invoke-Native python scripts\probe_maniskill_env_smoke.py --strict
Invoke-Native python scripts\probe_maniskill_fidelity_metadata.py --strict
Invoke-Native python scripts\audit_maniskill_render_video_preflight.py --timeout-seconds $RenderPreflightTimeoutSeconds --max-envs 4 --width 128 --height 128 --render-backend $AcceptedBackend --shader-pack $ShaderPack --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64
Invoke-Native python scripts\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds $PilotTimeoutSeconds --render-backend $AcceptedBackend --shader-pack $ShaderPack --render-width 128 --render-height 128
Invoke-Native python scripts\build_maniskill_render_machine_qualification.py

Write-Host ""
Write-Host "Bootstrap probes complete. If render-machine qualification is still DO_NOT_COLLECT_RENDER_MACHINE, do not run official collection."
"""
    OUT_COMMANDS.write_text(text, encoding="utf-8")
    return text


def build_payload() -> tuple[dict[str, Any], str]:
    onboarding = require_payload(RESULTS / "external_platform_onboarding_audit.json", "external_platform_onboarding_audit_v1")
    platform_probe = require_payload(RESULTS / "external_platform_probe.json", "external_platform_probe_v1")
    task_binding = require_payload(RESULTS / "maniskill_task_binding_probe.json", "maniskill_task_binding_probe_v1")
    env_smoke = require_payload(RESULTS / "maniskill_env_smoke_probe.json", "maniskill_env_smoke_probe_v1")
    fidelity_metadata = require_payload(RESULTS / "maniskill_fidelity_metadata_probe.json", "maniskill_fidelity_metadata_probe_v1")
    render_preflight = require_payload(RESULTS / "maniskill_render_video_preflight_audit.json", "maniskill_render_video_preflight_audit_v2")
    pilot_liveness = require_payload(RESULTS / "maniskill_pilot_runtime_liveness_audit.json", "maniskill_pilot_runtime_liveness_audit_v1")
    render_machine = require_payload(RESULTS / "maniskill_render_machine_qualification.json", "maniskill_render_machine_qualification_v1")
    collection_job = require_payload(RESULTS / "external_collection_job_packet_audit.json", "external_collection_job_packet_audit_v1")
    command_text = write_command_file()

    missing_assets = sorted(set(env_smoke.get("missing_asset_ids", []) or []))
    render_failures = sorted(set(render_preflight.get("renderer_failure_classes", []) or []))
    bootstrap_steps = [
        {
            "order": index + 1,
            "command": command,
            "evidence_boundary": "non_evidence_machine_probe",
        }
        for index, command in enumerate(BOOTSTRAP_COMMANDS)
    ]
    current_local_state = {
        "primary_route_install_ready": platform_probe.get("primary_route_install_ready") is True,
        "task_binding_ready": task_binding.get("strict_task_binding_install_ready") is True,
        "env_smoke_ready": env_smoke.get("strict_env_smoke_ready") is True,
        "fidelity_metadata_ready": fidelity_metadata.get("strict_metadata_ready") is True,
        "render_video_ready": render_preflight.get("render_video_ready") is True,
        "pilot_runtime_ready": pilot_liveness.get("pilot_runtime_ready") is True,
        "render_machine_qualified": render_machine.get("render_machine_qualified") is True,
        "render_machine_state": render_machine.get("qualification_state"),
        "renderer_failure_classes": render_failures,
        "missing_asset_ids": missing_assets,
    }
    no_real_outputs = (
        not (EXTERNAL / "manifest.json").exists()
        and not any((EXTERNAL / "logs").glob("*.jsonl"))
        and not any((EXTERNAL / "videos").glob("**/*.mp4"))
    )

    checks: list[dict[str, Any]] = []
    add_check(checks, "bootstrap_packet_is_non_evidence", True, "machine bootstrap probes only; it does not write official logs, videos, manifests, or acceptance files")
    add_check(
        checks,
        "source_platform_onboarding_ready",
        onboarding.get("passed") is True
        and onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False,
        f"ready={onboarding.get('platform_onboarding_ready')!r}, strict={onboarding.get('strict_evidence_ready')!r}",
    )
    add_check(
        checks,
        "source_collection_job_still_no_go",
        collection_job.get("passed") is True
        and collection_job.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and collection_job.get("strict_external_evidence_ready") is False,
        f"job_state={collection_job.get('job_state')!r}, strict={collection_job.get('strict_external_evidence_ready')!r}",
    )
    add_check(
        checks,
        "local_machine_not_promoted",
        render_machine.get("render_machine_qualified") is False
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("strict_external_evidence_ready") is False,
        f"qualified={render_machine.get('render_machine_qualified')!r}, state={render_machine.get('qualification_state')!r}",
    )
    add_check(
        checks,
        "bootstrap_commands_cover_machine_render_and_liveness",
        all(fragment in command_text for fragment in (
            "probe_external_platform.py --strict",
            "probe_maniskill_task_bindings.py --strict",
            "probe_maniskill_env_smoke.py --strict",
            "probe_maniskill_fidelity_metadata.py --strict",
            "audit_maniskill_render_video_preflight.py",
            "audit_maniskill_pilot_runtime_liveness.py",
            "build_maniskill_render_machine_qualification.py",
        )),
        "bootstrap command file covers platform, task, env, metadata, render, pilot, and qualification probes",
    )
    forbidden_present = [fragment for fragment in PROBE_ONLY_FORBIDDEN_FRAGMENTS if fragment in command_text]
    add_check(
        checks,
        "bootstrap_script_is_probe_only",
        not forbidden_present,
        f"forbidden_fragments={forbidden_present}",
    )
    add_check(
        checks,
        "install_guidance_mentions_core_optional_stack",
        all(fragment in command_text for fragment in ("mani_skill", "torch", "imageio-ffmpeg")),
        "optional installer covers local package deps, ManiSkill/SAPIEN dependency path, Torch, and video encoding",
    )
    add_check(checks, "no_real_outputs_written", no_real_outputs, "manifest/log/video evidence files remain absent before official collection")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "bootstrap_state": "READY_TO_BOOTSTRAP_EXTERNAL_MACHINE" if passed else "BOOTSTRAP_PACKET_NEEDS_ATTENTION",
        "source_reports": [
            rel(RESULTS / "external_platform_onboarding_audit.json"),
            rel(RESULTS / "external_platform_probe.json"),
            rel(RESULTS / "maniskill_task_binding_probe.json"),
            rel(RESULTS / "maniskill_env_smoke_probe.json"),
            rel(RESULTS / "maniskill_fidelity_metadata_probe.json"),
            rel(RESULTS / "maniskill_render_video_preflight_audit.json"),
            rel(RESULTS / "maniskill_pilot_runtime_liveness_audit.json"),
            rel(RESULTS / "maniskill_render_machine_qualification.json"),
            rel(RESULTS / "external_collection_job_packet_audit.json"),
        ],
        "command_file": rel(OUT_COMMANDS),
        "bootstrap_steps": bootstrap_steps,
        "current_local_state": current_local_state,
        "operator_preconditions": [
            "Use an independent GPU/Vulkan collection machine or robot-lab machine, not the current failing local render path.",
            "Run this bootstrap before materializing fidelity acceptance or official collection.",
            "Do not proceed unless render-machine qualification reports render_machine_qualified=true and pilot_runtime_ready=true with zero diagnostic fallbacks.",
            "After bootstrap success, use the guarded collection job packet for fidelity acceptance, strict readiness, official collection, postcollection sealing, manifest promotion, and final strict audits.",
        ],
        "remaining_submission_blockers": [
            "accepted real-robot or high-fidelity simulator evidence",
            "external rollout metrics recomputed from raw JSONL logs",
            "manifest-declared real task configs",
            "manifest-declared independent non-oracle baseline evidence",
        ],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    return payload, command_text


def write_outputs(payload: dict[str, Any]) -> None:
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    OUT_PACKET_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Collection Machine Bootstrap",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Bootstrap state: `{payload['bootstrap_state']}`.",
        f"Command file: `{payload['command_file']}`.",
        "",
        "This packet prepares the independent collection machine before fidelity acceptance or official collection. It does not write `external_validation/manifest.json`, official JSONL logs, rollout videos, checkpoints, or fidelity acceptance files.",
        "",
        "## Current Local State",
        "",
    ]
    for key, value in payload["current_local_state"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Bootstrap Steps", ""])
    for step in payload["bootstrap_steps"]:
        lines.append(f"{step['order']}. `{step['command']}`")
    lines.extend(["", "## Preconditions", ""])
    for item in payload["operator_preconditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Remaining Submission Blockers", ""])
    for item in payload["remaining_submission_blockers"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    audit_payload = {**payload, "version": AUDIT_VERSION, "packet_version": payload["version"]}
    OUT_AUDIT_JSON.write_text(json.dumps(audit_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_AUDIT_MD.write_text("\n".join(lines).replace("# External Collection Machine Bootstrap", "# External Collection Machine Bootstrap Audit", 1) + "\n", encoding="utf-8")


def main() -> int:
    payload, _command_text = build_payload()
    write_outputs(payload)
    print(
        f"External collection machine bootstrap: {'PASS' if payload['passed'] else 'FAIL'}; "
        f"state={payload['bootstrap_state']}; command={payload['command_file']}"
    )
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
