from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SCHEMA = EXTERNAL / "config_schema_v1.json"
TEMPLATE_DIR = EXTERNAL / "config_templates"
MANIFEST = EXTERNAL / "manifest.json"
TEMPLATE_OUT_JSON = RESULTS / "external_config_template_audit.json"
TEMPLATE_OUT_MD = RESULTS / "external_config_template_audit.md"
EVIDENCE_OUT_JSON = RESULTS / "external_config_evidence_audit.json"
EVIDENCE_OUT_MD = RESULTS / "external_config_evidence_audit.md"
HEX_DIGITS = set("0123456789abcdefABCDEF")


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in HEX_DIGITS for char in value)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def contains_forbidden_placeholder(value: Any, forbidden: set[str]) -> bool:
    if isinstance(value, str):
        return value in forbidden
    if isinstance(value, dict):
        return any(contains_forbidden_placeholder(item, forbidden) for item in value.values())
    if isinstance(value, list):
        return any(contains_forbidden_placeholder(item, forbidden) for item in value)
    return False


def backend_task_binding_errors(config: dict[str, Any]) -> list[str]:
    binding = config.get("backend_task_binding")
    if binding is None:
        return []
    errors: list[str] = []
    if not isinstance(binding, dict):
        return ["backend_task_binding must be an object when present"]
    for field in ("binding_source", "registry_probe_report", "primary_route", "primary_env_id", "binding_strength"):
        if not isinstance(binding.get(field), str) or not binding.get(field):
            errors.append(f"backend_task_binding.{field} must be nonempty string")
    support = binding.get("support_env_ids", [])
    if not isinstance(support, list):
        errors.append("backend_task_binding.support_env_ids must be a list")
    if binding.get("requires_operator_fidelity_acceptance") is not True:
        errors.append("backend_task_binding.requires_operator_fidelity_acceptance must be true")
    if binding.get("accepted_task_binding_ready") is not False:
        errors.append("backend_task_binding.accepted_task_binding_ready must remain false before fidelity acceptance")
    if binding.get("strict_external_evidence_ready") is not False:
        errors.append("backend_task_binding.strict_external_evidence_ready must remain false")
    return errors


