from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SPEC_DIR = EXTERNAL / "baseline_specs"
BASELINES_DIR = EXTERNAL / "baselines"
MANIFEST = EXTERNAL / "manifest.json"
LOG_SCHEMA = EXTERNAL / "log_schema_v1.json"
OUT_JSON = RESULTS / "external_adapter_contract_audit.json"
OUT_MD = RESULTS / "external_adapter_contract_audit.md"
EVIDENCE_OUT_JSON = RESULTS / "external_adapter_contract_evidence_audit.json"
EVIDENCE_OUT_MD = RESULTS / "external_adapter_contract_evidence_audit.md"

REQUIRED_API = ("initialize", "propose", "log", "reset")
REQUIRED_PROPOSAL_FIELDS = ("decision", "predicted_seam_risk", "failure_diagnosis", "repair_action")
REQUIRED_LOG_FIELDS = ("predicted_seam_risk", "decision", "failure_diagnosis", "repair_action", "policy_or_config_hash")
NON_ORACLE_EXCLUDED = {"oracle_basin_composer"}
HEX64 = "0123456789abcdef"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in HEX64 for char in value.lower())


def is_scaffold(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="ignore")
        return "SCAFFOLD_ONLY = True" in text or "NOT_EXTERNAL_EVIDENCE = True" in text
    metadata = path / "adapter_metadata.json"
    if metadata.exists():
        try:
            payload = read_json(metadata)
        except SystemExit:
            return True
        return payload.get("scaffold_only") is True or payload.get("not_external_evidence") is True
    return False


def import_adapter(path: Path) -> tuple[ModuleType | None, list[str]]:
    errors: list[str] = []
    if not path.exists():
        return None, [f"adapter path missing: {path}"]
    if path.is_dir():
        candidates = [path / "adapter.py", path / "adapter_template.py"]
        path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    if path.suffix != ".py":
        return None, [f"adapter path must be a .py file or directory containing adapter.py: {path}"]
    name = f"paper119_adapter_{digest(str(path))[:12]}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None, [f"could not import adapter: {path}"]
    module = importlib.util.module_from_spec(spec)
    old_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - report adapter import failures.
        errors.append(f"adapter import raised {type(exc).__name__}: {exc}")
        return None, errors
    finally:
        sys.dont_write_bytecode = old_dont_write_bytecode
    return module, errors


def synthetic_inputs(method: str) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    observation = {
        "scene_id": "synthetic_scene_000",
        "task_family": "peg_place_regrasp",
        "state": {"gripper_pose": [0.0, 0.1, 0.2], "object_pose": [0.2, 0.1, 0.0]},
        "contact": {"force_norm": 0.4, "mode": "free_to_contact"},
    }
    terminal_samples = [
        {"sample_id": "sample_0", "state_hash": digest("sample_0"), "features": [0.1, 0.2, 0.3]},
        {"sample_id": "sample_1", "state_hash": digest("sample_1"), "features": [0.2, 0.3, 0.4]},
    ]
    config = {
        "method_name": method,
        "policy_or_config_hash": digest(f"{method}:synthetic_config"),
        "fixed_risk_budget": 0.15,
    }
    compute_budget = {"wall_clock_seconds": 1.0, "simulator_query_budget": 4}
    outcome = {
        "success": True,
        "realized_seam_breach": False,
        "utility": 1.0,
        "composition_cost": 0.1,
    }
    return observation, terminal_samples, config, compute_budget, outcome


def validate_numeric_probability(value: Any, field: str, errors: list[str]) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{field} must be numeric in [0, 1]")
    elif not 0.0 <= float(value) <= 1.0:
        errors.append(f"{field}={value!r} outside [0, 1]")


