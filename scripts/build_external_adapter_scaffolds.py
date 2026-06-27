from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SPEC_DIR = EXTERNAL / "baseline_specs"
BASELINES_DIR = EXTERNAL / "baselines"
SUMMARY_MD = EXTERNAL / "baseline_adapter_scaffold.md"
OUT_JSON = RESULTS / "external_adapter_scaffold_audit.json"
OUT_MD = RESULTS / "external_adapter_scaffold_audit.md"

REQUIRED_API = ["initialize", "propose", "log", "reset"]
ORACLE_METHOD = "oracle_basin_composer"


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def spec_files() -> list[Path]:
    if not SPEC_DIR.exists():
        fail(f"missing baseline spec directory: {SPEC_DIR}")
    files = sorted(SPEC_DIR.glob("*.json"))
    if not files:
        fail(f"no baseline spec files in {SPEC_DIR}")
    return files


def adapter_template(spec: dict[str, Any]) -> str:
    method = str(spec["method"])
    entrypoint = str(spec.get("required_entrypoint", "declare_method_adapter"))
    return f'''"""
Scaffold-only adapter template for Paper 119 external validation.

This file is not external evidence. Replace every NotImplementedError with an
independent implementation before referencing this method in an evidence
manifest.
"""

NOT_EXTERNAL_EVIDENCE = True
SCAFFOLD_ONLY = True
METHOD_NAME = "{method}"
REQUIRED_ENTRYPOINT = "{entrypoint}"


def initialize(config):
    """Load method config/checkpoint and return declared hashes."""
    raise NotImplementedError(f"Replace scaffold for {{METHOD_NAME}} with an independent implementation.")


def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    """Return seam decision, optional repair action, predicted risk, and diagnosis."""
    raise NotImplementedError(f"Replace scaffold for {{METHOD_NAME}} with an independent implementation.")


def log(episode_context, proposal, outcome):
    """Return JSONL-ready fields required by external_validation/log_schema_v1.json."""
    raise NotImplementedError(f"Replace scaffold for {{METHOD_NAME}} with an independent implementation.")


def reset(reset_context):
    """Clear method-local state between paired resets unless online memory is explicitly logged."""
    raise NotImplementedError(f"Replace scaffold for {{METHOD_NAME}} with an independent implementation.")
'''


def write_adapter(spec: dict[str, Any]) -> dict[str, str]:
    method = str(spec["method"])
    method_dir = BASELINES_DIR / method
    method_dir.mkdir(parents=True, exist_ok=True)
    adapter_path = method_dir / "adapter_template.py"
    metadata_path = method_dir / "adapter_metadata.json"
    readme_path = method_dir / "README.md"
    is_oracle = method == ORACLE_METHOD

    adapter_path.write_text(adapter_template(spec), encoding="utf-8")
    metadata = {
        "version": "paper119_external_adapter_scaffold_v1",
        "not_external_evidence": True,
        "scaffold_only": True,
        "method": method,
        "role": spec.get("role", ""),
        "required_entrypoint": spec.get("required_entrypoint", ""),
        "adapter_api": spec.get("adapter_api", {}),
        "replacement_required_before_evidence": not is_oracle,
        "implementation_status": "post_hoc_upper_bound_only" if is_oracle else "scaffold_only_missing_external_source",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"# Adapter Scaffold: {method}",
        "",
        "Not external evidence: `true`.",
        "Scaffold only: `true`.",
        "",
        f"Role: {spec.get('role', '')}.",
        f"Required entrypoint: `{spec.get('required_entrypoint', '')}`.",
        "",
        "Replace `adapter_template.py` with an independent implementation before this method can appear in `external_validation/manifest.json` as evidence.",
        "",
        "## Allowed Inputs",
        "",
    ]
    for item in spec.get("allowed_inputs", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Forbidden Advantages", ""])
    for item in spec.get("forbidden_advantages", []):
        lines.append(f"- {item}")
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "method": method,
        "adapter": adapter_path.relative_to(ROOT).as_posix(),
        "metadata": metadata_path.relative_to(ROOT).as_posix(),
        "readme": readme_path.relative_to(ROOT).as_posix(),
        "status": metadata["implementation_status"],
    }


