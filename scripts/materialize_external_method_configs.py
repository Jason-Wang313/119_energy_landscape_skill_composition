from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SPEC_DIR = EXTERNAL / "baseline_specs"
METHOD_CONFIG_DIR = EXTERNAL / "method_config_candidates"

OUT_JSON = EXTERNAL / "method_config_materialization_plan.json"
OUT_MD = EXTERNAL / "method_config_materialization_plan.md"
OUT_CSV = EXTERNAL / "method_config_candidates.csv"
OUT_AUDIT_JSON = RESULTS / "external_method_config_materialization_audit.json"
OUT_AUDIT_MD = RESULTS / "external_method_config_materialization_audit.md"

VERSION = "external_method_config_materialization_plan_v1"
AUDIT_VERSION = "external_method_config_materialization_audit_v1"
CONFIG_VERSION = "paper119_candidate_method_config_v1"
ORACLE_METHOD = "oracle_basin_composer"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def require_payload(path: Path, version: str) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("version") != version:
        raise SystemExit(f"{rel(path)} version={payload.get('version')!r}, expected={version!r}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def load_specs() -> list[dict[str, Any]]:
    specs = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        spec = read_json(path)
        spec["_path"] = rel(path)
        spec["_sha256"] = sha256_file(path)
        specs.append(spec)
    return specs


def evidence_role(method: str) -> str:
    if method == "barrier_certified_energy_composer_v5":
        return "paper_method_under_test"
    if method == "proposed_energy_landscape_composer_v4_1":
        return "paper_predecessor_method"
    return "independent_non_oracle_method"


def candidate_config(spec: dict[str, Any]) -> dict[str, Any]:
    method = str(spec["method"])
    role = evidence_role(method)
    candidate_seed = stable_hash(f"paper119_method_config_candidate:{method}:v1")
    return {
        "version": CONFIG_VERSION,
        "method": method,
        "role": spec.get("role", ""),
        "evidence_role": role,
        "evidence_status": "candidate_config_not_manifest_evidence",
        "operator_acceptance_required": True,
        "manifest_declaration_required": True,
        "rollout_log_binding_required": True,
        "strict_adapter_evidence_ready": False,
        "baseline_spec_path": spec["_path"],
        "baseline_spec_sha256": spec["_sha256"],
        "required_entrypoint": spec.get("required_entrypoint", ""),
        "allowed_inputs": spec.get("allowed_inputs", []),
        "forbidden_advantages": spec.get("forbidden_advantages", []),
        "fairness_invariants": spec.get("fairness_invariants", []),
        "adapter_api": spec.get("adapter_api", {}),
        "required_release_evidence": spec.get("required_release_evidence", {}),
        "candidate_config_seed": candidate_seed,
        "candidate_runtime_contract": {
            "same_skill_library": True,
            "same_observation_interface": True,
            "same_compute_budget": True,
            "paired_resets": True,
            "oracle_access": False,
            "uses_scaffold_template": False,
            "uses_reference_adapter": False,
            "uses_eval_outcome_tuning": False,
            "uses_unblinded_method_identity_during_collection": False,
        },
        "operator_fill_fields": {
            "implementation": f"external_validation/implementations/{method}/adapter.py",
            "implementation_sha256_or_commit": "<operator-supplied implementation SHA256 or commit>",
            "implementation_origin": "<operator/lab/repository source>",
            "independent_operator_or_lab": "<independent operator or lab name>",
            "operator_signoff_id": "<dated signoff id>",
        },
    }


def manifest_stub(method: str, config_path: str, config_hash: str) -> dict[str, Any]:
    role = evidence_role(method)
    return {
        "name": method,
        "implementation": f"external_validation/implementations/{method}/adapter.py",
        "checkpoint_or_config_path": config_path,
        "checkpoint_or_config_hash": config_hash,
        "implementation_provenance": {
            "evidence_role": role,
            "implementation_origin": "<operator/lab/repository source for this implementation>",
            "independent_operator_or_lab": "<independent operator or lab name>",
            "operator_signoff_id": "<signoff id or dated note>",
            "fairness_contract_id": "<manifest.fairness_contract.contract_id>",
            "skill_library_hash": "<manifest.fairness_contract.skill_library_hash>",
            "observation_interface_id": "<manifest.fairness_contract.observation_interface_id>",
            "observation_interface_hash": "<manifest.fairness_contract.observation_interface_hash>",
            "compute_budget_id": "<manifest.fairness_contract.compute_budget_id>",
            "compute_budget_hash": "<manifest.fairness_contract.compute_budget_hash>",
            "paired_reset_protocol_id": "<manifest.fairness_contract.paired_reset_protocol_id>",
            "paired_reset_protocol_hash": "<manifest.fairness_contract.paired_reset_protocol_hash>",
            "same_skill_library": True,
            "same_observation_interface": True,
            "same_compute_budget": True,
            "policy_or_config_hash_locked": True,
            "oracle_access": False,
            "uses_scaffold_template": False,
            "uses_reference_adapter": False,
            "uses_eval_outcome_tuning": False,
            "uses_unblinded_method_identity_during_collection": False,
            "uses_proposed_method_code": method in {"barrier_certified_energy_composer_v5", "proposed_energy_landscape_composer_v4_1"},
        },
    }


def build_payload() -> dict[str, Any]:
    method_packet = require_payload(EXTERNAL / "method_implementation_packet.json", "external_method_implementation_packet_v1")
    method_audit = require_payload(RESULTS / "external_method_implementation_audit.json", "external_method_implementation_audit_v1")
    adapter_evidence = require_payload(
        RESULTS / "external_adapter_contract_evidence_audit.json",
        "external_adapter_contract_evidence_audit_v2",
    )
    specs = [spec for spec in load_specs() if spec.get("method") != ORACLE_METHOD]
    records: list[dict[str, Any]] = []

    for spec in specs:
        method = str(spec["method"])
        config_path = METHOD_CONFIG_DIR / f"{method}.json"
        write_json(config_path, candidate_config(spec))
        config_hash = sha256_file(config_path)
        records.append(
            {
                "method": method,
                "role": spec.get("role", ""),
                "evidence_role": evidence_role(method),
                "config_path": rel(config_path),
                "config_sha256": config_hash,
                "baseline_spec_path": spec["_path"],
                "baseline_spec_sha256": spec["_sha256"],
                "manifest_stub": manifest_stub(method, rel(config_path), config_hash),
                "strict_gate": r"python scripts\validate_external_adapters.py --strict",
                "blocking_until_real_evidence": True,
                "operator_action": "operator may use this candidate config only after independent implementation, provenance signoff, manifest declaration, and raw rollout logs bind policy_or_config_hash to this hash",
            }
        )

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "method",
                "evidence_role",
                "config_path",
                "config_sha256",
                "baseline_spec_path",
                "baseline_spec_sha256",
                "strict_gate",
                "blocking_until_real_evidence",
                "operator_action",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow({key: record[key] for key in writer.fieldnames})

    checks: list[dict[str, Any]] = []
    methods = {record["method"] for record in records}
    work_order_methods = {order.get("method") for order in method_packet.get("work_orders", []) or []}
    add_check(checks, "materialization_is_non_evidence", True, "candidate method configs are not manifest evidence and do not write logs, videos, checkpoints, or manifest")
    add_check(
        checks,
        "source_method_packet_ready",
        method_packet.get("not_external_evidence") is True
        and method_packet.get("method_implementation_packet_ready") is True
        and method_packet.get("strict_adapter_evidence_ready") is False
        and method_audit.get("passed") is True,
        f"packet_ready={method_packet.get('method_implementation_packet_ready')!r}, strict={method_packet.get('strict_adapter_evidence_ready')!r}",
    )
    add_check(
        checks,
        "candidate_configs_cover_non_oracle_methods",
        len(records) >= 11 and methods == work_order_methods and ORACLE_METHOD not in methods,
        f"records={len(records)}, missing={sorted(work_order_methods - methods)}, oracle={ORACLE_METHOD in methods}",
    )
    add_check(
        checks,
        "candidate_hashes_match_written_files",
        all((ROOT / record["config_path"]).exists() and sha256_file(ROOT / record["config_path"]) == record["config_sha256"] for record in records),
        "all candidate config hashes recompute",
    )
    add_check(
        checks,
        "manifest_stubs_bind_checkpoint_config_hashes",
        all(record["manifest_stub"]["checkpoint_or_config_hash"] == record["config_sha256"] for record in records),
        "every manifest stub binds checkpoint_or_config_hash to the candidate config artifact",
    )
    add_check(
        checks,
        "independent_implementation_still_required",
        all("<operator" in record["manifest_stub"]["implementation_provenance"]["implementation_origin"] for record in records)
        and adapter_evidence.get("passed") is False
        and adapter_evidence.get("adapter_count") == 0,
        f"adapter_evidence_passed={adapter_evidence.get('passed')!r}, adapters={adapter_evidence.get('adapter_count')!r}",
    )
    add_check(
        checks,
        "no_real_manifest_logs_videos_or_checkpoints_written",
        not (EXTERNAL / "manifest.json").exists()
        and not any((EXTERNAL / "logs").glob("*.jsonl"))
        and not any((EXTERNAL / "videos").glob("**/*.mp4"))
        and not any((EXTERNAL / "checkpoints").glob("*")),
        "official evidence paths remain absent before real collection",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_adapter_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "candidate_config_count": len(records),
        "oracle_excluded": ORACLE_METHOD not in methods,
        "candidate_config_dir": rel(METHOD_CONFIG_DIR),
        "candidate_manifest_csv": rel(OUT_CSV),
        "source_method_packet": "external_validation/method_implementation_packet.json",
        "source_adapter_evidence_audit": "results/external_adapter_contract_evidence_audit.json",
        "records": records,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    audit_payload = {**payload, "version": AUDIT_VERSION, "packet_version": payload["version"]}
    write_json(OUT_AUDIT_JSON, audit_payload)

    lines = [
        "# External Method Config Materialization Plan",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict adapter evidence ready: `{str(payload['strict_adapter_evidence_ready']).lower()}`.",
        f"Candidate configs: `{payload['candidate_config_count']}`.",
        f"Candidate config directory: `{payload['candidate_config_dir']}`.",
        f"Candidate manifest CSV: `{payload['candidate_manifest_csv']}`.",
        "",
        "These candidate method configs make the future `checkpoint_or_config_path` and `checkpoint_or_config_hash` fields concrete. They do not replace independent implementation provenance, manifest declaration, raw rollout logs, videos, or strict adapter evidence.",
        "",
        "## Candidate Configs",
        "",
    ]
    for record in payload["records"]:
        lines.append(f"- `{record['method']}`: `{record['config_path']}` sha256 `{record['config_sha256']}`")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_AUDIT_MD.write_text(
        "\n".join(lines).replace("# External Method Config Materialization Plan", "# External Method Config Materialization Audit", 1) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        f"External method config materialization: {'PASS' if payload['passed'] else 'FAIL'}; "
        f"configs={payload['candidate_config_count']}; strict_adapter_evidence_ready=false"
    )
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
