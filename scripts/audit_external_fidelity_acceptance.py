from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
MANIFEST = EXTERNAL / "manifest.json"
MANIFEST_TEMPLATE = EXTERNAL / "manifest_template.json"
TEMPLATE = EXTERNAL / "fidelity_acceptance_template.json"
DEFAULT_ACCEPTANCE = EXTERNAL / "fidelity_acceptance.json"
OUT_JSON = RESULTS / "external_fidelity_acceptance_audit.json"
OUT_MD = RESULTS / "external_fidelity_acceptance_audit.md"

TEMPLATE_VERSION = "paper119_fidelity_acceptance_template_v1"
EVIDENCE_VERSION = "paper119_fidelity_acceptance_v1"
VALID_ROUTES = {"real_robot", "high_fidelity_sim", "mixed"}
VALID_PLATFORM_TYPES = {"real_robot", "high_fidelity_sim"}
PLACEHOLDER_VALUES = {
    "",
    "FILL_AFTER_PLATFORM_SELECTION",
    "REPLACE_WITH_SOURCE_SKILL",
    "REPLACE_WITH_TARGET_SKILL",
    "DRAFT_NOT_LOCKED",
}
REQUIRED_TASKS = {
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
}
REQUIRED_PLATFORM_FIELDS = {
    "platform_type",
    "platform_name",
    "platform_version",
    "physics_engine",
    "contact_solver",
    "timestep_seconds",
    "substeps_per_control_step",
    "robot_model_source",
    "asset_sources",
    "sensor_modalities",
    "state_observation_channels",
    "contact_or_force_channels",
}
REQUIRED_TRUE_QUALIFICATION_FLAGS = {
    "pre_registered_before_rollouts",
    "deterministic_paired_resets",
    "shared_skill_library",
    "same_observation_interface",
    "same_compute_budget",
    "no_privileged_state_for_non_oracle",
    "raw_jsonl_is_source_of_truth",
    "videos_tied_to_run_ids",
    "failed_and_abstained_runs_logged",
}
REQUIRED_QUALIFICATION_TEXT = {
    "operator_independence_statement",
    "contact_dynamics_justification",
    "paired_reset_replay_test",
    "real_or_benchmark_calibration_basis",
    "known_limitations",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def has_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Fa-f0-9]{64}", value))


def has_commit_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Fa-f0-9]{40}", value.strip()))


def has_iso_date(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+\-Z]+)?", value.strip()))


