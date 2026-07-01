from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from audit_external_evidence import is_scaffold_implementation


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
TMP_ROOT = ROOT / "tmp"
OUT_JSON = RESULTS / "external_adapter_scaffold_guard_self_test.json"
OUT_MD = RESULTS / "external_adapter_scaffold_guard_self_test.md"
SCAFFOLD_DIR = "external_validation/baselines/barrier_certified_energy_composer_v5"
SCAFFOLD_FILE = f"{SCAFFOLD_DIR}/adapter_template.py"
REAL_REPORTS = [
    RESULTS / "external_adapter_scaffold_audit.json",
    RESULTS / "external_adapter_scaffold_audit.md",
    RESULTS / "external_adapter_contract_evidence_audit.json",
    RESULTS / "external_adapter_contract_evidence_audit.md",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def real_report_digests() -> dict[str, str | None]:
    return {path.relative_to(ROOT).as_posix(): file_digest(path) for path in REAL_REPORTS}


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Adapter Scaffold Guard Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Scaffold directory detected: `{str(payload['scaffold_directory_detected']).lower()}`.",
        f"Scaffold template detected: `{str(payload['scaffold_template_detected']).lower()}`.",
        f"Ordinary adapter falsely rejected: `{str(payload['ordinary_adapter_falsely_rejected']).lower()}`.",
        "",
        "This self-test exercises the strict scaffold detector used by the external evidence audit. It proves scaffold-only adapter directories and templates are rejected as evidence while an ordinary replacement adapter file is not falsely rejected. It writes only this receipt and leaves the real scaffold/evidence audit reports untouched.",
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
    report_before = real_report_digests()
    scaffold_directory_detected = is_scaffold_implementation(SCAFFOLD_DIR)
    scaffold_template_detected = is_scaffold_implementation(SCAFFOLD_FILE)

    if not scaffold_directory_detected:
        fail(f"scaffold directory was not detected as scaffold-only: {SCAFFOLD_DIR}")
    if not scaffold_template_detected:
        fail(f"scaffold adapter was not detected as scaffold-only: {SCAFFOLD_FILE}")

    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_adapter_scaffold_guard_", dir=TMP_ROOT) as tmp_name:
        temp_path = Path(tmp_name) / "ordinary_adapter.py"
        temp_path.write_text(
            "def initialize(config):\n    return {\"initialized\": True}\n",
            encoding="utf-8",
        )
        rel = temp_path.relative_to(ROOT).as_posix()
        ordinary_adapter_detected_as_scaffold = is_scaffold_implementation(rel)
        if ordinary_adapter_detected_as_scaffold:
            fail(f"ordinary adapter file was incorrectly detected as scaffold-only: {rel}")
    temp_file_removed = not temp_path.exists()

    report_after = real_report_digests()
    reports_untouched = report_before == report_after

    add_check(
        checks,
        "scaffold_directory_detected",
        scaffold_directory_detected,
        f"path={SCAFFOLD_DIR}",
    )
    add_check(
        checks,
        "scaffold_template_detected",
        scaffold_template_detected,
        f"path={SCAFFOLD_FILE}",
    )
    add_check(
        checks,
        "ordinary_replacement_adapter_not_flagged",
        ordinary_adapter_detected_as_scaffold is False,
        "temporary ordinary adapter file was not classified as scaffold-only",
    )
    add_check(
        checks,
        "temporary_adapter_file_removed",
        temp_file_removed,
        "temporary ordinary adapter file was removed after self-test",
    )
    add_check(
        checks,
        "real_adapter_reports_untouched",
        reports_untouched,
        f"before={report_before!r}, after={report_after!r}",
    )

    payload = {
        "version": "external_adapter_scaffold_guard_self_test_v1",
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "scaffold_directory": SCAFFOLD_DIR,
        "scaffold_file": SCAFFOLD_FILE,
        "scaffold_directory_detected": scaffold_directory_detected,
        "scaffold_template_detected": scaffold_template_detected,
        "ordinary_adapter_falsely_rejected": ordinary_adapter_detected_as_scaffold,
        "temporary_adapter_file_removed": temp_file_removed,
        "real_adapter_reports_untouched": reports_untouched,
        "real_report_digests_before": report_before,
        "real_report_digests_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    if payload["passed"] is not True:
        failed = [check for check in checks if not check["passed"]]
        fail(f"external adapter scaffold guard self-test failed checks: {failed}")

    print("External adapter scaffold guard self-test passed.")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
