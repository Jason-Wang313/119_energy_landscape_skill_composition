from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import validate_external_adapters as adapter_audit


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
TMP_ROOT = ROOT / "tmp"
OUT_JSON = RESULTS / "external_adapter_evidence_self_test.json"
OUT_MD = RESULTS / "external_adapter_evidence_self_test.md"
REAL_REPORT = RESULTS / "external_adapter_contract_evidence_audit.json"
NON_ORACLE_EXCLUDED = {"oracle_basin_composer"}


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def baseline_methods() -> list[str]:
    methods: list[str] = []
    for path in sorted((EXTERNAL / "baseline_specs").glob("*.json")):
        method = str(read_json(path).get("method", "")).strip()
        if method and method not in NON_ORACLE_EXCLUDED:
            methods.append(method)
    return methods


def write_valid_adapter(path: Path, method: str) -> None:
    path.write_text(
        f'''
POLICY_HASH = ""


def initialize(config):
    global POLICY_HASH
    POLICY_HASH = config.get("policy_or_config_hash", "")
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
'''.lstrip(),
        encoding="utf-8",
    )


def manifest_for_implementations(adapter_paths: dict[str, Path], config_paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "methods": [
            {
                "name": method,
                "implementation": rel(path),
                "checkpoint_or_config_path": rel(config_paths[method]),
                "checkpoint_or_config_hash": file_digest(config_paths[method]),
            }
            for method, path in sorted(adapter_paths.items())
        ]
        + [
            {
                "name": "oracle_basin_composer",
                "implementation": "post_hoc_upper_bound",
                "checkpoint_or_config_path": "",
                "checkpoint_or_config_hash": "",
            }
        ],
    }


def manifest_for_scaffolds() -> dict[str, Any]:
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "methods": [
            {
                "name": method,
                "implementation": rel(EXTERNAL / "baselines" / method / "adapter_template.py"),
                "checkpoint_or_config_path": "",
                "checkpoint_or_config_hash": digest(f"{method}:scaffold"),
            }
            for method in baseline_methods()
        ],
    }


def manifest_for_reference_adapters() -> dict[str, Any]:
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "methods": [
            {
                "name": method,
                "implementation": rel(EXTERNAL / "baselines" / method / "adapter.py"),
                "checkpoint_or_config_path": "",
                "checkpoint_or_config_hash": file_digest(EXTERNAL / "baselines" / method / "adapter.py"),
            }
            for method in baseline_methods()
        ],
    }


