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
    reference_preflight = require_payload(
        RESULTS / "maniskill_reference_collection_preflight_audit.json",
        "maniskill_reference_collection_preflight_audit_v1",
    )
    fidelity_draft = require_payload(
        RESULTS / "external_fidelity_acceptance_draft_audit.json",
        "external_fidelity_acceptance_draft_audit_v1",
    )
    fidelity_materialization = require_payload(
        RESULTS / "fidelity_acceptance_materialization_plan.json",
        "fidelity_acceptance_materialization_plan_v1",
    )
    fidelity_metadata = require_payload(
        RESULTS / "maniskill_fidelity_metadata_probe.json",
        "maniskill_fidelity_metadata_probe_v1",
    )
    render_preflight = require_payload(
        RESULTS / "maniskill_render_video_preflight_audit.json",
        "maniskill_render_video_preflight_audit_v1",
    )
    render_machine = require_payload(
        RESULTS / "maniskill_render_machine_qualification.json",
        "maniskill_render_machine_qualification_v1",
    )
    ablation_packet = require_payload(
        RESULTS / "external_ablation_collection_audit.json",
        "external_ablation_collection_audit_v1",
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
        "platform_probe",
        "task_binding_probe",
        "env_smoke_probe",
        "fidelity_metadata_probe",
        "platform_onboarding",
        "fidelity_provenance_packet",
        "fidelity_acceptance_draft",
        "fidelity_acceptance_materializer",
        "backend_integration_packet",
        "maniskill_reference_backend_audit",
        "maniskill_reference_collection_preflight",
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
        "maniskill_render_video_preflight",
        "maniskill_pilot_runtime_liveness",
        "maniskill_render_machine_qualification",
        "ablation_collection_packet",
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
    reference_blockers = list(reference_preflight.get("collection_blocking_missing", []) or [])
    add_check(
        checks,
        "maniskill_reference_preflight_reaches_only_fidelity_gate",
        reference_preflight.get("passed") is True
        and reference_preflight.get("not_external_evidence") is True
        and reference_preflight.get("reference_backend_contract_ready") is True
        and reference_preflight.get("collection_ready") is False
        and int(reference_preflight.get("collection_blocking_missing_count", 0) or 0) == 1
        and len(reference_blockers) == 1
        and "fidelity_acceptance_ready" in reference_blockers[0],
        f"blocking={reference_blockers}",
    )
    draft_checks = {check.get("name"): check.get("passed") for check in fidelity_draft.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_draft_ready_but_fail_closed",
        fidelity_draft.get("passed") is True
        and fidelity_draft.get("not_external_evidence") is True
        and fidelity_draft.get("draft_ready") is True
        and fidelity_draft.get("acceptance_ready") is False
        and fidelity_draft.get("strict_fidelity_evidence_ready") is False
        and fidelity_draft.get("strict_external_evidence_ready") is False
        and draft_checks.get("draft_is_non_evidence_and_fail_closed") is True
        and draft_checks.get("candidate_platform_prefilled_from_reference_route") is True
        and draft_checks.get("acceptance_gates_remain_unaccepted") is True
        and draft_checks.get("no_real_acceptance_or_manifest_written") is True,
        (
            f"draft_ready={fidelity_draft.get('draft_ready')!r}, "
            f"remaining_operator_inputs={fidelity_draft.get('remaining_operator_input_count')!r}"
        ),
    )
    materializer_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_guarded",
        fidelity_materialization.get("passed") is True
        and fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False
        and fidelity_materialization.get("strict_external_evidence_ready") is False
        and "materialize_fidelity_acceptance.py" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-real-platform" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-independent-operator" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-render-backed-videos" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-real-rollout-evidence" in str(fidelity_materialization.get("operator_write_command", ""))
        and "--confirm-manifest-declaration" in str(fidelity_materialization.get("operator_write_command", ""))
        and materializer_checks.get("operator_write_command_is_guarded") is True,
        (
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}"
        ),
    )
    metadata_action = actions.get("fidelity_metadata_probe", {})
    metadata_commands = "\n".join(metadata_action.get("commands", []) or [])
    add_check(
        checks,
        "fidelity_metadata_probe_ready_but_not_evidence",
        fidelity_metadata.get("passed") is True
        and fidelity_metadata.get("not_external_evidence") is True
        and fidelity_metadata.get("metadata_probe_ready") is True
        and fidelity_metadata.get("accepted_fidelity_ready") is False
        and fidelity_metadata.get("strict_fidelity_evidence_ready") is False
        and fidelity_metadata.get("strict_external_evidence_ready") is False
        and "probe_maniskill_fidelity_metadata.py" in metadata_commands,
        (
            f"strict_metadata_ready={fidelity_metadata.get('strict_metadata_ready')!r}, "
            f"primary_metadata_missing={fidelity_metadata.get('primary_metadata_missing')!r}"
        ),
    )
    render_action = actions.get("maniskill_render_video_preflight", {})
    render_commands = "\n".join(render_action.get("commands", []) or [])
    add_check(
        checks,
        "render_video_preflight_recorded_but_not_evidence",
        render_preflight.get("passed") is True
        and render_preflight.get("not_external_evidence") is True
        and render_preflight.get("strict_external_evidence_ready") is False
        and int(render_preflight.get("env_count", 0) or 0) >= 1
        and isinstance(render_preflight.get("render_video_ready"), bool)
        and (render_preflight.get("render_video_ready") is True or bool(render_preflight.get("renderer_failure_classes")))
        and (render_preflight.get("render_video_ready") is True or bool(render_preflight.get("operator_remediation")))
        and "audit_maniskill_render_video_preflight.py" in render_commands,
        (
            f"render_video_ready={render_preflight.get('render_video_ready')!r}, "
            f"envs={render_preflight.get('env_count')!r}, "
            f"failure_classes={render_preflight.get('renderer_failure_classes')!r}"
        ),
    )
    render_machine_action = actions.get("maniskill_render_machine_qualification", {})
    render_machine_commands = "\n".join(render_machine_action.get("commands", []) or [])
    add_check(
        checks,
        "render_machine_qualification_recorded_but_not_evidence",
        render_machine.get("passed") is True
        and render_machine.get("not_external_evidence") is True
        and render_machine.get("strict_external_evidence_ready") is False
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and bool(render_machine.get("blocking_missing"))
        and "build_maniskill_render_machine_qualification.py" in render_machine_commands,
        (
            f"qualification_state={render_machine.get('qualification_state')!r}, "
            f"render_machine_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"blocking={len(render_machine.get('blocking_missing', []) or [])}"
        ),
    )
    ablation_action = actions.get("ablation_collection_packet", {})
    ablation_commands = "\n".join(ablation_action.get("commands", []) or [])
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_packet.get("checks", []) or []}
    add_check(
        checks,
        "ablation_collection_packet_recorded_but_not_evidence",
        ablation_packet.get("passed") is True
        and ablation_packet.get("not_external_evidence") is True
        and ablation_packet.get("strict_external_evidence_ready") is False
        and ablation_packet.get("manifest_ablation_evidence_ready") is False
        and int(ablation_packet.get("work_order_count", 0) or 0) == 5
        and int(ablation_packet.get("expected_ablation_records", 0) or 0) >= 600
        and ablation_checks.get("every_required_ablation_has_work_order") is True
        and ablation_checks.get("task_and_reset_budget_preserved") is True
        and "build_external_ablation_collection_packet.py" in ablation_commands,
        (
            f"work_order_count={ablation_packet.get('work_order_count')!r}, "
            f"expected_ablation_records={ablation_packet.get('expected_ablation_records')!r}, "
            f"manifest_ablation_evidence_ready={ablation_packet.get('manifest_ablation_evidence_ready')!r}"
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
    reference_backend = str(reference_preflight.get("backend_module", "external_validation/runner/maniskill_reference_backend.py")).replace("/", "\\")
    reference_run_id = str(reference_preflight.get("run_id", "maniskill_sapien_reference_preflight_protocol_v1"))
    reference_pre_collection_gate_command = (
        "python scripts\\audit_external_collection_readiness.py --strict "
        f"--backend-module {reference_backend} --task-config-dir external_validation\\configs "
        f"--run-id {reference_run_id} --unsealed-alias-map"
    )
    reference_collection_command = (
        "python external_validation\\runner\\real_collection_runner.py "
        f"--backend-module {reference_backend} --task-config-dir external_validation\\configs "
        "--output-log-dir external_validation\\logs --video-dir external_validation\\videos "
        f"--run-id {reference_run_id} --unsealed-alias-map"
    )
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
        "tracked_maniskill_reference_route": {
            "not_external_evidence": True,
            "backend_module": reference_backend,
            "run_id": reference_run_id,
            "reference_backend_contract_ready": reference_preflight.get("reference_backend_contract_ready") is True,
            "collection_ready": reference_preflight.get("collection_ready") is True,
            "blocking_missing_count": int(reference_preflight.get("collection_blocking_missing_count", 0) or 0),
            "blocking_missing": reference_blockers,
            "pre_collection_gate_command": reference_pre_collection_gate_command,
            "collection_command_after_fidelity_acceptance": reference_collection_command,
            "audit_command": "python scripts\\audit_maniskill_reference_collection_preflight.py",
        },
        "fidelity_acceptance_draft": {
            "not_external_evidence": True,
            "draft_ready": fidelity_draft.get("draft_ready") is True,
            "acceptance_ready": fidelity_draft.get("acceptance_ready") is True,
            "strict_fidelity_evidence_ready": fidelity_draft.get("strict_fidelity_evidence_ready") is True,
            "draft_path": fidelity_draft.get("draft_path", "external_validation/fidelity_acceptance_draft.json"),
            "draft_md_path": fidelity_draft.get("draft_md_path", "external_validation/fidelity_acceptance_draft.md"),
            "real_acceptance_path": fidelity_draft.get("real_acceptance_path", "external_validation/fidelity_acceptance.json"),
            "remaining_operator_input_count": int(fidelity_draft.get("remaining_operator_input_count", 0) or 0),
            "machine_prefilled_ready": fidelity_draft.get("machine_prefilled_ready") is True,
            "operator_signoff_ready": fidelity_draft.get("operator_signoff_ready") is True,
            "operator_signoff_item_count": int(fidelity_draft.get("operator_signoff_item_count", 0) or 0),
            "build_command": "python scripts\\build_external_fidelity_acceptance_draft.py",
            "strict_audit_command_after_promotion": "python scripts\\audit_external_fidelity_acceptance.py --strict",
        },
        "fidelity_acceptance_materializer": {
            "not_external_evidence": True,
            "write_enabled": fidelity_materialization.get("write_enabled") is True,
            "acceptance_write_ready": fidelity_materialization.get("acceptance_write_ready") is True,
            "strict_fidelity_evidence_ready": fidelity_materialization.get("strict_fidelity_evidence_ready") is True,
            "strict_external_evidence_ready": fidelity_materialization.get("strict_external_evidence_ready") is True,
            "source_draft": fidelity_materialization.get("source_draft", "external_validation/fidelity_acceptance_draft.json"),
            "output_path": fidelity_materialization.get("output_path", "external_validation/fidelity_acceptance.json"),
            "plan_path": "results/fidelity_acceptance_materialization_plan.json",
            "plan_md_path": "results/fidelity_acceptance_materialization_plan.md",
            "missing_operator_text_count": len(fidelity_materialization.get("missing_operator_text", []) or []),
            "missing_confirmation_count": len(fidelity_materialization.get("missing_confirmations", []) or []),
            "operator_write_command": fidelity_materialization.get("operator_write_command", ""),
            "plan_command": "python scripts\\materialize_fidelity_acceptance.py",
        },
        "fidelity_metadata_probe": {
            "not_external_evidence": True,
            "metadata_probe_ready": fidelity_metadata.get("metadata_probe_ready") is True,
            "strict_metadata_ready": fidelity_metadata.get("strict_metadata_ready") is True,
            "accepted_fidelity_ready": fidelity_metadata.get("accepted_fidelity_ready") is True,
            "probe_path": "results/maniskill_fidelity_metadata_probe.json",
            "probe_md_path": "results/maniskill_fidelity_metadata_probe.md",
            "primary_metadata_missing": list(fidelity_metadata.get("primary_metadata_missing", []) or []),
            "primary_timing_summary": fidelity_metadata.get("primary_timing_summary", {}),
            "build_command": "python scripts\\probe_maniskill_fidelity_metadata.py",
        },
        "render_video_preflight": {
            "not_external_evidence": True,
            "render_video_ready": render_preflight.get("render_video_ready") is True,
            "strict_external_evidence_ready": render_preflight.get("strict_external_evidence_ready") is True,
            "env_count": int(render_preflight.get("env_count", 0) or 0),
            "render_ready_env_count": int(render_preflight.get("render_ready_env_count", 0) or 0),
            "blocking_missing": list(render_preflight.get("blocking_missing", []) or []),
            "renderer_failure_classes": list(render_preflight.get("renderer_failure_classes", []) or []),
            "operator_remediation": list(render_preflight.get("operator_remediation", []) or []),
            "renderer_profile_retest_commands": list(render_preflight.get("renderer_profile_retest_commands", []) or []),
            "audit_path": "results/maniskill_render_video_preflight_audit.json",
            "audit_md_path": "results/maniskill_render_video_preflight_audit.md",
            "build_command": "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4",
        },
        "render_machine_qualification": {
            "not_external_evidence": True,
            "qualification_state": render_machine.get("qualification_state"),
            "render_machine_qualified": render_machine.get("render_machine_qualified") is True,
            "strict_external_evidence_ready": render_machine.get("strict_external_evidence_ready") is True,
            "blocking_missing": list(render_machine.get("blocking_missing", []) or []),
            "packet_path": "external_validation/render_machine_qualification_packet.md",
            "audit_path": "results/maniskill_render_machine_qualification.json",
            "audit_md_path": "results/maniskill_render_machine_qualification.md",
            "build_command": "python scripts\\build_maniskill_render_machine_qualification.py",
        },
        "ablation_collection": {
            "not_external_evidence": True,
            "manifest_ablation_evidence_ready": ablation_packet.get("manifest_ablation_evidence_ready") is True,
            "strict_external_evidence_ready": ablation_packet.get("strict_external_evidence_ready") is True,
            "expected_ablation_records": int(ablation_packet.get("expected_ablation_records", 0) or 0),
            "work_order_count": int(ablation_packet.get("work_order_count", 0) or 0),
            "blocking_missing": list(ablation_packet.get("blocking_missing", []) or []),
            "packet_path": "external_validation/ablation_collection_packet.md",
            "work_orders_path": "external_validation/ablation_collection_work_orders.csv",
            "audit_path": "results/external_ablation_collection_audit.json",
            "audit_md_path": "results/external_ablation_collection_audit.md",
            "build_command": "python scripts\\build_external_ablation_collection_packet.py",
        },
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
            "results/external_platform_probe.json",
            "results/maniskill_task_binding_probe.json",
            "results/maniskill_env_smoke_probe.json",
            "results/maniskill_fidelity_metadata_probe.json",
            "results/maniskill_render_video_preflight_audit.json",
            "results/external_backend_contract_audit.json",
            "results/maniskill_backend_readiness_audit.json",
            "results/maniskill_reference_collection_preflight_audit.json",
            "results/external_fidelity_acceptance_draft_audit.json",
            "results/fidelity_acceptance_materialization_plan.json",
            "external_validation/fidelity_acceptance_draft.json",
            "external_validation/fidelity_acceptance_draft.md",
            "results/external_config_materialization_plan.json",
            "results/external_rollout_evidence_audit.json",
            "results/external_ablation_collection_audit.json",
            "results/external_fidelity_provenance_audit.json",
            "results/external_pilot_smoke_packet_audit.json",
            "results/maniskill_pilot_runtime_liveness_audit.json",
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

    reference = payload["tracked_maniskill_reference_route"]
    lines.extend(
        [
            "",
            "## Tracked ManiSkill Reference Route",
            "",
            "This tracked public-simulator route is not evidence and does not authorize collection. It shows that, after selecting the repository ManiSkill reference backend, prepared configs, an explicit run id, and unsealed aliases, the pre-collection path reaches the fidelity-acceptance gate.",
            "",
            f"- Backend module: `{reference['backend_module']}`",
            f"- Run id: `{reference['run_id']}`",
            f"- Reference backend contract ready: `{str(reference['reference_backend_contract_ready']).lower()}`",
            f"- Collection ready: `{str(reference['collection_ready']).lower()}`",
            f"- Remaining blockers after reference-route preflight: `{reference['blocking_missing_count']}`",
        ]
    )
    for blocker in reference["blocking_missing"] or ["none"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "Reference-route pre-collection gate:",
            "",
            "```powershell",
            reference["pre_collection_gate_command"],
            "```",
            "",
            "Reference-route collection command after fidelity acceptance passes:",
            "",
            "```powershell",
            reference["collection_command_after_fidelity_acceptance"],
            "```",
        ]
    )

    draft = payload["fidelity_acceptance_draft"]
    lines.extend(
        [
            "",
            "## Fidelity Acceptance Draft",
            "",
            "The draft is not evidence and does not satisfy fidelity acceptance. It pre-fills the tracked ManiSkill route's platform, backend, config, and smoke-probe anchors so the independent operator can replace draft fields with accepted provenance before collection.",
            "",
            f"- Draft JSON: `{draft['draft_path']}`",
            f"- Draft notes: `{draft['draft_md_path']}`",
            f"- Draft ready: `{str(draft['draft_ready']).lower()}`",
            f"- Acceptance ready: `{str(draft['acceptance_ready']).lower()}`",
            f"- Remaining operator inputs: `{draft['remaining_operator_input_count']}`",
            f"- Machine-prefilled ready: `{str(draft['machine_prefilled_ready']).lower()}`",
            f"- Operator signoff ready: `{str(draft['operator_signoff_ready']).lower()}`",
            f"- Operator signoff items: `{draft['operator_signoff_item_count']}`",
            "",
            "Draft rebuild command:",
            "",
            "```powershell",
            draft["build_command"],
            "```",
        ]
    )

    materializer = payload["fidelity_acceptance_materializer"]
    lines.extend(
        [
            "",
            "## Fidelity Acceptance Materializer",
            "",
            "The materializer is the guarded promotion path from the draft to `external_validation/fidelity_acceptance.json`. The default run writes only a plan; the write path requires independent operator fields, real platform confirmation, render-backed evidence-video readiness, real rollout evidence, and manifest declaration.",
            "",
            f"- Plan JSON: `{materializer['plan_path']}`",
            f"- Plan notes: `{materializer['plan_md_path']}`",
            f"- Source draft: `{materializer['source_draft']}`",
            f"- Output path: `{materializer['output_path']}`",
            f"- Write enabled: `{str(materializer['write_enabled']).lower()}`",
            f"- Acceptance write ready: `{str(materializer['acceptance_write_ready']).lower()}`",
            f"- Strict fidelity evidence ready: `{str(materializer['strict_fidelity_evidence_ready']).lower()}`",
            f"- Missing operator text fields: `{materializer['missing_operator_text_count']}`",
            f"- Missing confirmation flags: `{materializer['missing_confirmation_count']}`",
            "",
            "Dry-run plan command:",
            "",
            "```powershell",
            materializer["plan_command"],
            "```",
            "",
            "Guarded write command:",
            "",
            "```powershell",
            materializer["operator_write_command"],
            "```",
        ]
    )

    metadata = payload["fidelity_metadata_probe"]
    lines.extend(
        [
            "",
            "## ManiSkill Fidelity Metadata Probe",
            "",
            "This probe is not evidence and does not satisfy fidelity acceptance. It records timing, backend, controller, observation, and asset metadata that the independent operator should verify or replace before promoting the fidelity acceptance file.",
            "",
            f"- Probe JSON: `{metadata['probe_path']}`",
            f"- Probe notes: `{metadata['probe_md_path']}`",
            f"- Metadata probe ready: `{str(metadata['metadata_probe_ready']).lower()}`",
            f"- Strict metadata ready: `{str(metadata['strict_metadata_ready']).lower()}`",
            f"- Accepted fidelity ready: `{str(metadata['accepted_fidelity_ready']).lower()}`",
            f"- Primary metadata missing: `{metadata['primary_metadata_missing']}`",
            f"- Primary timing summary: `{metadata['primary_timing_summary']}`",
            "",
            "Probe rebuild command:",
            "",
            "```powershell",
            metadata["build_command"],
            "```",
        ]
    )

    render = payload["render_video_preflight"]
    lines.extend(
        [
            "",
            "## ManiSkill Render-Video Preflight",
            "",
            "This preflight is not evidence and does not satisfy fidelity acceptance. It checks whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before official collection, separating evidence-video readiness from diagnostic fallback videos.",
            "",
            f"- Audit JSON: `{render['audit_path']}`",
            f"- Audit notes: `{render['audit_md_path']}`",
            f"- Render video ready: `{str(render['render_video_ready']).lower()}`",
            f"- Strict external evidence ready: `{str(render['strict_external_evidence_ready']).lower()}`",
            f"- Environments probed: `{render['env_count']}`",
            f"- Render-ready environments: `{render['render_ready_env_count']}`",
            f"- Blocking missing: `{render['blocking_missing']}`",
            f"- Renderer failure classes: `{render['renderer_failure_classes']}`",
            f"- Operator remediation items: `{len(render['operator_remediation'])}`",
            "",
            "Render preflight command:",
            "",
            "```powershell",
            render["build_command"],
            "```",
            "",
            "Renderer profile retest commands:",
            "",
        ]
    )
    for command in render["renderer_profile_retest_commands"] or ["none"]:
        lines.extend(["```powershell", command, "```"])

    render_machine = payload["render_machine_qualification"]
    lines.extend(
        [
            "",
            "## ManiSkill Render Machine Qualification",
            "",
            "This packet is not evidence. It requires the exact collection machine to pass platform probing, render-backed MP4 preflight, pilot liveness, and zero diagnostic fallback videos before official collection can begin.",
            "",
            f"- Packet: `{render_machine['packet_path']}`",
            f"- Audit JSON: `{render_machine['audit_path']}`",
            f"- Audit notes: `{render_machine['audit_md_path']}`",
            f"- Qualification state: `{render_machine['qualification_state']}`",
            f"- Render machine qualified: `{str(render_machine['render_machine_qualified']).lower()}`",
            f"- Strict external evidence ready: `{str(render_machine['strict_external_evidence_ready']).lower()}`",
            f"- Blocking missing: `{render_machine['blocking_missing']}`",
            "",
            "Qualification packet command:",
            "",
            "```powershell",
            render_machine["build_command"],
            "```",
        ]
    )

    ablation = payload["ablation_collection"]
    lines.extend(
        [
            "",
            "## External Ablation Collection",
            "",
            "This packet is not evidence. It converts the strict external ablation requirement into five manifest-declared work orders that must use the same accepted configs, skill library, resets, observation interface, and compute budget as the primary method.",
            "",
            f"- Packet: `{ablation['packet_path']}`",
            f"- Work orders: `{ablation['work_orders_path']}`",
            f"- Audit JSON: `{ablation['audit_path']}`",
            f"- Audit notes: `{ablation['audit_md_path']}`",
            f"- Expected ablation records: `{ablation['expected_ablation_records']}`",
            f"- Work-order count: `{ablation['work_order_count']}`",
            f"- Manifest ablation evidence ready: `{str(ablation['manifest_ablation_evidence_ready']).lower()}`",
            f"- Strict external evidence ready: `{str(ablation['strict_external_evidence_ready']).lower()}`",
            f"- Blocking missing: `{ablation['blocking_missing']}`",
            "",
            "Ablation packet command:",
            "",
            "```powershell",
            ablation["build_command"],
            "```",
        ]
    )

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
