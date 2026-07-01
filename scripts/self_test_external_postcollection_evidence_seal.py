from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import build_external_postcollection_evidence_seal as seal_builder


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_postcollection_evidence_seal_self_test.json"
OUT_MD = RESULTS / "external_postcollection_evidence_seal_self_test.md"
REAL_SEAL = ROOT / "external_validation" / "postcollection_evidence_seal.json"
REAL_AUDIT = RESULTS / "external_postcollection_evidence_seal_audit.json"

VERSION = "external_postcollection_evidence_seal_self_test_v1"


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_mp4_like(path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41" + (label.encode("utf-8") + b"\n") * 80)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_fixture(root: Path, *, expected_records: int = 3, video_count: int = 3, manifest_exists: bool = False) -> None:
    external = root / "external_validation"
    results = root / "results"
    write_json(results / "external_collection_plan.json", {"total_required_records": expected_records})
    write_json(
        results / "external_precollection_freeze_receipt_audit.json",
        {
            "version": "external_precollection_freeze_receipt_audit_v1",
            "passed": True,
            "not_external_evidence": True,
            "strict_external_evidence_ready": False,
            "freeze_receipt_ready": True,
        },
    )
    for path, payload in (
        (results / "external_rollout_metrics.json", {"passed": False}),
        (results / "external_config_evidence_audit.json", {"passed": False}),
        (results / "external_adapter_contract_evidence_audit.json", {"passed": False}),
        (results / "external_evidence_audit.json", {"submission_ready": False}),
    ):
        write_json(path, payload)

    write_json(external / "precollection_freeze_receipt.json", {"freeze_receipt_ready": True, "run_id": "seal_self_test"})
    write_text(external / "operator_record_sheet.csv", "row_id,task_family\n0,peg_place_regrasp\n")
    write_text(external / "blinded_operator_sheet.csv", "row_id,method_alias\n0,method_01\n")
    write_json(external / "method_alias_map.json", {"method_01": "synthetic_method"})
    write_text(external / "method_manifest_cutover_checklist.csv", "method,ready\nsynthetic_method,false\n")
    write_text(external / "method_reference_provenance.csv", "method,path\nsynthetic_method,synthetic.py\n")
    write_json(external / "manifest_precollection_draft.json", {"draft_ready": True, "official_manifest_exists": False})
    write_json(
        external / "configs" / "peg_place_regrasp.json",
        {
            "version": "paper119_external_config_v1",
            "task_family": "peg_place_regrasp",
            "platform_type": "high_fidelity_sim",
            "paired_reset_count": expected_records,
        },
    )

    videos: list[Path] = []
    for index in range(video_count):
        video = external / "videos" / "peg_place_regrasp" / f"episode_{index:03d}.mp4"
        write_mp4_like(video, f"postcollection evidence seal self-test video {index}")
        videos.append(video)

    records = []
    for index in range(expected_records):
        video_path = videos[index % len(videos)] if videos else external / "videos" / "peg_place_regrasp" / "missing.mp4"
        records.append(
            {
                "episode_id": f"episode_{index:03d}",
                "task_family": "peg_place_regrasp",
                "method": "synthetic_method",
                "video_path": video_path.resolve().relative_to(root.resolve()).as_posix(),
            }
        )
    log = external / "logs" / "peg_place_regrasp.jsonl"
    write_text(log, "".join(json.dumps(record, sort_keys=True) + "\n" for record in records))
    if manifest_exists:
        write_json(external / "manifest.json", {"version": "paper119_external_manifest_v1", "self_test_only": True})


class PatchedSealBuilder:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.originals = {
            "ROOT": seal_builder.ROOT,
            "EXTERNAL": seal_builder.EXTERNAL,
            "RESULTS": seal_builder.RESULTS,
            "OUT_JSON": seal_builder.OUT_JSON,
            "OUT_MD": seal_builder.OUT_MD,
            "OUT_CSV": seal_builder.OUT_CSV,
            "AUDIT_JSON": seal_builder.AUDIT_JSON,
            "AUDIT_MD": seal_builder.AUDIT_MD,
        }

    def __enter__(self) -> None:
        external = self.root / "external_validation"
        results = self.root / "results"
        seal_builder.ROOT = self.root
        seal_builder.EXTERNAL = external
        seal_builder.RESULTS = results
        seal_builder.OUT_JSON = external / "postcollection_evidence_seal.json"
        seal_builder.OUT_MD = external / "postcollection_evidence_seal.md"
        seal_builder.OUT_CSV = external / "postcollection_evidence_seal.csv"
        seal_builder.AUDIT_JSON = results / "external_postcollection_evidence_seal_audit.json"
        seal_builder.AUDIT_MD = results / "external_postcollection_evidence_seal_audit.md"

    def __exit__(self, *_exc: object) -> None:
        for name, value in self.originals.items():
            setattr(seal_builder, name, value)


def args_for_fixture(*, operator_ready: bool = True) -> argparse.Namespace:
    return argparse.Namespace(
        backend_module="external_validation/runner/synthetic_backend.py",
        run_id="postcollection_evidence_seal_self_test_run",
        operator_id="Synthetic Postcollection Seal Self-Test Lab" if operator_ready else "",
        collection_machine="synthetic-render-machine" if operator_ready else "",
        date_sealed="2026-06-30" if operator_ready else "",
    )


def run_fixture(root: Path, *, operator_ready: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    with PatchedSealBuilder(root):
        payload = seal_builder.build_payload(args_for_fixture(operator_ready=operator_ready))
        audit = seal_builder.build_audit(payload)
    return payload, audit


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Postcollection Evidence Seal Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic seal ready: `{str(payload['synthetic_seal_ready']).lower()}`.",
        f"Missing operator metadata rejected: `{str(payload['missing_operator_metadata_rejected']).lower()}`.",
        f"Incomplete video set rejected: `{str(payload['incomplete_video_set_rejected']).lower()}`.",
        f"Manifest-present promotion rejected: `{str(payload['manifest_present_rejected']).lower()}`.",
        "",
        "This self-test builds temporary postcollection seal fixtures and exercises the seal builder directly. It proves a complete sealed raw-log/video/config fixture can reach manifest-promotion readiness, while missing operator metadata, incomplete official videos, and a pre-existing manifest remain fail-closed without overwriting the real seal or audit.",
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
    seal_before = file_digest(REAL_SEAL)
    audit_before = file_digest(REAL_AUDIT)

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_seal_selftest_ready_") as tmp_name:
        root = Path(tmp_name)
        write_fixture(root)
        ready_payload, ready_audit = run_fixture(root)

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_seal_selftest_operator_") as tmp_name:
        root = Path(tmp_name)
        write_fixture(root)
        missing_operator_payload, missing_operator_audit = run_fixture(root, operator_ready=False)

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_seal_selftest_videos_") as tmp_name:
        root = Path(tmp_name)
        write_fixture(root, expected_records=3, video_count=2)
        incomplete_video_payload, incomplete_video_audit = run_fixture(root)

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_seal_selftest_manifest_") as tmp_name:
        root = Path(tmp_name)
        write_fixture(root, manifest_exists=True)
        manifest_payload, manifest_audit = run_fixture(root)

    seal_after = file_digest(REAL_SEAL)
    audit_after = file_digest(REAL_AUDIT)
    ready_checks = {str(check.get("name")): check.get("passed") for check in ready_audit.get("checks", [])}
    missing_operator_checks = {str(check.get("name")): check.get("passed") for check in missing_operator_audit.get("checks", [])}
    incomplete_video_checks = {str(check.get("name")): check.get("passed") for check in incomplete_video_audit.get("checks", [])}
    manifest_checks = {str(check.get("name")): check.get("passed") for check in manifest_audit.get("checks", [])}

    add_check(
        checks,
        "synthetic_complete_seal_reaches_manifest_promotion",
        ready_payload.get("postcollection_seal_ready") is True
        and ready_payload.get("ready_for_manifest_promotion") is True
        and ready_audit.get("passed") is True
        and ready_audit.get("postcollection_seal_ready") is True
        and int(ready_payload.get("jsonl_record_count", 0) or 0) == 3
        and int(ready_payload.get("rollout_video_count", 0) or 0) == 3
        and int(ready_audit.get("sealed_artifact_count", 0) or 0) >= 10,
        (
            f"seal_ready={ready_payload.get('postcollection_seal_ready')!r}, "
            f"promotion={ready_payload.get('ready_for_manifest_promotion')!r}, "
            f"records={ready_payload.get('jsonl_record_count')!r}, videos={ready_payload.get('rollout_video_count')!r}, "
            f"artifacts={ready_audit.get('sealed_artifact_count')!r}"
        ),
    )
    add_check(
        checks,
        "synthetic_ready_checks_cover_order_inventory_and_boundary",
        ready_checks.get("seal_is_non_evidence_and_fail_closed") is True
        and ready_checks.get("hash_inventory_written_for_precollection_inputs") is True
        and ready_checks.get("strict_sequence_places_seal_after_collection_before_manifest") is True
        and ready_checks.get("seal_references_consistency_gate_before_manifest") is True
        and ready_checks.get("strict_evidence_gates_still_false") is True,
        f"ready_checks={ready_checks}",
    )
    add_check(
        checks,
        "missing_operator_metadata_rejected",
        missing_operator_payload.get("postcollection_seal_ready") is False
        and missing_operator_audit.get("passed") is False
        and missing_operator_checks.get("operator_metadata_still_required") is False,
        (
            f"seal_ready={missing_operator_payload.get('postcollection_seal_ready')!r}, "
            f"operator_check={missing_operator_checks.get('operator_metadata_still_required')!r}"
        ),
    )
    add_check(
        checks,
        "incomplete_video_set_rejected",
        incomplete_video_payload.get("postcollection_seal_ready") is False
        and incomplete_video_audit.get("passed") is False
        and incomplete_video_checks.get("raw_logs_and_videos_absent_before_collection") is False,
        (
            f"seal_ready={incomplete_video_payload.get('postcollection_seal_ready')!r}, "
            f"records={incomplete_video_payload.get('jsonl_record_count')!r}, "
            f"videos={incomplete_video_payload.get('rollout_video_count')!r}"
        ),
    )
    add_check(
        checks,
        "manifest_present_rejected_before_promotion",
        manifest_payload.get("postcollection_seal_ready") is False
        and manifest_audit.get("passed") is False
        and manifest_checks.get("no_real_manifest_written") is False,
        (
            f"seal_ready={manifest_payload.get('postcollection_seal_ready')!r}, "
            f"manifest_exists={manifest_payload.get('manifest_exists_before_seal')!r}"
        ),
    )
    add_check(
        checks,
        "real_postcollection_seal_reports_not_overwritten",
        seal_before == seal_after and audit_before == audit_after,
        f"seal_before={seal_before}, seal_after={seal_after}, audit_before={audit_before}, audit_after={audit_after}",
    )

    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "synthetic_seal_ready": ready_payload.get("postcollection_seal_ready") is True,
        "missing_operator_metadata_rejected": missing_operator_audit.get("passed") is False,
        "incomplete_video_set_rejected": incomplete_video_audit.get("passed") is False,
        "manifest_present_rejected": manifest_audit.get("passed") is False,
        "real_reports_untouched": seal_before == seal_after and audit_before == audit_after,
        "ready_summary": {
            "sealed_artifact_count": ready_audit.get("sealed_artifact_count"),
            "jsonl_record_count": ready_payload.get("jsonl_record_count"),
            "rollout_video_count": ready_payload.get("rollout_video_count"),
        },
        "checks": checks,
    }
    write_report(payload)
    print(
        "External postcollection evidence seal self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"synthetic_ready={payload['synthetic_seal_ready']}; "
        f"missing_operator_rejected={payload['missing_operator_metadata_rejected']}; "
        f"incomplete_video_rejected={payload['incomplete_video_set_rejected']}; "
        f"manifest_rejected={payload['manifest_present_rejected']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
