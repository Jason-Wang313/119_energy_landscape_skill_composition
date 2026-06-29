from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import audit_external_release_package as release_audit


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
TMP_ROOT = ROOT / "tmp"
OUT_JSON = RESULTS / "external_release_package_self_test.json"
OUT_MD = RESULTS / "external_release_package_self_test.md"
REAL_REPORT = RESULTS / "external_release_package_audit.json"


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


def sha256(path: Path) -> str:
    return release_audit.sha256_path(path)


def make_config(task_family: str) -> dict[str, Any]:
    return {
        "version": "paper119_external_config_v1",
        "config_schema": "external_validation/config_schema_v1.json",
        "task_family": task_family,
        "platform_type": "high_fidelity_sim",
        "platform_name": "ReleasePackageSelfTestSim-v1",
        "skill_i": f"{task_family}_source_skill",
        "skill_j": f"{task_family}_target_skill",
        "seam_under_test": "temporary release-package self-test seam",
        "paired_reset_count": 30,
        "fixed_risk_budget": 0.15,
    }


def write_complete_artifacts(tmp: Path) -> dict[str, list[dict[str, str]]]:
    artifact_dir = tmp / "release_artifacts"
    code = artifact_dir / "code" / "adapter.py"
    config = artifact_dir / "configs" / "peg_place_regrasp.json"
    log = artifact_dir / "logs" / "peg_place_regrasp.jsonl"
    video = artifact_dir / "videos" / "peg_place_regrasp" / "episode_000.mp4"
    checkpoint = artifact_dir / "checkpoints" / "policy.sha256"

    code.parent.mkdir(parents=True, exist_ok=True)
    code.write_text(
        """
def initialize(config):
    return {"ok": True}
""".lstrip(),
        encoding="utf-8",
    )
    write_json(config, make_config("peg_place_regrasp"))
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps({"run_id": "release_package_self_test", "method": "barrier_certified_energy_composer_v5"}) + "\n", encoding="utf-8")
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41" + (b"release package self-test rollout video bytes\n" * 40))
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint.write_text(digest("release-package-self-test-checkpoint") + "\n", encoding="utf-8")

    return {
        "code": [{"path": rel(code), "sha256": sha256(code)}],
        "configs": [{"path": rel(config), "sha256": sha256(config)}],
        "logs": [{"path": rel(log), "sha256": sha256(log)}],
        "videos": [{"path": rel(video), "sha256": sha256(video)}],
        "checkpoints": [{"path": rel(checkpoint), "sha256": sha256(checkpoint)}],
    }


def entry(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha256(path)}


def bad_release_artifacts(tmp: Path) -> dict[str, list[dict[str, str]]]:
    scaffold = EXTERNAL / "baselines" / "barrier_certified_energy_composer_v5" / "adapter_template.py"
    template_config = EXTERNAL / "config_templates" / "peg_place_regrasp.json"
    local_log = EXTERNAL / "local_dry_run" / "logs" / "peg_place_regrasp.jsonl"
    placeholder_video = EXTERNAL / "local_dry_run" / "videos" / "peg_place_regrasp" / "placeholder_not_external_evidence.mp4"
    local_checkpoint = EXTERNAL / "local_dry_run" / "checkpoints" / "barrier_certified_energy_composer_v5.sha256"
    for path in (scaffold, template_config, local_log, placeholder_video, local_checkpoint):
        if not path.exists():
            raise SystemExit(f"missing expected bad release fixture: {path}")
    internal_artifact_dir = tmp / "internal_artifacts"
    staged_log = internal_artifact_dir / "peg_place_regrasp.staging.jsonl"
    backup_log = internal_artifact_dir / "peg_place_regrasp.backup.jsonl"
    diagnostic_video = internal_artifact_dir / "peg_place_regrasp.diagnostic.mp4"
    fallback_video = internal_artifact_dir / "peg_place_regrasp.fallback.mp4"
    backup_video = internal_artifact_dir / "peg_place_regrasp.backup.mp4"
    empty_video_dir = internal_artifact_dir / "empty_video_dir"
    staged_log.parent.mkdir(parents=True, exist_ok=True)
    empty_video_dir.mkdir(parents=True, exist_ok=True)
    staged_log.write_text(json.dumps({"not_external_evidence": True, "kind": "staged_log"}) + "\n", encoding="utf-8")
    backup_log.write_text(json.dumps({"not_external_evidence": True, "kind": "backup_log"}) + "\n", encoding="utf-8")
    diagnostic_video.write_bytes((b"diagnostic release-package self-test video bytes\n" * 40))
    fallback_video.write_bytes((b"fallback release-package self-test video bytes\n" * 40))
    backup_video.write_bytes((b"backup release-package self-test video bytes\n" * 40))

    return {
        "code": [entry(scaffold)],
        "configs": [entry(template_config)],
        "logs": [entry(local_log), entry(staged_log), entry(backup_log)],
        "videos": [entry(placeholder_video), entry(diagnostic_video), entry(fallback_video), entry(backup_video), entry(empty_video_dir)],
        "checkpoints": [entry(local_checkpoint)],
    }


