from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_config_manifest_packet as config_packet


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_config_manifest_packet_self_test.json"
OUT_MD = REAL_RESULTS / "external_config_manifest_packet_self_test.md"
VERSION = "external_config_manifest_packet_self_test_v1"

REAL_OUTPUTS = [
    REAL_EXTERNAL / "config_manifest_packet.json",
    REAL_EXTERNAL / "config_manifest_packet.md",
    REAL_EXTERNAL / "config_manifest_work_orders.csv",
    REAL_RESULTS / "external_config_manifest_audit.json",
    REAL_RESULTS / "external_config_manifest_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_EXTERNAL / "config_schema_v1.json",
    REAL_EXTERNAL / "manifest_template.json",
    REAL_RESULTS / "external_config_materialization_plan.json",
    REAL_RESULTS / "external_config_template_audit.json",
    REAL_RESULTS / "external_config_evidence_audit.json",
    REAL_RESULTS / "external_collection_readiness_audit.json",
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
        raise AssertionError(f"missing config-manifest self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))
    shutil.copytree(REAL_EXTERNAL / "configs", root / "external_validation" / "configs")


def patch_config_packet(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": config_packet.ROOT,
        "EXTERNAL": config_packet.EXTERNAL,
        "CONFIG_DIR": config_packet.CONFIG_DIR,
        "RESULTS": config_packet.RESULTS,
        "PACKET_JSON": config_packet.PACKET_JSON,
        "PACKET_MD": config_packet.PACKET_MD,
        "WORK_ORDERS_CSV": config_packet.WORK_ORDERS_CSV,
        "AUDIT_JSON": config_packet.AUDIT_JSON,
        "AUDIT_MD": config_packet.AUDIT_MD,
    }
    config_packet.ROOT = root
    config_packet.EXTERNAL = external
    config_packet.CONFIG_DIR = external / "configs"
    config_packet.RESULTS = results
    config_packet.PACKET_JSON = external / "config_manifest_packet.json"
    config_packet.PACKET_MD = external / "config_manifest_packet.md"
    config_packet.WORK_ORDERS_CSV = external / "config_manifest_work_orders.csv"
    config_packet.AUDIT_JSON = results / "external_config_manifest_audit.json"
    config_packet.AUDIT_MD = results / "external_config_manifest_audit.md"
    return old


def restore_config_packet(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(config_packet, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_config_packet(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = config_packet.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_config_packet(old)
    packet_payload = read_json(root / "external_validation" / "config_manifest_packet.json")
    audit_payload = read_json(root / "results" / "external_config_manifest_audit.json")
    return int(status), packet_payload, audit_payload, buffer.getvalue()


def load_audit_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "external_validation" / "config_schema_v1.json"),
        read_json(root / "results" / "external_config_materialization_plan.json"),
        read_json(root / "results" / "external_config_template_audit.json"),
        read_json(root / "results" / "external_config_evidence_audit.json"),
        read_json(root / "results" / "external_collection_readiness_audit.json"),
        read_json(root / "external_validation" / "manifest_template.json"),
    )


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    packet_payload = read_json(root / "external_validation" / "config_manifest_packet.json")
    mutator(root, packet_payload)
    old = patch_config_packet(root)
    try:
        schema, materialization, template_audit, evidence_audit, collection, manifest_template = load_audit_inputs(root)
        return config_packet.audit_packet(
            packet_payload,
            schema,
            materialization,
            template_audit,
            evidence_audit,
            collection,
            manifest_template,
        )
    finally:
        restore_config_packet(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_config_manifest_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, packet_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, packet_payload, audit_payload
        return status, packet_payload, run_audit_case(root, mutator)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_task_work_order(_root: Path, payload: dict[str, Any]) -> None:
    payload["work_orders"] = [
        order for order in payload.get("work_orders", []) or [] if not str(order.get("id", "")).startswith("declare_")
    ]


def promote_packet_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_config_evidence_ready"] = True
    payload["manifest_declared_config_ready"] = True
    payload["manifest_written"] = True


def enable_materialization_write(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_config_materialization_plan.json"
    materialization = read_json(path)
    materialization["write_enabled"] = True
    write_json(path, materialization)


def shrink_template_audit(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_config_template_audit.json"
    audit = read_json(path)
    audit["config_count"] = 1
    write_json(path, audit)


def promote_strict_config_evidence(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_config_evidence_audit.json"
    audit = read_json(path)
    audit["passed"] = True
    for check in audit.get("checks", []) or []:
        if check.get("name") == "manifest_exists":
            check["passed"] = True
    write_json(path, audit)


def remove_manifest_task(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "manifest_template.json"
    manifest = read_json(path)
    manifest["tasks"] = manifest.get("tasks", [])[1:]
    write_json(path, manifest)


def corrupt_prepared_config_hash(_root: Path, payload: dict[str, Any]) -> None:
    payload["task_config_records"][0]["sha256"] = ""


def fail_prepared_config_validation(_root: Path, payload: dict[str, Any]) -> None:
    payload["task_config_records"][0]["strict_validation_passed_if_manifest_declared"] = False
    payload["task_config_records"][0]["strict_validation_errors"] = ["synthetic self-test validation failure"]


def drop_strict_config_command(_root: Path, payload: dict[str, Any]) -> None:
    payload["strict_acceptance_commands"] = [
        command for command in payload.get("strict_acceptance_commands", []) or [] if "validate_external_configs.py" not in command
    ]


def write_real_manifest_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def drift_manifest_paths(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "manifest_template.json"
    manifest = read_json(path)
    manifest["tasks"][0]["config_path"] = "external_validation/configs/synthetic_wrong_path.json"
    write_json(path, manifest)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Config Manifest Packet Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict config evidence ready: `false`.",
        f"Temporary packet ready: `{str(payload['temporary_packet_ready']).lower()}`.",
        f"Missing task work orders rejected: `{str(payload['missing_task_work_orders_rejected']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Materialization write drift rejected: `{str(payload['materialization_write_drift_rejected']).lower()}`.",
        f"Template audit shrink rejected: `{str(payload['template_audit_shrink_rejected']).lower()}`.",
        f"Strict config evidence promotion rejected: `{str(payload['strict_config_evidence_promotion_rejected']).lower()}`.",
        f"Manifest task omission rejected: `{str(payload['manifest_task_omission_rejected']).lower()}`.",
        f"Prepared config hash drift rejected: `{str(payload['prepared_config_hash_drift_rejected']).lower()}`.",
        f"Prepared config validation drift rejected: `{str(payload['prepared_config_validation_drift_rejected']).lower()}`.",
        f"Strict command drift rejected: `{str(payload['strict_command_drift_rejected']).lower()}`.",
        f"Real manifest write rejected: `{str(payload['real_manifest_write_rejected']).lower()}`.",
        f"Manifest path drift rejected: `{str(payload['manifest_path_drift_rejected']).lower()}`.",
        f"Real config manifest outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds the config manifest packet in temporary copied workspaces and mutates only those fixtures. It proves the packet remains non-evidence and rejects missing task config work orders, premature strict config evidence, accidental materialization writes, shrunken template coverage, strict evidence promotion, omitted manifest tasks, stale prepared-config hashes, failed prepared-config validation, strict-command drift, real manifest writes, and manifest path drift without touching real config-manifest outputs.",
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

    status, packet_payload, audit_payload = run_case()
    temporary_packet_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("config_manifest_packet_ready") is True
        and audit_payload.get("strict_config_evidence_ready") is False
        and audit_payload.get("manifest_declared_config_ready") is False
        and int(packet_payload.get("manifest_task_count", 0) or 0) >= 4
        and int(packet_payload.get("prepared_config_count", 0) or 0) >= 4
        and check_named(audit_payload, "prepared_config_files_have_hashes") is True
        and check_named(audit_payload, "collection_readiness_preserves_config_boundary") is True
    )
    add_check(
        checks,
        "temporary_config_manifest_packet_ready_but_non_evidence",
        temporary_packet_ready,
        (
            f"status={status}, passed={audit_payload.get('passed')!r}, "
            f"tasks={packet_payload.get('manifest_task_count')!r}, configs={packet_payload.get('prepared_config_count')!r}"
        ),
    )

    _, _, missing_orders = run_case(remove_task_work_order)
    missing_task_work_orders_rejected = (
        missing_orders.get("passed") is False
        and check_named(missing_orders, "work_orders_cover_config_to_manifest_path") is False
    )
    add_check(checks, "missing_task_work_orders_rejected", missing_task_work_orders_rejected, f"work_order_check={check_named(missing_orders, 'work_orders_cover_config_to_manifest_path')}")

    _, _, promoted_packet = run_case(promote_packet_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_packet.get("passed") is False
        and check_named(promoted_packet, "packet_is_non_evidence_and_fail_closed") is False
    )
    add_check(checks, "premature_evidence_promotion_rejected", premature_evidence_promotion_rejected, f"non_evidence_check={check_named(promoted_packet, 'packet_is_non_evidence_and_fail_closed')}")

    _, _, materialization_drift = run_case(enable_materialization_write)
    materialization_write_drift_rejected = (
        materialization_drift.get("passed") is False
        and check_named(materialization_drift, "materialization_plan_ready_but_not_evidence") is False
    )
    add_check(checks, "materialization_write_drift_rejected", materialization_write_drift_rejected, f"materialization_check={check_named(materialization_drift, 'materialization_plan_ready_but_not_evidence')}")

    _, _, template_drift = run_case(shrink_template_audit)
    template_audit_shrink_rejected = (
        template_drift.get("passed") is False
        and check_named(template_drift, "template_audit_passes") is False
    )
    add_check(checks, "template_audit_shrink_rejected", template_audit_shrink_rejected, f"template_check={check_named(template_drift, 'template_audit_passes')}")

    _, _, strict_evidence_drift = run_case(promote_strict_config_evidence)
    strict_config_evidence_promotion_rejected = (
        strict_evidence_drift.get("passed") is False
        and check_named(strict_evidence_drift, "strict_config_evidence_still_fails_without_manifest") is False
    )
    add_check(checks, "strict_config_evidence_promotion_rejected", strict_config_evidence_promotion_rejected, f"strict_config_check={check_named(strict_evidence_drift, 'strict_config_evidence_still_fails_without_manifest')}")

    _, _, manifest_task_drift = run_case(remove_manifest_task)
    manifest_task_omission_rejected = (
        manifest_task_drift.get("passed") is False
        and check_named(manifest_task_drift, "manifest_template_declares_all_collection_tasks") is False
    )
    add_check(checks, "manifest_task_omission_rejected", manifest_task_omission_rejected, f"manifest_task_check={check_named(manifest_task_drift, 'manifest_template_declares_all_collection_tasks')}")

    _, _, hash_drift = run_case(corrupt_prepared_config_hash)
    prepared_config_hash_drift_rejected = (
        hash_drift.get("passed") is False
        and check_named(hash_drift, "prepared_config_files_have_hashes") is False
    )
    add_check(checks, "prepared_config_hash_drift_rejected", prepared_config_hash_drift_rejected, f"hash_check={check_named(hash_drift, 'prepared_config_files_have_hashes')}")

    _, _, validation_drift = run_case(fail_prepared_config_validation)
    prepared_config_validation_drift_rejected = (
        validation_drift.get("passed") is False
        and check_named(validation_drift, "prepared_configs_pass_strict_schema_if_manifest_declared") is False
    )
    add_check(checks, "prepared_config_validation_drift_rejected", prepared_config_validation_drift_rejected, f"validation_check={check_named(validation_drift, 'prepared_configs_pass_strict_schema_if_manifest_declared')}")

    _, _, command_drift = run_case(drop_strict_config_command)
    strict_command_drift_rejected = (
        command_drift.get("passed") is False
        and check_named(command_drift, "strict_commands_cover_config_manifest_release_and_evidence") is False
    )
    add_check(checks, "strict_command_drift_rejected", strict_command_drift_rejected, f"command_check={check_named(command_drift, 'strict_commands_cover_config_manifest_release_and_evidence')}")

    _, _, real_manifest_drift = run_case(write_real_manifest_in_fixture)
    real_manifest_write_rejected = (
        real_manifest_drift.get("passed") is False
        and check_named(real_manifest_drift, "collection_readiness_preserves_config_boundary") is False
    )
    add_check(checks, "real_manifest_write_rejected", real_manifest_write_rejected, f"manifest_write_check={check_named(real_manifest_drift, 'collection_readiness_preserves_config_boundary')}")

    _, _, path_drift = run_case(drift_manifest_paths)
    manifest_path_drift_rejected = (
        path_drift.get("passed") is False
        and check_named(path_drift, "manifest_template_paths_match_prepared_configs") is False
    )
    add_check(checks, "manifest_path_drift_rejected", manifest_path_drift_rejected, f"path_check={check_named(path_drift, 'manifest_template_paths_match_prepared_configs')}")

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_config_manifest_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    check_map = {check["name"]: check["passed"] for check in checks}
    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "strict_config_evidence_ready": False,
        "manifest_declared_config_ready": False,
        "temporary_packet_ready": check_map.get("temporary_config_manifest_packet_ready_but_non_evidence") is True,
        "missing_task_work_orders_rejected": check_map.get("missing_task_work_orders_rejected") is True,
        "premature_evidence_promotion_rejected": check_map.get("premature_evidence_promotion_rejected") is True,
        "materialization_write_drift_rejected": check_map.get("materialization_write_drift_rejected") is True,
        "template_audit_shrink_rejected": check_map.get("template_audit_shrink_rejected") is True,
        "strict_config_evidence_promotion_rejected": check_map.get("strict_config_evidence_promotion_rejected") is True,
        "manifest_task_omission_rejected": check_map.get("manifest_task_omission_rejected") is True,
        "prepared_config_hash_drift_rejected": check_map.get("prepared_config_hash_drift_rejected") is True,
        "prepared_config_validation_drift_rejected": check_map.get("prepared_config_validation_drift_rejected") is True,
        "strict_command_drift_rejected": check_map.get("strict_command_drift_rejected") is True,
        "real_manifest_write_rejected": check_map.get("real_manifest_write_rejected") is True,
        "manifest_path_drift_rejected": check_map.get("manifest_path_drift_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External config manifest packet self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