def is_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        stripped = value.strip()
        return (
            stripped in PLACEHOLDER_VALUES
            or "FILL_AFTER" in stripped
            or "OPERATOR_VERIFY" in stripped
            or stripped.startswith("DRAFT_")
        )
    if isinstance(value, list):
        return any(is_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(is_placeholder(item) for item in value.values())
    return False


def has_nonempty_text(value: Any, *, min_len: int = 20) -> bool:
    return isinstance(value, str) and len(value.strip()) >= min_len and not is_placeholder(value)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def choose_source(manifest: dict[str, Any], manifest_exists: bool) -> tuple[Path, str]:
    if manifest_exists:
        value = str(manifest.get("fidelity_acceptance_path", "")).strip()
        return (rel_path(value), "manifest") if value else (DEFAULT_ACCEPTANCE, "default")
    if DEFAULT_ACCEPTANCE.exists():
        return DEFAULT_ACCEPTANCE, "precollection_acceptance"
    return TEMPLATE, "template"


def platform_counts(manifest: dict[str, Any]) -> dict[str, int]:
    counts = {"real_robot": 0, "high_fidelity_sim": 0}
    seen: set[tuple[str, str]] = set()
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        key = (str(task.get("task_family", "")), str(task.get("platform_type", "")))
        if key in seen:
            continue
        seen.add(key)
        if key[1] in counts:
            counts[key[1]] += 1
    return counts


def route_count_ok(route: str, counts: dict[str, int]) -> bool:
    return (
        (route == "real_robot" and counts["real_robot"] >= 3)
        or (route == "high_fidelity_sim" and counts["high_fidelity_sim"] >= 4)
        or (route == "mixed" and counts["real_robot"] >= 2 and counts["high_fidelity_sim"] >= 2)
    )


def audit_contract(payload: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    add_check(checks, "template_exists", TEMPLATE.exists(), rel(TEMPLATE))
    add_check(checks, "source_exists", source.exists(), rel(source) if source.exists() and source.is_relative_to(ROOT) else str(source))
    add_check(
        checks,
        "recognized_version",
        payload.get("version") in {TEMPLATE_VERSION, EVIDENCE_VERSION},
        f"version={payload.get('version')!r}",
    )
    add_check(
        checks,
        "template_declares_not_evidence",
        payload.get("not_external_evidence") is True,
        f"not_external_evidence={payload.get('not_external_evidence')!r}",
    )
    add_check(
        checks,
        "route_declared",
        payload.get("route") in VALID_ROUTES,
        f"route={payload.get('route')!r}",
    )
    platform = payload.get("platform", {})
    platform = platform if isinstance(platform, dict) else {}
    missing_platform_fields = sorted(REQUIRED_PLATFORM_FIELDS - set(platform))
    add_check(checks, "platform_fields_present", not missing_platform_fields, f"missing={missing_platform_fields}")
    qualification = payload.get("qualification", {})
    qualification = qualification if isinstance(qualification, dict) else {}
    missing_qual_flags = sorted(REQUIRED_TRUE_QUALIFICATION_FLAGS - set(qualification))
    missing_qual_text = sorted(REQUIRED_QUALIFICATION_TEXT - set(qualification))
    add_check(checks, "qualification_fields_present", not missing_qual_flags and not missing_qual_text, f"missing_flags={missing_qual_flags}, missing_text={missing_qual_text}")
    task_fidelity = payload.get("task_fidelity", [])
    task_fidelity = task_fidelity if isinstance(task_fidelity, list) else []
    task_names = {str(item.get("task_family", "")) for item in task_fidelity if isinstance(item, dict)}
    add_check(checks, "task_fidelity_covers_core_tasks", REQUIRED_TASKS <= task_names, f"missing={sorted(REQUIRED_TASKS - task_names)}")
    gates = payload.get("acceptance_gates", [])
    gates = gates if isinstance(gates, list) else []
    gate_names = {str(item.get("name", "")) for item in gates if isinstance(item, dict)}
    required_gate_names = {
        "platform_provenance_complete",
        "paired_reset_replay_verified",
        "contact_failure_observable",
        "non_oracle_methods_fair",
        "raw_logs_drive_metrics",
    }
    add_check(checks, "acceptance_gates_present", required_gate_names <= gate_names, f"missing={sorted(required_gate_names - gate_names)}")
    return checks


def audit_evidence(payload: dict[str, Any], source: Path, manifest: dict[str, Any], manifest_exists: bool, source_kind: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    manifest_acceptance_path = str(manifest.get("fidelity_acceptance_path", "")).strip() if manifest_exists else ""
    manifest_acceptance_matches_source = False
    if manifest_acceptance_path:
        try:
            manifest_acceptance_matches_source = rel_path(manifest_acceptance_path).resolve() == source.resolve()
        except OSError:
            manifest_acceptance_matches_source = False
    add_check(
        checks,
        "manifest_declaration_not_required_before_collection",
        not manifest_exists or bool(manifest_acceptance_path),
        f"manifest_exists={manifest_exists!r}, source_kind={source_kind}, fidelity_acceptance_path={manifest_acceptance_path!r}",
    )
    add_check(
        checks,
        "manifest_acceptance_path_consistent_when_present",
        not manifest_exists or manifest_acceptance_matches_source,
        f"source={source}, manifest_fidelity_acceptance_path={manifest_acceptance_path!r}",
    )
    add_check(checks, "real_acceptance_file_exists", source.exists() and source.name != TEMPLATE.name, rel(source) if source.exists() and source.is_relative_to(ROOT) else str(source))
    add_check(checks, "real_acceptance_version", payload.get("version") == EVIDENCE_VERSION, f"version={payload.get('version')!r}, expected={EVIDENCE_VERSION!r}")
    add_check(
        checks,
        "real_acceptance_declares_ready",
        payload.get("acceptance_ready") is True,
        f"acceptance_ready={payload.get('acceptance_ready')!r}",
    )
    add_check(
        checks,
        "not_template_only",
        payload.get("template_only") is not True,
        f"template_only={payload.get('template_only')!r}",
    )
    add_check(
        checks,
        "not_draft_only",
        payload.get("draft_only") is not True,
        f"draft_only={payload.get('draft_only')!r}",
    )
    add_check(
        checks,
        "strict_readiness_remains_external_to_acceptance",
        payload.get("not_external_evidence") is True
        and payload.get("strict_fidelity_evidence_ready") is False
        and payload.get("strict_external_evidence_ready") is False,
        (
            f"not_external_evidence={payload.get('not_external_evidence')!r}, "
            f"strict_fidelity_evidence_ready={payload.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={payload.get('strict_external_evidence_ready')!r}"
        ),
    )
    route = str(payload.get("route", ""))
    manifest_route = str(manifest.get("route", "")) if manifest_exists else ""
    counts = platform_counts(manifest)
    add_check(
        checks,
        "route_matches_manifest_when_present",
        not manifest_exists or (route == manifest_route and route in VALID_ROUTES),
        f"acceptance_route={route!r}, manifest_route={manifest_route!r}, manifest_exists={manifest_exists!r}",
    )
    add_check(
        checks,
        "manifest_task_coverage_when_present",
        not manifest_exists or route_count_ok(route, counts),
        f"route={route!r}, counts={counts}, manifest_exists={manifest_exists!r}",
    )

    platform = payload.get("platform", {})
    platform = platform if isinstance(platform, dict) else {}
    platform_placeholders = sorted(field for field in REQUIRED_PLATFORM_FIELDS if is_placeholder(platform.get(field)))
    add_check(checks, "platform_values_filled", not platform_placeholders and bool(platform), f"placeholder_fields={platform_placeholders}")
    add_check(
        checks,
        "platform_type_valid",
        platform.get("platform_type") in VALID_PLATFORM_TYPES,
        f"platform_type={platform.get('platform_type')!r}",
    )
    add_check(
        checks,
        "modalities_cover_state_camera_contact",
        {"state", "camera", "contact_or_force"} <= set(platform.get("sensor_modalities", []) if isinstance(platform.get("sensor_modalities"), list) else []),
        f"sensor_modalities={platform.get('sensor_modalities')!r}",
    )
    add_check(
        checks,
        "contact_channels_declared",
        isinstance(platform.get("contact_or_force_channels"), list) and len(platform.get("contact_or_force_channels")) >= 1 and not is_placeholder(platform.get("contact_or_force_channels")),
        f"contact_or_force_channels={platform.get('contact_or_force_channels')!r}",
    )

    qualification = payload.get("qualification", {})
    qualification = qualification if isinstance(qualification, dict) else {}
    false_flags = sorted(flag for flag in REQUIRED_TRUE_QUALIFICATION_FLAGS if qualification.get(flag) is not True)
    weak_text = sorted(field for field in REQUIRED_QUALIFICATION_TEXT if not has_nonempty_text(qualification.get(field)))
    add_check(checks, "qualification_flags_true", not false_flags and bool(qualification), f"false_or_missing={false_flags}")
    add_check(checks, "qualification_text_filled", not weak_text and bool(qualification), f"weak_or_placeholder={weak_text}")

    task_fidelity = payload.get("task_fidelity", [])
    task_fidelity = task_fidelity if isinstance(task_fidelity, list) else []
    weak_tasks = []
    for item in task_fidelity:
        if not isinstance(item, dict):
            weak_tasks.append("<non-object>")
            continue
        if item.get("task_family") in REQUIRED_TASKS and (
            item.get("seam_observable") is not True
            or item.get("failure_modes_visible_on_video") is not True
            or not has_nonempty_text(item.get("contact_or_dynamics_property"), min_len=12)
            or not has_nonempty_text(item.get("minimum_required_signal"), min_len=12)
        ):
            weak_tasks.append(str(item.get("task_family", "")))
    add_check(checks, "task_fidelity_details_filled", not weak_tasks and len(task_fidelity) >= len(REQUIRED_TASKS), f"weak_tasks={weak_tasks}")

    provenance = payload.get("provenance", {})
    provenance = provenance if isinstance(provenance, dict) else {}
    add_check(
        checks,
        "operator_independence_declared",
        provenance.get("operator_not_target_collaborator") is True and has_nonempty_text(provenance.get("operator_name_or_lab"), min_len=3),
        f"operator_not_target_collaborator={provenance.get('operator_not_target_collaborator')!r}",
    )
    add_check(checks, "date_locked_filled", not is_placeholder(provenance.get("date_locked")), f"date_locked={provenance.get('date_locked')!r}")
    add_check(checks, "date_locked_iso_like", has_iso_date(provenance.get("date_locked")), f"date_locked={provenance.get('date_locked')!r}")
    add_check(checks, "code_commit_filled", has_nonempty_text(provenance.get("code_commit"), min_len=7), f"code_commit={provenance.get('code_commit')!r}")
    add_check(checks, "code_commit_sha40", has_commit_sha(provenance.get("code_commit")), f"code_commit={provenance.get('code_commit')!r}")
    add_check(checks, "skill_library_hash_valid", has_sha(provenance.get("skill_library_hash")), "skill_library_hash must be 64-character SHA256")
    add_check(checks, "artifact_hash_policy_sha256", provenance.get("artifact_hash_policy") == "sha256", f"artifact_hash_policy={provenance.get('artifact_hash_policy')!r}")
    add_check(
        checks,
        "precollection_confirmation_booleans_true",
        provenance.get("real_platform_confirmed_by_operator") is True
        and provenance.get("render_backed_videos_confirmed_by_operator") is True,
        (
            f"real_platform_confirmed_by_operator={provenance.get('real_platform_confirmed_by_operator')!r}, "
            f"render_backed_videos_confirmed_by_operator="
            f"{provenance.get('render_backed_videos_confirmed_by_operator')!r}"
        ),
    )
    add_check(
        checks,
        "postcollection_evidence_deferred_until_manifest",
        provenance.get("manifest_declaration_required_after_collection") is True
        and provenance.get("real_rollout_evidence_required_after_collection") is True
        and provenance.get("manifest_declaration_confirmed_by_operator") is not True
        and provenance.get("real_rollout_evidence_confirmed_by_operator") is not True,
        (
            f"manifest_declaration_required_after_collection="
            f"{provenance.get('manifest_declaration_required_after_collection')!r}, "
            f"real_rollout_evidence_required_after_collection="
            f"{provenance.get('real_rollout_evidence_required_after_collection')!r}, "
            f"manifest_declaration_confirmed_by_operator="
            f"{provenance.get('manifest_declaration_confirmed_by_operator')!r}, "
            f"real_rollout_evidence_confirmed_by_operator="
            f"{provenance.get('real_rollout_evidence_confirmed_by_operator')!r}"
        ),
    )
    add_check(
        checks,
        "materialized_by_guarded_path",
        payload.get("materialized_by") == "scripts/materialize_fidelity_acceptance.py"
        and payload.get("materialized_from_draft_path") == "external_validation/fidelity_acceptance_draft.json",
        (
            f"materialized_by={payload.get('materialized_by')!r}, "
            f"materialized_from_draft_path={payload.get('materialized_from_draft_path')!r}"
        ),
    )

    gates = payload.get("acceptance_gates", [])
    gates = gates if isinstance(gates, list) else []
    unpassed_gates = [
        str(gate.get("name", "<unnamed>"))
        for gate in gates
        if not isinstance(gate, dict) or gate.get("status") not in {"passed", "accepted", True}
    ]
    add_check(checks, "all_acceptance_gates_passed", bool(gates) and not unpassed_gates, f"unpassed={unpassed_gates}")
    return checks


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# External Fidelity Acceptance Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not external evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Acceptance ready: `{str(payload['acceptance_ready']).lower()}`.",
        f"Readiness state: `{payload['readiness_state']}`.",
        f"Source: `{payload['source']}`.",
        f"Manifest exists: `{str(payload['manifest_exists']).lower()}`.",
        f"Blocking missing items: `{payload['blocking_missing_count']}`.",
        "",
        "This audit defines the platform/provenance standard for real-robot or accepted high-fidelity simulator validation. It is not rollout evidence and does not replace strict JSONL, video, config, checkpoint, or baseline evidence.",
        "",
        "## Blocking Missing Items",
        "",
    ]
    if payload["blocking_missing"]:
        for item in payload["blocking_missing"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Contract Checks", ""])
    for check in payload["contract_checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(["", "## Evidence Checks", ""])
    for check in payload["evidence_checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(["", "## Operator Next Actions", ""])
    for action in payload["operator_next_actions"]:
        lines.append(f"- {action}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Paper 119 external platform fidelity/provenance acceptance.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless a real platform acceptance file is ready.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    manifest_exists = MANIFEST.exists()
    manifest = read_json(MANIFEST) if manifest_exists else {}
    if not manifest_exists and MANIFEST_TEMPLATE.exists():
        manifest = read_json(MANIFEST_TEMPLATE)

    source, source_kind = choose_source(manifest, manifest_exists)
    if source.exists():
        payload = read_json(source)
    elif TEMPLATE.exists():
        payload = read_json(TEMPLATE)
    else:
        payload = {}

    contract_checks = audit_contract(payload, source if source.exists() else TEMPLATE)
    evidence_checks = audit_evidence(payload, source, manifest if manifest_exists else {}, manifest_exists, source_kind)
    contract_ready = all(check["passed"] for check in contract_checks)
    acceptance_ready = contract_ready and all(check["passed"] for check in evidence_checks)
    blocking_missing = [f"{check['name']}: {check['detail']}" for check in evidence_checks if not check["passed"]]
    readiness_state = "READY" if acceptance_ready else "COLLECT_PLATFORM_PROVENANCE"
    passed = contract_ready

    result = {
        "version": "external_fidelity_acceptance_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "acceptance_ready": acceptance_ready,
        "readiness_state": readiness_state,
        "source": rel(source) if source.exists() and source.is_relative_to(ROOT) else str(source),
        "source_kind": source_kind,
        "manifest_exists": manifest_exists,
        "expected_real_acceptance_path": rel(DEFAULT_ACCEPTANCE),
        "blocking_missing_count": len(blocking_missing),
        "blocking_missing": blocking_missing,
        "contract_checks": contract_checks,
        "evidence_checks": evidence_checks,
        "operator_next_actions": [
            "Select an external robot or accepted high-fidelity simulator before collecting rollouts.",
            "Use scripts/materialize_fidelity_acceptance.py with independent-operator signoff, real platform details, render-backed video readiness, paired-reset replay evidence, a SHA40 collection commit, and the current skill-library SHA256 to write external_validation/fidelity_acceptance.json before official collection.",
            "Fill platform physics/contact details, paired-reset replay evidence, operator independence, real/benchmark calibration basis, code commit, skill-library hash, and precollection confirmation booleans through the guarded materializer.",
            "After official collection and postcollection sealing, declare fidelity_acceptance_path in external_validation/manifest.json together with raw logs, videos, configs, methods, and hashes.",
            "Run audit_external_fidelity_acceptance.py --strict before collection readiness, then rely on manifest, rollout, release, pairing, adapter, config, and final evidence audits before counting any high-fidelity route as external evidence.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(result)

    status = "READY" if acceptance_ready else "COLLECT_PLATFORM_PROVENANCE"
    print(
        f"External fidelity acceptance audit: {status}; "
        f"contract_ready={contract_ready}; missing={len(blocking_missing)}; not_evidence=True"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    if args.strict and not acceptance_ready:
        return 1
    return 0 if passed or acceptance_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
