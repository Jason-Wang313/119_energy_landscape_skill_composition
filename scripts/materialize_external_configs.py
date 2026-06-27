from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SCHEMA = EXTERNAL / "config_schema_v1.json"
TEMPLATE_DIR = EXTERNAL / "config_templates"
OUTPUT_DIR = EXTERNAL / "configs"
OUT_JSON = RESULTS / "external_config_materialization_plan.json"
OUT_MD = RESULTS / "external_config_materialization_plan.md"

FORBIDDEN_WRITE_TOKENS = {"FILL", "REPLACE", "TEMPLATE", "DRY_RUN", "NOT_EVIDENCE", "PLACEHOLDER"}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def has_forbidden_write_token(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_forbidden_write_token(item) for item in value.values())
    if isinstance(value, list):
        return any(has_forbidden_write_token(item) for item in value)
    if not isinstance(value, str):
        return False
    upper = value.upper()
    return any(token in upper for token in FORBIDDEN_WRITE_TOKENS)


def template_paths(template_dir: Path) -> list[Path]:
    if not template_dir.exists():
        return []
    return sorted(template_dir.glob("*.json"))


def materialize_template(template: dict[str, Any], args: argparse.Namespace, schema: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(template))
    payload["version"] = schema["evidence_version"]
    payload["platform_type"] = args.platform_type
    payload["platform_name"] = args.platform_name
    payload["paired_reset_count"] = int(args.paired_reset_count)
    payload["not_external_evidence"] = False
    payload.pop("template_only", None)
    payload["compute_budget"]["wall_clock_seconds"] = int(args.wall_clock_seconds)
    payload["compute_budget"]["simulator_query_budget"] = int(args.simulator_query_budget)
    payload["reset_protocol"]["reset_count"] = int(args.paired_reset_count)
    return payload


