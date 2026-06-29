from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = RESULTS / "maniskill_render_machine_qualification.json"
OUT_MD = RESULTS / "maniskill_render_machine_qualification.md"
OUT_PACKET = EXTERNAL / "render_machine_qualification_packet.md"
VERSION = "maniskill_render_machine_qualification_v1"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def primary_env_ids(bindings: dict[str, Any]) -> list[str]:
    envs: list[str] = []
    for row in bindings.get("bindings", []) or []:
        if not isinstance(row, dict):
            continue
        env_id = str(row.get("primary_env_id", "")).strip()
        if env_id:
            envs.append(env_id)
    return envs


def render_records(preflight: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("records", "env_records", "environment_results"):
        records = preflight.get(key)
        if isinstance(records, list):
            return [record for record in records if isinstance(record, dict)]
    return []


def fallback_count(liveness: dict[str, Any]) -> int:
    value = liveness.get("diagnostic_video_fallbacks", 0)
    if isinstance(value, list):
        return len(value)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def classify_state(preflight: dict[str, Any], liveness: dict[str, Any], expected_envs: list[str]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    records = render_records(preflight)
    by_env = {str(record.get("env_id", "")): record for record in records}
    if preflight.get("render_video_ready") is not True:
        blockers.append("render_video_ready is false in results/maniskill_render_video_preflight_audit.json")
    for env_id in expected_envs:
        record = by_env.get(env_id)
        if not record:
            blockers.append(f"missing render preflight record for {env_id}")
            continue
        if record.get("render_video_ready") is not True:
            error = str(record.get("error", "") or "unknown render failure")
            blockers.append(f"{env_id} has no render-backed MP4: {error}")
        if record.get("mp4_ok") is not True:
            blockers.append(f"{env_id} did not write a renderer-backed MP4")
    if liveness.get("pilot_runtime_ready") is not True:
        blockers.append("pilot runtime liveness is not ready on the selected machine")
    if fallback_count(liveness) != 0:
        blockers.append("pilot runtime used diagnostic fallback video; fallback media cannot count as external evidence")
    if liveness.get("render_video_ready") is not True:
        blockers.append("pilot runtime render_video_ready is false")
    return ("QUALIFIED_FOR_RENDER_BACKED_PILOT" if not blockers else "DO_NOT_COLLECT_RENDER_MACHINE", blockers)


def renderer_failure_classes(preflight: dict[str, Any]) -> list[str]:
    classes = preflight.get("renderer_failure_classes", [])
    if isinstance(classes, list):
        return sorted({str(item) for item in classes if str(item).strip()})
    return []


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# ManiSkill Render Machine Qualification",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Qualification state: `{payload['qualification_state']}`.",
        f"Render machine qualified: `{str(payload['render_machine_qualified']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Renderer failure classes: `{payload['renderer_failure_classes']}`.",
        "",
        "This packet is an operator gate for the exact machine that will collect render-backed videos. It does not run collection, does not write `external_validation/manifest.json`, and does not turn diagnostic fallback videos into evidence.",
        "",
        "## Required Proof Before Official Collection",
        "",
        "- `results/external_platform_probe.json` must describe the exact accepted collection machine.",
        "- `results/maniskill_render_video_preflight_audit.json` must report render-backed MP4 success for every primary task family on that machine.",
        "- `results/maniskill_pilot_runtime_liveness_audit.json` must report `pilot_runtime_ready=true`, `render_video_ready=true`, and zero diagnostic fallback videos.",
        "- The independent operator must reference these artifacts in the fidelity acceptance materializer before official collection.",
        "",
    ]
    if payload["blocking_missing"]:
        lines.extend(["## Blocking Missing", ""])
        for item in payload["blocking_missing"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## Operator Commands", ""])
    for command in payload["operator_commands"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_PACKET.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    preflight = read_json(RESULTS / "maniskill_render_video_preflight_audit.json")
    liveness = read_json(RESULTS / "maniskill_pilot_runtime_liveness_audit.json")
    bindings = read_json(EXTERNAL / "maniskill_task_bindings.json")

    expected_envs = primary_env_ids(bindings)
    records = render_records(preflight)
    state, blockers = classify_state(preflight, liveness, expected_envs)
    failure_classes = renderer_failure_classes(preflight)
    checks: list[dict[str, Any]] = []

    add_check(checks, "qualification_packet_is_non_evidence", True, "this script writes only packet/audit files")
    add_check(
        checks,
        "source_audits_loaded",
        bool(platform_probe and preflight and liveness and expected_envs),
        f"expected_envs={expected_envs}",
    )
    add_check(
        checks,
        "render_preflight_remains_non_evidence",
        preflight.get("not_external_evidence") is True and preflight.get("strict_external_evidence_ready") is False,
        f"not_external_evidence={preflight.get('not_external_evidence')}, strict={preflight.get('strict_external_evidence_ready')}",
    )
    add_check(
        checks,
        "all_primary_envs_have_terminal_render_records",
        all(any(str(record.get("env_id")) == env_id for record in records) for env_id in expected_envs),
        f"records={len(records)}, expected={expected_envs}",
    )
    add_check(
        checks,
        "qualification_state_matches_render_and_liveness",
        (state == "QUALIFIED_FOR_RENDER_BACKED_PILOT") == (len(blockers) == 0),
        f"state={state}, blockers={len(blockers)}",
    )
    add_check(
        checks,
        "current_machine_fail_closed_when_render_not_ready",
        state == "DO_NOT_COLLECT_RENDER_MACHINE" or preflight.get("render_video_ready") is True,
        f"state={state}, render_video_ready={preflight.get('render_video_ready')}",
    )
    add_check(
        checks,
        "renderer_failure_classes_propagated",
        preflight.get("render_video_ready") is True or bool(failure_classes),
        f"failure_classes={failure_classes}",
    )
    add_check(
        checks,
        "diagnostic_fallbacks_block_evidence",
        fallback_count(liveness) == 0 or state == "DO_NOT_COLLECT_RENDER_MACHINE",
        f"diagnostic_fallbacks={fallback_count(liveness)}, state={state}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent before real evidence",
    )

    operator_commands = [
        "python scripts\\probe_external_platform.py",
        "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64",
        "python scripts\\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 180",
        "python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write",
        "python scripts\\audit_external_collection_readiness.py --strict --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --run-id <accepted_run_id> --unsealed-alias-map",
    ]
    add_check(
        checks,
        "operator_commands_cover_platform_render_liveness_acceptance_and_collection_readiness",
        all(
            any(term in command for command in operator_commands)
            for term in (
                "probe_external_platform.py",
                "audit_maniskill_render_video_preflight.py",
                "audit_maniskill_pilot_runtime_liveness.py",
                "materialize_fidelity_acceptance.py",
                "audit_external_collection_readiness.py",
            )
        ),
        "operator qualification commands are present",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "qualification_state": state,
        "render_machine_qualified": state == "QUALIFIED_FOR_RENDER_BACKED_PILOT",
        "renderer_failure_classes": failure_classes,
        "timeout_diagnosis_record_count": len(preflight.get("timeout_diagnosis_records", []) or []),
        "expected_primary_envs": expected_envs,
        "render_records_seen": len(records),
        "blocking_missing": blockers,
        "source_artifacts": [
            rel(RESULTS / "external_platform_probe.json"),
            rel(RESULTS / "maniskill_render_video_preflight_audit.json"),
            rel(RESULTS / "maniskill_pilot_runtime_liveness_audit.json"),
            rel(EXTERNAL / "maniskill_task_bindings.json"),
        ],
        "operator_commands": operator_commands,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    write_outputs(payload)
    print(
        "ManiSkill render machine qualification: "
        f"{'PASS' if passed else 'FAIL'}; state={state}; blockers={len(blockers)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_PACKET}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
