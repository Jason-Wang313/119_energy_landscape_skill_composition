from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import build_external_evidence_closure_brief as closure


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_DOCS = REAL_ROOT / "docs"
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"

REAL_OUT_JSON = REAL_RESULTS / "external_evidence_closure_brief.json"
REAL_OUT_MD = REAL_RESULTS / "external_evidence_closure_brief.md"
REAL_OUT_DOC = REAL_DOCS / "external_evidence_closure_brief.md"

OUT_JSON = REAL_RESULTS / "external_evidence_closure_brief_self_test.json"
OUT_MD = REAL_RESULTS / "external_evidence_closure_brief_self_test.md"

RESULT_FIXTURES = [
    "submission_readiness_gap_audit.json",
    "external_acquisition_packet.json",
    "external_execution_readiness_audit.json",
    "external_evidence_intake_ledger_audit.json",
    "external_operator_release_bundle_plan.json",
    "external_collection_job_packet_audit.json",
    "external_collection_machine_bootstrap_audit.json",
]

EXTERNAL_FIXTURES = [
    "collection_job_commands.ps1",
    "collection_job_commands.sh",
    "collection_machine_bootstrap.ps1",
    "collection_machine_bootstrap.sh",
]


def sha256_file(path: Path) -> str | None:
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


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing closure self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for name in RESULT_FIXTURES:
        copy_file(REAL_RESULTS / name, root / "results" / name)
    for name in EXTERNAL_FIXTURES:
        copy_file(REAL_EXTERNAL / name, root / "external_validation" / name)


def run_builder(root: Path) -> tuple[int, dict[str, Any]]:
    original = (
        closure.ROOT,
        closure.DOCS,
        closure.RESULTS,
        closure.EXTERNAL,
        closure.OUT_JSON,
        closure.OUT_MD,
        closure.OUT_DOC,
    )
    try:
        closure.ROOT = root
        closure.DOCS = root / "docs"
        closure.RESULTS = root / "results"
        closure.EXTERNAL = root / "external_validation"
        closure.OUT_JSON = closure.RESULTS / "external_evidence_closure_brief.json"
        closure.OUT_MD = closure.RESULTS / "external_evidence_closure_brief.md"
        closure.OUT_DOC = closure.DOCS / "external_evidence_closure_brief.md"
        try:
            status = closure.main()
        except SystemExit as exc:
            status = exc.code if isinstance(exc.code, int) else 1
        payload = read_json(closure.OUT_JSON) if closure.OUT_JSON.exists() else {}
        return status, payload
    finally:
        (
            closure.ROOT,
            closure.DOCS,
            closure.RESULTS,
            closure.EXTERNAL,
            closure.OUT_JSON,
            closure.OUT_MD,
            closure.OUT_DOC,
        ) = original


def run_case(mutator: Callable[[Path], None] | None = None) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_closure_brief_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_builder(root)


def add_unmapped_fifth_blocker(root: Path) -> None:
    path = root / "results" / "submission_readiness_gap_audit.json"
    payload = read_json(path)
    payload["blocking_missing_requirements"] = int(payload.get("blocking_missing_requirements", 0) or 0) + 1
    payload["missing_requirements"] = int(payload.get("missing_requirements", 0) or 0) + 1
    payload.setdefault("requirements", []).append(
        {
            "requirement": "Synthetic unmapped proof shortcut",
            "status": "missing",
            "submission_blocking": True,
            "blocker": "self-test should reject a fifth unmapped closure blocker",
            "evidence": ["results/external_evidence_closure_brief_self_test.json"],
        }
    )
    write_json(path, payload)


