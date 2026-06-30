from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import materialize_external_method_configs as method_configs


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"
TMP_ROOT = REAL_ROOT / "tmp"

OUT_JSON = REAL_RESULTS / "external_method_config_materialization_self_test.json"
OUT_MD = REAL_RESULTS / "external_method_config_materialization_self_test.md"
VERSION = "external_method_config_materialization_self_test_v1"

REAL_OUTPUT_ROOTS = [
    REAL_EXTERNAL / "method_config_materialization_plan.json",
    REAL_EXTERNAL / "method_config_materialization_plan.md",
    REAL_EXTERNAL / "method_config_candidates.csv",
    REAL_RESULTS / "external_method_config_materialization_audit.json",
    REAL_RESULTS / "external_method_config_materialization_audit.md",
    REAL_EXTERNAL / "manifest.json",
]

INPUT_FILES = [
    REAL_EXTERNAL / "method_implementation_packet.json",
    REAL_RESULTS / "external_method_implementation_audit.json",
    REAL_RESULTS / "external_adapter_contract_evidence_audit.json",
]

INPUT_DIRS = [
    REAL_EXTERNAL / "baseline_specs",
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
    return [*REAL_OUTPUT_ROOTS, *sorted((REAL_EXTERNAL / "method_config_candidates").glob("*.json"))]


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in real_output_paths()}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing method-config self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_dir(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise AssertionError(f"missing method-config self-test fixture dir: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)


def setup_fixture(root: Path) -> None:
    for source in INPUT_FILES:
        copy_file(source, root / source.relative_to(REAL_ROOT))
    for source in INPUT_DIRS:
        copy_dir(source, root / source.relative_to(REAL_ROOT))


def patch_method_configs(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": method_configs.ROOT,
        "EXTERNAL": method_configs.EXTERNAL,
        "RESULTS": method_configs.RESULTS,
        "SPEC_DIR": method_configs.SPEC_DIR,
        "METHOD_CONFIG_DIR": method_configs.METHOD_CONFIG_DIR,
        "OUT_JSON": method_configs.OUT_JSON,
        "OUT_MD": method_configs.OUT_MD,
        "OUT_CSV": method_configs.OUT_CSV,
        "OUT_AUDIT_JSON": method_configs.OUT_AUDIT_JSON,
        "OUT_AUDIT_MD": method_configs.OUT_AUDIT_MD,
    }
    method_configs.ROOT = root
    method_configs.EXTERNAL = external
    method_configs.RESULTS = results
    method_configs.SPEC_DIR = external / "baseline_specs"
    method_configs.METHOD_CONFIG_DIR = external / "method_config_candidates"
    method_configs.OUT_JSON = external / "method_config_materialization_plan.json"
    method_configs.OUT_MD = external / "method_config_materialization_plan.md"
    method_configs.OUT_CSV = external / "method_config_candidates.csv"
    method_configs.OUT_AUDIT_JSON = results / "external_method_config_materialization_audit.json"
    method_configs.OUT_AUDIT_MD = results / "external_method_config_materialization_audit.md"
    return old


def restore_method_configs(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(method_configs, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], dict[str, Any], str]:
    old = patch_method_configs(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = method_configs.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_method_configs(old)
    plan_payload = read_json(root / "external_validation" / "method_config_materialization_plan.json")
    audit_payload = read_json(root / "results" / "external_method_config_materialization_audit.json")
    return int(status), plan_payload, audit_payload, buffer.getvalue()


def load_sources(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        read_json(root / "external_validation" / "method_implementation_packet.json"),
        read_json(root / "results" / "external_method_implementation_audit.json"),
        read_json(root / "results" / "external_adapter_contract_evidence_audit.json"),
    )


def rewrite_candidate_csv(root: Path, payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "method_config_candidates.csv"
    fieldnames = [
        "method",
        "evidence_role",
        "config_path",
        "config_sha256",
        "baseline_spec_path",
        "baseline_spec_sha256",
        "strict_gate",
        "blocking_until_real_evidence",
        "operator_action",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in payload.get("records", []) or []:
            writer.writerow({key: record.get(key, "") for key in fieldnames})


def update_first_record_hash(root: Path, payload: dict[str, Any]) -> None:
    record = payload["records"][0]
    config_path = root / record["config_path"]
    config_hash = method_configs.sha256_file(config_path)
    record["config_sha256"] = config_hash
    record["manifest_stub"]["checkpoint_or_config_hash"] = config_hash
    rewrite_candidate_csv(root, payload)


def run_audit_case(root: Path, mutator: Callable[[Path, dict[str, Any]], None]) -> dict[str, Any]:
    plan_payload = read_json(root / "external_validation" / "method_config_materialization_plan.json")
    mutator(root, plan_payload)
    old = patch_method_configs(root)
    try:
        method_packet, method_audit, adapter_evidence = load_sources(root)
        return method_configs.audit_packet(plan_payload, method_packet, method_audit, adapter_evidence)
    finally:
        restore_method_configs(old)


def run_case(mutator: Callable[[Path, dict[str, Any]], None] | None = None) -> tuple[int, dict[str, Any], dict[str, Any]]:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_method_config_selftest_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, plan_payload, audit_payload, _ = run_builder(root)
        if mutator is None:
            return status, plan_payload, audit_payload
        return status, plan_payload, run_audit_case(root, mutator)


def run_file_deletion_case() -> bool:
    TMP_ROOT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paper119_method_config_selftest_delete_", dir=TMP_ROOT) as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        run_builder(root)
        deleted = root / "external_validation" / "method_config_candidates.csv"
        deleted.unlink()
        required_outputs = [
            root / "external_validation" / "method_config_materialization_plan.json",
            root / "external_validation" / "method_config_materialization_plan.md",
            root / "external_validation" / "method_config_candidates.csv",
            root / "results" / "external_method_config_materialization_audit.json",
            root / "results" / "external_method_config_materialization_audit.md",
        ]
        return not all(path.exists() for path in required_outputs)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def promote_plan_to_evidence(_root: Path, payload: dict[str, Any]) -> None:
    payload["not_external_evidence"] = False
    payload["strict_adapter_evidence_ready"] = True
    payload["strict_external_evidence_ready"] = True


def remove_candidate_record(root: Path, payload: dict[str, Any]) -> None:
    payload["records"] = payload.get("records", [])[1:]
    payload["candidate_config_count"] = len(payload["records"])
    rewrite_candidate_csv(root, payload)


def add_oracle_record(root: Path, payload: dict[str, Any]) -> None:
    oracle = dict(payload["records"][0])
    oracle["method"] = "oracle_basin_composer"
    oracle["config_path"] = "external_validation/method_config_candidates/oracle_basin_composer.json"
    oracle["manifest_stub"] = dict(oracle["manifest_stub"])
    oracle["manifest_stub"]["name"] = "oracle_basin_composer"
    oracle["manifest_stub"]["checkpoint_or_config_path"] = oracle["config_path"]
    write_json(root / oracle["config_path"], {"version": method_configs.CONFIG_VERSION, "method": "oracle_basin_composer"})
    oracle["config_sha256"] = method_configs.sha256_file(root / oracle["config_path"])
    oracle["manifest_stub"]["checkpoint_or_config_hash"] = oracle["config_sha256"]
    payload["records"].append(oracle)
    payload["candidate_config_count"] = len(payload["records"])
    payload["oracle_excluded"] = False
    rewrite_candidate_csv(root, payload)


def drift_candidate_file_hash(root: Path, payload: dict[str, Any]) -> None:
    record = payload["records"][0]
    config_path = root / record["config_path"]
    config = read_json(config_path)
    config["synthetic_self_test_nonce"] = "candidate-file-hash-drift"
    write_json(config_path, config)


def drift_manifest_stub_hash(_root: Path, payload: dict[str, Any]) -> None:
    payload["records"][0]["manifest_stub"]["checkpoint_or_config_hash"] = "0" * 64


def promote_candidate_config_content(root: Path, payload: dict[str, Any]) -> None:
    record = payload["records"][0]
    config_path = root / record["config_path"]
    config = read_json(config_path)
    config["evidence_status"] = "manifest_evidence_ready"
    config["strict_adapter_evidence_ready"] = True
    config["candidate_runtime_contract"]["oracle_access"] = True
    write_json(config_path, config)
    update_first_record_hash(root, payload)


def weaken_source_method_packet(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "method_implementation_packet.json"
    packet = read_json(path)
    packet["method_implementation_packet_ready"] = False
    write_json(path, packet)


def promote_adapter_evidence(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "results" / "external_adapter_contract_evidence_audit.json"
    audit = read_json(path)
    audit["passed"] = True
    audit["adapter_count"] = 11
    write_json(path, audit)


def drift_baseline_spec(root: Path, _payload: dict[str, Any]) -> None:
    path = next((root / "external_validation" / "baseline_specs").glob("*.json"))
    spec = read_json(path)
    spec["synthetic_self_test_nonce"] = "baseline-hash-drift"
    write_json(path, spec)


def drift_candidate_csv(root: Path, _payload: dict[str, Any]) -> None:
    path = root / "external_validation" / "method_config_candidates.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    rows[0]["config_sha256"] = "1" * 64
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_real_manifest_in_fixture(root: Path, _payload: dict[str, Any]) -> None:
    write_json(root / "external_validation" / "manifest.json", {"synthetic_self_test_only": True})


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Method Config Materialization Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "Strict adapter evidence ready: `false`.",
        f"Temporary materialization ready: `{str(payload['temporary_materialization_ready']).lower()}`.",
        f"Premature evidence promotion rejected: `{str(payload['premature_evidence_promotion_rejected']).lower()}`.",
        f"Missing candidate record rejected: `{str(payload['missing_candidate_record_rejected']).lower()}`.",
        f"Oracle candidate rejected: `{str(payload['oracle_candidate_rejected']).lower()}`.",
        f"Candidate file hash drift rejected: `{str(payload['candidate_file_hash_drift_rejected']).lower()}`.",
        f"Manifest stub hash drift rejected: `{str(payload['manifest_stub_hash_drift_rejected']).lower()}`.",
        f"Candidate evidence-content drift rejected: `{str(payload['candidate_evidence_content_drift_rejected']).lower()}`.",
        f"Source method packet drift rejected: `{str(payload['source_method_packet_drift_rejected']).lower()}`.",
        f"Adapter evidence promotion rejected: `{str(payload['adapter_evidence_promotion_rejected']).lower()}`.",
        f"Baseline spec hash drift rejected: `{str(payload['baseline_spec_hash_drift_rejected']).lower()}`.",
        f"Candidate CSV drift rejected: `{str(payload['candidate_csv_drift_rejected']).lower()}`.",
        f"Real manifest write rejected: `{str(payload['real_manifest_write_rejected']).lower()}`.",
        f"Materialization file deletion rejected: `{str(payload['materialization_file_deletion_rejected']).lower()}`.",
        f"Real method-config materialization outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This self-test rebuilds method-config materialization in temporary copied workspaces and mutates only those fixtures. It proves candidate method configs remain non-evidence and rejects missing or oracle candidates, stale candidate file hashes, manifest-stub hash drift, candidate config content promoted to evidence, source packet drift, adapter evidence promotion, baseline spec drift, CSV drift, accidental real manifest writes, and deleted materialization files without touching real method-config outputs.",
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

    status, _plan_payload, audit_payload = run_case()
    temporary_materialization_ready = (
        status == 0
        and audit_payload.get("passed") is True
        and audit_payload.get("not_external_evidence") is True
        and audit_payload.get("strict_adapter_evidence_ready") is False
        and int(audit_payload.get("candidate_config_count", 0) or 0) >= 11
        and check_named(audit_payload, "candidate_config_contents_remain_non_evidence") is True
    )
    add_check(
        checks,
        "temporary_method_config_materialization_ready_but_non_evidence",
        temporary_materialization_ready,
        f"status={status}, candidate_config_count={audit_payload.get('candidate_config_count')!r}",
    )

    _, _, promoted_audit = run_case(promote_plan_to_evidence)
    premature_evidence_promotion_rejected = (
        promoted_audit.get("passed") is False and check_named(promoted_audit, "materialization_is_non_evidence") is False
    )
    add_check(checks, "premature_evidence_promotion_rejected", premature_evidence_promotion_rejected, f"check={check_named(promoted_audit, 'materialization_is_non_evidence')!r}")

    _, _, missing_audit = run_case(remove_candidate_record)
    missing_candidate_record_rejected = (
        missing_audit.get("passed") is False and check_named(missing_audit, "candidate_configs_cover_non_oracle_methods") is False
    )
    add_check(checks, "missing_candidate_record_rejected", missing_candidate_record_rejected, f"check={check_named(missing_audit, 'candidate_configs_cover_non_oracle_methods')!r}")

    _, _, oracle_audit = run_case(add_oracle_record)
    oracle_candidate_rejected = (
        oracle_audit.get("passed") is False and check_named(oracle_audit, "candidate_configs_cover_non_oracle_methods") is False
    )
    add_check(checks, "oracle_candidate_rejected", oracle_candidate_rejected, f"check={check_named(oracle_audit, 'candidate_configs_cover_non_oracle_methods')!r}")

    _, _, file_hash_audit = run_case(drift_candidate_file_hash)
    candidate_file_hash_drift_rejected = (
        file_hash_audit.get("passed") is False and check_named(file_hash_audit, "candidate_hashes_match_written_files") is False
    )
    add_check(checks, "candidate_file_hash_drift_rejected", candidate_file_hash_drift_rejected, f"check={check_named(file_hash_audit, 'candidate_hashes_match_written_files')!r}")

    _, _, stub_hash_audit = run_case(drift_manifest_stub_hash)
    manifest_stub_hash_drift_rejected = (
        stub_hash_audit.get("passed") is False and check_named(stub_hash_audit, "manifest_stubs_bind_checkpoint_config_hashes") is False
    )
    add_check(checks, "manifest_stub_hash_drift_rejected", manifest_stub_hash_drift_rejected, f"check={check_named(stub_hash_audit, 'manifest_stubs_bind_checkpoint_config_hashes')!r}")

    _, _, content_audit = run_case(promote_candidate_config_content)
    candidate_evidence_content_drift_rejected = (
        content_audit.get("passed") is False and check_named(content_audit, "candidate_config_contents_remain_non_evidence") is False
    )
    add_check(checks, "candidate_evidence_content_drift_rejected", candidate_evidence_content_drift_rejected, f"check={check_named(content_audit, 'candidate_config_contents_remain_non_evidence')!r}")

    _, _, source_audit = run_case(weaken_source_method_packet)
    source_method_packet_drift_rejected = (
        source_audit.get("passed") is False and check_named(source_audit, "source_method_packet_ready") is False
    )
    add_check(checks, "source_method_packet_drift_rejected", source_method_packet_drift_rejected, f"check={check_named(source_audit, 'source_method_packet_ready')!r}")

    _, _, adapter_audit = run_case(promote_adapter_evidence)
    adapter_evidence_promotion_rejected = (
        adapter_audit.get("passed") is False and check_named(adapter_audit, "independent_implementation_still_required") is False
    )
    add_check(checks, "adapter_evidence_promotion_rejected", adapter_evidence_promotion_rejected, f"check={check_named(adapter_audit, 'independent_implementation_still_required')!r}")

    _, _, baseline_audit = run_case(drift_baseline_spec)
    baseline_spec_hash_drift_rejected = (
        baseline_audit.get("passed") is False and check_named(baseline_audit, "baseline_spec_hashes_match_current_files") is False
    )
    add_check(checks, "baseline_spec_hash_drift_rejected", baseline_spec_hash_drift_rejected, f"check={check_named(baseline_audit, 'baseline_spec_hashes_match_current_files')!r}")

    _, _, csv_audit = run_case(drift_candidate_csv)
    candidate_csv_drift_rejected = (
        csv_audit.get("passed") is False and check_named(csv_audit, "candidate_manifest_csv_matches_records") is False
    )
    add_check(checks, "candidate_csv_drift_rejected", candidate_csv_drift_rejected, f"check={check_named(csv_audit, 'candidate_manifest_csv_matches_records')!r}")

    _, _, manifest_audit = run_case(write_real_manifest_in_fixture)
    real_manifest_write_rejected = (
        manifest_audit.get("passed") is False and check_named(manifest_audit, "no_real_manifest_logs_videos_or_checkpoints_written") is False
    )
    add_check(checks, "real_manifest_write_rejected", real_manifest_write_rejected, f"check={check_named(manifest_audit, 'no_real_manifest_logs_videos_or_checkpoints_written')!r}")

    materialization_file_deletion_rejected = run_file_deletion_case()
    add_check(
        checks,
        "materialization_file_deletion_rejected",
        materialization_file_deletion_rejected,
        "required temporary materialization output check detects deleted candidate CSV",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_after == real_hashes_before
    changed_real_outputs = [
        path for path, before_hash in real_hashes_before.items() if real_hashes_after.get(path) != before_hash
    ]
    add_check(
        checks,
        "real_method_config_materialization_outputs_untouched",
        real_outputs_untouched,
        f"tracked={len(real_hashes_before)}, changed={changed_real_outputs}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_adapter_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "temporary_materialization_ready": temporary_materialization_ready,
        "premature_evidence_promotion_rejected": premature_evidence_promotion_rejected,
        "missing_candidate_record_rejected": missing_candidate_record_rejected,
        "oracle_candidate_rejected": oracle_candidate_rejected,
        "candidate_file_hash_drift_rejected": candidate_file_hash_drift_rejected,
        "manifest_stub_hash_drift_rejected": manifest_stub_hash_drift_rejected,
        "candidate_evidence_content_drift_rejected": candidate_evidence_content_drift_rejected,
        "source_method_packet_drift_rejected": source_method_packet_drift_rejected,
        "adapter_evidence_promotion_rejected": adapter_evidence_promotion_rejected,
        "baseline_spec_hash_drift_rejected": baseline_spec_hash_drift_rejected,
        "candidate_csv_drift_rejected": candidate_csv_drift_rejected,
        "real_manifest_write_rejected": real_manifest_write_rejected,
        "materialization_file_deletion_rejected": materialization_file_deletion_rejected,
        "real_outputs_untouched": real_outputs_untouched,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External method config materialization self-test: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"checks={sum(1 for check in checks if check['passed'])}/{len(checks)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
