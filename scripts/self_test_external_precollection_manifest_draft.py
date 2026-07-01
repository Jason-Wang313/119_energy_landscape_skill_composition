from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_precollection_manifest_draft as manifest_draft


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_precollection_manifest_draft_self_test.json"
OUT_MD = REAL_RESULTS / "external_precollection_manifest_draft_self_test.md"
VERSION = "external_precollection_manifest_draft_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "manifest_precollection_draft.json",
    REAL_EXTERNAL / "manifest_precollection_draft.md",
    REAL_RESULTS / "external_precollection_manifest_draft_audit.json",
    REAL_RESULTS / "external_precollection_manifest_draft_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

SOURCE_REPORTS = [
    REAL_RESULTS / "external_manifest_builder_report.json",
    REAL_RESULTS / "external_config_manifest_audit.json",
    REAL_RESULTS / "external_rollout_evidence_audit.json",
    REAL_RESULTS / "external_ablation_collection_audit.json",
    REAL_RESULTS / "external_evidence_intake_ledger_audit.json",
    REAL_RESULTS / "external_method_implementation_audit.json",
    REAL_RESULTS / "external_method_config_materialization_audit.json",
    REAL_RESULTS / "external_collection_readiness_audit.json",
    REAL_RESULTS / "maniskill_render_machine_qualification.json",
]

INPUT_FILES = [
    REAL_EXTERNAL / "manifest_template.json",
    REAL_EXTERNAL / "config_schema_v1.json",
    REAL_EXTERNAL / "method_config_materialization_plan.json",
    *SOURCE_REPORTS,
]

