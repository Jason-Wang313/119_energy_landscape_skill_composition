from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Callable

import build_external_precollection_freeze_receipt as freeze


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_precollection_freeze_receipt_self_test.json"
OUT_MD = RESULTS / "external_precollection_freeze_receipt_self_test.md"
REAL_RECEIPT = ROOT / "external_validation" / "precollection_freeze_receipt.json"
REAL_AUDIT = RESULTS / "external_precollection_freeze_receipt_audit.json"

VERSION = "external_precollection_freeze_receipt_self_test_v1"


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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def core_lock_paths(root: Path) -> list[Path]:
    external = root / "external_validation"
    results = root / "results"
    return [
        external / "blinded_operator_sheet.csv",
        external / "method_alias_map.json",
        external / "manifest_precollection_draft.json",
        external / "manifest_precollection_draft.md",
        external / "manifest_template.json",
        external / "log_schema_v1.json",
        external / "statistical_analysis_plan.json",
        external / "evidence_intake_ledger.json",
        external / "evidence_intake_ledger.md",
        external / "evidence_intake_ledger.csv",
        external / "method_manifest_cutover_checklist.csv",
        external / "method_manifest_cutover_checklist.md",
        external / "runner" / "backend_contract.py",
        external / "runner" / "real_collection_runner.py",
        results / "external_collection_readiness_audit.json",
        results / "external_fidelity_acceptance_audit.json",
        results / "fidelity_acceptance_materialization_plan.json",
        results / "external_config_manifest_audit.json",
        results / "external_method_implementation_audit.json",
        results / "external_evidence_intake_ledger_audit.json",
        results / "external_precollection_manifest_draft_audit.json",
    ]


def write_lock_file(path: Path) -> None:
    if path.suffix == ".json":
        payload: dict[str, Any] = {"self_test_path": path.name, "not_external_evidence": True}
        if path.name == "external_collection_readiness_audit.json":
            payload.update({"version": "external_collection_readiness_audit_v1", "passed": True, "collection_ready": True})
        if path.name == "external_fidelity_acceptance_audit.json":
            payload.update({"version": "external_fidelity_acceptance_audit_v1", "passed": True, "acceptance_ready": True})
        write_json(path, payload)
    elif path.suffix == ".py":
        write_text(path, "def self_test_placeholder():\n    return True\n")
    else:
        write_text(path, f"self-test lock artifact: {path.as_posix()}\n")


def write_fixture(root: Path, *, remove_core_artifact: bool = False) -> Path:
    external = root / "external_validation"
    for path in core_lock_paths(root):
        write_lock_file(path)
    if remove_core_artifact:
        target = external / "method_manifest_cutover_checklist.md"
        if target.exists():
            target.unlink()
    for task in ("peg_place_regrasp", "drawer_to_pick_transfer", "door_open_navigation", "cable_route_insert"):
        write_json(
            external / "configs" / f"{task}.json",
            {
                "version": "paper119_external_config_v1",
                "task_family": task,
                "platform_type": "high_fidelity_sim",
                "paired_reset_count": 30,
            },
        )
    write_text(external / "baselines" / "synthetic_method" / "adapter.py", "def initialize(config):\n    return config\n")
    backend = external / "runner" / "synthetic_backend.py"
    write_text(backend, "class Backend:\n    TEMPLATE_ONLY = False\n")
    return backend


def args_for_fixture(
    backend: Path | None,
    *,
    run_id: str = "precollection_freeze_self_test_run",
    unsealed_alias_map: bool = True,
    operator_ready: bool = True,
) -> argparse.Namespace:
    return argparse.Namespace(
        backend_module=str(backend) if backend is not None else "",
        run_id=run_id,
        operator_id="Synthetic Precollection Freeze Self-Test Lab" if operator_ready else "",
        collection_machine="synthetic-collection-machine" if operator_ready else "",
        date_locked="2026-06-30" if operator_ready else "",
        unsealed_alias_map=unsealed_alias_map,
    )