def validate_adapter(path: Path, method: str, *, strict: bool) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if strict and is_scaffold(path):
        errors.append("strict adapter validation rejects scaffold/not_external_evidence implementations")
    module, import_errors = import_adapter(path)
    errors.extend(import_errors)
    if module is None:
        return False, errors

    for name in REQUIRED_API:
        if not callable(getattr(module, name, None)):
            errors.append(f"missing callable {name}")
    if errors:
        return False, errors

    observation, terminal_samples, config, compute_budget, outcome = synthetic_inputs(method)
    try:
        init_result = module.initialize(dict(config))
    except NotImplementedError:
        errors.append("initialize raised NotImplementedError")
        return False, errors
    except Exception as exc:  # noqa: BLE001 - report adapter execution failures.
        errors.append(f"initialize raised {type(exc).__name__}: {exc}")
        return False, errors
    if not isinstance(init_result, dict):
        errors.append("initialize must return a dict")

    try:
        proposal = module.propose(dict(observation), list(terminal_samples), "source_skill", "target_skill", dict(compute_budget))
    except NotImplementedError:
        errors.append("propose raised NotImplementedError")
        return False, errors
    except Exception as exc:  # noqa: BLE001
        errors.append(f"propose raised {type(exc).__name__}: {exc}")
        return False, errors
    if not isinstance(proposal, dict):
        errors.append("propose must return a dict")
        proposal = {}
    for field in REQUIRED_PROPOSAL_FIELDS:
        if field not in proposal:
            errors.append(f"proposal missing {field}")
    if "predicted_seam_risk" in proposal:
        validate_numeric_probability(proposal["predicted_seam_risk"], "proposal.predicted_seam_risk", errors)

    try:
        log_record = module.log(
            {"scene_id": observation["scene_id"], "method": method, "episode_index": 0},
            dict(proposal),
            dict(outcome),
        )
    except NotImplementedError:
        errors.append("log raised NotImplementedError")
        return False, errors
    except Exception as exc:  # noqa: BLE001
        errors.append(f"log raised {type(exc).__name__}: {exc}")
        return False, errors
    if not isinstance(log_record, dict):
        errors.append("log must return a dict")
        log_record = {}
    for field in REQUIRED_LOG_FIELDS:
        if field not in log_record:
            errors.append(f"log record missing {field}")
    if "predicted_seam_risk" in log_record:
        validate_numeric_probability(log_record["predicted_seam_risk"], "log.predicted_seam_risk", errors)
    if "policy_or_config_hash" in log_record and not is_hash(log_record["policy_or_config_hash"]):
        errors.append("log.policy_or_config_hash must be a 64-character SHA256")

    try:
        module.reset({"scene_id": observation["scene_id"], "seed": 0})
    except NotImplementedError:
        errors.append("reset raised NotImplementedError")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"reset raised {type(exc).__name__}: {exc}")

    return not errors, errors


def write_temp_adapter(path: Path, *, valid: bool) -> None:
    if valid:
        path.write_text(
            f"""
POLICY_HASH = "{digest('valid_adapter_policy')}"

def initialize(config):
    return {{"method_name": config.get("method_name"), "policy_or_config_hash": POLICY_HASH}}

def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    return {{
        "decision": "accept",
        "predicted_seam_risk": 0.05,
        "failure_diagnosis": "none",
        "repair_action": "none",
    }}

def log(episode_context, proposal, outcome):
    return {{
        "predicted_seam_risk": proposal["predicted_seam_risk"],
        "decision": proposal["decision"],
        "failure_diagnosis": proposal["failure_diagnosis"],
        "repair_action": proposal["repair_action"],
        "policy_or_config_hash": POLICY_HASH,
    }}

def reset(reset_context):
    return None
""".lstrip(),
            encoding="utf-8",
        )
    else:
        path.write_text(
            """
def initialize(config):
    return {}

def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    return {"decision": "accept"}
""".lstrip(),
            encoding="utf-8",
        )


def run_contract_self_test() -> tuple[bool, list[str]]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="paper119_adapter_contract_") as tmp_name:
        tmp = Path(tmp_name)
        good = tmp / "good_adapter.py"
        bad = tmp / "bad_adapter.py"
        write_temp_adapter(good, valid=True)
        write_temp_adapter(bad, valid=False)
        good_ok, good_errors = validate_adapter(good, "synthetic_good_adapter", strict=True)
        if not good_ok:
            errors.append(f"valid temporary adapter failed: {good_errors}")
        bad_ok, bad_errors = validate_adapter(bad, "synthetic_bad_adapter", strict=True)
        if bad_ok:
            errors.append("invalid temporary adapter unexpectedly passed")
        if not any("missing callable log" in error or "proposal missing" in error for error in bad_errors):
            errors.append(f"invalid temporary adapter failed for the wrong reason: {bad_errors}")
    return not errors, errors


def baseline_spec_methods() -> list[str]:
    if not SPEC_DIR.exists():
        return []
    methods = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        payload = read_json(path)
        method = str(payload.get("method", "")).strip()
        if method:
            methods.append(method)
    return methods


