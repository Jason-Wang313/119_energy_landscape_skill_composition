from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"

OUT_JSON = RESULTS / "external_operator_packet.json"
OUT_MD = RESULTS / "external_operator_packet.md"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def require_payload(path: Path, version: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def action_lookup(acquisition: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(action.get("id", "")): action
        for action in acquisition.get("operator_actions", []) or []
        if str(action.get("id", ""))
    }


def build_payload() -> dict[str, Any]:
    collection = require_payload(
        RESULTS / "external_collection_readiness_audit.json",
        "external_collection_readiness_audit_v1",
    )
    acquisition = require_payload(
        RESULTS / "external_acquisition_packet.json",
        "external_acquisition_packet_v1",
    )
    backend_contract = require_payload(
        RESULTS / "external_backend_contract_audit.json",
        "external_backend_contract_audit_v1",
    )
    materialization = require_payload(
        RESULTS / "external_config_materialization_plan.json",
        "external_config_materialization_plan_v1",
    )

    actions = action_lookup(acquisition)
    collection_blockers = list(collection.get("blocking_missing", []) or [])
    post_collection_commands = list(collection.get("post_collection_strict_commands", []) or [])
    if not post_collection_commands:
        post_collection_commands = list(acquisition.get("post_collection_strict_commands", []) or [])

    required_action_ids = {
        "platform_onboarding",
        "fidelity_provenance_packet",
        "backend_integration_packet",
        "backend_module",
        "config_manifest_packet",
        "rollout_evidence_packet",
        "real_task_configs",
        "platform_fidelity",
        "alias_unseal",
        "specific_run_id",
        "method_implementation_packet",
        "real_method_implementations",
        "pilot_smoke_packet",
        "run_collection",
        "manifest_and_release",
        "strict_rollout_recompute",
        "strict_adapter_evidence",
        "final_strict_gate",
    }

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "acquisition_packet_ready",
        acquisition.get("passed") is True
        and acquisition.get("not_external_evidence") is True
        and acquisition.get("strict_evidence_ready") is False,
        (
            f"passed={acquisition.get('passed')!r}, "
            f"strict_evidence_ready={acquisition.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "collection_preflight_fail_closed",
        collection.get("passed") is True
        and collection.get("not_external_evidence") is True
        and collection.get("collection_ready") is False
        and int(collection.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"collection_ready={collection.get('collection_ready')!r}, "
            f"blocking_missing_count={collection.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "operator_actions_cover_start_to_finish",
        required_action_ids.issubset(set(actions)),
        f"missing={sorted(required_action_ids - set(actions))}",
    )
    missing_titles = sorted(action_id for action_id, action in actions.items() if not action.get("title"))
    add_check(
        checks,
        "operator_action_titles_present",
        not missing_titles,
        f"missing_titles={missing_titles}",
    )
    add_check(
        checks,
        "config_materializer_is_guarded",
        materialization.get("passed") is True
        and materialization.get("not_external_evidence") is True
        and materialization.get("write_enabled") is False
        and str(materialization.get("operator_write_command", "")).endswith("--confirm-real-platform --write"),
        (
            f"write_enabled={materialization.get('write_enabled')!r}, "
            f"task_count={materialization.get('task_count')!r}"
        ),
    )
    add_check(
        checks,
        "backend_contract_gate_is_explicit",
        backend_contract.get("passed") is True
        and backend_contract.get("not_external_evidence") is True
        and backend_contract.get("backend_contract_harness_ready") is True
        and backend_contract.get("actual_backend_ready") is False
        and "audit_external_backend_contract.py --strict" in str(backend_contract.get("strict_command", "")),
        str(backend_contract.get("strict_command", "")),
    )
    backend_action = actions.get("backend_module", {})
    backend_action_commands = "\n".join(backend_action.get("commands", []) or [])
    add_check(
        checks,
        "backend_action_runs_contract_before_readiness",
        "audit_external_backend_contract.py --strict" in backend_action_commands
        and "audit_external_collection_readiness.py" in backend_action_commands,
        backend_action_commands,
    )
    add_check(
        checks,
        "strict_collection_command_is_explicit",
        "--backend-module <module_or_path>" in str(collection.get("strict_collection_command", ""))
        and "--unsealed-alias-map" in str(collection.get("strict_collection_command", "")),
        str(collection.get("strict_collection_command", "")),
    )
    add_check(
        checks,
        "post_collection_gates_cover_evidence",
        any("validate_external_rollouts.py" in command for command in post_collection_commands)
        and any("audit_external_evidence.py" in command for command in post_collection_commands)
        and any("audit_external_pairing_integrity.py" in command for command in post_collection_commands),
        f"commands={len(post_collection_commands)}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )
    add_check(
        checks,
        "packet_artifacts_exist",
        all(
            path.exists()
            for path in (
                EXTERNAL / "collection_runbook.md",
                EXTERNAL / "runner" / "real_collection_runner.py",
                EXTERNAL / "blinded_operator_sheet.csv",
                EXTERNAL / "method_alias_map.json",
                EXTERNAL / "platform_qualification_checklist.md",
                EXTERNAL / "config_schema_v1.json",
            )
        ),
        "runbook, runner, blinded sheet, alias map, platform checklist, and config schema",
    )

    passed = all(check["passed"] for check in checks)
    go_to_collect = collection.get("collection_ready") is True
    return {
        "version": "external_operator_packet_v1",
        "passed": passed,
        "not_external_evidence": True,
        "operator_packet_ready": passed,
        "strict_evidence_ready": False,
        "go_to_collect": go_to_collect,
        "start_state": "READY_TO_COLLECT_EXTERNAL_EVIDENCE" if go_to_collect else "DO_NOT_COLLECT_YET",
        "collection_ready": collection.get("collection_ready"),
        "blocking_missing_count": int(collection.get("blocking_missing_count", 0) or 0),
        "pre_collection_blockers": collection_blockers,
        "pre_collection_gate_command": (
            "python scripts\\audit_external_collection_readiness.py --strict "
            "--backend-module <module_or_path> --task-config-dir external_validation\\configs "
            "--run-id <specific_run_id> --unsealed-alias-map"
        ),
        "backend_contract_gate_command": backend_contract.get("strict_command", ""),
        "config_materialization_command": materialization.get("operator_write_command", ""),
        "strict_collection_command": collection.get("strict_collection_command", ""),
        "post_collection_strict_commands": post_collection_commands,
        "operator_actions": acquisition.get("operator_actions", []) or [],
        "source_reports": [
            "results/external_collection_readiness_audit.json",
            "results/external_acquisition_packet.json",
            "results/external_backend_contract_audit.json",
            "results/external_config_materialization_plan.json",
            "results/external_rollout_evidence_audit.json",
            "results/external_fidelity_provenance_audit.json",
            "results/external_pilot_smoke_packet_audit.json",
        ],
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Operator Packet",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict evidence ready: `{str(payload['strict_evidence_ready']).lower()}`.",
        f"Start state: `{payload['start_state']}`.",
        "",
        "This packet is the independent operator entry point for turning the current non-evidence validation plan into real robot or accepted high-fidelity simulator evidence. It does not replace the strict external audits.",
        "",
        "## Go / No-Go",
        "",
    ]
    if payload["go_to_collect"]:
        lines.append("- Go: strict collection preflight is ready. Run the collection command below.")
    else:
        lines.append("- No-go: do not start collection until every pre-collection blocker below is cleared by the strict preflight gate.")
    lines.extend(["", "## Pre-Collection Blockers", ""])
    for blocker in payload["pre_collection_blockers"] or ["none"]:
        lines.append(f"- {blocker}")

    lines.extend(
        [
            "",
            "## Commands",
            "",
            "Materialize real configs after platform selection:",
            "",
            "```powershell",
            payload["config_materialization_command"],
            "```",
            "",
            "Strict backend qualification gate:",
            "",
            "```powershell",
            payload["backend_contract_gate_command"],
            "```",
            "",
            "Strict pre-collection gate:",
            "",
            "```powershell",
            payload["pre_collection_gate_command"],
            "```",
            "",
            "Actual collection command after the strict gate passes:",
            "",
            "```powershell",
            payload["strict_collection_command"],
            "```",
            "",
            "Post-collection strict gates:",
            "",
        ]
    )
    for command in payload["post_collection_strict_commands"]:
        lines.append(f"- `{command}`")

    lines.extend(["", "## Operator Actions", ""])
    for action in payload["operator_actions"]:
        lines.append(f"- `{action.get('id')}`: {action.get('title')}")

    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "External operator packet: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"start_state={payload['start_state']}; "
        f"blockers={payload['blocking_missing_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