class PatchedFreezeBuilder:
    def __init__(self, root: Path, *, dirty_checkout: bool = False) -> None:
        self.root = root
        self.dirty_checkout = dirty_checkout
        self.originals = {
            "ROOT": freeze.ROOT,
            "EXTERNAL": freeze.EXTERNAL,
            "RESULTS": freeze.RESULTS,
            "OUT_JSON": freeze.OUT_JSON,
            "OUT_MD": freeze.OUT_MD,
            "OUT_CSV": freeze.OUT_CSV,
            "AUDIT_JSON": freeze.AUDIT_JSON,
            "AUDIT_MD": freeze.AUDIT_MD,
            "CORE_LOCK_PATHS": freeze.CORE_LOCK_PATHS,
            "run_git": freeze.run_git,
        }

    def fake_run_git(self, args: list[str]) -> str:
        if args == ["rev-parse", "HEAD"]:
            return "a" * 40
        if args == ["status", "--short"]:
            return " M synthetic_dirty_marker.py" if self.dirty_checkout else ""
        return ""

    def __enter__(self) -> None:
        external = self.root / "external_validation"
        results = self.root / "results"
        freeze.ROOT = self.root
        freeze.EXTERNAL = external
        freeze.RESULTS = results
        freeze.OUT_JSON = external / "precollection_freeze_receipt.json"
        freeze.OUT_MD = external / "precollection_freeze_receipt.md"
        freeze.OUT_CSV = external / "precollection_freeze_receipt.csv"
        freeze.AUDIT_JSON = results / "external_precollection_freeze_receipt_audit.json"
        freeze.AUDIT_MD = results / "external_precollection_freeze_receipt_audit.md"
        freeze.CORE_LOCK_PATHS = core_lock_paths(self.root)
        freeze.run_git = self.fake_run_git  # type: ignore[assignment]

    def __exit__(self, *_exc: object) -> None:
        for name, value in self.originals.items():
            setattr(freeze, name, value)


