from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_operator_release_bundle as release


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = REAL_ROOT / "results"
REAL_EXTERNAL = REAL_ROOT / "external_validation"

REAL_OUTPUTS = [
    REAL_RESULTS / "external_operator_release_bundle_plan.json",
    REAL_RESULTS / "external_operator_release_bundle_plan.md",
    REAL_EXTERNAL / "operator_release_bundle_manifest.csv",
    REAL_EXTERNAL / "operator_release_bundle_README.md",
    REAL_RESULTS / "paper119_external_operator_release_bundle.zip",
]

OUT_JSON = REAL_RESULTS / "external_operator_release_bundle_self_test.json"
OUT_MD = REAL_RESULTS / "external_operator_release_bundle_self_test.md"


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_upper(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in REAL_OUTPUTS}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing release-bundle self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    handoff = read_json(REAL_RESULTS / "external_operator_handoff_bundle.json")
    copy_file(REAL_RESULTS / "external_operator_handoff_bundle.json", root / "results" / "external_operator_handoff_bundle.json")
    copy_file(REAL_RESULTS / "external_collection_job_packet_audit.json", root / "results" / "external_collection_job_packet_audit.json")
    for record in handoff.get("included_files", []) or []:
        if isinstance(record, dict):
            path_text = str(record.get("path", "")).strip()
            if path_text:
                copy_file(REAL_ROOT / path_text, root / path_text)


def payload_from_temp(root: Path) -> dict[str, Any]:
    path = root / "results" / "external_operator_release_bundle_plan.json"
    if path.exists():
        return read_json(path)
    return {"passed": False, "checks": []}


def run_builder(root: Path, *, write_archive: bool = False) -> tuple[int, dict[str, Any]]:
    original = (
        release.ROOT,
        release.EXTERNAL,
        release.RESULTS,
        release.OUT_JSON,
        release.OUT_MD,
        release.OUT_MANIFEST,
        release.OUT_README,
        release.ARCHIVE_PATH,
    )
    try:
        release.ROOT = root
        release.EXTERNAL = root / "external_validation"
        release.RESULTS = root / "results"
        release.OUT_JSON = release.RESULTS / "external_operator_release_bundle_plan.json"
        release.OUT_MD = release.RESULTS / "external_operator_release_bundle_plan.md"
        release.OUT_MANIFEST = release.EXTERNAL / "operator_release_bundle_manifest.csv"
        release.OUT_README = release.EXTERNAL / "operator_release_bundle_README.md"
        release.ARCHIVE_PATH = release.RESULTS / "paper119_external_operator_release_bundle.zip"
        with redirect_stdout(io.StringIO()):
            try:
                payload = release.build_payload(write_archive=write_archive)
                release.write_outputs(payload)
                status = 0 if payload.get("passed") is True else 1
            except SystemExit as exc:
                status = exc.code if isinstance(exc.code, int) else 1
                payload = payload_from_temp(root)
                payload["error"] = str(exc)
                return status, payload
        return status, payload_from_temp(root)
    finally:
        (
            release.ROOT,
            release.EXTERNAL,
            release.RESULTS,
            release.OUT_JSON,
            release.OUT_MD,
            release.OUT_MANIFEST,
            release.OUT_README,
            release.ARCHIVE_PATH,
        ) = original


def run_case(
    mutator: Callable[[Path], None] | None = None,
    *,
    write_archive: bool = False,
) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_operator_release_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        return run_builder(root, write_archive=write_archive)


def check_named(payload: dict[str, Any], name: str) -> bool | None:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed") is True
    return None


def mutate_handoff(root: Path, mutator: Callable[[dict[str, Any]], None]) -> None:
    path = root / "results" / "external_operator_handoff_bundle.json"
    payload = read_json(path)
    mutator(payload)
    write_json(path, payload)


def remove_handoff_source(root: Path) -> None:
    (root / "results" / "external_operator_handoff_bundle.json").unlink()


def promote_handoff_state(root: Path) -> None:
    def mutate(payload: dict[str, Any]) -> None:
        payload["start_state"] = "READY_TO_COLLECT"
        payload["strict_evidence_ready"] = True

    mutate_handoff(root, mutate)


def delete_included_file(root: Path) -> None:
    (root / "external_validation" / "collection_job_packet.md").unlink()


def corrupt_included_file(root: Path) -> None:
    path = root / "external_validation" / "collection_job_packet.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nsynthetic self-test drift\n", encoding="utf-8")


def add_forbidden_record(root: Path) -> None:
    log_path = root / "external_validation" / "logs" / "synthetic_release_selftest.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text('{"synthetic_self_test_only": true}\n', encoding="utf-8")

    def mutate(payload: dict[str, Any]) -> None:
        records = list(payload.get("included_files", []) or [])
        records.append(
            {
                "path": "external_validation/logs/synthetic_release_selftest.jsonl",
                "category": "generated_non_evidence_report",
                "bytes": log_path.stat().st_size,
                "sha256": sha256_upper(log_path),
                "exists": True,
            }
        )
        payload["included_files"] = records
        payload["included_file_count"] = len(records)
        category_counts = dict(payload.get("category_counts", {}) or {})
        category_counts["generated_non_evidence_report"] = int(category_counts.get("generated_non_evidence_report", 0) or 0) + 1
        payload["category_counts"] = category_counts

    mutate_handoff(root, mutate)