def manifest_implementation_entries() -> list[tuple[str, Path]]:
    if not MANIFEST.exists():
        return []
    manifest = read_json(MANIFEST)
    entries = []
    methods = manifest.get("methods", [])
    methods = methods if isinstance(methods, list) else []
    for method in methods:
        if not isinstance(method, dict):
            continue
        name = str(method.get("name", "")).strip()
        if not name or name in NON_ORACLE_EXCLUDED:
            continue
        implementation = str(method.get("implementation", "")).strip()
        if implementation:
            entries.append((name, rel_path(implementation)))
    return entries


def scaffold_paths() -> list[tuple[str, Path]]:
    paths = []
    for method in baseline_spec_methods():
        if method in NON_ORACLE_EXCLUDED:
            continue
        paths.append((method, BASELINES_DIR / method / "adapter_template.py"))
    return paths


def build_audit(*, strict: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    spec_methods = baseline_spec_methods()
    self_test_ok, self_test_errors = run_contract_self_test()

    add_check(checks, "baseline_specs_present", len(spec_methods) >= 12, f"spec_methods={len(spec_methods)}")
    add_check(checks, "contract_self_test_passed", self_test_ok, "; ".join(self_test_errors) if self_test_errors else "temporary good/bad adapters behaved as expected")
    add_check(checks, "log_schema_exists", LOG_SCHEMA.exists(), str(LOG_SCHEMA))

    entries = manifest_implementation_entries() if strict else scaffold_paths()
    if strict:
        add_check(checks, "manifest_exists", MANIFEST.exists(), str(MANIFEST) if MANIFEST.exists() else "external_validation/manifest.json missing")
        add_check(checks, "manifest_implementation_entries_present", bool(entries), f"entries={len(entries)}")
    else:
        add_check(checks, "scaffold_entries_present", len(entries) >= 11, f"entries={len(entries)}")

    for method, path in entries:
        ok, errors = validate_adapter(path, method, strict=strict)
        if not strict and is_scaffold(path):
            # Non-strict mode checks that scaffolds are structurally present, not executable evidence.
            text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
            structural_errors = []
            for name in REQUIRED_API:
                if f"def {name}(" not in text:
                    structural_errors.append(f"missing function {name}")
            if "raise NotImplementedError" not in text:
                structural_errors.append("scaffold should raise NotImplementedError")
            ok = not structural_errors
            errors = structural_errors
        results.append(
            {
                "method": method,
                "path": path.relative_to(ROOT).as_posix() if path.exists() and path.is_relative_to(ROOT) else str(path),
                "passed": ok,
                "errors": errors,
            }
        )

    failed = [item for item in results if not item["passed"]]
    add_check(checks, "adapter_results_passed", bool(results) and not failed, f"failed={len(failed)}")

    passed = all(check["passed"] for check in checks)
    return {
        "version": "external_adapter_contract_evidence_audit_v1" if strict else "external_adapter_contract_audit_v1",
        "strict": strict,
        "not_external_evidence": not strict,
        "passed": passed,
        "adapter_count": len(results),
        "failed_adapters": failed,
        "adapter_results": results,
        "checks": checks,
    }


def write_outputs(audit: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    out_json = EVIDENCE_OUT_JSON if audit["strict"] else OUT_JSON
    out_md = EVIDENCE_OUT_MD if audit["strict"] else OUT_MD
    out_json.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Adapter Contract Evidence Audit" if audit["strict"] else "# External Adapter Contract Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Strict: `{str(audit['strict']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Adapters checked: `{audit['adapter_count']}`.",
        "",
        "Non-strict mode validates the adapter contract harness and scaffold structure only. Strict mode validates manifest-declared real implementations and rejects scaffold-only adapters.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    lines.extend(["", "## Adapter Results", ""])
    for result in audit["adapter_results"]:
        status = "pass" if result["passed"] else "fail"
        detail = "; ".join(result["errors"]) if result["errors"] else "ok"
        lines.append(f"- `{status}` `{result['method']}`: `{result['path']}`; {detail}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Paper 119 external baseline adapter contract.")
    parser.add_argument("--strict", action="store_true", help="Validate manifest-declared real implementations instead of scaffold structure.")
    args = parser.parse_args()

    audit = build_audit(strict=args.strict)
    write_outputs(audit)
    label = "External adapter contract evidence audit" if args.strict else "External adapter contract audit"
    status = "PASS" if audit["passed"] else "NOT_READY"
    print(f"{label}: {status}; adapters={audit['adapter_count']}")
    print(f"Wrote {EVIDENCE_OUT_JSON if args.strict else OUT_JSON}")
    print(f"Wrote {EVIDENCE_OUT_MD if args.strict else OUT_MD}")
    return 0 if audit["passed"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
