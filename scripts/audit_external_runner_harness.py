from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RUNNER = EXTERNAL / "runner"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_runner_harness_audit.json"
OUT_MD = RESULTS / "external_runner_harness_audit.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_command(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []
    contract_path = RUNNER / "backend_contract.py"
    runner_path = RUNNER / "real_collection_runner.py"
    readme_path = RUNNER / "README.md"
    contract = read(contract_path)
    runner = read(runner_path)
    readme = read(readme_path)

    required_files = [
        contract_path,
        runner_path,
        readme_path,
        RUNNER / "__init__.py",
        RUNNER / "backend_templates" / "__init__.py",
        RUNNER / "backend_templates" / "maniskill_backend.py",
        RUNNER / "backend_templates" / "mujoco_robosuite_backend.py",
        RUNNER / "backend_templates" / "isaac_backend.py",
        RUNNER / "backend_templates" / "robot_lab_backend.py",
    ]
    missing_files = [path.relative_to(ROOT).as_posix() for path in required_files if not path.exists()]
    add_check(checks, "runner_files_exist", not missing_files, f"missing={missing_files}")

    required_api = [
        "platform_provenance",
        "load_task_config",
        "reset_scene",
        "capture_observation",
        "terminal_samples",
        "run_method",
        "execute_skill_pair",
        "record_video",
        "policy_or_config_hash",
    ]
    missing_api = [name for name in required_api if name not in contract]
    add_check(checks, "backend_contract_api_complete", not missing_api, f"missing_api={missing_api}")
    add_check(checks, "backend_contract_fail_closed", "TEMPLATE_ONLY = True" in contract and "NotImplementedError" in contract, "template base raises NotImplementedError")
    add_check(checks, "backend_contract_has_hash_helpers", "sha256_json" in contract and "sha256_file" in contract, "stable hash helpers")

    required_runner_terms = [
        "blinded_operator_sheet.csv",
        "method_alias_map.json",
        "log_schema_v1.json",
        "--backend-module",
        "--dry-run",
        "--unsealed-alias-map",
        "--task-config-dir",
        "--output-log-dir",
        "--video-dir",
        "validate_backend_object",
        "refusing template/non-evidence config",
        "expected_video_path",
        "terminal_sample_set_hash",
        "policy_or_config_hash",
        "validate_official_video",
        "validate_official_record",
        "validate_external_rollouts",
        "MIN_OFFICIAL_VIDEO_BYTES",
        ".diagnostic.json",
        "ftyp",
    ]
    missing_runner_terms = [term for term in required_runner_terms if term not in runner]
    add_check(checks, "runner_references_required_contracts", not missing_runner_terms, f"missing_terms={missing_runner_terms}")
    official_video_guard_terms = [
        "validate_official_video",
        "expected_target",
        "official video directory",
        "diagnostic fallback video sidecar",
        "MIN_OFFICIAL_VIDEO_BYTES",
        "ftyp",
    ]
    missing_video_guard_terms = [term for term in official_video_guard_terms if term not in runner]
    add_check(
        checks,
        "runner_rejects_diagnostic_or_non_mp4_videos_before_jsonl_write",
        not missing_video_guard_terms,
        f"missing_terms={missing_video_guard_terms}",
    )
    official_jsonl_guard_terms = [
        "validate_official_record",
        "validate_external_rollouts",
        "strict_video_evidence=True",
        "schema-invalid official JSONL record",
    ]
    missing_jsonl_guard_terms = [term for term in official_jsonl_guard_terms if term not in runner]
    add_check(
        checks,
        "runner_rejects_schema_invalid_records_before_jsonl_write",
        not missing_jsonl_guard_terms,
        f"missing_terms={missing_jsonl_guard_terms}",
    )
    add_check(checks, "runner_does_not_write_manifest", "manifest.json" not in runner.lower(), "runner writes JSONL/video only; manifest remains separate")

    template_texts = [read(path) for path in sorted((RUNNER / "backend_templates").glob("*_backend.py"))]
    add_check(checks, "backend_templates_count", len(template_texts) >= 4, f"templates={len(template_texts)}")
    add_check(checks, "backend_templates_are_template_only", all("TEMPLATE_ONLY = True" in text for text in template_texts), "all route templates are fail-closed")

    dry_code, dry_output = run_command([sys.executable, str(runner_path), "--dry-run", "--max-rows", "3"])
    add_check(checks, "runner_dry_run_passes_without_writes", dry_code == 0 and '"writes_logs": false' in dry_output, dry_output[:300])

    reject_code, reject_output = run_command(
        [
            sys.executable,
            str(runner_path),
            "--backend-module",
            "external_validation.runner.backend_templates.maniskill_backend",
            "--max-rows",
            "1",
            "--unsealed-alias-map",
        ]
    )
    add_check(
        checks,
        "runner_rejects_template_backend_for_actual_collection",
        reject_code != 0 and "TEMPLATE_ONLY=True" in reject_output,
        reject_output[:300],
    )

    add_check(checks, "readme_declares_not_evidence", "Not external evidence: `true`" in readme, "README keeps evidence boundary")
    add_check(checks, "readme_has_strict_commands", "validate_external_rollouts.py --strict" in readme and "audit_external_evidence.py --strict" in readme, "strict validation commands documented")
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_runner_harness_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "runner_harness_ready": passed,
        "actual_execution_ready": False,
        "missing_for_actual_execution": [
            "non-template backend module",
            "strict real configs in external_validation/configs",
            "intentional alias unsealing at execution time",
            "official MP4-like videos without diagnostic sidecars plus schema-valid real JSONL logs",
            "manifest-declared hashes and strict evidence audits",
        ],
        "checks": checks,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Runner Harness Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Runner harness ready: `{str(payload['runner_harness_ready']).lower()}`.",
        f"Actual execution ready: `{str(payload['actual_execution_ready']).lower()}`.",
        "",
        "This audit checks the fail-closed runner used to collect future external JSONL logs and videos. It is not robot or high-fidelity simulation evidence.",
        "",
        "## Missing For Actual Execution",
        "",
    ]
    for item in payload["missing_for_actual_execution"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"External runner harness audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