def validate_payload(payload: dict[str, Any], schema: dict[str, Any], *, for_write: bool) -> list[str]:
    errors: list[str] = []
    missing = sorted(set(schema.get("required_fields", [])) - set(payload))
    if missing:
        errors.append(f"missing required fields {missing}")
    if payload.get("version") != schema.get("evidence_version"):
        errors.append(f"version={payload.get('version')!r}, expected={schema.get('evidence_version')!r}")
    if payload.get("not_external_evidence") is True or payload.get("template_only") is True:
        errors.append("materialized config must not be marked not_external_evidence/template_only")
    if payload.get("platform_type") not in set(schema.get("allowed_platform_types", [])):
        errors.append(f"invalid platform_type={payload.get('platform_type')!r}")
    if not payload.get("platform_name"):
        errors.append("platform_name must be nonempty")
    compute = payload.get("compute_budget", {})
    if compute.get("same_for_all_non_oracle_methods") is not True:
        errors.append("compute_budget.same_for_all_non_oracle_methods must remain true")
    for field in schema.get("required_compute_budget_fields", []):
        if field not in compute:
            errors.append(f"compute_budget missing {field}")
    if for_write and has_forbidden_write_token(payload):
        errors.append("write blocked because materialized payload still contains dry-run/template/placeholder tokens")
    return errors


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    schema = read_json(args.schema)
    paths = template_paths(args.template_dir)
    checks: list[dict[str, Any]] = []
    add_check(checks, "schema_exists", args.schema.exists(), rel(args.schema))
    add_check(checks, "schema_version", schema.get("version") == "external_config_schema_v1", f"version={schema.get('version')!r}")
    add_check(checks, "template_dir_exists", args.template_dir.exists(), rel(args.template_dir))
    add_check(checks, "template_count_ge_4", len(paths) >= 4, f"templates={len(paths)}")
    add_check(checks, "output_dir_exists", args.output_dir.exists(), rel(args.output_dir))
    add_check(
        checks,
        "write_requires_explicit_flag",
        args.write is False or args.confirm_real_platform is True,
        f"write={args.write!r}, confirm_real_platform={args.confirm_real_platform!r}",
    )

    materialized: list[dict[str, Any]] = []
    errors_by_task: dict[str, list[str]] = {}
    for path in paths:
        template = read_json(path)
        task = str(template.get("task_family", path.stem))
        payload = materialize_template(template, args, schema)
        errors = validate_payload(payload, schema, for_write=args.write)
        errors_by_task[task] = errors
        materialized.append(
            {
                "task_family": task,
                "template_path": rel(path),
                "output_path": rel(args.output_dir / f"{task}.json"),
                "passed": not errors,
                "errors": errors,
            }
        )

    add_check(
        checks,
        "materialized_payloads_validate",
        bool(materialized) and all(item["passed"] for item in materialized),
        f"failed={[item['task_family'] for item in materialized if not item['passed']]}",
    )

    passed = all(check["passed"] for check in checks)
    files_written: list[str] = []
    if args.write and not passed:
        raise SystemExit("refusing to write external configs because materialization checks did not pass")
    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for path in paths:
            template = read_json(path)
            task = str(template.get("task_family", path.stem))
            payload = materialize_template(template, args, schema)
            target = args.output_dir / f"{task}.json"
            if target.exists() and not args.force:
                raise SystemExit(f"refusing to overwrite existing config without --force: {target}")
            target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            files_written.append(rel(target))

    return {
        "version": "external_config_materialization_plan_v1",
        "passed": passed,
        "not_external_evidence": True,
        "write_enabled": bool(args.write),
        "confirm_real_platform": bool(args.confirm_real_platform),
        "materialization_ready_for_operator": passed and not args.write,
        "strict_config_evidence_ready": False,
        "schema": rel(args.schema),
        "template_dir": rel(args.template_dir),
        "output_dir": rel(args.output_dir),
        "platform_type": args.platform_type,
        "platform_name": args.platform_name,
        "paired_reset_count": int(args.paired_reset_count),
        "wall_clock_seconds": int(args.wall_clock_seconds),
        "simulator_query_budget": int(args.simulator_query_budget),
        "task_count": len(materialized),
        "materialized_configs": materialized,
        "files_written": files_written,
        "operator_write_command": (
            "python scripts\\materialize_external_configs.py "
            "--platform-type <real_robot|high_fidelity_sim> "
            "--platform-name <accepted_platform_name> "
            "--wall-clock-seconds <seconds> "
            "--simulator-query-budget <queries> "
            "--confirm-real-platform --write"
        ),
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Config Materialization Plan",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Write enabled: `{str(payload['write_enabled']).lower()}`.",
        f"Strict config evidence ready: `{str(payload['strict_config_evidence_ready']).lower()}`.",
        "",
        "This report checks that real task configs can be materialized from the non-evidence templates once an operator supplies a real platform and compute budget. The default report does not write configs and does not satisfy strict config evidence.",
        "",
        "## Operator Write Command",
        "",
        "```powershell",
        payload["operator_write_command"],
        "```",
        "",
        "## Materialized Config Targets",
        "",
        "| Task | Template | Output | Status |",
        "|---|---|---|---|",
    ]
    for item in payload["materialized_configs"]:
        status = "pass" if item["passed"] else "fail"
        lines.append(f"| `{item['task_family']}` | `{item['template_path']}` | `{item['output_path']}` | `{status}` |")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize real Paper 119 external task configs from guarded templates.")
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--template-dir", type=Path, default=TEMPLATE_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--platform-type", choices=["real_robot", "high_fidelity_sim"], default="high_fidelity_sim")
    parser.add_argument("--platform-name", default="DRY_RUN_PLATFORM_NOT_EVIDENCE")
    parser.add_argument("--wall-clock-seconds", type=int, default=30)
    parser.add_argument("--simulator-query-budget", type=int, default=100)
    parser.add_argument("--paired-reset-count", type=int, default=30)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--confirm-real-platform", action="store_true")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "External config materialization plan: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"tasks={payload['task_count']}; write={payload['write_enabled']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