def write_common_readme(entries: list[dict[str, str]]) -> None:
    lines = [
        "# External Baseline Adapter Scaffolds",
        "",
        "Not external evidence: `true`.",
        "",
        "These directories provide executable templates for plugging independent baselines into the external validation protocol. They intentionally raise `NotImplementedError` and must not be cited as independent implementations.",
        "",
        "## Required Adapter API",
        "",
    ]
    for name in REQUIRED_API:
        lines.append(f"- `{name}`")
    lines.extend(["", "## Scaffolds", ""])
    for entry in entries:
        lines.append(f"- `{entry['method']}`: `{entry['adapter']}`; status `{entry['status']}`.")
    (BASELINES_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = [
        "# Baseline Adapter Scaffold Summary",
        "",
        "Not external evidence: `true`.",
        "",
        "This file summarizes scaffold templates only. A strict external evidence package still needs real source implementations, configs/checkpoints, hashes, logs, and videos.",
        "",
        "## Generated Adapters",
        "",
    ]
    for entry in entries:
        summary.append(f"- `{entry['method']}`: `{entry['adapter']}`; `{entry['metadata']}`.")
    SUMMARY_MD.write_text("\n".join(summary) + "\n", encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_audit(entries: list[dict[str, str]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    missing_files = []
    api_missing = []
    scaffold_marker_missing = []
    not_implemented_missing = []
    metadata_not_scaffold = []

    for entry in entries:
        adapter_path = ROOT / entry["adapter"]
        metadata_path = ROOT / entry["metadata"]
        readme_path = ROOT / entry["readme"]
        for path in (adapter_path, metadata_path, readme_path):
            if not path.exists():
                missing_files.append(path.relative_to(ROOT).as_posix())
        if adapter_path.exists():
            text = adapter_path.read_text(encoding="utf-8")
            missing_api = [name for name in REQUIRED_API if f"def {name}(" not in text]
            if missing_api:
                api_missing.append(f"{entry['method']}: {missing_api}")
            if "NOT_EXTERNAL_EVIDENCE = True" not in text or "SCAFFOLD_ONLY = True" not in text:
                scaffold_marker_missing.append(entry["method"])
            if "raise NotImplementedError" not in text:
                not_implemented_missing.append(entry["method"])
        if metadata_path.exists():
            metadata = read_json(metadata_path)
            if metadata.get("scaffold_only") is not True or metadata.get("not_external_evidence") is not True:
                metadata_not_scaffold.append(entry["method"])

    non_oracle = [entry for entry in entries if entry["method"] != ORACLE_METHOD]
    add_check(checks, "not_external_evidence_declared", True, "adapter scaffolds are templates only")
    add_check(checks, "method_count_ge_12", len(entries) >= 12, f"method_count={len(entries)}")
    add_check(checks, "non_oracle_scaffold_count_ge_11", len(non_oracle) >= 11, f"non_oracle={len(non_oracle)}")
    add_check(checks, "scaffold_files_exist", not missing_files, f"missing={missing_files[:8]}")
    add_check(checks, "required_api_present", not api_missing, "; ".join(api_missing[:6]) if api_missing else "all adapter functions present")
    add_check(checks, "scaffold_markers_present", not scaffold_marker_missing, f"missing={scaffold_marker_missing}")
    add_check(checks, "templates_raise_not_implemented", not not_implemented_missing, f"missing={not_implemented_missing}")
    add_check(checks, "metadata_marks_scaffold_only", not metadata_not_scaffold, f"bad={metadata_not_scaffold}")
    add_check(checks, "summary_exists", SUMMARY_MD.exists(), str(SUMMARY_MD))
    add_check(checks, "baselines_readme_exists", (BASELINES_DIR / "README.md").exists(), str(BASELINES_DIR / "README.md"))

    return {
        "version": "external_adapter_scaffold_audit_v1",
        "not_external_evidence": True,
        "passed": all(check["passed"] for check in checks),
        "implementations_ready": False,
        "method_count": len(entries),
        "non_oracle_scaffold_count": len(non_oracle),
        "summary": SUMMARY_MD.relative_to(ROOT).as_posix(),
        "entries": entries,
        "checks": checks,
    }


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Adapter Scaffold Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Implementations ready: `{str(audit['implementations_ready']).lower()}`.",
        f"Methods: `{audit['method_count']}`.",
        "",
        "This audit verifies scaffold completeness only. It deliberately does not claim that manifest-declared independent baseline evidence exists.",
        "",
        "## Generated Scaffolds",
        "",
    ]
    for entry in audit["entries"]:
        lines.append(f"- `{entry['method']}`: `{entry['adapter']}`; status `{entry['status']}`")
    lines.extend(["", "## Checks", ""])
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    EXTERNAL.mkdir(exist_ok=True)
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    specs = [read_json(path) for path in spec_files()]
    specs.sort(key=lambda item: str(item.get("method", "")))
    entries = [write_adapter(spec) for spec in specs]
    write_common_readme(entries)
    audit = build_audit(entries)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    status = "PASS" if audit["passed"] else "FAIL"
    print(
        f"External adapter scaffold audit: {status}; methods={audit['method_count']}; "
        f"implementations_ready={audit['implementations_ready']}"
    )
    print(f"Wrote {SUMMARY_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
