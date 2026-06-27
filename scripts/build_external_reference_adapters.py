from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
BASELINES = EXTERNAL / "baselines"
SPEC_DIR = EXTERNAL / "baseline_specs"
RESULTS = ROOT / "results"

OUT_JSON = RESULTS / "external_reference_adapter_audit.json"
OUT_MD = RESULTS / "external_reference_adapter_audit.md"
SUMMARY_MD = EXTERNAL / "reference_adapter_report.md"

NON_ORACLE_EXCLUDED = {"oracle_basin_composer"}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def spec_methods() -> list[str]:
    if not SPEC_DIR.exists():
        raise SystemExit(f"missing baseline spec directory: {SPEC_DIR}")
    methods = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        payload = read_json(path)
        method = str(payload.get("method", "")).strip()
        if method:
            methods.append(method)
    if not methods:
        raise SystemExit(f"no baseline specs found in {SPEC_DIR}")
    return methods


def adapter_wrapper(method: str) -> str:
    return f'''from __future__ import annotations

import sys
from pathlib import Path


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common_reference_adapter import make_adapter


METHOD_NAME = "{method}"
REFERENCE_IMPLEMENTATION = True
ADAPTER_VERSION = "paper119_reference_adapter_v1"

_ADAPTER = make_adapter(METHOD_NAME)


def initialize(config):
    return _ADAPTER.initialize(config)


def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    return _ADAPTER.propose(observation, terminal_samples, skill_i, skill_j, compute_budget)


def log(episode_context, proposal, outcome):
    return _ADAPTER.log(episode_context, proposal, outcome)


def reset(reset_context):
    return _ADAPTER.reset(reset_context)
'''


def write_reference_adapter(method: str) -> dict[str, Any]:
    method_dir = BASELINES / method
    method_dir.mkdir(parents=True, exist_ok=True)
    adapter_path = method_dir / "adapter.py"
    metadata_path = method_dir / "reference_adapter_metadata.json"
    adapter_path.write_text(adapter_wrapper(method), encoding="utf-8")
    metadata = {
        "version": "paper119_reference_adapter_metadata_v1",
        "method": method,
        "adapter": rel(adapter_path),
        "reference_implementation": True,
        "evidence_status": "implementation_only_not_rollout_evidence",
        "strict_manifest_path": rel(adapter_path),
        "uses_shared_common_adapter": rel(BASELINES / "common_reference_adapter.py"),
        "oracle_boundary": "post_hoc_upper_bound_only" if method in NON_ORACLE_EXCLUDED else "non_oracle_reference_adapter",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "method": method,
        "adapter": rel(adapter_path),
        "metadata": rel(metadata_path),
        "oracle_boundary": metadata["oracle_boundary"],
    }


def import_validator():
    sys.path.insert(0, str(ROOT))
    from scripts.validate_external_adapters import validate_adapter

    return validate_adapter


def build_audit(entries: list[dict[str, Any]]) -> dict[str, Any]:
    validate_adapter = import_validator()
    checks: list[dict[str, Any]] = []
    adapter_results: list[dict[str, Any]] = []
    missing = []
    for entry in entries:
        path = ROOT / entry["adapter"]
        if not path.exists():
            missing.append(entry["adapter"])
            continue
        ok, errors = validate_adapter(path, str(entry["method"]), strict=True)
        adapter_results.append(
            {
                "method": entry["method"],
                "path": entry["adapter"],
                "passed": ok,
                "errors": errors,
            }
        )

    failed = [item for item in adapter_results if item["passed"] is not True]
    non_oracle = [item for item in adapter_results if item["method"] not in NON_ORACLE_EXCLUDED]
    add_check(checks, "common_reference_adapter_exists", (BASELINES / "common_reference_adapter.py").exists(), rel(BASELINES / "common_reference_adapter.py"))
    add_check(checks, "reference_adapters_exist", not missing, f"missing={missing}")
    add_check(checks, "method_count_ge_12", len(adapter_results) >= 12, f"methods={len(adapter_results)}")
    add_check(checks, "non_oracle_reference_adapters_ge_11", len(non_oracle) >= 11, f"non_oracle={len(non_oracle)}")
    add_check(checks, "all_reference_adapters_pass_contract", not failed and bool(adapter_results), f"failed={failed[:4]}")
    add_check(
        checks,
        "audit_not_rollout_evidence",
        True,
        "reference adapters are executable implementation shims, not robot or high-fidelity rollout evidence",
    )

    return {
        "version": "external_reference_adapter_audit_v1",
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "implementation_only_not_rollout_evidence": True,
        "adapter_count": len(adapter_results),
        "non_oracle_adapter_count": len(non_oracle),
        "entries": entries,
        "adapter_results": adapter_results,
        "checks": checks,
        "failed_adapters": failed,
    }


def write_summary(audit: dict[str, Any]) -> None:
    lines = [
        "# External Reference Adapter Report",
        "",
        "Not external evidence: `true`.",
        "Evidence status: `implementation_only_not_rollout_evidence`.",
        "",
        "These adapters are executable reference implementations for the external validation harness. They can remove adapter engineering ambiguity for an independent operator, but they do not supply real robot or accepted high-fidelity simulator evidence by themselves.",
        "",
        "Strict evidence still requires a manifest, raw JSONL logs, videos, task configs, checkpoints or hashes, and recomputed rollout metrics.",
        "",
        "## Adapters",
        "",
    ]
    for entry in audit["entries"]:
        lines.append(f"- `{entry['method']}`: `{entry['adapter']}`; metadata `{entry['metadata']}`.")
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    md = [
        "# External Reference Adapter Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Adapters checked: `{audit['adapter_count']}`.",
        f"Non-oracle adapters: `{audit['non_oracle_adapter_count']}`.",
        "",
        "This audit imports and exercises the executable reference adapters against the same API used by strict manifest-declared evidence validation. It is an implementation-readiness check only.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        md.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    md.extend(["", "## Adapter Results", ""])
    for result in audit["adapter_results"]:
        status = "pass" if result["passed"] else "fail"
        detail = "; ".join(result["errors"]) if result["errors"] else "ok"
        md.append(f"- `{status}` `{result['method']}`: `{result['path']}`; {detail}")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    BASELINES.mkdir(parents=True, exist_ok=True)
    entries = [write_reference_adapter(method) for method in spec_methods()]
    audit = build_audit(entries)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(audit)
    status = "PASS" if audit["passed"] else "FAIL"
    print(f"External reference adapter audit: {status}; adapters={audit['adapter_count']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {SUMMARY_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
