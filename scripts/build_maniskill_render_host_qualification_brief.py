from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = RESULTS / "maniskill_render_host_qualification_brief_audit.json"
OUT_AUDIT_MD = RESULTS / "maniskill_render_host_qualification_brief_audit.md"
OUT_DOCS = DOCS / "maniskill_render_host_qualification_brief.md"
OUT_EXTERNAL = EXTERNAL / "render_host_qualification_brief.md"

VERSION = "maniskill_render_host_qualification_brief_v1"
SOURCE_CHECK_DATE = "2026-06-30"

OFFICIAL_SOURCES = [
    {
        "name": "ManiSkill installation docs",
        "url": "https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html",
        "operator_note": "Use this as the install and supported-environment anchor before rerunning render probes.",
    },
    {
        "name": "SAPIEN documentation",
        "url": "https://sapien.ucsd.edu/docs/latest/index.html",
        "operator_note": "Record the exact SAPIEN version, renderer, GPU/Vulkan path, and scene/render settings.",
    },
    {
        "name": "Vulkan vkAllocateDescriptorSets reference",
        "url": "https://registry.khronos.org/vulkan/specs/latest/man/html/vkAllocateDescriptorSets.html",
        "operator_note": "The current failure signature is a descriptor-pool allocation failure surfaced through SAPIEN/Vulkan.",
    },
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def render_records(preflight: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("env_records", "records", "environment_results"):
        records = preflight.get(key)
        if isinstance(records, list):
            return [record for record in records if isinstance(record, dict)]
    return []


def unique_text(items: list[Any]) -> list[str]:
    return sorted({str(item).strip() for item in items if str(item).strip()})


def diagnostic_fallback_count(liveness: dict[str, Any]) -> int:
    value = liveness.get("diagnostic_video_fallbacks", 0)
    if isinstance(value, list):
        return len(value)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def collect_error_signatures(*payloads: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for payload in payloads:
        for record_key in ("env_records", "records", "environment_results"):
            for record in as_list(payload.get(record_key)):
                if isinstance(record, dict):
                    error = str(record.get("error", "")).strip()
                    if error:
                        errors.append(error)
        for stage in as_list(payload.get("backend_progress_stages")):
            if isinstance(stage, dict):
                error = str(stage.get("render_error", "")).strip()
                if error:
                    errors.append(error.replace("RuntimeError: ", ""))
        for error in as_list(payload.get("liveness_render_errors")):
            errors.append(str(error).replace("RuntimeError: ", "").strip())
    return unique_text(errors)


def resource_sweep_failures(resource_sweep: dict[str, Any]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for record in as_list(resource_sweep.get("records")):
        if not isinstance(record, dict):
            continue
        if record.get("mp4_ok") is True:
            continue
        failures.append(
            {
                "profile": str(record.get("profile", "")).strip(),
                "env_id": str(record.get("env_id", "")).strip(),
                "error": str(record.get("error", "")).strip(),
                "failure_progress_stage": str(record.get("failure_progress_stage", "")).strip(),
                "last_progress_stage": str(record.get("last_progress_stage", "")).strip(),
            }
        )
    return failures


def build_payload() -> dict[str, Any]:
    render_machine = read_json(RESULTS / "maniskill_render_machine_qualification.json")
    preflight = read_json(RESULTS / "maniskill_render_video_preflight_audit.json")
    resource_sweep = read_json(RESULTS / "maniskill_render_resource_sweep.json")
    liveness = read_json(RESULTS / "maniskill_pilot_runtime_liveness_audit.json")
    remediation = read_json(RESULTS / "maniskill_render_failure_remediation.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    bindings = read_json(EXTERNAL / "maniskill_task_bindings.json")

    failure_classes = unique_text(
        as_list(render_machine.get("renderer_failure_classes"))
        + as_list(preflight.get("renderer_failure_classes"))
        + as_list(resource_sweep.get("renderer_failure_classes"))
    )
    failure_stages = unique_text(
        as_list(render_machine.get("renderer_failure_stages")) + as_list(preflight.get("renderer_failure_stages"))
    )
    errors = collect_error_signatures(preflight, resource_sweep, liveness, remediation)
    sweep_failures = resource_sweep_failures(resource_sweep)
    expected_envs = unique_text(as_list(render_machine.get("expected_primary_envs")))

    host_requirements = [
        "Run on an independent GPU/Vulkan-capable collection machine rather than the current local host.",
        "Capture exact OS, Python, package, GPU, driver, Vulkan, ManiSkill, SAPIEN, code commit, and config/backend hashes with the strict platform probe.",
        "Pass render-backed MP4 preflight for every primary task-family environment using the accepted render backend and shader pack.",
        "Pass bounded pilot runtime liveness with JSONL writer ready, render_video_ready=true, runner_io_ready=true, and zero diagnostic fallback videos.",
        "Only after those pass, materialize fidelity acceptance and rerun strict collection readiness; do not write external_validation/manifest.json beforehand.",
    ]
    acceptance_criteria = [
        "results/maniskill_render_machine_qualification.json reports qualification_state=QUALIFIED_FOR_RENDER_BACKED_PILOT and render_machine_qualified=true on the accepted machine.",
        "results/maniskill_render_video_preflight_audit.json reports render_video_ready=true and render-backed MP4 success for PegInsertionSide-v1, OpenCabinetDrawer-v1, OpenCabinetDoor-v1, and PullCubeTool-v1.",
        "results/maniskill_pilot_runtime_liveness_audit.json reports pilot_runtime_ready=true, render_video_ready=true, runner_io_ready=true, records_observed>=1, videos_written>=1, and diagnostic_video_fallbacks=0.",
        "The official video guard remains enabled and no diagnostic fallback, staging, placeholder, or local dry-run media enters external_validation/manifest.json.",
        "Fidelity acceptance and collection readiness pass after render qualification; strict external evidence remains false until real manifest-declared logs, videos, configs, baselines, and recomputed metrics pass.",
    ]
    operator_commands = [
        "python scripts\\probe_external_platform.py --strict",
        "python scripts\\audit_maniskill_render_resource_sweep.py --timeout-seconds 45 --max-envs 1",
        "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64",
        "python scripts\\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --render-width 128 --render-height 128",
        "python scripts\\build_maniskill_render_machine_qualification.py",
        "python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write",
        "python scripts\\audit_external_collection_readiness.py --strict --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --run-id <accepted_run_id> --unsealed-alias-map",
    ]

    checks: list[dict[str, Any]] = []
    add_check(checks, "brief_is_non_evidence", True, "brief is an operator qualification artifact only")
    add_check(
        checks,
        "current_render_host_fails_closed",
        render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and preflight.get("render_video_ready") is False,
        (
            f"qualification_state={render_machine.get('qualification_state')!r}, "
            f"render_machine_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"render_video_ready={preflight.get('render_video_ready')!r}"
        ),
    )
    add_check(
        checks,
        "vulkan_descriptor_pool_failure_preserved",
        "vulkan_descriptor_pool_exhaustion" in failure_classes
        and "initial_render_start" in failure_stages
        and any("ErrorOutOfPoolMemory" in error for error in errors),
        f"classes={failure_classes}, stages={failure_stages}, errors={errors}",
    )
    add_check(
        checks,
        "minimum_resource_sweep_preserved",
        resource_sweep.get("descriptor_pool_failure_persists_at_minimum_resolution") is True
        and len(sweep_failures) >= 3
        and all("16x16" in item["profile"] for item in sweep_failures[:3]),
        f"sweep_failures={sweep_failures[:3]}",
    )
    add_check(
        checks,
        "pilot_liveness_guard_preserved",
        liveness.get("pilot_runtime_ready") is False
        and liveness.get("render_video_ready") is False
        and liveness.get("official_video_guard_blocked_diagnostic_fallback") is True
        and diagnostic_fallback_count(liveness) >= 1,
        (
            f"pilot_runtime_ready={liveness.get('pilot_runtime_ready')!r}, "
            f"render_video_ready={liveness.get('render_video_ready')!r}, "
            f"guard={liveness.get('official_video_guard_blocked_diagnostic_fallback')!r}, "
            f"fallbacks={diagnostic_fallback_count(liveness)}"
        ),
    )
    add_check(
        checks,
        "official_source_urls_present",
        any("maniskill.readthedocs.io" in item["url"] for item in OFFICIAL_SOURCES)
        and any("sapien.ucsd.edu" in item["url"] for item in OFFICIAL_SOURCES)
        and any("registry.khronos.org" in item["url"] for item in OFFICIAL_SOURCES),
        f"source_check_date={SOURCE_CHECK_DATE}",
    )
    add_check(
        checks,
        "operator_commands_cover_probe_sweep_preflight_liveness_qualification",
        all(
            any(fragment in command for command in operator_commands)
            for fragment in (
                "probe_external_platform.py --strict",
                "audit_maniskill_render_resource_sweep.py",
                "audit_maniskill_render_video_preflight.py",
                "audit_maniskill_pilot_runtime_liveness.py",
                "build_maniskill_render_machine_qualification.py",
                "materialize_fidelity_acceptance.py",
                "audit_external_collection_readiness.py --strict",
            )
        ),
        "operator command spine covers host probe, render sweep, render preflight, pilot liveness, qualification, fidelity acceptance, and collection readiness",
    )
    add_check(
        checks,
        "acceptance_criteria_close_all_render_host_gates",
        all(
            any(term in criterion for criterion in acceptance_criteria)
            for term in (
                "QUALIFIED_FOR_RENDER_BACKED_PILOT",
                "render_video_ready=true",
                "pilot_runtime_ready=true",
                "diagnostic fallback",
                "strict external evidence remains false",
            )
        ),
        f"criteria={len(acceptance_criteria)}",
    )
    add_check(
        checks,
        "haonan_is_not_a_dependency",
        True,
        "brief requires independent operator evidence and does not depend on Haonan or Yilun",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "host_qualification_state": "RENDER_HOST_NOT_QUALIFIED"
        if render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        else "RENDER_HOST_READY_FOR_PILOT",
        "collection_state": render_machine.get("qualification_state"),
        "render_machine_qualified": render_machine.get("render_machine_qualified"),
        "render_video_ready": preflight.get("render_video_ready"),
        "pilot_runtime_ready": liveness.get("pilot_runtime_ready"),
        "runner_io_ready": liveness.get("runner_io_ready"),
        "diagnostic_video_fallback_count": diagnostic_fallback_count(liveness),
        "renderer_failure_classes": failure_classes,
        "renderer_failure_stages": failure_stages,
        "error_signatures": errors,
        "minimum_resource_sweep_failures": sweep_failures,
        "expected_primary_envs": expected_envs,
        "host_requirements": host_requirements,
        "acceptance_criteria": acceptance_criteria,
        "operator_commands": operator_commands,
        "official_sources": OFFICIAL_SOURCES,
        "source_check_date": SOURCE_CHECK_DATE,
        "haonan_dependency": False,
        "source_artifacts": [
            rel(RESULTS / "maniskill_render_machine_qualification.json"),
            rel(RESULTS / "maniskill_render_video_preflight_audit.json"),
            rel(RESULTS / "maniskill_render_resource_sweep.json"),
            rel(RESULTS / "maniskill_pilot_runtime_liveness_audit.json"),
            rel(RESULTS / "maniskill_render_failure_remediation.json"),
            rel(RESULTS / "external_platform_probe.json"),
            rel(EXTERNAL / "maniskill_task_bindings.json"),
        ],
        "platform_probe_install_ready": platform_probe.get("install_ready"),
        "task_binding_rows": len(as_list(bindings.get("bindings"))),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def build_operator_brief(payload: dict[str, Any]) -> str:
    lines = [
        "# ManiSkill Render Host Qualification Brief",
        "",
        "This is a non-evidence operator brief for the Paper 119 skill-seam world/action-model validation route. It explains why the current local render host must not collect evidence and what a replacement host must prove before official collection can begin.",
        "",
        f"State: `{payload['host_qualification_state']}`.",
        f"Collection gate: `{payload['collection_state']}`.",
        f"Render machine qualified: `{str(payload['render_machine_qualified']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Haonan dependency: `{str(payload['haonan_dependency']).lower()}`.",
        "",
        "## Current No-Go",
        "",
        f"- Renderer failure classes: `{payload['renderer_failure_classes']}`",
        f"- Renderer failure stages: `{payload['renderer_failure_stages']}`",
        f"- Error signatures: `{payload['error_signatures']}`",
        f"- Render video ready: `{str(payload['render_video_ready']).lower()}`",
        f"- Pilot runtime ready: `{str(payload['pilot_runtime_ready']).lower()}`",
        f"- Runner I/O ready: `{str(payload['runner_io_ready']).lower()}`",
        f"- Diagnostic fallback count: `{payload['diagnostic_video_fallback_count']}`",
        "",
        "The current local machine fails at `initial_render_start` with `vk::Device::allocateDescriptorSetsUnique: ErrorOutOfPoolMemory`. The 16x16 sweep reproduces the failure across the tested `cpu/minimal`, `gpu/minimal`, and `sapien_cuda/minimal` render profiles, so the next step is a different qualified host, not official collection on this machine.",
        "",
        "## Minimum Resource Sweep Evidence",
        "",
    ]
    for item in payload["minimum_resource_sweep_failures"]:
        lines.append(
            f"- `{item['profile']}` on `{item['env_id']}`: `{item['error']}` "
            f"(failure stage `{item['failure_progress_stage']}`, terminal stage `{item['last_progress_stage']}`)"
        )
    lines.extend(["", "## Host Requirements", ""])
    for requirement in payload["host_requirements"]:
        lines.append(f"- {requirement}")
    lines.extend(["", "## Operator Command Spine", ""])
    for command in payload["operator_commands"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Close Criteria", ""])
    for criterion in payload["acceptance_criteria"]:
        lines.append(f"- {criterion}")
    lines.extend(["", "## Official Source Anchors", ""])
    for source in payload["official_sources"]:
        lines.append(f"- {source['name']}: {source['url']} - {source['operator_note']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This brief does not produce rollout evidence, does not write `external_validation/manifest.json`, and cannot satisfy strict external evidence by itself. It is intentionally independent of Haonan/Yilun; a collaboration can improve the paper, but the validation route must stand without requiring them.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    operator_brief = build_operator_brief(payload)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_DOCS.write_text(operator_brief + "\n", encoding="utf-8")
    OUT_EXTERNAL.write_text(operator_brief + "\n", encoding="utf-8")

    lines = [
        "# ManiSkill Render Host Qualification Brief Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Host qualification state: `{payload['host_qualification_state']}`.",
        f"Collection gate: `{payload['collection_state']}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- `{rel(OUT_DOCS)}`",
            f"- `{rel(OUT_EXTERNAL)}`",
            f"- `{rel(OUT_JSON)}`",
            "",
        ]
    )
    OUT_AUDIT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        "ManiSkill render host qualification brief: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; state={payload['host_qualification_state']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_AUDIT_MD}")
    print(f"Wrote {OUT_DOCS}")
    print(f"Wrote {OUT_EXTERNAL}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
