from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import audit_external_postcollection_seal_consistency as consistency


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_postcollection_seal_consistency_self_test.json"
OUT_MD = RESULTS / "external_postcollection_seal_consistency_self_test.md"
REAL_REPORT = RESULTS / "external_postcollection_seal_consistency_audit.json"

VERSION = "external_postcollection_seal_consistency_self_test_v1"


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return consistency.sha256_file(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_mp4_like(path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41" + (label.encode("utf-8") + b"\n") * 64)


def write_fixture(root: Path) -> dict[str, Path]:
    external = root / "external_validation"
    results = root / "results"
    config = external / "configs" / "peg_place_regrasp.json"
    log = external / "logs" / "peg_place_regrasp.jsonl"
    videos = [
        external / "videos" / "peg_place_regrasp" / f"episode_{index:03d}.mp4"
        for index in range(3)
    ]
    precollection = external / "precollection_freeze_receipt.json"
    metadata = external / "postcollection_operator_metadata.json"

    write_json(
        config,
        {
            "version": "paper119_external_config_v1",
            "task_family": "peg_place_regrasp",
            "platform_type": "high_fidelity_sim",
            "paired_reset_count": 3,
            "fixed_risk_budget": 0.15,
        },
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {"episode_id": f"episode_{index:03d}", "task_family": "peg_place_regrasp", "method": "synthetic_method"}
        for index in range(3)
    ]
    log.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    for index, video in enumerate(videos):
        write_mp4_like(video, f"postcollection consistency self-test video {index}")
    write_json(
        precollection,
        {
            "version": "external_precollection_freeze_receipt_v1",
            "freeze_receipt_ready": True,
            "run_id": "postcollection_consistency_self_test",
        },
    )
    write_json(
        metadata,
        {
            "operator_id": "Synthetic Postcollection Consistency Self-Test Lab",
            "collection_machine": "synthetic-fixture",
            "date_sealed": "2026-06-30",
        },
    )

    artifacts: list[dict[str, Any]] = [
        {
            "role": "prepared_or_manifest_task_config",
            "path": rel(root, config),
            "exists": True,
            "sha256": sha256_file(config),
        },
        {
            "role": "official_raw_jsonl_log",
            "path": rel(root, log),
            "exists": True,
            "sha256": sha256_file(log),
        },
        {
            "role": "precollection_freeze_receipt",
            "path": rel(root, precollection),
            "exists": True,
            "sha256": sha256_file(precollection),
        },
        {
            "role": "operator_metadata",
            "path": rel(root, metadata),
            "exists": True,
            "sha256": sha256_file(metadata),
        },
    ]
    for video in videos:
        artifacts.append(
            {
                "role": "official_rollout_video",
                "path": rel(root, video),
                "exists": True,
                "sha256": sha256_file(video),
            }
        )

    write_json(
        external / "postcollection_evidence_seal.json",
        {
            "version": consistency.SEAL_VERSION,
            "passed": True,
            "not_external_evidence": True,
            "strict_external_evidence_ready": False,
            "postcollection_seal_ready": True,
            "ready_for_manifest_promotion": True,
            "expected_records": 3,
            "jsonl_record_count": 3,
            "rollout_video_count": 3,
            "seal_artifacts": artifacts,
        },
    )
    write_json(
        results / "external_postcollection_evidence_seal_audit.json",
        {
            "version": consistency.SEAL_AUDIT_VERSION,
            "passed": True,
            "not_external_evidence": True,
            "strict_external_evidence_ready": False,
            "postcollection_seal_ready": True,
            "ready_for_manifest_promotion": True,
        },
    )
    return {"config": config, "log": log, "metadata": metadata, "precollection": precollection}


class PatchedConsistency:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.originals = {
            "ROOT": consistency.ROOT,
            "EXTERNAL": consistency.EXTERNAL,
            "RESULTS": consistency.RESULTS,
            "SEAL_JSON": consistency.SEAL_JSON,
            "SEAL_AUDIT_JSON": consistency.SEAL_AUDIT_JSON,
            "OUT_JSON": consistency.OUT_JSON,
            "OUT_MD": consistency.OUT_MD,
        }

    def __enter__(self) -> None:
        external = self.root / "external_validation"
        results = self.root / "results"
        consistency.ROOT = self.root
        consistency.EXTERNAL = external
        consistency.RESULTS = results
        consistency.SEAL_JSON = external / "postcollection_evidence_seal.json"
        consistency.SEAL_AUDIT_JSON = results / "external_postcollection_evidence_seal_audit.json"
        consistency.OUT_JSON = results / "external_postcollection_seal_consistency_audit.json"
        consistency.OUT_MD = results / "external_postcollection_seal_consistency_audit.md"

    def __exit__(self, *_exc: object) -> None:
        for name, value in self.originals.items():
            setattr(consistency, name, value)


def run_fixture_audit(root: Path) -> dict[str, Any]:
    args = argparse.Namespace(backend_module="synthetic_backend.py", run_id="postcollection_consistency_self_test")
    with PatchedConsistency(root):
        return consistency.build_payload(args)


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Postcollection Seal Consistency Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic consistency ready: `{str(payload['synthetic_consistency_ready']).lower()}`.",
        f"Drift rejected: `{str(payload['drift_rejected']).lower()}`.",
        f"Unsealed official artifact rejected: `{str(payload['unsealed_official_artifact_rejected']).lower()}`.",
        "",
        "This self-test builds a temporary postcollection seal fixture and exercises the consistency gate directly. It proves the ready path can pass for a complete sealed raw-log/video/config set, hash drift fails, unsealed official artifacts fail, and the real consistency report is not overwritten.",
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

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_consistency_selftest_") as tmp_name:
        root = Path(tmp_name)
        paths = write_fixture(root)
        ready_payload = run_fixture_audit(root)

        paths["config"].write_text(paths["config"].read_text(encoding="utf-8").replace("0.15", "0.20"), encoding="utf-8")
        drift_payload = run_fixture_audit(root)

    with tempfile.TemporaryDirectory(prefix="paper119_postcollection_consistency_extra_selftest_") as tmp_name:
        root = Path(tmp_name)
        write_fixture(root)
        write_mp4_like(root / "external_validation" / "videos" / "peg_place_regrasp" / "unsealed_extra.mp4", "unsealed extra")
        extra_payload = run_fixture_audit(root)

    report_after = file_digest(REAL_REPORT)
    ready_checks = {str(check.get("name")): check.get("passed") for check in ready_payload.get("checks", [])}
    drift_checks = {str(check.get("name")): check.get("passed") for check in drift_payload.get("checks", [])}
    extra_checks = {str(check.get("name")): check.get("passed") for check in extra_payload.get("checks", [])}

    add_check(
        checks,
        "synthetic_ready_seal_consistency_passes",
        ready_payload.get("passed") is True
        and ready_payload.get("seal_consistency_ready") is True
        and ready_payload.get("ready_for_manifest_promotion") is True
        and int(ready_payload.get("current_jsonl_record_count", 0) or 0) == 3
        and int(ready_payload.get("current_rollout_video_count", 0) or 0) == 3
        and int(ready_payload.get("matched_hash_count", 0) or 0) >= 7,
        (
            f"passed={ready_payload.get('passed')!r}, ready={ready_payload.get('seal_consistency_ready')!r}, "
            f"records={ready_payload.get('current_jsonl_record_count')!r}, videos={ready_payload.get('current_rollout_video_count')!r}, "
            f"matched={ready_payload.get('matched_hash_count')!r}"
        ),
    )
    add_check(
        checks,
        "synthetic_ready_checks_cover_hashes_counts_and_order",
        ready_checks.get("sealed_hashes_recompute_without_drift") is True
        and ready_checks.get("current_counts_match_default_or_ready_state") is True
        and ready_checks.get("strict_sequence_places_consistency_after_seal_before_manifest") is True,
        f"ready_checks={ready_checks}",
    )
    add_check(
        checks,
        "hash_drift_rejected",
        drift_payload.get("passed") is False
        and drift_payload.get("seal_consistency_ready") is False
        and bool(drift_payload.get("mismatched_hashes")),
        f"passed={drift_payload.get('passed')!r}, mismatches={drift_payload.get('mismatched_hashes')!r}",
    )
    add_check(
        checks,
        "hash_drift_fails_recompute_and_promotion_checks",
        drift_checks.get("sealed_hashes_recompute_without_drift") is False
        and drift_checks.get("manifest_promotion_requires_ready_seal_and_consistency") is False,
        f"drift_checks={drift_checks}",
    )
    add_check(
        checks,
        "unsealed_official_artifact_rejected",
        extra_payload.get("passed") is False
        and extra_payload.get("seal_consistency_ready") is False
        and bool(extra_payload.get("extra_official_artifacts")),
        f"passed={extra_payload.get('passed')!r}, extra={extra_payload.get('extra_official_artifacts')!r}",
    )
    add_check(
        checks,
        "unsealed_artifact_fails_official_artifact_check",
        extra_checks.get("no_unsealed_official_artifacts_before_manifest_promotion") is False,
        f"extra_checks={extra_checks}",
    )
    add_check(
        checks,
        "real_consistency_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "synthetic_consistency_ready": ready_payload.get("seal_consistency_ready") is True,
        "drift_rejected": drift_payload.get("passed") is False,
        "unsealed_official_artifact_rejected": extra_payload.get("passed") is False,
        "real_report_untouched": report_before == report_after,
        "ready_summary": {
            "matched_hash_count": ready_payload.get("matched_hash_count"),
            "current_jsonl_record_count": ready_payload.get("current_jsonl_record_count"),
            "current_rollout_video_count": ready_payload.get("current_rollout_video_count"),
        },
        "drift_summary": {
            "mismatched_hashes": drift_payload.get("mismatched_hashes", []),
        },
        "extra_artifact_summary": {
            "extra_official_artifacts": extra_payload.get("extra_official_artifacts", []),
        },
        "checks": checks,
    }
    write_report(payload)
    print(
        "External postcollection seal consistency self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"synthetic_ready={payload['synthetic_consistency_ready']}; "
        f"drift_rejected={payload['drift_rejected']}; "
        f"extra_rejected={payload['unsealed_official_artifact_rejected']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
