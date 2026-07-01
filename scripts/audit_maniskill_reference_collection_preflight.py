from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
BACKEND = EXTERNAL / "runner" / "maniskill_reference_backend.py"
RUN_ID = "maniskill_sapien_reference_preflight_protocol_v1"
OUT_JSON = RESULTS / "maniskill_reference_collection_preflight_audit.json"
OUT_MD = RESULTS / "maniskill_reference_collection_preflight_audit.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import audit_external_backend_contract as backend_contract  # noqa: E402
from scripts import audit_external_collection_readiness as collection_readiness  # noqa: E402


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    backend_module = args.backend_module.as_posix()
    contract_args = SimpleNamespace(
        backend_module=backend_module,
        task_config_dir=args.task_config_dir,
        alias_map=args.alias_map,
        strict=True,
    )
    collection_args = SimpleNamespace(
        backend_module=backend_module,
        operator_sheet=args.operator_sheet,
        alias_map=args.alias_map,
        task_config_dir=args.task_config_dir,
        output_log_dir=args.output_log_dir,
        video_dir=args.video_dir,
        fidelity_audit=args.fidelity_audit,
        runner=args.runner,
        schema=args.schema,
        run_id=args.run_id,
        unsealed_alias_map=True,
        force=False,
        strict=True,
    )
    contract_payload = backend_contract.build_payload(contract_args)
    collection_payload = collection_readiness.build_payload(collection_args)
    collection_checks = {check.get("name"): check.get("passed") for check in collection_payload.get("checks", [])}
    blocking = list(collection_payload.get("blocking_missing", []) or [])

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "reference_backend_contract_strict_passes",
        contract_payload.get("passed") is True
        and contract_payload.get("strict") is True
        and contract_payload.get("actual_backend_ready") is True
        and contract_payload.get("not_external_evidence") is True,
        (
            f"passed={contract_payload.get('passed')!r}, "
            f"actual_backend_ready={contract_payload.get('actual_backend_ready')!r}"
        ),
    )
    add_check(
        checks,
        "reference_backend_collection_preflight_reaches_fidelity_gate",
        collection_payload.get("collection_ready") is False
        and collection_payload.get("not_external_evidence") is True
        and collection_checks.get("backend_module_ready") is True
        and collection_checks.get("real_task_configs_ready") is True
        and collection_checks.get("alias_unsealing_explicit") is True
        and collection_checks.get("run_id_specific") is True
        and collection_checks.get("fidelity_acceptance_ready") is False
        and len(blocking) == 1
        and "fidelity_acceptance_ready" in blocking[0],
        f"blocking={blocking}",
    )
    add_check(
        checks,
        "official_collection_still_not_ready",
        collection_payload.get("collection_ready") is False
        and not (EXTERNAL / "manifest.json").exists(),
        "no manifest is written and fidelity acceptance remains required",
    )
    add_check(
        checks,
        "default_audits_are_not_overwritten",
        OUT_JSON != backend_contract.OUT_JSON and OUT_JSON != collection_readiness.OUT_JSON,
        f"out={rel(OUT_JSON)}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": "maniskill_reference_collection_preflight_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "backend_module": rel(args.backend_module),
        "run_id": args.run_id,
        "reference_backend_contract_ready": contract_payload.get("actual_backend_ready") is True,
        "collection_ready": collection_payload.get("collection_ready") is True,
        "collection_blocking_missing": blocking,
        "collection_blocking_missing_count": len(blocking),
        "strict_external_evidence_ready": False,
        "contract_summary": {
            "passed": contract_payload.get("passed"),
            "actual_backend_ready": contract_payload.get("actual_backend_ready"),
            "backend_contract_harness_ready": contract_payload.get("backend_contract_harness_ready"),
            "blocking_missing": contract_payload.get("blocking_missing", []),
        },
        "collection_summary": {
            "collection_ready": collection_payload.get("collection_ready"),
            "readiness_state": collection_payload.get("readiness_state"),
            "blocking_missing": blocking,
            "checks": collection_payload.get("checks", []),
        },
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ManiSkill Reference Collection Preflight Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Backend module: `{payload['backend_module']}`.",
        f"Reference backend contract ready: `{str(payload['reference_backend_contract_ready']).lower()}`.",
        f"Collection ready: `{str(payload['collection_ready']).lower()}`.",
        f"Collection blocking missing items: `{payload['collection_blocking_missing_count']}`.",
        "",
        "This audit runs the strict backend-contract and explicit collection-preflight checks for the tracked ManiSkill reference backend without writing rollout logs, videos, manifests, or evidence. It documents that backend/module/config/run-id/alias preflight can reach the fidelity-acceptance gate, while official external collection remains blocked until real platform fidelity provenance is accepted.",
        "",
        "## Blocking Missing",
        "",
    ]
    for item in payload["collection_blocking_missing"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit explicit collection preflight for the tracked ManiSkill reference backend.")
    parser.add_argument("--backend-module", type=Path, default=BACKEND)
    parser.add_argument("--operator-sheet", type=Path, default=EXTERNAL / "blinded_operator_sheet.csv")
    parser.add_argument("--alias-map", type=Path, default=EXTERNAL / "method_alias_map.json")
    parser.add_argument("--task-config-dir", type=Path, default=EXTERNAL / "configs")
    parser.add_argument("--output-log-dir", type=Path, default=EXTERNAL / "logs")
    parser.add_argument("--video-dir", type=Path, default=EXTERNAL / "videos")
    parser.add_argument("--fidelity-audit", type=Path, default=RESULTS / "external_fidelity_acceptance_audit.json")
    parser.add_argument("--runner", type=Path, default=EXTERNAL / "runner" / "real_collection_runner.py")
    parser.add_argument("--schema", type=Path, default=EXTERNAL / "log_schema_v1.json")
    parser.add_argument("--run-id", default=RUN_ID)
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload)
    print(
        "ManiSkill reference collection preflight audit: "
        f"contract_ready={payload['reference_backend_contract_ready']}; "
        f"collection_ready={payload['collection_ready']}; "
        f"blocking={payload['collection_blocking_missing_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