def write_premature_manifest(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def remove_linux_command_spine(root: Path) -> None:
    (root / "external_validation" / "collection_job_commands.sh").unlink()


def make_route_haonan_dependent(root: Path) -> None:
    path = root / "results" / "external_acquisition_packet.json"
    payload = read_json(path)
    for check in payload.get("checks", []) or []:
        if check.get("name") == "route_independent_of_haonan":
            check["passed"] = False
            check["detail"] = "synthetic self-test Haonan-dependent route"
    write_json(path, payload)


def remove_source_packet(root: Path) -> None:
    (root / "results" / "external_evidence_intake_ledger_audit.json").unlink()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Evidence Closure Brief Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Unmapped blocker rejected: `{str(payload['unmapped_blocker_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Missing Linux command spine rejected: `{str(payload['missing_linux_command_spine_rejected']).lower()}`.",
        f"Haonan-dependent route rejected: `{str(payload['haonan_dependent_route_rejected']).lower()}`.",
        f"Missing source packet rejected: `{str(payload['missing_source_packet_rejected']).lower()}`.",
        f"Real closure outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It rebuilds the external evidence closure brief in temporary copied workspaces and proves the compact closure recipe rejects fifth-blocker drift, premature real manifests, missing Linux command spines, Haonan-dependent route drift, and missing source packets without touching the real closure brief.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    real_before = {
        "json": sha256_file(REAL_OUT_JSON),
        "md": sha256_file(REAL_OUT_MD),
        "doc": sha256_file(REAL_OUT_DOC),
    }

    checks: list[dict[str, Any]] = []

    ready_status, ready_payload = run_case()
    ready_checks = {check.get("name"): check.get("passed") for check in ready_payload.get("checks", []) or []}
    temporary_fixture_ready = (
        ready_status == 0
        and ready_payload.get("passed") is True
        and ready_payload.get("not_external_evidence") is True
        and ready_payload.get("strict_external_evidence_ready") is False
        and ready_payload.get("missing_requirements") == closure.EXPECTED_MISSING_REQUIREMENTS
        and ready_checks.get("command_spine_covers_all_strict_gates") is True
        and ready_checks.get("independent_route_not_haonan_dependent") is True
    )
    add_check(
        checks,
        "temporary_fixture_builds_current_closure_brief",
        temporary_fixture_ready,
        f"status={ready_status}, blockers={len(ready_payload.get('missing_requirements', []) or [])}",
    )

    unmapped_status, unmapped_payload = run_case(add_unmapped_fifth_blocker)
    unmapped_rejected = unmapped_status != 0 and unmapped_payload.get("passed") is False
    add_check(
        checks,
        "unmapped_fifth_blocker_rejected",
        unmapped_rejected,
        f"status={unmapped_status}, exact_four={next((c.get('passed') for c in unmapped_payload.get('checks', []) if c.get('name') == 'exact_four_submission_blockers_mapped'), None)}",
    )

    manifest_status, manifest_payload = run_case(write_premature_manifest)
    manifest_rejected = manifest_status != 0 and manifest_payload.get("passed") is False
    add_check(
        checks,
        "premature_manifest_rejected",
        manifest_rejected,
        f"status={manifest_status}, no_manifest={next((c.get('passed') for c in manifest_payload.get('checks', []) if c.get('name') == 'no_real_manifest_written_before_external_evidence'), None)}",
    )

    linux_status, linux_payload = run_case(remove_linux_command_spine)
    linux_rejected = linux_status != 0 and linux_payload.get("passed") is False
    add_check(
        checks,
        "missing_linux_command_spine_rejected",
        linux_rejected,
        f"status={linux_status}, command_spines={next((c.get('passed') for c in linux_payload.get('checks', []) if c.get('name') == 'collection_spines_exist_for_windows_and_linux'), None)}",
    )

    route_status, route_payload = run_case(make_route_haonan_dependent)
    route_rejected = route_status != 0 and route_payload.get("passed") is False
    add_check(
        checks,
        "haonan_dependent_route_rejected",
        route_rejected,
        f"status={route_status}, route_check={next((c.get('passed') for c in route_payload.get('checks', []) if c.get('name') == 'independent_route_not_haonan_dependent'), None)}",
    )

    missing_source_status, missing_source_payload = run_case(remove_source_packet)
    missing_source_rejected = missing_source_status != 0 and not missing_source_payload
    add_check(
        checks,
        "missing_source_packet_rejected",
        missing_source_rejected,
        f"status={missing_source_status}, payload_written={bool(missing_source_payload)}",
    )

    real_after = {
        "json": sha256_file(REAL_OUT_JSON),
        "md": sha256_file(REAL_OUT_MD),
        "doc": sha256_file(REAL_OUT_DOC),
    }
    real_outputs_untouched = real_before == real_after
    add_check(
        checks,
        "real_repository_closure_outputs_untouched",
        real_outputs_untouched,
        f"before={real_before}, after={real_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_evidence_closure_brief_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "unmapped_blocker_rejected": unmapped_rejected,
        "premature_manifest_rejected": manifest_rejected,
        "missing_linux_command_spine_rejected": linux_rejected,
        "haonan_dependent_route_rejected": route_rejected,
        "missing_source_packet_rejected": missing_source_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(
        "External evidence closure brief self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; unmapped_rejected={unmapped_rejected}; "
        f"manifest_rejected={manifest_rejected}; missing_linux_rejected={linux_rejected}; "
        f"haonan_rejected={route_rejected}; source_rejected={missing_source_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    if not passed:
        for check in payload["failed_checks"]:
            print(f"FAILED {check['name']}: {check['detail']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
