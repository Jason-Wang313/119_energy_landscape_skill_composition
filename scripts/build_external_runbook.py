from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
PLAN_JSON = RESULTS / "external_collection_plan.json"
SCHEMA_JSON = EXTERNAL / "log_schema_v1.json"

RUNBOOK_MD = EXTERNAL / "collection_runbook.md"
TASK_CARD_DIR = EXTERNAL / "task_cards"
CONFIG_TEMPLATE_DIR = EXTERNAL / "config_templates"
OPERATOR_SHEET = EXTERNAL / "operator_record_sheet.csv"
OUT_JSON = RESULTS / "external_runbook_audit.json"
OUT_MD = RESULTS / "external_runbook_audit.md"

REQUIRED_COMMAND_FRAGMENTS = [
    "probe_maniskill_fidelity_metadata.py",
    "audit_external_runner_harness.py",
    "audit_external_backend_contract.py",
    "audit_maniskill_backend_readiness.py",
    "audit_maniskill_reference_collection_preflight.py",
    "self_test_external_runner_backend.py",
    "audit_maniskill_render_video_preflight.py",
    "audit_maniskill_pilot_runtime_liveness.py",
    "build_maniskill_render_machine_qualification.py",
    "materialize_external_configs.py --platform-type high_fidelity_sim",
    "build_external_precollection_freeze_receipt.py",
    "real_collection_runner.py --backend-module <module_or_path>",
    "build_external_postcollection_evidence_seal.py",
    "audit_external_evidence_preflight.py",
    "build_external_ablation_collection_packet.py",
    "build_external_evidence_intake_ledger.py",
]


