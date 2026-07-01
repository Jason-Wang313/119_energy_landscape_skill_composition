from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import build_external_manifest as manifest_builder
import self_test_external_evidence_pipeline as fixture
import validate_external_rollouts as rollout


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_manifest_builder_self_test.json"
OUT_MD = RESULTS / "external_manifest_builder_self_test.md"

REAL_PATHS = [
    EXTERNAL / "manifest.json",
    EXTERNAL / "manifest_assembly_checklist.csv",
    RESULTS / "external_manifest_builder_report.json",
    RESULTS / "external_manifest_builder_report.md",
]


def digest_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def real_path_digests() -> dict[str, str | None]:
    return {rel(ROOT, path): digest_file(path) for path in REAL_PATHS}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def patch_manifest_builder(root: Path, external: Path, results: Path) -> None:
    manifest_builder.ROOT = root
    manifest_builder.EXTERNAL = external
    manifest_builder.RESULTS = results
    manifest_builder.DEFAULT_TEMPLATE = external / "manifest_template.json"
    manifest_builder.DEFAULT_OUTPUT = external / "manifest.json"
    manifest_builder.DEFAULT_SCHEMA = external / "log_schema_v1.json"
    manifest_builder.REPORT_JSON = results / "external_manifest_builder_report.json"
    manifest_builder.REPORT_MD = results / "external_manifest_builder_report.md"
    manifest_builder.ASSEMBLY_CHECKLIST_CSV = external / "manifest_assembly_checklist.csv"


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def build_template(root: Path, external: Path) -> dict[str, Any]:
    skill_library_hash = fixture.digest_text("manifest builder self-test skill library")
    fairness_contract = fixture.synthetic_fairness_contract(skill_library_hash)
    methods, _, _, policy_hashes = fixture.write_baseline_artifacts(root, external, fairness_contract)
    tasks, _, _, _ = fixture.write_task_artifacts(root, external, policy_hashes)
    return {
        "version": "external_validation_v1",
        "synthetic_self_test_only": True,
        "log_schema": "external_validation/log_schema_v1.json",
        "route": "high_fidelity_sim",
        "code_commit": "manifest-builder-self-test",
        "skill_library_hash": skill_library_hash,
        "fidelity_acceptance_path": "external_validation/fidelity_acceptance.json",
        "shared_skill_library": True,
        "same_initial_states": True,
        "same_observation_interface": True,
        "same_compute_budget": True,
        "paired_resets": True,
        "fairness_contract": fairness_contract,
        "tasks": tasks,
        "methods": methods,
        "ablations": {
            "basin_overlap": True,
            "barrier_height": True,
            "descent_continuity": True,
            "risk_calibration": True,
            "seam_repair": True,
        },
        "release_artifacts": {"code": [], "configs": [], "logs": [], "videos": [], "checkpoints": []},
    }


