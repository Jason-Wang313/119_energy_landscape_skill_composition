from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable

import build_external_baseline_contract as baseline


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_EXTERNAL = REAL_ROOT / "external_validation"
REAL_RESULTS = REAL_ROOT / "results"

OUT_JSON = REAL_RESULTS / "external_baseline_contract_self_test.json"
OUT_MD = REAL_RESULTS / "external_baseline_contract_self_test.md"
VERSION = "external_baseline_contract_self_test_v1"


def baseline_outputs() -> list[Path]:
    outputs = [
        REAL_EXTERNAL / "baseline_implementation_contract.md",
        REAL_EXTERNAL / "baseline_implementation_matrix.csv",
        REAL_RESULTS / "external_baseline_contract_audit.json",
        REAL_RESULTS / "external_baseline_contract_audit.md",
    ]
    outputs.extend(sorted((REAL_EXTERNAL / "baseline_specs").glob("*.json")))
    return outputs


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def real_output_hashes() -> dict[str, str | None]:
    return {path.relative_to(REAL_ROOT).as_posix(): sha256_file(path) for path in baseline_outputs()}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise AssertionError(f"missing baseline-contract self-test fixture: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def setup_fixture(root: Path) -> None:
    copy_file(REAL_EXTERNAL / "manifest_template.json", root / "external_validation" / "manifest_template.json")


def patch_baseline(root: Path) -> dict[str, Any]:
    external = root / "external_validation"
    results = root / "results"
    old = {
        "ROOT": baseline.ROOT,
        "EXTERNAL": baseline.EXTERNAL,
        "RESULTS": baseline.RESULTS,
        "MANIFEST_TEMPLATE": baseline.MANIFEST_TEMPLATE,
        "SPEC_DIR": baseline.SPEC_DIR,
        "CONTRACT_MD": baseline.CONTRACT_MD,
        "MATRIX_CSV": baseline.MATRIX_CSV,
        "OUT_JSON": baseline.OUT_JSON,
        "OUT_MD": baseline.OUT_MD,
    }
    baseline.ROOT = root
    baseline.EXTERNAL = external
    baseline.RESULTS = results
    baseline.MANIFEST_TEMPLATE = external / "manifest_template.json"
    baseline.SPEC_DIR = external / "baseline_specs"
    baseline.CONTRACT_MD = external / "baseline_implementation_contract.md"
    baseline.MATRIX_CSV = external / "baseline_implementation_matrix.csv"
    baseline.OUT_JSON = results / "external_baseline_contract_audit.json"
    baseline.OUT_MD = results / "external_baseline_contract_audit.md"
    return old


def restore_baseline(old: dict[str, Any]) -> None:
    for name, value in old.items():
        setattr(baseline, name, value)


def run_builder(root: Path) -> tuple[int, dict[str, Any], str]:
    old = patch_baseline(root)
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            status = baseline.main()
    except SystemExit as exc:
        status = int(exc.code or 0) if isinstance(exc.code, int) else 1
    finally:
        restore_baseline(old)
    payload = read_json(root / "results" / "external_baseline_contract_audit.json")
    return int(status), payload, buffer.getvalue()


def run_audit_case(
    root: Path,
    payload: dict[str, Any],
    mutator: Callable[[Path, list[str], list[dict[str, str]], list[str]], None],
) -> dict[str, Any]:
    manifest = read_json(root / "external_validation" / "manifest_template.json")
    names = baseline.method_names(manifest)
    rows = baseline.method_rows(names)
    spec_files = list(payload.get("spec_files", []) or [])
    old_paths = patch_baseline(root)
    old_api = dict(baseline.ADAPTER_API)
    old_invariants = list(baseline.FAIRNESS_INVARIANTS)
    try:
        mutator(root, names, rows, spec_files)
        return baseline.build_audit(names, rows, spec_files)
    finally:
        baseline.ADAPTER_API = old_api
        baseline.FAIRNESS_INVARIANTS = old_invariants
        restore_baseline(old_paths)


def run_case(
    mutator: Callable[[Path, list[str], list[dict[str, str]], list[str]], None] | None = None,
) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="paper119_baseline_contract_selftest_") as temp_name:
        root = Path(temp_name)
        setup_fixture(root)
        status, payload, _ = run_builder(root)
        if mutator is None:
            return status, payload
        return status, run_audit_case(root, payload, mutator)


def check_named(payload: dict[str, Any], name: str) -> Any:
    for check in payload.get("checks", []) or []:
        if check.get("name") == name:
            return check.get("passed")
    return None


def remove_required_method(_root: Path, names: list[str], rows: list[dict[str, str]], spec_files: list[str]) -> None:
    method = "greedy_module_sequence"
    names[:] = [name for name in names if name != method]
    rows[:] = [row for row in rows if row.get("method") != method]
    spec_files[:] = [path for path in spec_files if not path.endswith(f"/{method}.json")]


