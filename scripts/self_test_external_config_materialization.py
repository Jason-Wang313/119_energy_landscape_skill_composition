from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import materialize_external_configs as config_materializer


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_config_materialization_self_test.json"
OUT_MD = REAL_RESULTS / "external_config_materialization_self_test.md"
VERSION = "external_config_materialization_self_test_v1"

INPUT_FILES = [
    REAL_EXTERNAL / "config_schema_v1.json",
    REAL_EXTERNAL / "maniskill_task_bindings.json",
]
INPUT_DIRS = [
    REAL_EXTERNAL / "config_templates",
]

REAL_OUTPUT_ROOTS = [
    REAL_RESULTS / "external_config_materialization_plan.json",
    REAL_RESULTS / "external_config_materialization_plan.md",
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


def real_output_paths() -> list[Path]:
    return [
        *REAL_OUTPUT_ROOTS,
        *sorted((REAL_EXTERNAL / "configs").glob("*.json")),
    ]


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in real_output_paths()}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing config materialization self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_dir(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise AssertionError(f"missing config materialization self-test fixture dir: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))
    for source in INPUT_DIRS:
        copy_dir(source, root / source.relative_to(REAL_ROOT))
    (root / "external_validation" / "configs").mkdir(parents=True, exist_ok=True)
    (root / "results").mkdir(parents=True, exist_ok=True)


def patch_materializer(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": config_materializer.ROOT,
        "EXTERNAL": config_materializer.EXTERNAL,
        "RESULTS": config_materializer.RESULTS,
        "SCHEMA": config_materializer.SCHEMA,
        "TEMPLATE_DIR": config_materializer.TEMPLATE_DIR,
        "OUTPUT_DIR": config_materializer.OUTPUT_DIR,
        "DEFAULT_BINDINGS": config_materializer.DEFAULT_BINDINGS,
        "OUT_JSON": config_materializer.OUT_JSON,
        "OUT_MD": config_materializer.OUT_MD,
    }
    config_materializer.ROOT = root
    config_materializer.EXTERNAL = external
    config_materializer.RESULTS = results
    config_materializer.SCHEMA = external / "config_schema_v1.json"
    config_materializer.TEMPLATE_DIR = external / "config_templates"
    config_materializer.OUTPUT_DIR = external / "configs"
    config_materializer.DEFAULT_BINDINGS = external / "maniskill_task_bindings.json"
    config_materializer.OUT_JSON = results / "external_config_materialization_plan.json"
    config_materializer.OUT_MD = results / "external_config_materialization_plan.md"
    return old


def restore_materializer(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(config_materializer, name, value)


def make_args(root: Path, **overrides: Any) -> argparse.Namespace:
    external = root / "external_validation"
    values = {
        "schema": external / "config_schema_v1.json",
        "template_dir": external / "config_templates",
        "output_dir": external / "configs",
        "task_binding_file": external / "maniskill_task_bindings.json",
        "platform_type": "high_fidelity_sim",
        "platform_name": "DRY_RUN_PLATFORM_NOT_EVIDENCE",
        "wall_clock_seconds": 30,
        "simulator_query_budget": 100,
        "paired_reset_count": 30,
        "write": False,
        "force": False,
        "confirm_real_platform": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def run_build(root: Path, **overrides: Any) -> tuple[int, dict[str, Any], str]:
    old = patch_materializer(root)
    try:
        try:
            payload = config_materializer.build_payload(make_args(root, **overrides))
            return 0 if payload.get("passed") else 1, payload, ""
        except SystemExit as exc:
            status = int(exc.code or 1) if isinstance(exc.code, int) else 1
            return status, {}, str(exc)
    finally:
        restore_materializer(old)


def run_case(
    mutator: Callable[[Path], None] | None = None,
    **overrides: Any,
) -> tuple[int, dict[str, Any], str, list[dict[str, Any]]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_config_materialization_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        if mutator is not None:
            mutator(root)
        status, payload, message = run_build(root, **overrides)
        written = sorted((root / "external_validation" / "configs").glob("*.json"))
        written_payloads = [read_json(path) for path in written]
        return status, payload, message, written_payloads


def run_overwrite_case() -> bool:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_config_materialization_overwrite_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, payload, _message = run_build(
            root,
            platform_name="ManiSkill-SAPIEN-accepted-fixture",
            wall_clock_seconds=120,
            simulator_query_budget=4096,
            write=True,
            confirm_real_platform=True,
        )
        if status != 0 or int(payload.get("task_count", 0) or 0) < 4:
            return False
        second_status, _second_payload, second_message = run_build(
            root,
            platform_name="ManiSkill-SAPIEN-accepted-fixture",
            wall_clock_seconds=120,
            simulator_query_budget=4096,
            write=True,
            confirm_real_platform=True,
        )
        return second_status != 0 and "refusing to overwrite existing config" in second_message


def remove_task_binding_file(root: Path) -> None:
    (root / "external_validation" / "maniskill_task_bindings.json").unlink()


def inject_template_placeholder(root: Path) -> None:
    template = next((root / "external_validation" / "config_templates").glob("*.json"))
    payload = read_json(template)
    payload["synthetic_bad_placeholder"] = "PLACEHOLDER_SHOULD_BLOCK_CONFIRMED_WRITE"
    write_json(template, payload)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def written_configs_are_valid(configs: list[dict[str, Any]]) -> bool:
    if len(configs) < 4:
        return False
    schema = read_json(REAL_EXTERNAL / "config_schema_v1.json")
    for payload in configs:
        if config_materializer.validate_payload(payload, schema, for_write=True):
            return False
        if payload.get("not_external_evidence") is not False:
            return False
        if payload.get("platform_name") != "ManiSkill-SAPIEN-accepted-fixture":
            return False
        binding = payload.get("backend_task_binding", {}) or {}
        if binding.get("accepted_task_binding_ready") is not False:
            return False
        if binding.get("strict_external_evidence_ready") is not False:
            return False
    return True


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Config Materialization Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict config evidence ready: `false`.",
        f"Temporary plan ready: `{str(payload['temporary_plan_ready']).lower()}`.",
        f"Confirmed write fixture ready: `{str(payload['confirmed_write_fixture_ready']).lower()}`.",
        f"Write without confirmation rejected: `{str(payload['write_without_confirm_rejected']).lower()}`.",
        f"Placeholder platform write rejected: `{str(payload['placeholder_platform_write_rejected']).lower()}`.",
        f"Template token write rejected: `{str(payload['template_token_write_rejected']).lower()}`.",
        f"Missing task binding rejected: `{str(payload['missing_task_binding_rejected']).lower()}`.",
        f"Overwrite without force rejected: `{str(payload['overwrite_without_force_rejected']).lower()}`.",
        f"Real config materialization outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test exercises the guarded task-config materializer in temporary copied workspaces only. It proves the default plan writes no configs, a confirmed fixture write can materialize schema-valid task configs, and missing confirmation, placeholder platform names, template tokens, missing task bindings, and overwrite attempts fail closed without touching real prepared configs or materialization reports.",
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

    status, plan_payload, _message, default_written = run_case()
    temporary_plan_ready = (
        status == 0
        and plan_payload.get("version") == "external_config_materialization_plan_v1"
        and plan_payload.get("passed") is True
        and plan_payload.get("not_external_evidence") is True
        and plan_payload.get("write_enabled") is False
        and plan_payload.get("materialization_ready_for_operator") is True
        and plan_payload.get("strict_config_evidence_ready") is False
        and int(plan_payload.get("task_count", 0) or 0) >= 4
        and not default_written
    )
    add_check(
        checks,
        "temporary_config_materialization_plan_ready_but_non_evidence",
        temporary_plan_ready,
        f"status={status}, task_count={plan_payload.get('task_count')!r}, written={len(default_written)}",
    )

    status, write_payload, _message, written = run_case(
        platform_name="ManiSkill-SAPIEN-accepted-fixture",
        wall_clock_seconds=120,
        simulator_query_budget=4096,
        write=True,
        confirm_real_platform=True,
    )
    confirmed_write_fixture_ready = (
        status == 0
        and write_payload.get("passed") is True
        and write_payload.get("write_enabled") is True
        and int(write_payload.get("task_count", 0) or 0) >= 4
        and len(write_payload.get("files_written", []) or []) >= 4
        and written_configs_are_valid(written)
    )
    add_check(
        checks,
        "confirmed_temp_write_materializes_schema_valid_configs",
        confirmed_write_fixture_ready,
        f"status={status}, files_written={len(write_payload.get('files_written', []) or [])}, temp_files={len(written)}",
    )

    status, _payload, message, written = run_case(
        platform_name="ManiSkill-SAPIEN-accepted-fixture",
        wall_clock_seconds=120,
        simulator_query_budget=4096,
        write=True,
        confirm_real_platform=False,
    )
    write_without_confirm_rejected = status != 0 and not written and "refusing to write external configs" in message
    add_check(checks, "write_without_confirmation_rejected", write_without_confirm_rejected, f"status={status}, written={len(written)}")

    status, _payload, message, written = run_case(write=True, confirm_real_platform=True)
    placeholder_platform_write_rejected = status != 0 and not written and "refusing to write external configs" in message
    add_check(checks, "placeholder_platform_write_rejected", placeholder_platform_write_rejected, f"status={status}, written={len(written)}")

    status, _payload, message, written = run_case(
        inject_template_placeholder,
        platform_name="ManiSkill-SAPIEN-accepted-fixture",
        wall_clock_seconds=120,
        simulator_query_budget=4096,
        write=True,
        confirm_real_platform=True,
    )
    template_token_write_rejected = status != 0 and not written and "refusing to write external configs" in message
    add_check(checks, "template_token_write_rejected", template_token_write_rejected, f"status={status}, written={len(written)}")

    status, missing_binding_payload, _message, _written = run_case(remove_task_binding_file)
    missing_binding_checks = {check.get("name"): check.get("passed") for check in missing_binding_payload.get("checks", []) or []}
    missing_task_binding_rejected = status != 0 and missing_binding_checks.get("task_binding_file_ready") is False
    add_check(
        checks,
        "missing_task_binding_file_rejected",
        missing_task_binding_rejected,
        f"status={status}, task_binding_check={missing_binding_checks.get('task_binding_file_ready')!r}",
    )

    overwrite_without_force_rejected = run_overwrite_case()
    add_check(
        checks,
        "overwrite_without_force_rejected",
        overwrite_without_force_rejected,
        "second confirmed fixture write without --force is rejected",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_after == real_hashes_before
    changed_real_outputs = [
        path for path, before_hash in real_hashes_before.items() if real_hashes_after.get(path) != before_hash
    ]
    add_check(
        checks,
        "real_config_materialization_outputs_untouched",
        real_outputs_untouched,
        f"tracked={len(real_hashes_before)}, changed={changed_real_outputs}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_config_evidence_ready": False,
        "temporary_plan_ready": temporary_plan_ready,
        "confirmed_write_fixture_ready": confirmed_write_fixture_ready,
        "write_without_confirm_rejected": write_without_confirm_rejected,
        "placeholder_platform_write_rejected": placeholder_platform_write_rejected,
        "template_token_write_rejected": template_token_write_rejected,
        "missing_task_binding_rejected": missing_task_binding_rejected,
        "overwrite_without_force_rejected": overwrite_without_force_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External config materialization self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"checks={sum(1 for check in checks if check['passed'])}/{len(checks)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