def run_manifest_builder(root: Path, external: Path, results: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    patch_manifest_builder(root, external, results)
    template = external / "manifest_template.json"
    output = external / "manifest.json"
    schema_path = external / "log_schema_v1.json"

    manifest = manifest_builder.read_json(template)
    schema = manifest_builder.read_json(schema_path)
    warnings = manifest_builder.update_manifest_hashes(root, manifest)
    artifact_dirs = {kind: external / name for kind, name in manifest_builder.ARTIFACT_DIR_NAMES.items()}
    manifest["release_artifacts"] = manifest_builder.scan_artifacts(root, artifact_dirs, manifest)
    records, schema_errors = manifest_builder.load_records(root, manifest, schema, check_video_paths=True)

    summary: dict[str, Any] = {"episodes": 0}
    if records and not schema_errors:
        summary = manifest_builder.summarize_records(records, schema)
        metrics = manifest.setdefault("metrics", {})
        for key in (
            "external_success_margin",
            "external_utility_margin",
            "paired_win_rate",
            "fixed_risk_budget",
            "fixed_risk_breach",
            "fixed_risk_coverage",
            "positive_task_families",
            "external_task_families",
        ):
            metrics[key] = summary.get(key)
        methods = set(summary.get("method_summary", {}))
        metrics["oracle_reported"] = manifest_builder.ORACLE_METHOD in methods
        oracle = summary.get("method_summary", {}).get(manifest_builder.ORACLE_METHOD) if isinstance(summary.get("method_summary"), dict) else None
        primary = summary.get("method_summary", {}).get(manifest_builder.PRIMARY_METHOD) if isinstance(summary.get("method_summary"), dict) else None
        if oracle and primary:
            metrics["oracle_stronger_or_saturated_explained"] = (
                float(oracle.get("success", 0.0)) >= float(primary.get("success", 0.0))
                and float(oracle.get("utility", 0.0)) >= float(primary.get("utility", 0.0))
            )

    rows = manifest_builder.build_manifest_assembly_checklist(root, manifest, records, schema_errors, warnings, summary)
    write_blocking_rows = manifest_builder.manifest_write_blocking_rows(rows)
    ready = bool(records) and not schema_errors and not warnings and not write_blocking_rows
    if ready:
        output.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    report = {
        "version": "external_manifest_builder_report_v1",
        "template": str(template),
        "output": str(output),
        "manifest_written": ready,
        "ready_to_write_manifest": ready,
        "not_external_evidence": not ready,
        "records_loaded": len(records),
        "schema_errors": schema_errors,
        "warnings": warnings,
        "summary": summary,
        "assembly_checklist_csv": rel(root, external / "manifest_assembly_checklist.csv"),
        "assembly_checklist_row_count": len(rows),
        "assembly_blocking_count": sum(1 for row in rows if row.get("blocking_until_real_evidence") == "true"),
        "manifest_write_blocking_count": len(write_blocking_rows),
        "manifest_write_blocking_rows": write_blocking_rows,
        "assembly_checklist_rows": rows,
    }
    manifest_builder.write_report(report)
    return manifest, report


def inspect_real_template() -> dict[str, Any]:
    manifest = manifest_builder.read_json(EXTERNAL / "manifest_template.json")
    schema = manifest_builder.read_json(EXTERNAL / "log_schema_v1.json")
    records, schema_errors = manifest_builder.load_records(ROOT, manifest, schema, check_video_paths=True)
    warnings = manifest_builder.update_manifest_hashes(ROOT, manifest)
    rows = manifest_builder.build_manifest_assembly_checklist(
        ROOT,
        manifest,
        records,
        schema_errors,
        warnings,
        {"episodes": 0},
    )
    write_blocking_rows = manifest_builder.manifest_write_blocking_rows(rows)
    return {
        "ready_to_write_manifest": bool(records) and not schema_errors and not warnings and not write_blocking_rows,
        "records_loaded": len(records),
        "schema_error_count": len(schema_errors),
        "warning_count": len(warnings),
        "manifest_write_blocking_count": len(write_blocking_rows),
    }


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Manifest Builder Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic manifest written: `{str(payload['synthetic_manifest_written']).lower()}`.",
        f"Synthetic records loaded: `{payload['synthetic_records_loaded']}`.",
        "",
        "This self-test builds a temporary complete manifest fixture with raw JSONL logs, videos, configs, method implementations, checkpoints, and release artifacts. It exercises the external manifest builder's hash, record-loading, metric-recompute, report, and manifest-write path without touching the real `external_validation/manifest.json` or real manifest-builder report.",
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
    real_before = real_path_digests()
    template_status = inspect_real_template()

    with tempfile.TemporaryDirectory(prefix="paper119_manifest_builder_selftest_") as tmp_name:
        root = Path(tmp_name)
        external = root / "external_validation"
        results = root / "results"
        external.mkdir()
        results.mkdir()
        (external / "log_schema_v1.json").write_text((EXTERNAL / "log_schema_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
        (external / "config_schema_v1.json").write_text((EXTERNAL / "config_schema_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
        write_json(external / "fidelity_acceptance.json", fixture.make_fidelity_acceptance())
        write_json(external / "manifest_template.json", build_template(root, external))

        manifest, builder_report = run_manifest_builder(root, external, results)
        output_manifest = external / "manifest.json"
        output_payload = read_json(output_manifest) if output_manifest.exists() else {}
        release_artifacts = output_payload.get("release_artifacts", {}) if isinstance(output_payload, dict) else {}
        metrics = output_payload.get("metrics", {}) if isinstance(output_payload, dict) else {}
        release_counts = {kind: len(release_artifacts.get(kind, [])) for kind in ("code", "configs", "logs", "videos", "checkpoints")}

        add_check(
            checks,
            "synthetic_manifest_builder_ready",
            builder_report.get("ready_to_write_manifest") is True
            and builder_report.get("manifest_written") is True
            and builder_report.get("records_loaded") == 1440
            and not builder_report.get("schema_errors"),
            f"ready={builder_report.get('ready_to_write_manifest')!r}, records={builder_report.get('records_loaded')}, schema_errors={len(builder_report.get('schema_errors', []))}",
        )
        add_check(
            checks,
            "synthetic_manifest_written_to_temp_output",
            output_manifest.exists()
            and output_payload.get("version") == "external_validation_v1"
            and output_payload.get("synthetic_self_test_only") is True,
            f"exists={output_manifest.exists()}, version={output_payload.get('version')!r}",
        )
        add_check(
            checks,
            "raw_logs_drive_manifest_metrics",
            float(metrics.get("external_success_margin", 0.0)) > 0.0
            and float(metrics.get("external_utility_margin", 0.0)) > 0.0
            and float(metrics.get("paired_win_rate", 0.0)) == 1.0
            and int(metrics.get("positive_task_families", 0)) == 4,
            f"success_margin={metrics.get('external_success_margin')}, utility_margin={metrics.get('external_utility_margin')}, paired_win_rate={metrics.get('paired_win_rate')}",
        )
        add_check(
            checks,
            "release_artifacts_scanned_from_temp_workspace",
            all(len(release_artifacts.get(kind, [])) >= 1 for kind in ("code", "configs", "logs", "videos", "checkpoints")),
            f"counts={release_counts}",
        )
        add_check(
            checks,
            "config_and_method_hashes_materialized",
            all(task.get("config_hash") for task in output_payload.get("tasks", []))
            and all(
                method.get("name") == rollout.ORACLE_METHOD or method.get("checkpoint_or_config_hash")
                for method in output_payload.get("methods", [])
            ),
            f"tasks={len(output_payload.get('tasks', []))}, methods={len(output_payload.get('methods', []))}",
        )
        add_check(
            checks,
            "manifest_report_and_checklist_written_in_temp_workspace",
            (results / "external_manifest_builder_report.json").exists()
            and (results / "external_manifest_builder_report.md").exists()
            and (external / "manifest_assembly_checklist.csv").exists()
            and int(builder_report.get("assembly_checklist_row_count", 0) or 0) >= 30,
            f"checklist_rows={builder_report.get('assembly_checklist_row_count')}",
        )

    with tempfile.TemporaryDirectory(prefix="paper119_manifest_builder_partial_selftest_") as tmp_name:
        root = Path(tmp_name)
        external = root / "external_validation"
        results = root / "results"
        external.mkdir()
        results.mkdir()
        (external / "log_schema_v1.json").write_text((EXTERNAL / "log_schema_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
        (external / "config_schema_v1.json").write_text((EXTERNAL / "config_schema_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
        write_json(external / "fidelity_acceptance.json", fixture.make_fidelity_acceptance())
        template = build_template(root, external)
        missing_method = "greedy_module_sequence"
        for method in template.get("methods", []):
            if isinstance(method, dict) and method.get("name") == missing_method:
                implementation = root / str(method.get("implementation", ""))
                if implementation.exists():
                    implementation.unlink()
                method["implementation"] = f"external_validation/implementations/{missing_method}/missing_adapter.py"
                break
        write_json(external / "manifest_template.json", template)

        _, partial_report = run_manifest_builder(root, external, results)
        partial_output = external / "manifest.json"
        partial_blockers = partial_report.get("manifest_write_blocking_rows", []) or []
        add_check(
            checks,
            "partial_manifest_with_missing_method_refuses_write",
            partial_report.get("ready_to_write_manifest") is False
            and partial_report.get("manifest_written") is False
            and not partial_output.exists()
            and any(missing_method in str(row.get("item", "")) for row in partial_blockers),
            (
                f"ready={partial_report.get('ready_to_write_manifest')!r}, "
                f"written={partial_report.get('manifest_written')!r}, "
                f"write_blockers={len(partial_blockers)}"
            ),
        )

    real_after = real_path_digests()
    add_check(
        checks,
        "real_manifest_template_remains_fail_closed",
        template_status["ready_to_write_manifest"] is False
        and template_status["records_loaded"] == 0
        and template_status["schema_error_count"] >= 1,
        f"template_status={template_status}",
    )
    add_check(
        checks,
        "real_manifest_and_reports_not_overwritten",
        real_before == real_after,
        f"before={real_before}, after={real_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_manifest_builder_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_manifest_written": any(check["name"] == "synthetic_manifest_written_to_temp_output" and check["passed"] for check in checks),
        "synthetic_records_loaded": 1440 if any(check["name"] == "synthetic_manifest_builder_ready" and check["passed"] for check in checks) else 0,
        "real_template_ready_to_write_manifest": template_status["ready_to_write_manifest"],
        "real_manifest_and_reports_unchanged": real_before == real_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External manifest builder self-test: "
        f"{'PASS' if passed else 'FAIL'}; synthetic_manifest_written={payload['synthetic_manifest_written']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