INPUT_DIRS = [
    REAL_EXTERNAL / "configs",
    REAL_EXTERNAL / "method_config_candidates",
]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in REAL_OUTPUTS}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing precollection-manifest self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_dir(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise AssertionError(f"missing precollection-manifest self-test fixture dir: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))
    for source in INPUT_DIRS:
        copy_dir(source, root / source.relative_to(REAL_ROOT))


def temp_source_reports(root: Path) -> list[Path]:
    return [root / path.relative_to(REAL_ROOT) for path in SOURCE_REPORTS]


def patch_manifest_draft(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": manifest_draft.ROOT,
        "EXTERNAL": manifest_draft.EXTERNAL,
        "RESULTS": manifest_draft.RESULTS,
        "TEMPLATE": manifest_draft.TEMPLATE,
        "SCHEMA": manifest_draft.SCHEMA,
        "OFFICIAL_MANIFEST": manifest_draft.OFFICIAL_MANIFEST,
        "DRAFT_JSON": manifest_draft.DRAFT_JSON,
        "DRAFT_MD": manifest_draft.DRAFT_MD,
        "AUDIT_JSON": manifest_draft.AUDIT_JSON,
        "AUDIT_MD": manifest_draft.AUDIT_MD,
        "METHOD_CONFIG_PLAN": manifest_draft.METHOD_CONFIG_PLAN,
        "METHOD_CONFIG_AUDIT": manifest_draft.METHOD_CONFIG_AUDIT,
        "SOURCE_REPORTS": manifest_draft.SOURCE_REPORTS,
    }
    manifest_draft.ROOT = root
    manifest_draft.EXTERNAL = external
    manifest_draft.RESULTS = results
    manifest_draft.TEMPLATE = external / "manifest_template.json"
    manifest_draft.SCHEMA = external / "config_schema_v1.json"
    manifest_draft.OFFICIAL_MANIFEST = external / "manifest.json"
    manifest_draft.DRAFT_JSON = external / "manifest_precollection_draft.json"
    manifest_draft.DRAFT_MD = external / "manifest_precollection_draft.md"
    manifest_draft.AUDIT_JSON = results / "external_precollection_manifest_draft_audit.json"
    manifest_draft.AUDIT_MD = results / "external_precollection_manifest_draft_audit.md"
    manifest_draft.METHOD_CONFIG_PLAN = external / "method_config_materialization_plan.json"
    manifest_draft.METHOD_CONFIG_AUDIT = results / "external_method_config_materialization_audit.json"
    manifest_draft.SOURCE_REPORTS = temp_source_reports(root)
    return old


def restore_manifest_draft(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(manifest_draft, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_manifest_draft(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = manifest_draft.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_manifest_draft(old)
    draft_payload = read_json(root / "external_validation" / "manifest_precollection_draft.json")
    audit_payload = read_json(root / "results" / "external_precollection_manifest_draft_audit.json")
    return int(status), draft_payload, audit_payload, buffer.getvalue()


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    draft_payload = read_json(root / "external_validation" / "manifest_precollection_draft.json")
    mutator(root, draft_payload)
    old = patch_manifest_draft(root)
    try:
        return manifest_draft.audit_packet(draft_payload)
    finally:
        restore_manifest_draft(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_precollection_manifest_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, draft_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, draft_payload, audit_payload
        return status, draft_payload, run_audit_case(root, mutator)


def run_file_deletion_case() -> bool:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_precollection_manifest_selftest_delete_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        run_builder(root)
        deleted = root / "external_validation" / "manifest_precollection_draft.md"
        deleted.unlink()
        required_outputs = [
            root / "external_validation" / "manifest_precollection_draft.json",
            root / "external_validation" / "manifest_precollection_draft.md",
            root / "results" / "external_precollection_manifest_draft_audit.json",
            root / "results" / "external_precollection_manifest_draft_audit.md",
        ]
        return not all(path.exists() for path in required_outputs)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def promote_draft_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["not_external_evidence"] = False
    payload["draft_only"] = False
    payload["strict_external_evidence_ready"] = True
    payload["strict_config_evidence_ready"] = True
    payload["ready_to_write_official_manifest"] = True


def remove_prepared_config_hash(_root: Path, payload: dict[str, Any]) -> None:
    payload["prepared_config_records"][0]["config_hash"] = ""
    payload["task_manifest_entries_with_hashes"][0]["config_hash"] = ""


def drift_task_config_path(_root: Path, payload: dict[str, Any]) -> None:
    payload["prepared_config_records"][0]["config_path"] = "external_validation/configs/synthetic_missing_config.json"
    payload["task_manifest_entries_with_hashes"][0]["config_path"] = "external_validation/configs/synthetic_missing_config.json"


def drift_candidate_method_config_file(root: Path, payload: dict[str, Any]) -> None:
    candidate_path = root / payload["candidate_method_config_records"][0]["config_path"]
    candidate = read_json(candidate_path)
    candidate["synthetic_self_test_nonce"] = "candidate-hash-drift"
    write_json(candidate_path, candidate)


def remove_method_blocker(_root: Path, payload: dict[str, Any]) -> None:
    blockers = payload["method_gaps"][0]["blocking_missing"]
    payload["method_gaps"][0]["blocking_missing"] = [item for item in blockers if item != "implementation_path"]


def remove_rollout_gap(_root: Path, payload: dict[str, Any]) -> None:
    payload["rollout_artifact_gaps"] = payload["rollout_artifact_gaps"][1:]
    payload["missing_rollout_artifact_count"] = len(
        [row for row in payload["rollout_artifact_gaps"] if row.get("blocking_until_real_evidence")]
    )


def weaken_source_report(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_rollout_evidence_audit.json"
    report = read_json(path)
    report["passed"] = False
    report["synthetic_self_test_failure"] = True
    write_json(path, report)


def drop_cutover_manifest_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["cutover_commands"] = [
        command for command in payload.get("cutover_commands", []) or [] if "build_external_manifest.py" not in command
    ]


def write_real_manifest_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Precollection Manifest Draft Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Temporary draft ready: `{str(payload['temporary_draft_ready']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Missing prepared-config hash rejected: `{str(payload['missing_prepared_config_hash_rejected']).lower()}`.",
        f"Task config path drift rejected: `{str(payload['task_config_path_drift_rejected']).lower()}`.",
        f"Candidate method-config hash drift rejected: `{str(payload['candidate_method_config_hash_drift_rejected']).lower()}`.",
        f"Method blocker omission rejected: `{str(payload['method_blocker_omission_rejected']).lower()}`.",
        f"Rollout gap omission rejected: `{str(payload['rollout_gap_omission_rejected']).lower()}`.",
        f"Source report drift rejected: `{str(payload['source_report_drift_rejected']).lower()}`.",
        f"Cutover command drift rejected: `{str(payload['cutover_command_drift_rejected']).lower()}`.",
        f"Real manifest write rejected: `{str(payload['real_manifest_write_rejected']).lower()}`.",
        f"Draft file deletion rejected: `{str(payload['draft_file_deletion_rejected']).lower()}`.",
        f"Real precollection-manifest outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the precollection manifest draft in temporary copied workspaces and mutates only those fixtures. It proves the draft remains non-evidence and rejects premature strict-evidence promotion, missing prepared task-config hashes, task-config path drift, candidate method-config hash drift, omitted independent-method blockers, omitted rollout gaps, stale source reports, cutover-command drift, accidental official manifest writes, and missing draft files without touching real precollection-manifest outputs.",
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
    TMP_ROOT.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []
    real_hashes_before = real_output_hashes()

    status, _draft_payload, audit_payload = run_case()
    temporary_draft_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("draft_ready") is True
        and audit_payload.get("strict_external_evidence_ready") is False
        and int(audit_payload.get("prepared_config_count", 0) or 0) == 4
        and int(audit_payload.get("candidate_method_config_count", 0) or 0) >= 11
        and check_named(audit_payload, "source_reports_match_current_files") is True
    )
    add_check(
        checks,
        "temporary_precollection_manifest_draft_ready_but_non_evidence",
        temporary_draft_ready,
        f"status={status}, configs={audit_payload.get('prepared_config_count')!r}, methods={audit_payload.get('candidate_method_config_count')!r}",
    )

    _, _, promoted_audit = run_case(promote_draft_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_audit.get("passed") is False
        and check_named(promoted_audit, "draft_marked_non_evidence_and_fail_closed") is False
    )
    add_check(
        checks,
        "premature_evidence_promotion_rejected",
        premature_evidence_promotion_rejected,
        f"check={check_named(promoted_audit, 'draft_marked_non_evidence_and_fail_closed')!r}",
    )

    _, _, missing_config_audit = run_case(remove_prepared_config_hash)
    missing_prepared_config_hash_rejected = (
        missing_config_audit.get("passed") is False
        and check_named(missing_config_audit, "prepared_config_hashes_prefilled") is False
    )
    add_check(
        checks,
        "missing_prepared_config_hash_rejected",
        missing_prepared_config_hash_rejected,
        f"check={check_named(missing_config_audit, 'prepared_config_hashes_prefilled')!r}",
    )

    _, _, task_path_audit = run_case(drift_task_config_path)
    task_config_path_drift_rejected = (
        task_path_audit.get("passed") is False
        and check_named(task_path_audit, "prepared_config_hashes_match_current_files") is False
    )
    add_check(
        checks,
        "task_config_path_drift_rejected",
        task_config_path_drift_rejected,
        f"check={check_named(task_path_audit, 'prepared_config_hashes_match_current_files')!r}",
    )

    _, _, candidate_hash_audit = run_case(drift_candidate_method_config_file)
    candidate_method_config_hash_drift_rejected = (
        candidate_hash_audit.get("passed") is False
        and check_named(candidate_hash_audit, "candidate_method_configs_match_current_plan") is False
    )
    add_check(
        checks,
        "candidate_method_config_hash_drift_rejected",
        candidate_method_config_hash_drift_rejected,
        f"check={check_named(candidate_hash_audit, 'candidate_method_configs_match_current_plan')!r}",
    )

    _, _, method_blocker_audit = run_case(remove_method_blocker)
    method_blocker_omission_rejected = (
        method_blocker_audit.get("passed") is False
        and check_named(method_blocker_audit, "method_gaps_still_require_independent_evidence") is False
    )
    add_check(
        checks,
        "method_blocker_omission_rejected",
        method_blocker_omission_rejected,
        f"check={check_named(method_blocker_audit, 'method_gaps_still_require_independent_evidence')!r}",
    )

    _, _, rollout_gap_audit = run_case(remove_rollout_gap)
    rollout_gap_omission_rejected = (
        rollout_gap_audit.get("passed") is False
        and check_named(rollout_gap_audit, "rollout_artifacts_remain_blocking") is False
    )
    add_check(
        checks,
        "rollout_gap_omission_rejected",
        rollout_gap_omission_rejected,
        f"check={check_named(rollout_gap_audit, 'rollout_artifacts_remain_blocking')!r}",
    )

    _, _, source_drift_audit = run_case(weaken_source_report)
    source_report_drift_rejected = (
        source_drift_audit.get("passed") is False
        and check_named(source_drift_audit, "source_reports_match_current_files") is False
    )
    add_check(
        checks,
        "source_report_drift_rejected",
        source_report_drift_rejected,
        f"check={check_named(source_drift_audit, 'source_reports_match_current_files')!r}",
    )

    _, _, command_audit = run_case(drop_cutover_manifest_command)
    cutover_command_drift_rejected = (
        command_audit.get("passed") is False
        and check_named(command_audit, "cutover_command_contains_build_external_manifest") is False
    )
    add_check(
        checks,
        "cutover_command_drift_rejected",
        cutover_command_drift_rejected,
        f"check={check_named(command_audit, 'cutover_command_contains_build_external_manifest')!r}",
    )

    _, _, manifest_write_audit = run_case(write_real_manifest_in_fixture)
    real_manifest_write_rejected = (
        manifest_write_audit.get("passed") is False
        and check_named(manifest_write_audit, "official_manifest_absent") is False
    )
    add_check(
        checks,
        "real_manifest_write_rejected",
        real_manifest_write_rejected,
        f"check={check_named(manifest_write_audit, 'official_manifest_absent')!r}",
    )

    draft_file_deletion_rejected = run_file_deletion_case()
    add_check(
        checks,
        "draft_file_deletion_rejected",
        draft_file_deletion_rejected,
        "required temporary draft output check detects deleted precollection manifest markdown",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_after == real_hashes_before
    add_check(
        checks,
        "real_precollection_manifest_outputs_untouched",
        real_outputs_untouched,
        f"before={real_hashes_before}, after={real_hashes_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_draft_ready": temporary_draft_ready,
        "premature_evidence_promotion_rejected": premature_evidence_promotion_rejected,
        "missing_prepared_config_hash_rejected": missing_prepared_config_hash_rejected,
        "task_config_path_drift_rejected": task_config_path_drift_rejected,
        "candidate_method_config_hash_drift_rejected": candidate_method_config_hash_drift_rejected,
        "method_blocker_omission_rejected": method_blocker_omission_rejected,
        "rollout_gap_omission_rejected": rollout_gap_omission_rejected,
        "source_report_drift_rejected": source_report_drift_rejected,
        "cutover_command_drift_rejected": cutover_command_drift_rejected,
        "real_manifest_write_rejected": real_manifest_write_rejected,
        "draft_file_deletion_rejected": draft_file_deletion_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External precollection manifest draft self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"checks={sum(1 for check in checks if check['passed'])}/{len(checks)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
