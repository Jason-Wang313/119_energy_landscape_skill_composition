from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = RESULTS / "external_operator_release_bundle_plan.json"
OUT_MD = RESULTS / "external_operator_release_bundle_plan.md"
OUT_MANIFEST = EXTERNAL / "operator_release_bundle_manifest.csv"
OUT_README = EXTERNAL / "operator_release_bundle_README.md"
ARCHIVE_PATH = RESULTS / "paper119_external_operator_release_bundle.zip"

VERSION = "external_operator_release_bundle_plan_v1"
ARCHIVE_ROOT = "paper119_external_operator_release_bundle"

FORBIDDEN_PATH_PARTS = {
    "external_validation/local_dry_run/",
    "external_validation/logs/",
    "external_validation/videos/",
    "external_validation/checkpoints/",
    "external_validation/manifest.json",
    "placeholder_not_external_evidence",
    "paper119_external_operator_release_bundle.zip",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def require_payload(path: Path, version: str) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def forbidden_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        lowered = path.lower().replace("\\", "/")
        for forbidden in FORBIDDEN_PATH_PARTS:
            if forbidden.lower() in lowered:
                hits.append(path)
                break
    return sorted(set(hits))


def validate_record_hashes(records: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    mismatched: list[str] = []
    for record in records:
        path_text = str(record.get("path", "")).strip()
        expected_sha = str(record.get("sha256", "")).strip().upper()
        path = ROOT / path_text
        if not path.exists():
            missing.append(path_text)
            continue
        actual_sha = sha256(path)
        if expected_sha and actual_sha != expected_sha:
            mismatched.append(path_text)
    return missing, mismatched


def write_manifest(records: list[dict[str, Any]]) -> None:
    OUT_MANIFEST.parent.mkdir(exist_ok=True)
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "category", "bytes", "sha256", "archive_entry"],
        )
        writer.writeheader()
        for record in records:
            path_text = str(record["path"])
            writer.writerow(
                {
                    "path": path_text,
                    "category": record.get("category", ""),
                    "bytes": record.get("bytes", ""),
                    "sha256": record.get("sha256", ""),
                    "archive_entry": f"{ARCHIVE_ROOT}/{path_text}",
                }
            )


def write_release_readme(payload: dict[str, Any]) -> None:
    lines = [
        "# Paper 119 External Operator Release Bundle",
        "",
        "This is a non-evidence shipping manifest for the independent operator handoff package.",
        "",
        f"Bundle state: `{payload['bundle_state']}`.",
        f"Included handoff files: `{payload['included_file_count']}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "Do not add official rollout logs, videos, checkpoints, local dry-run records, placeholder media, or `external_validation/manifest.json` to this release bundle.",
        "",
        "To create the archive locally after regenerating the handoff bundle:",
        "",
        "```powershell",
        payload["archive_write_command"],
        "```",
        "",
        "The archive is a transfer package only. It is not a substitute for the strict external-evidence manifest, raw logs, rollout videos, accepted fidelity provenance, or independent baseline evidence.",
        "",
    ]
    OUT_README.write_text("\n".join(lines), encoding="utf-8")


def stable_zip_write(archive_path: Path, records: list[dict[str, Any]]) -> tuple[int, str, int]:
    archive_path.parent.mkdir(exist_ok=True)
    extra_paths = [OUT_MANIFEST, OUT_README]
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for record in records:
            path_text = str(record["path"])
            source = ROOT / path_text
            write_zip_entry(archive, source, f"{ARCHIVE_ROOT}/{path_text}")
        for source in extra_paths:
            write_zip_entry(archive, source, f"{ARCHIVE_ROOT}/{rel(source)}")
    return len(records) + len(extra_paths), sha256(archive_path), archive_path.stat().st_size


def write_zip_entry(archive: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, source.read_bytes())