def run_strict_with_manifest(manifest_path: Path) -> dict[str, Any]:
    old_manifest = adapter_audit.MANIFEST
    try:
        adapter_audit.MANIFEST = manifest_path
        return adapter_audit.build_audit(strict=True)
    finally:
        adapter_audit.MANIFEST = old_manifest


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Adapter Evidence Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic strict adapter evidence ready: `{str(payload['synthetic_adapter_evidence_ready']).lower()}`.",
        "",
        "This self-test builds temporary manifest-declared adapter implementations and exercises the strict external-adapter evidence gate directly. It proves complete synthetic adapters can pass, missing manifests fail, scaffold templates and reference adapters are rejected as evidence, and the real adapter evidence audit report is not overwritten.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks: list[dict[str, Any]] = []
    report_before = file_digest(REAL_REPORT)
    TMP_ROOT.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="paper119_adapter_evidence_selftest_", dir=TMP_ROOT) as tmp_name:
        tmp = Path(tmp_name)
        adapter_dir = tmp / "adapters"
        config_dir = tmp / "configs"
        adapter_paths: dict[str, Path] = {}
        config_paths: dict[str, Path] = {}
        for method in baseline_methods():
            target = adapter_dir / method / "adapter.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            write_valid_adapter(target, method)
            adapter_paths[method] = target
            config = config_dir / method / "config.json"
            write_json(
                config,
                {
                    "method": method,
                    "fixed_risk_budget": 0.15,
                    "self_test_only": True,
                },
            )
            config_paths[method] = config

        complete_manifest = tmp / "manifest_complete.json"
        missing_manifest = tmp / "manifest_missing.json"
        scaffold_manifest = tmp / "manifest_scaffolds.json"
        reference_manifest = tmp / "manifest_reference_adapters.json"
        write_json(complete_manifest, manifest_for_implementations(adapter_paths, config_paths))
        write_json(scaffold_manifest, manifest_for_scaffolds())
        write_json(reference_manifest, manifest_for_reference_adapters())

        complete_audit = run_strict_with_manifest(complete_manifest)
        missing_manifest_audit = run_strict_with_manifest(missing_manifest)
        scaffold_audit = run_strict_with_manifest(scaffold_manifest)
        reference_audit = run_strict_with_manifest(reference_manifest)

    report_after = file_digest(REAL_REPORT)

    complete_checks = {check.get("name"): check.get("passed") for check in complete_audit.get("checks", [])}
    missing_manifest_checks = {check.get("name"): check.get("passed") for check in missing_manifest_audit.get("checks", [])}
    scaffold_failed = scaffold_audit.get("failed_adapters", [])
    reference_failed = reference_audit.get("failed_adapters", [])

    add_check(
        checks,
        "synthetic_strict_adapters_pass",
        complete_audit.get("passed") is True
        and complete_audit.get("strict") is True
        and complete_audit.get("not_external_evidence") is False
        and int(complete_audit.get("adapter_count", 0) or 0) >= 11
        and complete_checks.get("manifest_exists") is True
        and complete_checks.get("manifest_implementation_entries_present") is True
        and complete_checks.get("manifest_declares_all_required_non_oracle_methods") is True
        and complete_checks.get("manifest_implementation_entries_cover_required_non_oracle_methods") is True
        and complete_checks.get("manifest_required_hashes_match_artifacts") is True
        and complete_checks.get("adapter_results_passed") is True,
        f"passed={complete_audit.get('passed')!r}, adapter_count={complete_audit.get('adapter_count')!r}",
    )
    add_check(
        checks,
        "synthetic_manifest_entries_cover_non_oracle_methods",
        {result.get("method") for result in complete_audit.get("adapter_results", [])} == set(baseline_methods()),
        f"methods={len(complete_audit.get('adapter_results', []))}",
    )
    add_check(
        checks,
        "missing_manifest_fails_strict",
        missing_manifest_audit.get("passed") is False
        and missing_manifest_checks.get("manifest_exists") is False
        and missing_manifest_checks.get("manifest_implementation_entries_present") is False,
        f"passed={missing_manifest_audit.get('passed')!r}, checks={missing_manifest_checks}",
    )
    add_check(
        checks,
        "scaffold_adapters_rejected_as_strict_evidence",
        scaffold_audit.get("passed") is False
        and len(scaffold_failed) >= 11
        and all(
            any("rejects scaffold/not_external_evidence" in str(error) for error in result.get("errors", []))
            for result in scaffold_failed
        ),
        f"failed_adapters={len(scaffold_failed)}",
    )
    add_check(
        checks,
        "reference_adapters_rejected_as_strict_evidence",
        reference_audit.get("passed") is False
        and len(reference_failed) >= 11
        and all(
            any("rejects reference adapters as independent evidence" in str(error) for error in result.get("errors", []))
            for result in reference_failed
        ),
        f"failed_adapters={len(reference_failed)}",
    )
    add_check(
        checks,
        "real_adapter_evidence_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_adapter_evidence_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_adapter_evidence_ready": complete_audit.get("passed") is True,
        "scaffold_adapter_evidence_ready": scaffold_audit.get("passed") is True,
        "reference_adapter_evidence_ready": reference_audit.get("passed") is True,
        "missing_manifest_ready": missing_manifest_audit.get("passed") is True,
        "real_adapter_evidence_report_before": report_before,
        "real_adapter_evidence_report_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External adapter evidence self-test: "
        f"{'PASS' if passed else 'FAIL'}; synthetic_adapter_evidence_ready={payload['synthetic_adapter_evidence_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