def validate_config(path: Path, schema: dict[str, Any], *, strict: bool, manifest_task: dict[str, Any] | None = None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    config = read_json(path)
    required = set(schema.get("required_fields", []))
    missing = sorted(required - set(config))
    if missing:
        errors.append(f"missing required fields {missing}")

    expected_version = schema["evidence_version"] if strict else schema["template_version"]
    if config.get("version") != expected_version:
        errors.append(f"version={config.get('version')!r}, expected={expected_version!r}")
    if config.get("config_schema") != "external_validation/config_schema_v1.json":
        errors.append(f"config_schema={config.get('config_schema')!r}")

    allowed_tasks = set(schema.get("allowed_task_families", []))
    if config.get("task_family") not in allowed_tasks:
        errors.append(f"invalid task_family={config.get('task_family')!r}")
    allowed_platforms = set(schema.get("allowed_platform_types", []))
    if config.get("platform_type") not in allowed_platforms:
        errors.append(f"invalid platform_type={config.get('platform_type')!r}")

    if not isinstance(config.get("skill_i"), str) or not config.get("skill_i"):
        errors.append("skill_i must be nonempty string")
    if not isinstance(config.get("skill_j"), str) or not config.get("skill_j"):
        errors.append("skill_j must be nonempty string")
    if not isinstance(config.get("seam_under_test"), str) or len(str(config.get("seam_under_test", ""))) < 20:
        errors.append("seam_under_test must be descriptive")
    if not isinstance(config.get("required_fidelity_checks"), list) or len(config.get("required_fidelity_checks", [])) < 3:
        errors.append("required_fidelity_checks must list at least three checks")

    reset_protocol = config.get("reset_protocol", {})
    if not isinstance(reset_protocol, dict):
        errors.append("reset_protocol must be object")
        reset_protocol = {}
    for field in schema.get("required_reset_protocol_fields", []):
        if field not in reset_protocol:
            errors.append(f"reset_protocol missing {field}")
    if reset_protocol.get("paired_resets") is not True:
        errors.append("reset_protocol.paired_resets must be true")
    if reset_protocol.get("initial_state_hash_required") is not True:
        errors.append("reset_protocol.initial_state_hash_required must be true")

    paired_reset_count = config.get("paired_reset_count")
    if isinstance(paired_reset_count, bool) or not isinstance(paired_reset_count, int) or paired_reset_count < 30:
        errors.append(f"paired_reset_count={paired_reset_count!r}, expected integer >= 30")
    reset_count = reset_protocol.get("reset_count")
    if isinstance(reset_count, bool) or not isinstance(reset_count, int) or reset_count < 30:
        errors.append(f"reset_protocol.reset_count={reset_count!r}, expected integer >= 30")
    if isinstance(reset_count, int) and isinstance(paired_reset_count, int) and reset_count != paired_reset_count:
        errors.append("reset_protocol.reset_count must equal paired_reset_count")

    observation = config.get("observation_interface", {})
    if not isinstance(observation, dict):
        errors.append("observation_interface must be object")
        observation = {}
    for field in schema.get("required_observation_interface_fields", []):
        if observation.get(field) is not True:
            errors.append(f"observation_interface.{field} must be true")

    compute = config.get("compute_budget", {})
    if not isinstance(compute, dict):
        errors.append("compute_budget must be object")
        compute = {}
    for field in schema.get("required_compute_budget_fields", []):
        if field not in compute:
            errors.append(f"compute_budget missing {field}")
    if compute.get("same_for_all_non_oracle_methods") is not True:
        errors.append("compute_budget.same_for_all_non_oracle_methods must be true")

    budget = config.get("fixed_risk_budget")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or not (0 < float(budget) <= 1):
        errors.append(f"fixed_risk_budget={budget!r}, expected numeric in (0, 1]")

    must_log = set(config.get("must_log", [])) if isinstance(config.get("must_log"), list) else set()
    missing_log = sorted(set(schema.get("required_log_fields", [])) - must_log)
    if missing_log:
        errors.append(f"must_log missing {missing_log}")
    errors.extend(backend_task_binding_errors(config))

    if strict:
        if config.get("not_external_evidence") is True or config.get("template_only") is True:
            errors.append("strict config must not be marked not_external_evidence/template_only")
        forbidden = set(schema.get("strict_forbidden_values", []))
        if contains_forbidden_placeholder(config, forbidden):
            errors.append("strict config contains template placeholder values")
        if manifest_task:
            manifest_config_hash = manifest_task.get("config_hash")
            if not manifest_config_hash:
                errors.append("manifest config_hash is required for strict config evidence")
            elif not is_sha256(manifest_config_hash):
                errors.append("manifest config_hash must be 64-character SHA256")
            elif sha256_file(path).lower() != str(manifest_config_hash).lower():
                errors.append("manifest config_hash does not match config_path")
            for key in ("task_family", "platform_type"):
                if config.get(key) != manifest_task.get(key):
                    errors.append(f"{key} mismatch: config={config.get(key)!r}, manifest={manifest_task.get(key)!r}")
            if isinstance(manifest_task.get("episodes_per_method"), int) and paired_reset_count < manifest_task["episodes_per_method"]:
                errors.append("paired_reset_count is smaller than manifest episodes_per_method")
    else:
        if config.get("not_external_evidence") is not True or config.get("template_only") is not True:
            errors.append("template config must be marked not_external_evidence and template_only")

    return not errors, errors


def template_paths() -> list[Path]:
    if not TEMPLATE_DIR.exists():
        return []
    return sorted(TEMPLATE_DIR.glob("*.json"))


def manifest_config_entries() -> list[tuple[dict[str, Any], Path]]:
    if not MANIFEST.exists():
        return []
    manifest = read_json(MANIFEST)
    tasks = manifest.get("tasks", [])
    tasks = tasks if isinstance(tasks, list) else []
    entries: list[tuple[dict[str, Any], Path]] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        config_path = str(task.get("config_path", ""))
        if config_path:
            entries.append((task, rel_path(config_path)))
    return entries


def build_audit(*, strict: bool) -> dict[str, Any]:
    schema = read_json(SCHEMA)
    checks: list[dict[str, Any]] = []
    add_check(checks, "config_schema_exists", SCHEMA.exists(), str(SCHEMA))
    add_check(checks, "config_schema_version", schema.get("version") == "external_config_schema_v1", f"version={schema.get('version')!r}")

    results = []
    if strict:
        entries = manifest_config_entries()
        add_check(checks, "manifest_exists", MANIFEST.exists(), str(MANIFEST) if MANIFEST.exists() else "external_validation/manifest.json missing")
        add_check(checks, "manifest_config_entries_present", bool(entries), f"entries={len(entries)}")
        for task, path in entries:
            if not path.exists():
                results.append({"path": path.relative_to(ROOT).as_posix() if not path.is_absolute() else str(path), "passed": False, "errors": ["config file missing"]})
                continue
            ok, errors = validate_config(path, schema, strict=True, manifest_task=task)
            results.append({"path": path.relative_to(ROOT).as_posix(), "passed": ok, "errors": errors})
    else:
        paths = template_paths()
        add_check(checks, "template_count_ge_4", len(paths) >= 4, f"templates={len(paths)}")
        for path in paths:
            ok, errors = validate_config(path, schema, strict=False)
            results.append({"path": path.relative_to(ROOT).as_posix(), "passed": ok, "errors": errors})

    failed = [result for result in results if not result["passed"]]
    add_check(checks, "configs_pass_validation", bool(results) and not failed, f"failed={len(failed)}")

    return {
        "version": "external_config_evidence_audit_v1" if strict else "external_config_template_audit_v1",
        "strict": strict,
        "not_external_evidence": not strict,
        "passed": all(check["passed"] for check in checks),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "config_count": len(results),
        "failed_configs": failed,
        "config_results": results,
        "checks": checks,
    }


def write_md(audit: dict[str, Any], path: Path) -> None:
    lines = [
        "# External Config Evidence Audit" if audit["strict"] else "# External Config Template Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Strict: `{str(audit['strict']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Configs checked: `{audit['config_count']}`.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(["", "## Config Results", ""])
    for result in audit["config_results"]:
        status = "pass" if result["passed"] else "fail"
        detail = "; ".join(result["errors"]) if result["errors"] else "ok"
        lines.append(f"- `{status}` `{result['path']}`: {detail}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Paper 119 external task config templates or strict evidence configs.")
    parser.add_argument("--strict", action="store_true", help="Validate manifest-declared real configs instead of non-evidence templates.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    audit = build_audit(strict=args.strict)
    out_json = EVIDENCE_OUT_JSON if args.strict else TEMPLATE_OUT_JSON
    out_md = EVIDENCE_OUT_MD if args.strict else TEMPLATE_OUT_MD
    out_json.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(audit, out_md)

    label = "External config evidence audit" if args.strict else "External config template audit"
    status = "PASS" if audit["passed"] else "NOT_READY"
    print(f"{label}: {status}; configs={audit['config_count']}")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0 if audit["passed"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
