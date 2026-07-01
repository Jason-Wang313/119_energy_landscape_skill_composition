from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import audit_external_evidence_preflight as preflight


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"

OUT_JSON = REAL_RESULTS / "external_evidence_preflight_self_test.json"
OUT_MD = REAL_RESULTS / "external_evidence_preflight_self_test.md"
VERSION = "external_evidence_preflight_self_test_v1"

REAL_OUTPUTS = [
    REAL_RESULTS / "external_evidence_preflight.json",
    REAL_RESULTS / "external_evidence_preflight.md",
    REAL_EXTERNAL / "manifest.json",
]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_upper(path: Path) -> str:
    value = sha256_file(path)
    if value is None:
        raise FileNotFoundError(path)
    return value.upper()


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in REAL_OUTPUTS}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def copy_template(root: Path) -> None:
    target = root / "external_validation" / "manifest_template.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_EXTERNAL / "manifest_template.json", target)


def write_synthetic_mp4(path: Path, *, placeholder: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if placeholder:
        path.write_bytes(b"placeholder")
        return
    header = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41"
    payload = b"\x00\x00\x08\x00mdat" + (b"external evidence preflight self-test frame bytes\n" * 64)
    path.write_bytes(header + payload)


def write_log(path: Path, rows: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for index in range(rows):
            handle.write(json.dumps({"episode_index": index, "synthetic_preflight_self_test": True}) + "\n")


def write_implementation(path: Path, method: str, *, scaffold: bool = False) -> None:
    path.mkdir(parents=True, exist_ok=True)
    body = (
        "def run(*_args, **_kwargs):\n"
        "    raise NotImplementedError('scaffold fixture')\n"
        if scaffold
        else f"def run(*_args, **_kwargs):\n    return {{'method': {method!r}, 'status': 'ok'}}\n"
    )
    (path / "implementation.py").write_text(body, encoding="utf-8")


def make_config(task: str, *, template: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": "external_config_evidence_v1",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "PreflightSelfTestHighFidelitySim-v1",
        "paired_reset_count": 30,
        "fixed_risk_budget": 0.15,
    }
    if template:
        payload["not_external_evidence"] = True
    return payload


def make_complete_fixture(root: Path) -> None:
    copy_template(root)
    external = root / "external_validation"
    manifest = read_json(REAL_EXTERNAL / "manifest_template.json")
    manifest["code_commit"] = "preflight-self-test-commit"
    manifest["skill_library_hash"] = hashlib.sha256(b"preflight self-test skill library").hexdigest()
    manifest["shared_skill_library"] = True
    manifest["same_initial_states"] = True
    manifest["same_observation_interface"] = True
    manifest["same_compute_budget"] = True
    manifest["paired_resets"] = True

    method_count = len(manifest["methods"])
    release_configs: list[str] = []
    release_logs: list[str] = []
    release_videos: list[str] = []
    release_checkpoints: list[str] = []

    for task in manifest["tasks"]:
        task_family = task["task_family"]
        task["platform_name"] = "PreflightSelfTestHighFidelitySim-v1"
        task["episodes_per_method"] = 30

        config_path = external / "configs" / f"{task_family}.json"
        write_json(config_path, make_config(task_family))
        task["config_path"] = rel(root, config_path)
        task["config_hash"] = sha256_upper(config_path)
        release_configs.append(task["config_path"])

        log_path = external / "logs" / f"{task_family}.jsonl"
        write_log(log_path, rows=30 * method_count)
        task["log_jsonl"] = rel(root, log_path)
        release_logs.append(task["log_jsonl"])

        video_dir = external / "videos" / task_family
        video_path = video_dir / "rollout_000.mp4"
        write_synthetic_mp4(video_path)
        task["video_dir"] = rel(root, video_dir)
        release_videos.append(rel(root, video_path))

    for method in manifest["methods"]:
        name = method["name"]
        if name == "oracle_basin_composer":
            method["implementation"] = "post_hoc_upper_bound"
            continue
        impl_dir = external / "implementations" / name
        write_implementation(impl_dir, name)
        method["implementation"] = rel(root, impl_dir)

        checkpoint = external / "checkpoints" / f"{name}.json"
        write_json(checkpoint, {"method": name, "synthetic_preflight_self_test": True})
        method["checkpoint_or_config_path"] = rel(root, checkpoint)
        method["checkpoint_or_config_hash"] = sha256_upper(checkpoint)
        release_checkpoints.append(method["checkpoint_or_config_path"])

    manifest["release_artifacts"] = {
        "code": ["scripts/audit_external_evidence_preflight.py"],
        "configs": release_configs,
        "logs": release_logs,
        "videos": release_videos,
        "checkpoints": release_checkpoints,
    }
    write_json(external / "manifest.json", manifest)


def patch_preflight(root: Path) -> dict[str, Any]:
    results = root / "results"
    external = root / "external_validation"
    old = {
        "ROOT": preflight.ROOT,
        "EXTERNAL": preflight.EXTERNAL,
        "RESULTS": preflight.RESULTS,
        "DEFAULT_MANIFEST": preflight.DEFAULT_MANIFEST,
        "DEFAULT_TEMPLATE": preflight.DEFAULT_TEMPLATE,
        "OUT_JSON": preflight.OUT_JSON,
        "OUT_MD": preflight.OUT_MD,
    }
    preflight.ROOT = root
    preflight.EXTERNAL = external
    preflight.RESULTS = results
    preflight.DEFAULT_MANIFEST = external / "manifest.json"
    preflight.DEFAULT_TEMPLATE = external / "manifest_template.json"
    preflight.OUT_JSON = results / "external_evidence_preflight.json"
    preflight.OUT_MD = results / "external_evidence_preflight.md"
    return old


def restore_preflight(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(preflight, name, value)


def run_preflight(root: Path) -> tuple[int, dict[str, Any], str]:
    old = patch_preflight(root)
    old_argv = sys.argv[:]
    buffer = io.StringIO()
    try:
        sys.argv = ["audit_external_evidence_preflight.py"]
        with redirect_stdout(buffer):
            status = preflight.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        sys.argv = old_argv
        restore_preflight(old)
    payload_path = root / "results" / "external_evidence_preflight.json"
    payload = read_json(payload_path) if payload_path.exists() else {}
    return int(status), payload, buffer.getvalue()


def run_case(mutator: Callable[[Path], None] | None = None, *, complete: bool) -> tuple[int, dict[str, Any], str]:
    with tempfile.TemporaryDirectory(prefix="paper119_preflight_selftest_") as temp_name:
        root = Path(temp_name)
        if complete:
            make_complete_fixture(root)
        else:
            copy_template(root)
        if mutator is not None:
            mutator(root)
        return run_preflight(root)


def remove_records(root: Path) -> None:
    log_path = root / "external_validation" / "logs" / "peg_place_regrasp.jsonl"
    write_log(log_path, rows=1)


def replace_with_placeholder_video(root: Path) -> None:
    video_dir = root / "external_validation" / "videos" / "peg_place_regrasp"
    for child in video_dir.glob("*"):
        child.unlink()
    write_synthetic_mp4(video_dir / "placeholder_not_external_evidence.mp4", placeholder=True)


def mark_config_as_template(root: Path) -> None:
    manifest_path = root / "external_validation" / "manifest.json"
    manifest = read_json(manifest_path)
    config_path = root / manifest["tasks"][0]["config_path"]
    config = read_json(config_path)
    config["not_external_evidence"] = True
    write_json(config_path, config)
    manifest["tasks"][0]["config_hash"] = sha256_upper(config_path)
    write_json(manifest_path, manifest)


def make_method_scaffold(root: Path) -> None:
    manifest_path = root / "external_validation" / "manifest.json"
    manifest = read_json(manifest_path)
    for method in manifest["methods"]:
        if method["name"] != "oracle_basin_composer":
            impl_dir = root / method["implementation"]
            write_implementation(impl_dir, method["name"], scaffold=True)
            break


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def blocker_contains(payload: dict[str, Any], fragment: str) -> bool:
    return any(fragment in str(item) for item in payload.get("blocking_missing", []))


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Evidence Preflight Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Tracked no-manifest fail-closed: `{str(payload['tracked_no_manifest_fail_closed']).lower()}`.",
        f"Temporary complete fixture ready: `{str(payload['temporary_complete_fixture_ready']).lower()}`.",
        f"Incomplete log rejected: `{str(payload['incomplete_log_rejected']).lower()}`.",
        f"Placeholder video rejected: `{str(payload['placeholder_video_rejected']).lower()}`.",
        f"Template config rejected: `{str(payload['template_config_rejected']).lower()}`.",
        f"Scaffold implementation rejected: `{str(payload['scaffold_implementation_rejected']).lower()}`.",
        f"Real preflight outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This is a tooling-only mutation test. It runs the external evidence preflight in temporary workspaces, proves the current no-real-manifest route stays in collection mode, proves a complete temporary 1,440-record package can reach the strict-audit handoff state, and proves incomplete logs, placeholder videos, template configs, and scaffold implementations fail closed without touching the real preflight reports or real manifest.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    REAL_RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []
    real_hashes_before = real_output_hashes()

    no_manifest_status, no_manifest_payload, _ = run_case(complete=False)
    tracked_no_manifest_fail_closed = (
        no_manifest_status == 0
        and no_manifest_payload.get("evidence_ready") is False
        and no_manifest_payload.get("readiness_state") == "COLLECT_EXTERNAL_EVIDENCE"
        and no_manifest_payload.get("real_manifest_exists") is False
        and int(no_manifest_payload.get("expected_records", 0) or 0) >= 1440
        and int(no_manifest_payload.get("observed_records", -1)) == 0
        and blocker_contains(no_manifest_payload, "external_validation/manifest.json")
    )
    add_check(
        checks,
        "tracked_no_manifest_preflight_fails_closed",
        tracked_no_manifest_fail_closed,
        f"status={no_manifest_status}, state={no_manifest_payload.get('readiness_state')!r}, missing={no_manifest_payload.get('blocking_missing_count')!r}",
    )

    complete_status, complete_payload, _ = run_case(complete=True)
    temporary_complete_fixture_ready = (
        complete_status == 0
        and complete_payload.get("evidence_ready") is True
        and complete_payload.get("readiness_state") == "READY_FOR_STRICT_AUDIT"
        and complete_payload.get("real_manifest_exists") is True
        and int(complete_payload.get("expected_records", 0) or 0) >= 1440
        and complete_payload.get("observed_records") == complete_payload.get("expected_records")
        and int(complete_payload.get("blocking_missing_count", -1)) == 0
        and int(complete_payload.get("task_count", 0) or 0) >= 4
        and int(complete_payload.get("method_count", 0) or 0) >= 12
    )
    add_check(
        checks,
        "temporary_complete_preflight_reaches_strict_audit_handoff",
        temporary_complete_fixture_ready,
        f"status={complete_status}, state={complete_payload.get('readiness_state')!r}, records={complete_payload.get('observed_records')!r}/{complete_payload.get('expected_records')!r}",
    )

    incomplete_status, incomplete_payload, _ = run_case(remove_records, complete=True)
    incomplete_log_rejected = (
        incomplete_status == 0
        and incomplete_payload.get("evidence_ready") is False
        and blocker_contains(incomplete_payload, "log_jsonl has 1 records")
    )
    add_check(
        checks,
        "incomplete_log_records_rejected",
        incomplete_log_rejected,
        f"status={incomplete_status}, missing={incomplete_payload.get('blocking_missing_count')!r}",
    )

    placeholder_status, placeholder_payload, _ = run_case(replace_with_placeholder_video, complete=True)
    placeholder_video_rejected = (
        placeholder_status == 0
        and placeholder_payload.get("evidence_ready") is False
        and blocker_contains(placeholder_payload, "video_dir has no non-placeholder rollout videos")
    )
    add_check(
        checks,
        "placeholder_video_rejected",
        placeholder_video_rejected,
        f"status={placeholder_status}, missing={placeholder_payload.get('blocking_missing_count')!r}",
    )

    template_status, template_payload, _ = run_case(mark_config_as_template, complete=True)
    template_config_rejected = (
        template_status == 0
        and template_payload.get("evidence_ready") is False
        and blocker_contains(template_payload, "config_path still appears to be a non-evidence template")
    )
    add_check(
        checks,
        "template_config_rejected",
        template_config_rejected,
        f"status={template_status}, missing={template_payload.get('blocking_missing_count')!r}",
    )

    scaffold_status, scaffold_payload, _ = run_case(make_method_scaffold, complete=True)
    scaffold_implementation_rejected = (
        scaffold_status == 0
        and scaffold_payload.get("evidence_ready") is False
        and blocker_contains(scaffold_payload, "implementation appears to be a scaffold/template")
    )
    add_check(
        checks,
        "scaffold_implementation_rejected",
        scaffold_implementation_rejected,
        f"status={scaffold_status}, missing={scaffold_payload.get('blocking_missing_count')!r}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(checks, "real_preflight_outputs_untouched", real_outputs_untouched, f"before={real_hashes_before}, after={real_hashes_after}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "tracked_no_manifest_fail_closed": tracked_no_manifest_fail_closed,
        "temporary_complete_fixture_ready": temporary_complete_fixture_ready,
        "incomplete_log_rejected": incomplete_log_rejected,
        "placeholder_video_rejected": placeholder_video_rejected,
        "template_config_rejected": template_config_rejected,
        "scaffold_implementation_rejected": scaffold_implementation_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External evidence preflight self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"tracked_no_manifest_fail_closed={tracked_no_manifest_fail_closed}; "
        f"temporary_complete_fixture_ready={temporary_complete_fixture_ready}; "
        f"incomplete_log_rejected={incomplete_log_rejected}; "
        f"placeholder_video_rejected={placeholder_video_rejected}; "
        f"template_config_rejected={template_config_rejected}; "
        f"scaffold_implementation_rejected={scaffold_implementation_rejected}; "
        f"real_outputs_untouched={real_outputs_untouched}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
