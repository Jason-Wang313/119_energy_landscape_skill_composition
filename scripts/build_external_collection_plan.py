from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_TEMPLATE = EXTERNAL / "manifest_template.json"
DEFAULT_SCHEMA = EXTERNAL / "log_schema_v1.json"
OUT_JSON = RESULTS / "external_collection_plan.json"
OUT_MD = RESULTS / "external_collection_plan.md"


REQUIRED_COMMANDS = [
    r"python scripts\build_external_collection_plan.py",
    r"python scripts\build_external_analysis_plan.py",
    r"python scripts\build_independent_validation_route.py",
    r"python scripts\probe_external_platform.py",
    r"python scripts\probe_maniskill_task_bindings.py",
    r"python scripts\probe_maniskill_env_smoke.py",
    r"python scripts\probe_maniskill_fidelity_metadata.py",
    r"python scripts\build_external_platform_onboarding.py",
    r"python scripts\audit_external_fidelity_acceptance.py",
    r"python scripts\build_external_fidelity_provenance_packet.py",
    r"python scripts\build_external_fidelity_acceptance_draft.py",
    r"python scripts\audit_external_runner_harness.py",
    r"python scripts\audit_external_backend_contract.py",
    r"python scripts\audit_maniskill_backend_readiness.py",
    r"python scripts\audit_maniskill_reference_collection_preflight.py",
    r"python scripts\build_external_backend_integration_packet.py",
    r"python scripts\self_test_external_runner_backend.py",
    r"python scripts\build_external_config_manifest_packet.py",
    r"python scripts\build_external_rollout_evidence_packet.py",
    r"python scripts\audit_external_pilot_smoke.py",
    r"python scripts\build_external_pilot_smoke_packet.py",
    r"python scripts\audit_maniskill_render_video_preflight.py",
    r"python scripts\audit_maniskill_pilot_runtime_liveness.py",
    r"python scripts\build_maniskill_render_machine_qualification.py",
    r"python scripts\build_external_blind_eval_plan.py",
    r"python scripts\audit_external_collection_readiness.py",
    r"python scripts\validate_external_configs.py",
    r"python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
    r"python scripts\build_external_baseline_contract.py",
    r"python scripts\build_external_adapter_scaffolds.py",
    r"python scripts\validate_external_adapters.py",
    r"python scripts\build_external_method_implementation_packet.py",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\audit_external_collection_readiness.py --strict",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence_preflight.py",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
    r"python scripts\build_external_ablation_collection_packet.py",
    r"python scripts\build_external_evidence_intake_ledger.py",
    r"python scripts\audit_external_evidence.py --strict",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def clean_methods(manifest: dict[str, Any]) -> list[str]:
    methods = manifest.get("methods", [])
    if not isinstance(methods, list):
        return []
    names = [str(method.get("name", "")).strip() for method in methods if isinstance(method, dict)]
    return [name for name in names if name]


def clean_tasks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = manifest.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    return [task for task in tasks if isinstance(task, dict)]


def route_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"real_robot": 0, "high_fidelity_sim": 0, "mixed": 0}
    seen: set[tuple[str, str]] = set()
    for task in tasks:
        family = str(task.get("task_family", ""))
        platform = str(task.get("platform_type", ""))
        key = (family, platform)
        if key in seen:
            continue
        seen.add(key)
        if platform in counts:
            counts[platform] += 1
    counts["mixed"] = counts["real_robot"] + counts["high_fidelity_sim"]
    return counts


def route_is_valid(route: str, counts: dict[str, int]) -> bool:
    return (
        (route == "real_robot" and counts["real_robot"] >= 3)
        or (route == "high_fidelity_sim" and counts["high_fidelity_sim"] >= 4)
        or (route == "mixed" and counts["real_robot"] >= 2 and counts["high_fidelity_sim"] >= 2)
    )