def write_premature_manifest(root: Path) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def promote_collection_job(root: Path) -> None:
    path = root / "results" / "external_collection_job_packet_audit.json"
    payload = read_json(path)
    payload["job_state"] = "READY_FOR_OPERATOR_CONFIRMED_COLLECTION"
    write_json(path, payload)


def remove_collection_job_from_handoff(root: Path) -> None:
    def mutate(payload: dict[str, Any]) -> None:
        records = [
            record
            for record in payload.get("included_files", []) or []
            if "collection_job_packet" not in str(record.get("path", ""))
            and "collection_job_commands" not in str(record.get("path", ""))
            and "build_external_collection_job_packet.py" not in str(record.get("path", ""))
        ]
        payload["included_files"] = records
        payload["included_file_count"] = len(records)

    mutate_handoff(root, mutate)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# External Operator Release Bundle Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Temporary fixture ready: `{str(payload['temporary_fixture_ready']).lower()}`.",
        f"Explicit archive fixture ready: `{str(payload['explicit_archive_fixture_ready']).lower()}`.",
        f"Missing handoff rejected: `{str(payload['missing_handoff_rejected']).lower()}`.",
        f"Handoff no-go drift rejected: `{str(payload['handoff_no_go_drift_rejected']).lower()}`.",
        f"Missing file rejected: `{str(payload['missing_file_rejected']).lower()}`.",
        f"Hash drift rejected: `{str(payload['hash_drift_rejected']).lower()}`.",
        f"Forbidden evidence path rejected: `{str(payload['forbidden_evidence_path_rejected']).lower()}`.",
        f"Premature manifest rejected: `{str(payload['premature_manifest_rejected']).lower()}`.",
        f"Collection-job go-state rejected: `{str(payload['collection_job_go_state_rejected']).lower()}`.",
        f"Collection-job omission rejected: `{str(payload['collection_job_omission_rejected']).lower()}`.",
        f"Real release outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It rebuilds the operator release bundle plan in temporary copied workspaces, verifies the default no-archive path and explicit archive path, and proves missing handoff sources, no-go drift, missing files, hash drift, forbidden evidence paths, premature manifests, collection-job go-state drift, and collection-job omission fail closed without touching the real release outputs.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    real_hashes_before = real_output_hashes()
    checks: list[dict[str, Any]] = []

    complete_status, complete_payload = run_case()
    complete_checks = {check.get("name"): check.get("passed") for check in complete_payload.get("checks", []) or []}
    temporary_fixture_ready = (
        complete_status == 0
        and complete_payload.get("version") == "external_operator_release_bundle_plan_v1"
        and complete_payload.get("passed") is True
        and complete_payload.get("not_external_evidence") is True
        and complete_payload.get("strict_external_evidence_ready") is False
        and complete_payload.get("bundle_state") == "READY_TO_SEND_OPERATOR_PACKAGE"
        and complete_payload.get("archive_write_enabled") is False
        and complete_payload.get("archive_written") is False
        and int(complete_payload.get("included_file_count", 0) or 0) >= 300
        and complete_checks.get("source_handoff_bundle_ready") is True
        and complete_checks.get("collection_job_packet_present_in_handoff") is True
        and complete_checks.get("handoff_hashes_recomputed") is True
        and complete_checks.get("forbidden_evidence_paths_excluded") is True
        and complete_checks.get("release_manifest_covers_all_handoff_files") is True
        and complete_checks.get("archive_writer_is_explicit_and_optional") is True
        and complete_checks.get("no_real_manifest_written") is True
        and complete_checks.get("archive_not_written_by_default") is True
    )
    add_check(checks, "temporary_fixture_builds_current_release_plan", temporary_fixture_ready, f"status={complete_status}, files={complete_payload.get('included_file_count')!r}, archive={complete_payload.get('archive_written')!r}")

    archive_status, archive_payload = run_case(write_archive=True)
    archive_checks = {check.get("name"): check.get("passed") for check in archive_payload.get("checks", []) or []}
    explicit_archive_fixture_ready = (
        archive_status == 0
        and archive_payload.get("passed") is True
        and archive_payload.get("archive_write_enabled") is True
        and archive_payload.get("archive_written") is True
        and len(str(archive_payload.get("archive_sha256", ""))) == 64
        and int(archive_payload.get("archive_entry_count", 0) or 0) >= int(archive_payload.get("included_file_count", 0) or 0) + 2
        and archive_checks.get("archive_written_with_expected_entries") is True
    )
    add_check(checks, "explicit_archive_fixture_writes_deterministic_transfer_zip", explicit_archive_fixture_ready, f"status={archive_status}, entries={archive_payload.get('archive_entry_count')!r}, sha={archive_payload.get('archive_sha256')!r}")

    missing_status, missing_payload = run_case(remove_handoff_source)
    missing_handoff_rejected = missing_status != 0 and "external_operator_handoff_bundle.json" in str(missing_payload.get("error", ""))
    add_check(checks, "missing_handoff_source_rejected", missing_handoff_rejected, f"status={missing_status}, error={missing_payload.get('error', '')!r}")

    no_go_status, no_go_payload = run_case(promote_handoff_state)
    handoff_no_go_drift_rejected = no_go_status != 0 and no_go_payload.get("passed") is False and check_named(no_go_payload, "source_handoff_bundle_ready") is False
    add_check(checks, "handoff_no_go_drift_rejected", handoff_no_go_drift_rejected, f"status={no_go_status}, source_check={check_named(no_go_payload, 'source_handoff_bundle_ready')}")

    missing_file_status, missing_file_payload = run_case(delete_included_file)
    missing_file_rejected = missing_file_status != 0 and missing_file_payload.get("passed") is False and check_named(missing_file_payload, "handoff_hashes_recomputed") is False
    add_check(checks, "missing_file_rejected", missing_file_rejected, f"status={missing_file_status}, hash_check={check_named(missing_file_payload, 'handoff_hashes_recomputed')}")

    hash_status, hash_payload = run_case(corrupt_included_file)
    hash_drift_rejected = hash_status != 0 and hash_payload.get("passed") is False and check_named(hash_payload, "handoff_hashes_recomputed") is False
    add_check(checks, "hash_drift_rejected", hash_drift_rejected, f"status={hash_status}, hash_check={check_named(hash_payload, 'handoff_hashes_recomputed')}")

    forbidden_status, forbidden_payload = run_case(add_forbidden_record)
    forbidden_evidence_path_rejected = forbidden_status != 0 and forbidden_payload.get("passed") is False and check_named(forbidden_payload, "forbidden_evidence_paths_excluded") is False
    add_check(checks, "forbidden_evidence_path_rejected", forbidden_evidence_path_rejected, f"status={forbidden_status}, forbidden_check={check_named(forbidden_payload, 'forbidden_evidence_paths_excluded')}")

    manifest_status, manifest_payload = run_case(write_premature_manifest)
    premature_manifest_rejected = manifest_status != 0 and manifest_payload.get("passed") is False and check_named(manifest_payload, "no_real_manifest_written") is False
    add_check(checks, "premature_manifest_rejected", premature_manifest_rejected, f"status={manifest_status}, manifest_check={check_named(manifest_payload, 'no_real_manifest_written')}")

    job_status, job_payload = run_case(promote_collection_job)
    collection_job_go_state_rejected = job_status != 0 and job_payload.get("passed") is False and check_named(job_payload, "collection_job_packet_present_in_handoff") is False
    add_check(checks, "collection_job_go_state_rejected", collection_job_go_state_rejected, f"status={job_status}, job_check={check_named(job_payload, 'collection_job_packet_present_in_handoff')}")

    omission_status, omission_payload = run_case(remove_collection_job_from_handoff)
    collection_job_omission_rejected = omission_status != 0 and omission_payload.get("passed") is False and check_named(omission_payload, "collection_job_packet_present_in_handoff") is False
    add_check(checks, "collection_job_omission_rejected", collection_job_omission_rejected, f"status={omission_status}, job_check={check_named(omission_payload, 'collection_job_packet_present_in_handoff')}")

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(checks, "real_repository_release_outputs_untouched", real_outputs_untouched, f"before={real_hashes_before}, after={real_hashes_after}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_operator_release_bundle_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_fixture_ready": temporary_fixture_ready,
        "explicit_archive_fixture_ready": explicit_archive_fixture_ready,
        "missing_handoff_rejected": missing_handoff_rejected,
        "handoff_no_go_drift_rejected": handoff_no_go_drift_rejected,
        "missing_file_rejected": missing_file_rejected,
        "hash_drift_rejected": hash_drift_rejected,
        "forbidden_evidence_path_rejected": forbidden_evidence_path_rejected,
        "premature_manifest_rejected": premature_manifest_rejected,
        "collection_job_go_state_rejected": collection_job_go_state_rejected,
        "collection_job_omission_rejected": collection_job_omission_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(payload)
    print(
        "External operator release bundle self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"fixture_ready={temporary_fixture_ready}; "
        f"archive_ready={explicit_archive_fixture_ready}; "
        f"missing_handoff_rejected={missing_handoff_rejected}; "
        f"no_go_drift_rejected={handoff_no_go_drift_rejected}; "
        f"missing_file_rejected={missing_file_rejected}; "
        f"hash_drift_rejected={hash_drift_rejected}; "
        f"forbidden_rejected={forbidden_evidence_path_rejected}; "
        f"manifest_rejected={premature_manifest_rejected}; "
        f"job_go_rejected={collection_job_go_state_rejected}; "
        f"job_omission_rejected={collection_job_omission_rejected}; "
        f"real_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
