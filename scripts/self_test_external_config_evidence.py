from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import validate_external_configs as config_audit


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
TMP_ROOT = ROOT / "tmp"
OUT_JSON = RESULTS / "external_config_evidence_self_test.json"
OUT_MD = RESULTS / "external_config_evidence_self_test.md"
REAL_REPORT = RESULTS / "external_config_evidence_audit.json"
TASKS = [
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
]


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


def prepared_config_paths() -> list[Path]:
    paths: list[Path] = []
    for task in TASKS:
        path = EXTERNAL / "configs" / f"{task}.json"
        if not path.exists():
            raise SystemExit(f"missing prepared task config for self-test: {path}")
        payload = read_json(path)
        if payload.get("task_family") != task:
            raise SystemExit(f"prepared task config has wrong task_family: {path}")
        paths.append(path)
    return paths


def make_evidence_config(template: dict[str, Any], *, platform_name: str) -> dict[str, Any]:
    payload = json.loads(json.dumps(template))
    schema = read_json(config_audit.SCHEMA)
    payload["version"] = schema["evidence_version"]
    payload["platform_type"] = "high_fidelity_sim"
    payload["platform_name"] = platform_name
    payload["not_external_evidence"] = False
    payload.pop("template_only", None)
    payload["paired_reset_count"] = 30
    payload["reset_protocol"]["reset_count"] = 30
    payload["compute_budget"]["wall_clock_seconds"] = 60
    payload["compute_budget"]["simulator_query_budget"] = 128
    return payload


def manifest_for_configs(config_paths: list[Path]) -> dict[str, Any]:
    tasks = []
    for path in config_paths:
        config = read_json(path)
        tasks.append(
            {
                "task_family": config["task_family"],
                "platform_type": config["platform_type"],
                "episodes_per_method": 30,
                "config_path": rel(path),
                "config_hash": file_digest(path),
            }
        )
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "tasks": tasks,
    }


def manifest_for_templates() -> dict[str, Any]:
    tasks = []
    for path in sorted((EXTERNAL / "config_templates").glob("*.json")):
        config = read_json(path)
        tasks.append(
            {
                "task_family": config["task_family"],
                "platform_type": config["platform_type"],
                "episodes_per_method": 30,
                "config_path": rel(path),
            }
        )
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "tasks": tasks,
    }