def run_fixture(
    root: Path,
    args_factory: Callable[[Path | None], argparse.Namespace],
    *,
    remove_core_artifact: bool = False,
    dirty_checkout: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    backend = write_fixture(root, remove_core_artifact=remove_core_artifact)
    args = args_factory(backend)
    with PatchedFreezeBuilder(root, dirty_checkout=dirty_checkout):
        payload = freeze.build_payload(args)
        audit = freeze.build_audit(payload)
    return payload, audit


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Precollection Freeze Receipt Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic freeze ready: `{str(payload['synthetic_freeze_ready']).lower()}`.",
        f"Missing backend rejected: `{str(payload['missing_backend_rejected']).lower()}`.",
        f"Placeholder run rejected: `{str(payload['placeholder_run_rejected']).lower()}`.",
        f"Missing lock artifact rejected: `{str(payload['missing_lock_artifact_rejected']).lower()}`.",
        f"Dirty checkout rejected: `{str(payload['dirty_checkout_rejected']).lower()}`.",
        "",
        "This self-test builds temporary precollection freeze fixtures and exercises the receipt builder directly. It proves a complete backend/config/operator/run-id/clean-checkout fixture can reach collection readiness, while missing backend selection, placeholder run identity, missing lock artifacts, and dirty checkout remain fail-closed without overwriting the real receipt or audit.",
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
    receipt_before = file_digest(REAL_RECEIPT)
    audit_before = file_digest(REAL_AUDIT)

    with tempfile.TemporaryDirectory(prefix="paper119_precollection_freeze_selftest_ready_") as tmp_name:
        ready_payload, ready_audit = run_fixture(Path(tmp_name), lambda backend: args_for_fixture(backend))

    with tempfile.TemporaryDirectory(prefix="paper119_precollection_freeze_selftest_backend_") as tmp_name:
        missing_backend_payload, missing_backend_audit = run_fixture(Path(tmp_name), lambda _backend: args_for_fixture(None))

    with tempfile.TemporaryDirectory(prefix="paper119_precollection_freeze_selftest_runid_") as tmp_name:
        placeholder_payload, placeholder_audit = run_fixture(
            Path(tmp_name),
            lambda backend: args_for_fixture(backend, run_id=freeze.PLACEHOLDER_RUN_ID, unsealed_alias_map=False),
        )

    with tempfile.TemporaryDirectory(prefix="paper119_precollection_freeze_selftest_lock_") as tmp_name:
        missing_lock_payload, missing_lock_audit = run_fixture(
            Path(tmp_name),
            lambda backend: args_for_fixture(backend),
            remove_core_artifact=True,
        )

    with tempfile.TemporaryDirectory(prefix="paper119_precollection_freeze_selftest_dirty_") as tmp_name:
        dirty_payload, dirty_audit = run_fixture(
            Path(tmp_name),
            lambda backend: args_for_fixture(backend),
            dirty_checkout=True,
        )

    receipt_after = file_digest(REAL_RECEIPT)
    audit_after = file_digest(REAL_AUDIT)
    ready_checks = {str(check.get("name")): check.get("passed") for check in ready_audit.get("checks", [])}
    missing_backend_checks = {str(check.get("name")): check.get("passed") for check in missing_backend_audit.get("checks", [])}
    placeholder_checks = {str(check.get("name")): check.get("passed") for check in placeholder_audit.get("checks", [])}
    missing_lock_checks = {str(check.get("name")): check.get("passed") for check in missing_lock_audit.get("checks", [])}

    add_check(
        checks,
        "synthetic_complete_freeze_reaches_collection_readiness",
        ready_payload.get("freeze_receipt_ready") is True
        and ready_payload.get("ready_to_collect_after_receipt") is True
        and ready_audit.get("passed") is True
        and ready_audit.get("freeze_receipt_ready") is True
        and int(ready_audit.get("locked_artifact_count", 0) or 0) >= 25
        and not ready_payload.get("missing_lock_paths"),
        (
            f"freeze_ready={ready_payload.get('freeze_receipt_ready')!r}, "
            f"ready_to_collect={ready_payload.get('ready_to_collect_after_receipt')!r}, "
            f"locked={ready_audit.get('locked_artifact_count')!r}, missing={ready_payload.get('missing_lock_paths')!r}"
        ),
    )
    add_check(
        checks,
        "synthetic_ready_checks_cover_hashes_identity_and_order",
        ready_checks.get("receipt_is_non_evidence_and_fail_closed") is True
        and ready_checks.get("core_lock_artifacts_hashed") is True
        and ready_checks.get("prepared_task_configs_hashed") is True
        and ready_checks.get("backend_module_still_operator_supplied") is True
        and ready_checks.get("run_identity_still_operator_supplied") is True
        and ready_checks.get("operator_metadata_still_required") is True
        and ready_checks.get("strict_sequence_places_receipt_before_collection") is True,
        f"ready_checks={ready_checks}",
    )
    add_check(
        checks,
        "missing_backend_selection_rejected",
        missing_backend_payload.get("freeze_receipt_ready") is False
        and missing_backend_audit.get("passed") is False
        and "selected_backend_module" in (missing_backend_payload.get("missing_lock_paths", []) or []),
        (
            f"freeze_ready={missing_backend_payload.get('freeze_receipt_ready')!r}, "
            f"missing={missing_backend_payload.get('missing_lock_paths')!r}, checks={missing_backend_checks}"
        ),
    )
    add_check(
        checks,
        "placeholder_run_identity_rejected",
        placeholder_payload.get("freeze_receipt_ready") is False
        and placeholder_audit.get("passed") is False
        and placeholder_checks.get("run_identity_still_operator_supplied") is True
        and placeholder_payload.get("unsealed_alias_map") is False,
        (
            f"freeze_ready={placeholder_payload.get('freeze_receipt_ready')!r}, "
            f"run_id={placeholder_payload.get('run_id')!r}, unsealed={placeholder_payload.get('unsealed_alias_map')!r}"
        ),
    )
    add_check(
        checks,
        "missing_lock_artifact_rejected",
        missing_lock_payload.get("freeze_receipt_ready") is False
        and missing_lock_audit.get("passed") is False
        and bool(missing_lock_payload.get("missing_lock_paths"))
        and missing_lock_checks.get("core_lock_artifacts_hashed") is False,
        f"missing={missing_lock_payload.get('missing_lock_paths')!r}, checks={missing_lock_checks}",
    )
    add_check(
        checks,
        "dirty_checkout_rejected",
        dirty_payload.get("freeze_receipt_ready") is False
        and dirty_payload.get("current_checkout", {}).get("clean_checkout") is False
        and bool(dirty_payload.get("current_checkout", {}).get("dirty_status_lines")),
        f"checkout={dirty_payload.get('current_checkout')!r}",
    )
    add_check(
        checks,
        "real_precollection_freeze_reports_not_overwritten",
        receipt_before == receipt_after and audit_before == audit_after,
        f"receipt_before={receipt_before}, receipt_after={receipt_after}, audit_before={audit_before}, audit_after={audit_after}",
    )

    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "synthetic_freeze_ready": ready_payload.get("freeze_receipt_ready") is True,
        "missing_backend_rejected": missing_backend_payload.get("freeze_receipt_ready") is False,
        "placeholder_run_rejected": placeholder_payload.get("freeze_receipt_ready") is False,
        "missing_lock_artifact_rejected": missing_lock_payload.get("freeze_receipt_ready") is False,
        "dirty_checkout_rejected": dirty_payload.get("freeze_receipt_ready") is False,
        "real_reports_untouched": receipt_before == receipt_after and audit_before == audit_after,
        "ready_summary": {
            "locked_artifact_count": ready_audit.get("locked_artifact_count"),
            "config_count": len([row for row in ready_payload.get("lock_artifacts", []) if row.get("role") == "prepared_task_config"]),
            "code_commit": ready_payload.get("current_checkout", {}).get("code_commit"),
        },
        "checks": checks,
    }
    write_report(payload)
    print(
        "External precollection freeze receipt self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"synthetic_ready={payload['synthetic_freeze_ready']}; "
        f"missing_backend_rejected={payload['missing_backend_rejected']}; "
        f"placeholder_run_rejected={payload['placeholder_run_rejected']}; "
        f"missing_lock_rejected={payload['missing_lock_artifact_rejected']}; "
        f"dirty_checkout_rejected={payload['dirty_checkout_rejected']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