def manifest(release_artifacts: dict[str, list[dict[str, str]]], *, mark_local: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": "paper119_external_manifest_v1",
        "code_commit": "release-package-self-test",
        "skill_library_hash": digest("release-package-self-test-skill-library"),
        "release_artifacts": release_artifacts,
    }
    if mark_local:
        payload["local_dry_run_only"] = True
        payload["not_external_evidence"] = True
    return payload


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Release Package Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic release package ready: `{str(payload['synthetic_release_package_ready']).lower()}`.",
        "",
        "This self-test builds temporary manifest-declared release artifacts and exercises the external release-package hash gate directly. It proves complete synthetic artifacts can pass, missing manifests fail, local-dry-run/template/scaffold/placeholder artifacts plus staged/backup/diagnostic/fallback log-video artifacts, empty video directories, and non-MP4-like video artifacts are rejected as evidence, and the real release-package audit report is not overwritten.",
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

    with tempfile.TemporaryDirectory(prefix="paper119_release_package_selftest_", dir=TMP_ROOT) as tmp_name:
        tmp = Path(tmp_name)
        complete_manifest = tmp / "manifest_complete.json"
        bad_manifest = tmp / "manifest_bad.json"
        missing_manifest = tmp / "manifest_missing.json"

        write_json(complete_manifest, manifest(write_complete_artifacts(tmp)))
        write_json(bad_manifest, manifest(bad_release_artifacts(tmp), mark_local=True))

        complete_audit = release_audit.build_payload(complete_manifest)
        bad_audit = release_audit.build_payload(bad_manifest)
        missing_audit = release_audit.build_payload(missing_manifest)

    report_after = file_digest(REAL_REPORT)
    bad_blockers = "\n".join(bad_audit.get("blocking_missing", []))

    add_check(
        checks,
        "synthetic_release_package_passes",
        complete_audit.get("release_package_ready") is True
        and complete_audit.get("not_external_evidence") is False
        and all(int(complete_audit.get("artifact_counts", {}).get(kind, 0) or 0) >= 1 for kind in release_audit.ARTIFACT_TYPES)
        and not complete_audit.get("blocking_missing"),
        f"ready={complete_audit.get('release_package_ready')!r}, counts={complete_audit.get('artifact_counts')!r}",
    )
    add_check(
        checks,
        "missing_manifest_fails_release_readiness",
        missing_audit.get("release_package_ready") is False
        and missing_audit.get("not_external_evidence") is True
        and "manifest.json has not been written" in "\n".join(missing_audit.get("blocking_missing", [])),
        f"ready={missing_audit.get('release_package_ready')!r}, blockers={missing_audit.get('blocking_missing')!r}",
    )
    add_check(
        checks,
        "bad_artifacts_rejected_as_release_evidence",
        bad_audit.get("release_package_ready") is False
        and all(
            fragment in bad_blockers
            for fragment in (
                "local_dry_run artifact cannot be release evidence",
                "config template artifact cannot be release evidence",
                "adapter scaffold/template cannot be release evidence",
                "logs artifact contains forbidden non-evidence fragment",
                "videos artifact contains forbidden non-evidence fragment",
                "staging",
                "backup",
                "diagnostic",
                "fallback",
                "video directory contains no MP4 files",
                "manifest is marked local_dry_run_only/not_external_evidence",
            )
        ),
        f"blocking_fragments_present=True, blockers={len(bad_audit.get('blocking_missing', []))}",
    )
    add_check(
        checks,
        "release_hashes_are_recomputed",
        all(report.get("actual_sha256") and report.get("actual_sha256") == report.get("declared_sha256") for report in complete_audit.get("entry_reports", [])),
        f"entries={len(complete_audit.get('entry_reports', []))}",
    )
    add_check(
        checks,
        "real_release_package_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_release_package_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_release_package_ready": complete_audit.get("release_package_ready") is True,
        "bad_release_package_ready": bad_audit.get("release_package_ready") is True,
        "missing_manifest_ready": missing_audit.get("release_package_ready") is True,
        "real_release_package_report_before": report_before,
        "real_release_package_report_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External release package self-test: "
        f"{'PASS' if passed else 'FAIL'}; synthetic_release_package_ready={payload['synthetic_release_package_ready']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