def run_strict_with_manifest(manifest_path: Path) -> dict[str, Any]:
    old_manifest = config_audit.MANIFEST
    try:
        config_audit.MANIFEST = manifest_path
        return config_audit.build_audit(strict=True)
    finally:
        config_audit.MANIFEST = old_manifest


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Config Evidence Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic strict config evidence ready: `{str(payload['synthetic_config_evidence_ready']).lower()}`.",
        f"Prepared config fixture ready: `{str(payload['prepared_config_fixture_ready']).lower()}`.",
        "",
        "This self-test builds temporary manifest-declared task configs and exercises the strict external-config evidence gate directly. It proves complete synthetic configs can pass, the prepared task configs can bind to a temporary strict manifest with recomputed hashes, missing manifests fail, stale manifest config hashes fail, template configs are rejected as evidence, and the real config evidence audit report is not overwritten.",
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

    with tempfile.TemporaryDirectory(prefix="paper119_config_evidence_selftest_", dir=TMP_ROOT) as tmp_name:
        tmp = Path(tmp_name)
        config_dir = tmp / "configs"
        config_paths: list[Path] = []
        for template_path in sorted((EXTERNAL / "config_templates").glob("*.json")):
            template = read_json(template_path)
            config = make_evidence_config(template, platform_name="ConfigEvidenceSelfTestSim-v1")
            target = config_dir / template_path.name
            write_json(target, config)
            config_paths.append(target)

        complete_manifest = tmp / "manifest_complete.json"
        prepared_manifest = tmp / "manifest_prepared_configs.json"
        stale_hash_manifest = tmp / "manifest_stale_hash.json"
        template_manifest = tmp / "manifest_templates.json"
        missing_manifest = tmp / "manifest_missing.json"
        complete_manifest_payload = manifest_for_configs(config_paths)
        prepared_paths = prepared_config_paths()
        prepared_manifest_payload = manifest_for_configs(prepared_paths)
        stale_hash_payload = json.loads(json.dumps(complete_manifest_payload))
        stale_hash_payload["tasks"][0]["config_hash"] = "0" * 64
        write_json(complete_manifest, complete_manifest_payload)
        write_json(prepared_manifest, prepared_manifest_payload)
        write_json(stale_hash_manifest, stale_hash_payload)
        write_json(template_manifest, manifest_for_templates())

        complete_audit = run_strict_with_manifest(complete_manifest)
        prepared_audit = run_strict_with_manifest(prepared_manifest)
        stale_hash_audit = run_strict_with_manifest(stale_hash_manifest)
        missing_manifest_audit = run_strict_with_manifest(missing_manifest)
        template_audit = run_strict_with_manifest(template_manifest)

    report_after = file_digest(REAL_REPORT)

    complete_checks = {check.get("name"): check.get("passed") for check in complete_audit.get("checks", [])}
    prepared_checks = {check.get("name"): check.get("passed") for check in prepared_audit.get("checks", [])}
    missing_manifest_checks = {check.get("name"): check.get("passed") for check in missing_manifest_audit.get("checks", [])}
    stale_hash_errors = [
        str(error)
        for result in stale_hash_audit.get("failed_configs", [])
        for error in result.get("errors", [])
    ]
    template_failed_configs = template_audit.get("failed_configs", [])

    add_check(
        checks,
        "synthetic_strict_configs_pass",
        complete_audit.get("passed") is True
        and complete_audit.get("strict") is True
        and complete_audit.get("config_count") >= 4
        and complete_checks.get("manifest_exists") is True
        and complete_checks.get("manifest_config_entries_present") is True
        and complete_checks.get("configs_pass_validation") is True,
        f"passed={complete_audit.get('passed')!r}, config_count={complete_audit.get('config_count')!r}",
    )
    add_check(
        checks,
        "synthetic_manifest_entries_cover_tasks",
        {result.get("path") for result in complete_audit.get("config_results", [])}
        and int(complete_audit.get("config_count", 0) or 0) >= 4,
        f"config_count={complete_audit.get('config_count')!r}",
    )
    add_check(
        checks,
        "prepared_task_configs_pass_strict_with_temp_manifest",
        prepared_audit.get("passed") is True
        and prepared_audit.get("strict") is True
        and prepared_audit.get("not_external_evidence") is False
        and int(prepared_audit.get("config_count", 0) or 0) == len(TASKS)
        and prepared_checks.get("manifest_exists") is True
        and prepared_checks.get("manifest_config_entries_present") is True
        and prepared_checks.get("configs_pass_validation") is True,
        (
            f"passed={prepared_audit.get('passed')!r}, "
            f"config_count={prepared_audit.get('config_count')!r}, checks={prepared_checks}"
        ),
    )
    add_check(
        checks,
        "prepared_task_config_methods_match_collection_tasks",
        {read_json(path).get("task_family") for path in prepared_paths} == set(TASKS)
        and {Path(result.get("path", "")).stem for result in prepared_audit.get("config_results", [])} == set(TASKS),
        f"prepared_tasks={len(prepared_paths)}, config_results={len(prepared_audit.get('config_results', []))}",
    )
    add_check(
        checks,
        "missing_manifest_fails_strict",
        missing_manifest_audit.get("passed") is False
        and missing_manifest_checks.get("manifest_exists") is False
        and missing_manifest_checks.get("manifest_config_entries_present") is False,
        f"passed={missing_manifest_audit.get('passed')!r}, checks={missing_manifest_checks}",
    )
    add_check(
        checks,
        "stale_manifest_config_hash_fails_strict",
        stale_hash_audit.get("passed") is False
        and any("manifest config_hash does not match config_path" in error for error in stale_hash_errors),
        f"passed={stale_hash_audit.get('passed')!r}, errors={stale_hash_errors[:4]!r}",
    )
    add_check(
        checks,
        "template_configs_rejected_as_strict_evidence",
        template_audit.get("passed") is False
        and len(template_failed_configs) >= 4
        and all(
            any("expected='paper119_external_config_v1'" in str(error) for error in result.get("errors", []))
            or any("strict config must not be marked" in str(error) for error in result.get("errors", []))
            for result in template_failed_configs
        ),
        f"failed_configs={len(template_failed_configs)}",
    )
    add_check(
        checks,
        "real_config_evidence_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_config_evidence_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_config_evidence_ready": complete_audit.get("passed") is True,
        "prepared_config_fixture_ready": prepared_audit.get("passed") is True,
        "prepared_config_count": len(prepared_paths),
        "prepared_config_tasks": TASKS,
        "stale_config_hash_ready": stale_hash_audit.get("passed") is True,
        "template_config_evidence_ready": template_audit.get("passed") is True,
        "missing_manifest_ready": missing_manifest_audit.get("passed") is True,
        "real_config_evidence_report_before": report_before,
        "real_config_evidence_report_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External config evidence self-test: "
        f"{'PASS' if passed else 'FAIL'}; synthetic_config_evidence_ready={payload['synthetic_config_evidence_ready']}; "
        f"prepared_config_fixture_ready={payload['prepared_config_fixture_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