def reset_plan(task_family: str, episodes_per_method: int, methods: list[str]) -> list[dict[str, Any]]:
    resets: list[dict[str, Any]] = []
    for index in range(episodes_per_method):
        resets.append(
            {
                "reset_index": index,
                "scene_id": f"{task_family}_reset_{index:03d}",
                "seed": index,
                "skill_i": "REPLACE_WITH_SOURCE_SKILL",
                "skill_j": "REPLACE_WITH_TARGET_SKILL",
                "required_methods": methods,
                "records_required": len(methods),
                "paired_comparison_key_requirements": {
                    "same_task_family": True,
                    "same_platform_type": True,
                    "same_scene_id": True,
                    "same_seed": True,
                    "same_skill_i": True,
                    "same_skill_j": True,
                    "same_initial_state_hash": True,
                },
            }
        )
    return resets


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_plan(manifest: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    methods = clean_methods(manifest)
    tasks = clean_tasks(manifest)
    route = str(manifest.get("route", ""))
    counts = route_counts(tasks)
    required_fields = sorted(schema.get("required_fields", {}).keys())
    paired_key = schema.get("paired_comparison_key", [])
    paired_key = paired_key if isinstance(paired_key, list) else []

    task_plans = []
    total_records = 0
    total_resets = 0
    for task in tasks:
        task_family = str(task.get("task_family", ""))
        episodes = int(task.get("episodes_per_method", 0) or 0)
        planned_resets = reset_plan(task_family, episodes, methods)
        records = episodes * len(methods)
        total_records += records
        total_resets += episodes
        task_plans.append(
            {
                "task_family": task_family,
                "platform_type": str(task.get("platform_type", "")),
                "platform_name": str(task.get("platform_name", "")),
                "episodes_per_method": episodes,
                "required_records": records,
                "log_jsonl": str(task.get("log_jsonl", "")),
                "video_dir": str(task.get("video_dir", "")),
                "config_path": str(task.get("config_path", "")),
                "reset_plan": planned_resets,
            }
        )

    checks: list[dict[str, Any]] = []
    add_check(checks, "route_is_valid", route_is_valid(route, counts), f"route={route}, counts={counts}")
    add_check(checks, "shared_skill_library", manifest.get("shared_skill_library") is True, f"value={manifest.get('shared_skill_library')!r}")
    add_check(checks, "paired_resets", manifest.get("paired_resets") is True, f"value={manifest.get('paired_resets')!r}")
    add_check(checks, "same_initial_states", manifest.get("same_initial_states") is True, f"value={manifest.get('same_initial_states')!r}")
    add_check(checks, "same_observation_interface", manifest.get("same_observation_interface") is True, f"value={manifest.get('same_observation_interface')!r}")
    add_check(checks, "same_compute_budget", manifest.get("same_compute_budget") is True, f"value={manifest.get('same_compute_budget')!r}")
    add_check(checks, "method_count_ge_12", len(methods) >= 12, f"method_count={len(methods)}")
    add_check(checks, "task_count_ge_4", len(tasks) >= 4, f"task_count={len(tasks)}")
    weak_tasks = [plan["task_family"] for plan in task_plans if plan["episodes_per_method"] < 30]
    add_check(checks, "episodes_per_method_ge_30", not weak_tasks, f"weak_tasks={weak_tasks}")
    add_check(checks, "required_fields_complete", len(required_fields) >= 28, f"required_field_count={len(required_fields)}")
    add_check(
        checks,
        "paired_key_contains_initial_state",
        "initial_state_hash" in paired_key and "scene_id" in paired_key and "seed" in paired_key,
        f"paired_key={paired_key}",
    )
    add_check(checks, "total_required_records_ge_1440", total_records >= 1440, f"total_required_records={total_records}")

    return {
        "version": "external_collection_plan_v1",
        "not_external_evidence": True,
        "purpose": "Concrete collection schedule for creating a real external validation package; this plan is not evidence.",
        "source_manifest_template": str(DEFAULT_TEMPLATE.relative_to(ROOT)),
        "source_log_schema": str(DEFAULT_SCHEMA.relative_to(ROOT)),
        "route": route,
        "claim": str(manifest.get("claim", "")),
        "route_counts": counts,
        "method_count": len(methods),
        "methods": methods,
        "task_family_count": len(tasks),
        "total_paired_resets": total_resets,
        "total_required_records": total_records,
        "required_log_fields": required_fields,
        "paired_comparison_key": paired_key,
        "collection_invariants": [
            "Every method must run on the same reset/scene/seed/skill pair for paired comparison.",
            "Every JSONL record must include hashes for the initial state, terminal samples, and method policy/config.",
            "Videos must be linked per episode and must exist before strict validation.",
            "Manifest metrics must be recomputed from JSONL logs; hand-entered metrics are not accepted.",
            "The oracle is a post hoc upper bound and must not be used for deployment decisions.",
            "The selected robot or high-fidelity simulator must clear the fidelity acceptance audit before rollout evidence is counted.",
            "The operator should execute the blinded, randomized sheet so method identity and outcome analysis are separated until logs are frozen.",
        ],
        "validation_commands": REQUIRED_COMMANDS,
        "tasks": task_plans,
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }


def write_md(plan: dict[str, Any]) -> None:
    lines = [
        "# External Collection Plan",
        "",
        f"Passed: `{str(plan['passed']).lower()}`.",
        f"Not evidence: `{str(plan['not_external_evidence']).lower()}`.",
        f"Route: `{plan['route']}`.",
        f"Task families: `{plan['task_family_count']}`.",
        f"Methods: `{plan['method_count']}`.",
        f"Paired resets: `{plan['total_paired_resets']}`.",
        f"Required JSONL records: `{plan['total_required_records']}`.",
        "",
        "This file is a collection schedule only. It does not count as external validation evidence.",
        "",
        "## Validation Commands",
        "",
    ]
    for command in plan["validation_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Invariants", ""])
    for invariant in plan["collection_invariants"]:
        lines.append(f"- {invariant}")
    lines.extend(["", "## Tasks", ""])
    for task in plan["tasks"]:
        lines.append(
            f"- `{task['task_family']}` on `{task['platform_type']}`: "
            f"`{task['episodes_per_method']}` paired resets x `{plan['method_count']}` methods = `{task['required_records']}` records; "
            f"log `{task['log_jsonl']}`; videos `{task['video_dir']}`."
        )
    lines.extend(["", "## Checks", ""])
    for check in plan["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a non-evidence external validation collection plan from the manifest template.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    manifest = read_json(args.template)
    schema = read_json(args.schema)
    plan = build_plan(manifest, schema)

    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(plan)

    status = "PASS" if plan["passed"] else "FAIL"
    print(f"External collection plan: {status}; required_records={plan['total_required_records']}; not_evidence={plan['not_external_evidence']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if plan["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
