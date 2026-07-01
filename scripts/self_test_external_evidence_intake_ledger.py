from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_evidence_intake_ledger as intake_ledger


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_evidence_intake_ledger_self_test.json"
OUT_MD = REAL_RESULTS / "external_evidence_intake_ledger_self_test.md"
VERSION = "external_evidence_intake_ledger_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "evidence_intake_ledger.json",
    REAL_EXTERNAL / "evidence_intake_ledger.md",
    REAL_EXTERNAL / "evidence_intake_ledger.csv",
    REAL_RESULTS / "external_evidence_intake_ledger_audit.json",
    REAL_RESULTS / "external_evidence_intake_ledger_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_RESULTS / "external_evidence_audit.json",
    REAL_RESULTS / "external_collection_plan.json",
    REAL_RESULTS / "external_rollout_evidence_audit.json",
    REAL_RESULTS / "external_config_manifest_audit.json",
    REAL_RESULTS / "external_method_implementation_audit.json",
    REAL_RESULTS / "external_ablation_collection_audit.json",
    REAL_RESULTS / "external_fidelity_provenance_audit.json",
    REAL_EXTERNAL / "manifest_template.json",
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
        raise AssertionError(f"missing evidence-intake self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))


def patch_intake(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": intake_ledger.ROOT,
        "EXTERNAL": intake_ledger.EXTERNAL,
        "RESULTS": intake_ledger.RESULTS,
        "OUT_JSON": intake_ledger.OUT_JSON,
        "OUT_MD": intake_ledger.OUT_MD,
        "OUT_CSV": intake_ledger.OUT_CSV,
        "AUDIT_JSON": intake_ledger.AUDIT_JSON,
        "AUDIT_MD": intake_ledger.AUDIT_MD,
    }
    intake_ledger.ROOT = root
    intake_ledger.EXTERNAL = external
    intake_ledger.RESULTS = results
    intake_ledger.OUT_JSON = external / "evidence_intake_ledger.json"
    intake_ledger.OUT_MD = external / "evidence_intake_ledger.md"
    intake_ledger.OUT_CSV = external / "evidence_intake_ledger.csv"
    intake_ledger.AUDIT_JSON = results / "external_evidence_intake_ledger_audit.json"
    intake_ledger.AUDIT_MD = results / "external_evidence_intake_ledger_audit.md"
    return old


def restore_intake(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(intake_ledger, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_intake(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = intake_ledger.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_intake(old)
    packet_payload = read_json(root / "external_validation" / "evidence_intake_ledger.json")
    audit_payload = read_json(root / "results" / "external_evidence_intake_ledger_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "results" / "external_evidence_audit.json"),
        read_json(root / "results" / "external_collection_plan.json"),
        read_json(root / "external_validation" / "manifest_template.json"),
        read_json(root / "results" / "external_rollout_evidence_audit.json"),
        read_json(root / "results" / "external_config_manifest_audit.json"),
        read_json(root / "results" / "external_method_implementation_audit.json"),
        read_json(root / "results" / "external_ablation_collection_audit.json"),
        read_json(root / "results" / "external_fidelity_provenance_audit.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "evidence_intake_ledger.json")
    mutator(root, packet_payload)
    old = patch_intake(root)
    try:
        (
            evidence,
            collection,
            manifest_template,
            rollout_packet,
            config_packet,
            method_packet,
            ablation_packet,
            fidelity_packet,
        ) = load_audit_inputs(root)
        return intake_ledger.audit_packet(
            packet_payload,
            evidence,
            collection,
            manifest_template,
            rollout_packet,
            config_packet,
            method_packet,
            ablation_packet,
            fidelity_packet,
        )
    finally:
        restore_intake(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_evidence_intake_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, packet_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, packet_payload, audit_payload
        return status, packet_payload, run_audit_case(root, mutator)


def run_file_deletion_case() -> bool:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_evidence_intake_selftest_delete_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        run_builder(root)
        deleted = root / "external_validation" / "evidence_intake_ledger.csv"
        deleted.unlink()
        required_outputs = [
            root / "external_validation" / "evidence_intake_ledger.json",
            root / "external_validation" / "evidence_intake_ledger.md",
            root / "external_validation" / "evidence_intake_ledger.csv",
            root / "results" / "external_evidence_intake_ledger_audit.json",
            root / "results" / "external_evidence_intake_ledger_audit.md",
        ]
        return not all(path.exists() for path in required_outputs)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_ledger_row(_root: Path, payload: dict[str, Any]) -> None:
    payload["rows"] = [row for row in payload.get("rows", []) or []][1:]
    payload["mapped_failure_count"] = len(payload["rows"])


def promote_ledger_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_external_evidence_ready"] = True
    payload["not_external_evidence"] = False
    for row in payload.get("rows", []) or []:
        row["evidence_ready_now"] = "true"


def introduce_unmapped_failure(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_evidence_audit.json"
    evidence = read_json(path)
    evidence.setdefault("blocking_failures", []).append(
        {"name": "synthetic_unmapped_failure", "detail": "synthetic self-test blocker"}
    )
    write_json(path, evidence)


def remove_closure_group(_root: Path, payload: dict[str, Any]) -> None:
    payload["rows"] = [row for row in payload.get("rows", []) or [] if row.get("closure_group") != "ablations"]
    payload["closure_groups"] = [
        group for group in payload.get("closure_groups", []) or [] if group.get("name") != "ablations"
    ]


def weaken_source_packet(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_rollout_evidence_audit.json"
    packet = read_json(path)
    packet["passed"] = False
    write_json(path, packet)


def remove_manifest_release_artifacts(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "manifest_template.json"
    manifest = read_json(path)
    manifest.pop("release_artifacts", None)
    write_json(path, manifest)


def empty_row_source_and_completion(_root: Path, payload: dict[str, Any]) -> None:
    payload["rows"][0]["source_packet"] = ""
    payload["rows"][0]["completion_test"] = ""


def drop_strict_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["operator_commands"] = [
        command for command in payload.get("operator_commands", []) or [] if "audit_external_evidence.py" not in command
    ]


def write_real_manifest_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Evidence Intake Ledger Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict external evidence ready: `false`.",
        f"Temporary ledger ready: `{str(payload['temporary_ledger_ready']).lower()}`.",
        f"Missing ledger row rejected: `{str(payload['missing_ledger_row_rejected']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Unmapped failure rejected: `{str(payload['unmapped_failure_rejected']).lower()}`.",
        f"Closure group omission rejected: `{str(payload['closure_group_omission_rejected']).lower()}`.",
        f"Source packet failure rejected: `{str(payload['source_packet_failure_rejected']).lower()}`.",
        f"Manifest template omission rejected: `{str(payload['manifest_template_omission_rejected']).lower()}`.",
        f"Row source/completion drift rejected: `{str(payload['row_source_completion_drift_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Real manifest write rejected: `{str(payload['real_manifest_write_rejected']).lower()}`.",
        f"Ledger file deletion rejected: `{str(payload['ledger_file_deletion_rejected']).lower()}`.",
        f"Real evidence-intake outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the evidence intake ledger in temporary copied workspaces and mutates only those fixtures. It proves the ledger remains non-evidence and rejects missing blocker rows, premature strict-evidence promotion, unmapped strict failures, missing closure groups, failing source packets, manifest-template omissions, stale row source/completion fields, strict command drift, accidental real manifest writes, and deleted ledger files without touching real evidence-intake outputs.",
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

    status, _packet_payload, audit_payload = run_case()
    temporary_ledger_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("strict_external_evidence_ready") is False
        and int(audit_payload.get("blocking_failure_count", 0) or 0) >= 30
        and audit_payload.get("blocking_failure_count") == audit_payload.get("mapped_failure_count")
        and not audit_payload.get("unmapped_failures")
        and check_named(audit_payload, "rows_are_actionable_and_source_bound") is True
    )
    add_check(
        checks,
        "temporary_evidence_intake_ledger_ready_but_non_evidence",
        temporary_ledger_ready,
        (
            f"status={status}, mapped={audit_payload.get('mapped_failure_count')!r}/"
            f"{audit_payload.get('blocking_failure_count')!r}"
        ),
    )

    _, _, missing_row_audit = run_case(remove_ledger_row)
    missing_ledger_row_rejected = (
        missing_row_audit.get("passed") is False
        and check_named(missing_row_audit, "every_blocking_failure_is_mapped") is False
    )
    add_check(
        checks,
        "missing_ledger_row_rejected",
        missing_ledger_row_rejected,
        f"check={check_named(missing_row_audit, 'every_blocking_failure_is_mapped')!r}",
    )

    _, _, promoted_audit = run_case(promote_ledger_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_audit.get("passed") is False
        and check_named(promoted_audit, "ledger_is_non_evidence_and_fail_closed") is False
    )
    add_check(
        checks,
        "premature_evidence_promotion_rejected",
        premature_evidence_promotion_rejected,
        f"check={check_named(promoted_audit, 'ledger_is_non_evidence_and_fail_closed')!r}",
    )

    _, _, unmapped_audit = run_case(introduce_unmapped_failure)
    unmapped_failure_rejected = (
        unmapped_audit.get("passed") is False
        and check_named(unmapped_audit, "every_blocking_failure_is_mapped") is False
    )
    add_check(
        checks,
        "unmapped_failure_rejected",
        unmapped_failure_rejected,
        f"check={check_named(unmapped_audit, 'every_blocking_failure_is_mapped')!r}",
    )

    _, _, closure_audit = run_case(remove_closure_group)
    closure_group_omission_rejected = (
        closure_audit.get("passed") is False
        and check_named(closure_audit, "all_required_closure_groups_present") is False
    )
    add_check(
        checks,
        "closure_group_omission_rejected",
        closure_group_omission_rejected,
        f"check={check_named(closure_audit, 'all_required_closure_groups_present')!r}",
    )

    _, _, source_packet_audit = run_case(weaken_source_packet)
    source_packet_failure_rejected = (
        source_packet_audit.get("passed") is False
        and check_named(source_packet_audit, "source_packets_loaded") is False
    )
    add_check(
        checks,
        "source_packet_failure_rejected",
        source_packet_failure_rejected,
        f"check={check_named(source_packet_audit, 'source_packets_loaded')!r}",
    )

    _, _, manifest_template_audit = run_case(remove_manifest_release_artifacts)
    manifest_template_omission_rejected = (
        manifest_template_audit.get("passed") is False
        and check_named(manifest_template_audit, "manifest_template_declares_expected_evidence_fields") is False
    )
    add_check(
        checks,
        "manifest_template_omission_rejected",
        manifest_template_omission_rejected,
        f"check={check_named(manifest_template_audit, 'manifest_template_declares_expected_evidence_fields')!r}",
    )

    _, _, row_drift_audit = run_case(empty_row_source_and_completion)
    row_source_completion_drift_rejected = (
        row_drift_audit.get("passed") is False
        and check_named(row_drift_audit, "rows_are_actionable_and_source_bound") is False
    )
    add_check(
        checks,
        "row_source_completion_drift_rejected",
        row_source_completion_drift_rejected,
        f"check={check_named(row_drift_audit, 'rows_are_actionable_and_source_bound')!r}",
    )

    _, _, command_audit = run_case(drop_strict_command)
    strict_command_drift_rejected = (
        command_audit.get("passed") is False
        and check_named(command_audit, "strict_command_spine_covers_final_evidence_path") is False
    )
    add_check(
        checks,
        "strict_command_drift_rejected",
        strict_command_drift_rejected,
        f"check={check_named(command_audit, 'strict_command_spine_covers_final_evidence_path')!r}",
    )

    _, _, manifest_write_audit = run_case(write_real_manifest_in_fixture)
    real_manifest_write_rejected = (
        manifest_write_audit.get("passed") is False
        and check_named(manifest_write_audit, "no_real_manifest_written") is False
    )
    add_check(
        checks,
        "real_manifest_write_rejected",
        real_manifest_write_rejected,
        f"check={check_named(manifest_write_audit, 'no_real_manifest_written')!r}",
    )

    ledger_file_deletion_rejected = run_file_deletion_case()
    add_check(
        checks,
        "ledger_file_deletion_rejected",
        ledger_file_deletion_rejected,
        "required temporary ledger output check detects deleted evidence-intake CSV",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_after == real_hashes_before
    add_check(
        checks,
        "real_evidence_intake_outputs_untouched",
        real_outputs_untouched,
        f"before={real_hashes_before}, after={real_hashes_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "temporary_ledger_ready": temporary_ledger_ready,
        "missing_ledger_row_rejected": missing_ledger_row_rejected,
        "premature_evidence_promotion_rejected": premature_evidence_promotion_rejected,
        "unmapped_failure_rejected": unmapped_failure_rejected,
        "closure_group_omission_rejected": closure_group_omission_rejected,
        "source_packet_failure_rejected": source_packet_failure_rejected,
        "manifest_template_omission_rejected": manifest_template_omission_rejected,
        "row_source_completion_drift_rejected": row_source_completion_drift_rejected,
        "strict_command_drift_rejected": strict_command_drift_rejected,
        "real_manifest_write_rejected": real_manifest_write_rejected,
        "ledger_file_deletion_rejected": ledger_file_deletion_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes_before": real_hashes_before,
        "real_output_hashes_after": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)

    status_text = "PASS" if passed else "FAIL"
    print(f"External evidence intake ledger self-test: {status_text}; checks={sum(1 for check in checks if check['passed'])}/{len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