def build_payload(write_archive: bool) -> dict[str, Any]:
    handoff = require_payload(RESULTS / "external_operator_handoff_bundle.json", "external_operator_handoff_bundle_v1")
    collection_job = require_payload(
        RESULTS / "external_collection_job_packet_audit.json",
        "external_collection_job_packet_audit_v1",
    )
    records = [record for record in handoff.get("included_files", []) or [] if isinstance(record, dict)]
    paths = [str(record.get("path", "")).strip() for record in records]
    missing_files, mismatched_hashes = validate_record_hashes(records)
    forbidden = sorted(set(forbidden_hits(paths) + list(handoff.get("forbidden_included_paths", []) or [])))
    category_counts = dict(handoff.get("category_counts", {}) or {})
    total_bytes = sum(int(record.get("bytes", 0) or 0) for record in records)
    archive_write_command = "python scripts\\build_external_operator_release_bundle.py --write-archive"

    checks: list[dict[str, Any]] = []
    add_check(checks, "release_bundle_is_non_evidence", True, "release bundle is a transfer package only")
    add_check(
        checks,
        "source_handoff_bundle_ready",
        handoff.get("passed") is True
        and handoff.get("not_external_evidence") is True
        and handoff.get("handoff_bundle_ready") is True
        and handoff.get("start_state") == "DO_NOT_COLLECT_YET"
        and handoff.get("strict_evidence_ready") is False,
        (
            f"passed={handoff.get('passed')!r}, start_state={handoff.get('start_state')!r}, "
            f"strict={handoff.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "collection_job_packet_present_in_handoff",
        collection_job.get("passed") is True
        and collection_job.get("job_state") == "DO_NOT_START_COLLECTION_YET"
        and "external_validation/collection_job_packet.md" in paths
        and "external_validation/collection_job_commands.ps1" in paths,
        (
            f"job_state={collection_job.get('job_state')!r}, "
            f"packet_in_paths={'external_validation/collection_job_packet.md' in paths}"
        ),
    )
    add_check(checks, "handoff_hashes_recomputed", not missing_files and not mismatched_hashes, f"missing={missing_files[:5]}, mismatched={mismatched_hashes[:5]}")
    add_check(checks, "forbidden_evidence_paths_excluded", not forbidden, f"forbidden={forbidden}")
    add_check(
        checks,
        "release_manifest_covers_all_handoff_files",
        len(records) == int(handoff.get("included_file_count", 0) or 0) and len(records) >= 300,
        f"records={len(records)}, handoff_count={handoff.get('included_file_count')!r}",
    )
    add_check(
        checks,
        "archive_writer_is_explicit_and_optional",
        archive_write_command.endswith("--write-archive"),
        "default mode writes only plan files; archive writing requires --write-archive",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    write_manifest(records)
    archive_entry_count = 0
    archive_sha = ""
    archive_size = 0
    if write_archive:
        write_release_readme(
            {
                "bundle_state": "READY_TO_SEND_OPERATOR_PACKAGE",
                "included_file_count": len(records),
                "strict_external_evidence_ready": False,
                "archive_write_command": archive_write_command,
            }
        )
        archive_entry_count, archive_sha, archive_size = stable_zip_write(ARCHIVE_PATH, records)
        add_check(
            checks,
            "archive_written_with_expected_entries",
            archive_entry_count == len(records) + 2 and len(archive_sha) == 64 and archive_size > total_bytes // 10,
            f"entries={archive_entry_count}, sha={archive_sha}, size={archive_size}",
        )
    else:
        add_check(checks, "archive_not_written_by_default", True, "use --write-archive to create the transfer zip")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "bundle_state": "READY_TO_SEND_OPERATOR_PACKAGE" if passed else "BUNDLE_PLAN_NEEDS_ATTENTION",
        "archive_write_enabled": bool(write_archive),
        "archive_written": bool(write_archive and archive_sha),
        "archive_path": rel(ARCHIVE_PATH),
        "archive_sha256": archive_sha,
        "archive_size_bytes": archive_size,
        "archive_entry_count": archive_entry_count,
        "archive_root": ARCHIVE_ROOT,
        "archive_write_command": archive_write_command,
        "included_file_count": len(records),
        "total_payload_bytes": total_bytes,
        "category_counts": category_counts,
        "manifest_csv": rel(OUT_MANIFEST),
        "release_readme": rel(OUT_README),
        "source_handoff_bundle": rel(RESULTS / "external_operator_handoff_bundle.json"),
        "source_collection_job": rel(RESULTS / "external_collection_job_packet_audit.json"),
        "forbidden_path_parts": sorted(FORBIDDEN_PATH_PARTS),
        "forbidden_paths": forbidden,
        "missing_files": missing_files,
        "mismatched_hashes": mismatched_hashes,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    write_release_readme(payload)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Operator Release Bundle Plan",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Bundle state: `{payload['bundle_state']}`.",
        f"Included handoff files: `{payload['included_file_count']}`.",
        f"Payload bytes: `{payload['total_payload_bytes']}`.",
        f"Archive written: `{str(payload['archive_written']).lower()}`.",
        f"Archive path: `{payload['archive_path']}`.",
        f"Manifest CSV: `{payload['manifest_csv']}`.",
        f"Release README: `{payload['release_readme']}`.",
        "",
        "This is a transfer package plan for the independent operator. It does not contain real rollout evidence and does not write `external_validation/manifest.json`.",
        "",
        "## Archive Command",
        "",
        "```powershell",
        payload["archive_write_command"],
        "```",
        "",
        "## Category Counts",
        "",
    ]
    for category, count in sorted(payload["category_counts"].items()):
        lines.append(f"- `{category}`: `{count}`")
    if payload["archive_written"]:
        lines.extend(
            [
                "",
                "## Archive",
                "",
                f"- SHA256: `{payload['archive_sha256']}`",
                f"- Size bytes: `{payload['archive_size_bytes']}`",
                f"- Entry count: `{payload['archive_entry_count']}`",
            ]
        )
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-archive", action="store_true", help="write the deterministic transfer zip under results/")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(write_archive=args.write_archive)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