def promote_non_oracle_implementations(_root: Path, _names: list[str], rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    for row in rows:
        if row.get("method") != "oracle_basin_composer":
            row["implementation_status"] = "manifest_declared_external_source"


def remove_independent_source_requirement(_root: Path, _names: list[str], rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    for row in rows:
        if row.get("method") == "greedy_module_sequence":
            row["requires_independent_source"] = "false"
            return


def corrupt_oracle_boundary(_root: Path, _names: list[str], rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    for row in rows:
        if row.get("method") == "oracle_basin_composer":
            row["oracle_boundary"] = "non_oracle"
            return


def shrink_fairness_invariants(_root: Path, _names: list[str], _rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    baseline.FAIRNESS_INVARIANTS = baseline.FAIRNESS_INVARIANTS[:1]


def drop_adapter_api_method(_root: Path, _names: list[str], _rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    baseline.ADAPTER_API = {key: value for key, value in baseline.ADAPTER_API.items() if key != "log"}


def corrupt_spec_method_binding(root: Path, _names: list[str], _rows: list[dict[str, str]], spec_files: list[str]) -> None:
    path = root / spec_files[0]
    payload = read_json(path)
    payload["method"] = "synthetic_wrong_method"
    write_json(path, payload)


def remove_release_evidence(root: Path, _names: list[str], _rows: list[dict[str, str]], spec_files: list[str]) -> None:
    path = root / spec_files[0]
    payload = read_json(path)
    payload.pop("required_release_evidence", None)
    write_json(path, payload)


def remove_policy_hash_log_field(root: Path, _names: list[str], _rows: list[dict[str, str]], spec_files: list[str]) -> None:
    path = root / spec_files[0]
    payload = read_json(path)
    fields = payload.get("required_release_evidence", {}).get("episode_log_fields", [])
    payload["required_release_evidence"]["episode_log_fields"] = [
        field for field in fields if field != "policy_or_config_hash"
    ]
    write_json(path, payload)


def delete_contract_file(root: Path, _names: list[str], _rows: list[dict[str, str]], _spec_files: list[str]) -> None:
    (root / "external_validation" / "baseline_implementation_contract.md").unlink()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Baseline Contract Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Implementations ready: `{str(payload['implementations_ready']).lower()}`.",
        f"Temporary contract ready: `{str(payload['temporary_contract_ready']).lower()}`.",
        f"Missing required method rejected: `{str(payload['missing_required_method_rejected']).lower()}`.",
        f"Premature implementation promotion rejected: `{str(payload['premature_implementation_promotion_rejected']).lower()}`.",
        f"Independent-source drift rejected: `{str(payload['independent_source_drift_rejected']).lower()}`.",
        f"Oracle-boundary drift rejected: `{str(payload['oracle_boundary_drift_rejected']).lower()}`.",
        f"Fairness invariant shrink rejected: `{str(payload['fairness_invariant_shrink_rejected']).lower()}`.",
        f"Adapter API drift rejected: `{str(payload['adapter_api_drift_rejected']).lower()}`.",
        f"Spec method-binding drift rejected: `{str(payload['spec_method_binding_drift_rejected']).lower()}`.",
        f"Release-evidence spec drift rejected: `{str(payload['release_evidence_spec_drift_rejected']).lower()}`.",
        f"Policy/config log-field drift rejected: `{str(payload['policy_config_log_field_drift_rejected']).lower()}`.",
        f"Contract-file deletion rejected: `{str(payload['contract_file_deletion_rejected']).lower()}`.",
        f"Real baseline-contract outputs untouched: `{str(payload['real_outputs_untouched']).lower()}`.",
        "",
        "This tooling-only self-test rebuilds the baseline implementation contract in temporary copied workspaces. It proves the contract remains non-evidence and rejects missing required methods, premature implementation readiness, independent-source drift, oracle-boundary drift, weakened fairness invariants, adapter API drift, spec method-binding drift, missing release-evidence requirements, missing `policy_or_config_hash` log requirements, and deleted contract files without touching real baseline-contract outputs.",
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
    real_hashes_before = real_output_hashes()
    checks: list[dict[str, Any]] = []

    status, ready_payload = run_case()
    ready_checks = {check.get("name"): check.get("passed") for check in ready_payload.get("checks", []) or []}
    temporary_contract_ready = (
        status == 0
        and ready_payload.get("version") == "external_baseline_contract_audit_v1"
        and ready_payload.get("passed") is True
        and ready_payload.get("not_external_evidence") is True
        and ready_payload.get("implementations_ready") is False
        and int(ready_payload.get("method_count", 0) or 0) >= 12
        and len(ready_payload.get("missing_implementations", []) or []) >= 11
        and ready_checks.get("specs_require_release_evidence") is True
        and ready_checks.get("specs_require_policy_config_hash_logs") is True
    )
    add_check(
        checks,
        "temporary_baseline_contract_ready_but_non_evidence",
        temporary_contract_ready,
        f"status={status}, passed={ready_payload.get('passed')!r}, methods={ready_payload.get('method_count')!r}",
    )

    _, missing_method = run_case(remove_required_method)
    add_check(
        checks,
        "missing_required_method_rejected",
        missing_method.get("passed") is False and check_named(missing_method, "all_required_methods_present") is False,
        f"method_check={check_named(missing_method, 'all_required_methods_present')}",
    )

    _, promotion = run_case(promote_non_oracle_implementations)
    add_check(
        checks,
        "premature_implementation_promotion_rejected",
        promotion.get("passed") is False and check_named(promotion, "implementations_not_marked_ready") is False,
        f"implementation_check={check_named(promotion, 'implementations_not_marked_ready')}",
    )

    _, independent_source = run_case(remove_independent_source_requirement)
    add_check(
        checks,
        "independent_source_drift_rejected",
        independent_source.get("passed") is False and check_named(independent_source, "non_oracle_requires_independent_source") is False,
        f"source_check={check_named(independent_source, 'non_oracle_requires_independent_source')}",
    )

    _, oracle = run_case(corrupt_oracle_boundary)
    add_check(
        checks,
        "oracle_boundary_drift_rejected",
        oracle.get("passed") is False and check_named(oracle, "oracle_post_hoc_only") is False,
        f"oracle_check={check_named(oracle, 'oracle_post_hoc_only')}",
    )

    _, fairness = run_case(shrink_fairness_invariants)
    add_check(
        checks,
        "fairness_invariant_shrink_rejected",
        fairness.get("passed") is False and check_named(fairness, "fairness_invariants_declared") is False,
        f"fairness_check={check_named(fairness, 'fairness_invariants_declared')}",
    )

    _, adapter_api = run_case(drop_adapter_api_method)
    add_check(
        checks,
        "adapter_api_drift_rejected",
        adapter_api.get("passed") is False and check_named(adapter_api, "adapter_api_covers_required_methods") is False,
        f"adapter_api_check={check_named(adapter_api, 'adapter_api_covers_required_methods')}",
    )

    _, spec_binding = run_case(corrupt_spec_method_binding)
    add_check(
        checks,
        "spec_method_binding_drift_rejected",
        spec_binding.get("passed") is False and check_named(spec_binding, "spec_files_are_method_bound") is False,
        f"spec_binding_check={check_named(spec_binding, 'spec_files_are_method_bound')}",
    )

    _, release_evidence = run_case(remove_release_evidence)
    add_check(
        checks,
        "release_evidence_spec_drift_rejected",
        release_evidence.get("passed") is False and check_named(release_evidence, "specs_require_release_evidence") is False,
        f"release_evidence_check={check_named(release_evidence, 'specs_require_release_evidence')}",
    )

    _, policy_hash = run_case(remove_policy_hash_log_field)
    add_check(
        checks,
        "policy_config_log_field_drift_rejected",
        policy_hash.get("passed") is False and check_named(policy_hash, "specs_require_policy_config_hash_logs") is False,
        f"policy_hash_check={check_named(policy_hash, 'specs_require_policy_config_hash_logs')}",
    )

    _, contract_file = run_case(delete_contract_file)
    add_check(
        checks,
        "contract_file_deletion_rejected",
        contract_file.get("passed") is False and check_named(contract_file, "contract_file_exists") is False,
        f"contract_file_check={check_named(contract_file, 'contract_file_exists')}",
    )

    real_hashes_after = real_output_hashes()
    real_outputs_untouched = real_hashes_before == real_hashes_after
    add_check(
        checks,
        "real_baseline_contract_outputs_untouched",
        real_outputs_untouched,
        f"changed={[key for key in real_hashes_before if real_hashes_before.get(key) != real_hashes_after.get(key)]}",
    )

    check_map = {check["name"]: check["passed"] for check in checks}
    payload = {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "implementations_ready": False,
        "temporary_contract_ready": check_map.get("temporary_baseline_contract_ready_but_non_evidence") is True,
        "missing_required_method_rejected": check_map.get("missing_required_method_rejected") is True,
        "premature_implementation_promotion_rejected": check_map.get("premature_implementation_promotion_rejected") is True,
        "independent_source_drift_rejected": check_map.get("independent_source_drift_rejected") is True,
        "oracle_boundary_drift_rejected": check_map.get("oracle_boundary_drift_rejected") is True,
        "fairness_invariant_shrink_rejected": check_map.get("fairness_invariant_shrink_rejected") is True,
        "adapter_api_drift_rejected": check_map.get("adapter_api_drift_rejected") is True,
        "spec_method_binding_drift_rejected": check_map.get("spec_method_binding_drift_rejected") is True,
        "release_evidence_spec_drift_rejected": check_map.get("release_evidence_spec_drift_rejected") is True,
        "policy_config_log_field_drift_rejected": check_map.get("policy_config_log_field_drift_rejected") is True,
        "contract_file_deletion_rejected": check_map.get("contract_file_deletion_rejected") is True,
        "real_outputs_untouched": real_outputs_untouched,
        "real_output_hashes": real_hashes_after,
        "checks": checks,
    }
    write_report(payload)
    print(
        "External baseline contract self-test: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; not_evidence=true"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