TASK_DETAILS = {
    "peg_place_regrasp": {
        "skill_i": "place_peg_on_fixture",
        "skill_j": "regrasp_for_insertion",
        "seam": "terminal peg pose must lie inside the next insertion or regrasp basin",
        "fidelity": ["contact-rich insertion geometry", "resettable peg pose", "camera or state pose logging"],
    },
    "drawer_to_pick_transfer": {
        "skill_i": "open_drawer_to_clearance",
        "skill_j": "pick_object_from_drawer",
        "seam": "drawer contact and terminal handle pose must leave a reachable grasp basin",
        "fidelity": ["drawer joint friction", "handle contact", "object pose logging"],
    },
    "door_open_navigation": {
        "skill_i": "open_door_to_passage",
        "skill_j": "navigate_through_doorway",
        "seam": "contact-mode transition must not leave the next navigation skill outside its feasible start set",
        "fidelity": ["door hinge dynamics", "doorway clearance", "robot base pose logging"],
    },
    "cable_route_insert": {
        "skill_i": "route_cable_along_path",
        "skill_j": "insert_cable_endpoint",
        "seam": "deformable cable state must remain in the insertion basin after routing",
        "fidelity": ["deformable or contact-rich cable model", "endpoint pose/state logging", "failure video coverage"],
    },
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def ensure_dirs() -> None:
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    TASK_CARD_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


def methods(plan: dict[str, Any]) -> list[str]:
    names = plan.get("methods", [])
    if not isinstance(names, list):
        return []
    return [str(name) for name in names if str(name)]


def tasks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    entries = plan.get("tasks", [])
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def task_detail(task_family: str) -> dict[str, Any]:
    return TASK_DETAILS.get(
        task_family,
        {
            "skill_i": "REPLACE_WITH_SOURCE_SKILL",
            "skill_j": "REPLACE_WITH_TARGET_SKILL",
            "seam": "candidate skill handoff must be predicted, diagnosed, and logged",
            "fidelity": ["document simulator or robot fidelity", "log state/camera/contact evidence"],
        },
    )


def row_for(task: dict[str, Any], reset: dict[str, Any], method: str) -> dict[str, str]:
    family = str(task["task_family"])
    detail = task_detail(family)
    reset_index = int(reset["reset_index"])
    run_id = f"paper119_ext_{family}_r{reset_index:03d}_{method}"
    video_path = f"external_validation/videos/{family}/{run_id}.mp4"
    return {
        "not_external_evidence": "true",
        "run_id": run_id,
        "task_family": family,
        "platform_type": str(task.get("platform_type", "")),
        "platform_name": "FILL_AFTER_PLATFORM_SELECTION",
        "reset_index": str(reset_index),
        "scene_id": str(reset["scene_id"]),
        "episode_index": str(reset_index),
        "seed": str(reset["seed"]),
        "method": method,
        "skill_i": detail["skill_i"],
        "skill_j": detail["skill_j"],
        "expected_log_jsonl": str(task.get("log_jsonl", "")),
        "expected_video_path": video_path,
        "config_template": f"external_validation/config_templates/{family}.json",
        "status": "uncollected",
        "operator_notes": "",
    }


def build_operator_rows(plan: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    names = methods(plan)
    for task in tasks(plan):
        for reset in task.get("reset_plan", []):
            if not isinstance(reset, dict):
                continue
            for method in names:
                rows.append(row_for(task, reset, method))
    return rows


def write_operator_sheet(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "not_external_evidence",
        "run_id",
        "task_family",
        "platform_type",
        "platform_name",
        "reset_index",
        "scene_id",
        "episode_index",
        "seed",
        "method",
        "skill_i",
        "skill_j",
        "expected_log_jsonl",
        "expected_video_path",
        "config_template",
        "status",
        "operator_notes",
    ]
    with OPERATOR_SHEET.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_config_template(task: dict[str, Any]) -> Path:
    family = str(task["task_family"])
    detail = task_detail(family)
    payload = {
        "version": "paper119_external_config_template_v1",
        "config_schema": "external_validation/config_schema_v1.json",
        "not_external_evidence": True,
        "template_only": True,
        "task_family": family,
        "platform_type": task.get("platform_type", ""),
        "platform_name": "FILL_AFTER_PLATFORM_SELECTION",
        "skill_i": detail["skill_i"],
        "skill_j": detail["skill_j"],
        "seam_under_test": detail["seam"],
        "required_fidelity_checks": detail["fidelity"],
        "reset_protocol": {
            "paired_resets": True,
            "reset_count": int(task.get("episodes_per_method", 0)),
            "scene_id_template": f"{family}_reset_{{index:03d}}",
            "initial_state_hash_required": True,
        },
        "observation_interface": {
            "state_logging_required": True,
            "camera_logging_required": True,
            "contact_or_force_logging_required": True,
        },
        "compute_budget": {
            "same_for_all_non_oracle_methods": True,
            "wall_clock_seconds": "FILL_AFTER_PLATFORM_SELECTION",
            "simulator_query_budget": "FILL_AFTER_PLATFORM_SELECTION",
        },
        "paired_reset_count": int(task.get("episodes_per_method", 0)),
        "fixed_risk_budget": 0.15,
        "must_log": [
            "initial_state_hash",
            "terminal_sample_set_hash",
            "basin_estimate",
            "barrier_score",
            "descent_continuity_score",
            "predicted_seam_risk",
            "decision",
            "failure_diagnosis",
            "success",
            "realized_seam_breach",
            "utility",
            "video_path",
            "policy_or_config_hash",
        ],
    }
    path = CONFIG_TEMPLATE_DIR / f"{family}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_task_card(task: dict[str, Any], names: list[str]) -> Path:
    family = str(task["task_family"])
    detail = task_detail(family)
    lines = [
        f"# Task Card: {family}",
        "",
        "Not external evidence: `true`.",
        "",
        f"Seam under test: {detail['seam']}.",
        f"Skill pair: `{detail['skill_i']}` -> `{detail['skill_j']}`.",
        f"Platform type: `{task.get('platform_type', '')}`.",
        f"Required paired resets per method: `{task.get('episodes_per_method', 0)}`.",
        f"Expected log: `{task.get('log_jsonl', '')}`.",
        f"Expected videos: `{task.get('video_dir', '')}`.",
        "",
        "## Fidelity Checks",
        "",
    ]
    for item in detail["fidelity"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Method Checklist",
            "",
            "Run every method on the same reset, scene, seed, source skill, target skill, and initial-state hash before moving to the next reset.",
            "",
        ]
    )
    for method in names:
        lines.append(f"- [ ] `{method}`")
    lines.extend(
        [
            "",
            "## Blocking Mistakes",
            "",
            "- Do not tune v5 after seeing baseline outcomes on the same reset.",
            "- Do not omit failed, abstained, or damaged episodes.",
            "- Do not replace raw JSONL records with tables.",
            "- Do not cite this task card as evidence.",
        ]
    )
    path = TASK_CARD_DIR / f"{family}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_runbook(plan: dict[str, Any], schema: dict[str, Any], row_count: int) -> None:
    lines = [
        "# Paper 119 External Validation Runbook",
        "",
        "Not external evidence: `true`.",
        "",
        "This runbook turns the independent validation protocol into operator-facing collection steps. It does not satisfy the external-evidence gate until real or accepted high-fidelity logs, videos, configs, checkpoints, and manifest-declared independent baseline evidence are collected and validated.",
        "",
        "## Collection Scale",
        "",
        f"- Route: `{plan.get('route')}`.",
        f"- Task families: `{plan.get('task_family_count')}`.",
        f"- Methods: `{plan.get('method_count')}`.",
        f"- Paired resets: `{plan.get('total_paired_resets')}`.",
        f"- Required JSONL records: `{row_count}`.",
        f"- Operator sheet: `{OPERATOR_SHEET.relative_to(ROOT).as_posix()}`.",
        "- Blinded operator sheet: `external_validation/blinded_operator_sheet.csv`.",
        "- Method alias map: `external_validation/method_alias_map.json`.",
        "",
        "## Operator Sequence",
        "",
        "1. Select the robot or accepted high-fidelity simulator and fill `platform_name` in the task config template.",
        "2. Generate and use the blinded operator sheet; keep `method_alias_map.json` sealed until logs, videos, configs, checkpoints, and implementation hashes are frozen.",
        "3. For each task card, instantiate all paired resets before running any method-specific tuning.",
        "4. Run all declared aliases on the same reset in `run_order_within_reset` order before changing the scene.",
        "5. Write one JSONL record per episode using the schema fields below.",
        "6. Save representative videos for successes, failures, abstentions, repairs, and oracle-gap cases.",
        "7. Run the strict validators and do not edit manifest metrics by hand.",
        "",
        "## Required JSONL Fields",
        "",
    ]
    for field in sorted(schema.get("required_fields", {})):
        lines.append(f"- `{field}`")
    lines.extend(["", "## Strict Validation Commands", ""])
    for command in plan.get("validation_commands", []):
        lines.append(f"- `{command}`")
    lines.extend(["", "## Task Cards", ""])
    for task in tasks(plan):
        family = task["task_family"]
        lines.append(f"- `{(TASK_CARD_DIR / (family + '.md')).relative_to(ROOT).as_posix()}`")
    RUNBOOK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_audit(plan: dict[str, Any], schema: dict[str, Any], rows: list[dict[str, str]], card_paths: list[Path], config_paths: list[Path]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    required_records = int(plan.get("total_required_records", 0))
    commands = [str(command) for command in plan.get("validation_commands", [])]
    command_text = "\n".join(commands)
    add_check(checks, "not_external_evidence_declared", True, "runbook and generated sheets are collection scaffolding only")
    add_check(checks, "operator_row_count_matches_plan", len(rows) == required_records, f"rows={len(rows)}, required={required_records}")
    add_check(checks, "operator_row_count_ge_1440", len(rows) >= 1440, f"rows={len(rows)}")
    add_check(checks, "task_cards_match_tasks", len(card_paths) == int(plan.get("task_family_count", 0)), f"cards={len(card_paths)}")
    add_check(checks, "config_templates_match_tasks", len(config_paths) == int(plan.get("task_family_count", 0)), f"templates={len(config_paths)}")
    add_check(checks, "method_count_ge_12", int(plan.get("method_count", 0)) >= 12, f"method_count={plan.get('method_count')}")
    add_check(checks, "required_fields_ge_28", len(schema.get("required_fields", {})) >= 28, f"required_fields={len(schema.get('required_fields', {}))}")
    add_check(checks, "strict_commands_present", any("--strict" in command for command in commands), "strict validation command found")
    missing_fragments = [fragment for fragment in REQUIRED_COMMAND_FRAGMENTS if fragment not in command_text]
    add_check(
        checks,
        "current_maniskill_route_gates_present",
        not missing_fragments,
        f"missing={missing_fragments}",
    )
    gate_order_fragments = [
        "audit_external_fidelity_acceptance.py",
        "audit_external_backend_contract.py",
        "audit_maniskill_reference_collection_preflight.py",
        "audit_maniskill_render_video_preflight.py",
        "build_external_precollection_freeze_receipt.py",
        "real_collection_runner.py --backend-module <module_or_path>",
        "build_external_postcollection_evidence_seal.py",
        "build_external_manifest.py --write --check-video-paths",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_evidence.py --strict",
    ]
    gate_positions = [command_text.find(fragment) for fragment in gate_order_fragments]
    add_check(
        checks,
        "gate_order_preserves_preflight_before_collection_and_evidence",
        all(position >= 0 for position in gate_positions) and gate_positions == sorted(gate_positions),
        f"positions={dict(zip(gate_order_fragments, gate_positions))}",
    )
    add_check(checks, "operator_sheet_exists", OPERATOR_SHEET.exists(), str(OPERATOR_SHEET.relative_to(ROOT)))
    add_check(checks, "runbook_exists", RUNBOOK_MD.exists(), str(RUNBOOK_MD.relative_to(ROOT)))
    return {
        "version": "external_runbook_audit_v1",
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "runbook": RUNBOOK_MD.relative_to(ROOT).as_posix(),
        "operator_record_sheet": OPERATOR_SHEET.relative_to(ROOT).as_posix(),
        "operator_rows": len(rows),
        "validation_command_count": len(commands),
        "required_command_fragments": REQUIRED_COMMAND_FRAGMENTS,
        "task_cards": [path.relative_to(ROOT).as_posix() for path in card_paths],
        "config_templates": [path.relative_to(ROOT).as_posix() for path in config_paths],
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Runbook Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Operator rows: `{audit['operator_rows']}`.",
        f"Validation commands: `{audit['validation_command_count']}`.",
        f"Runbook: `{audit['runbook']}`.",
        f"Operator sheet: `{audit['operator_record_sheet']}`.",
        "",
        "## Task Cards",
        "",
    ]
    for path in audit["task_cards"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Config Templates", ""])
    for path in audit["config_templates"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Checks", ""])
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    plan = read_json(PLAN_JSON)
    schema = read_json(SCHEMA_JSON)
    names = methods(plan)
    rows = build_operator_rows(plan)
    write_operator_sheet(rows)

    card_paths = []
    config_paths = []
    for task in tasks(plan):
        card_paths.append(write_task_card(task, names))
        config_paths.append(write_config_template(task))
    write_runbook(plan, schema, len(rows))

    audit = build_audit(plan, schema, rows, card_paths, config_paths)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    status = "PASS" if audit["passed"] else "FAIL"
    print(f"External runbook audit: {status}; operator_rows={audit['operator_rows']}; not_evidence={audit['not_external_evidence']}")
    print(f"Wrote {RUNBOOK_MD}")
    print(f"Wrote {OPERATOR_SHEET}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
