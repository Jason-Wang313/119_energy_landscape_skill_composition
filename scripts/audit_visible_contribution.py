from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "visible_contribution_audit.json"
OUT_MD = RESULTS / "visible_contribution_audit.md"


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def contains_all(text: str, terms: list[str]) -> tuple[bool, list[str]]:
    missing = [term for term in terms if term not in text]
    return not missing, missing


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    summary = read_json(RESULTS / "submission_readiness_gap_audit.json")
    operator = read_json(RESULTS / "external_operator_packet.json")
    handoff = read_json(RESULTS / "external_operator_handoff_bundle.json")
    materialization = read_json(RESULTS / "external_config_materialization_plan.json")
    ledger = read_json(DOCS / "claim_evidence_ledger.json")

    files = {
        "README": ROOT / "README.md",
        "final_audit": DOCS / "final_audit.md",
        "readiness_decision": DOCS / "submission_readiness_decision.md",
        "readiness_audit": DOCS / "submission_readiness_audit_v5.md",
        "version_log": DOCS / "submission_version_log.md",
        "child_status": ROOT / "child_status.md",
        "outreach": DOCS / "haonan_yilun_outreach_package.md",
    }
    texts = {name: read_text(path) for name, path in files.items()}

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "readiness_gap_state_visible",
        summary.get("objective_complete") is False
        and int(summary.get("satisfied_requirements", 0) or 0) == 17
        and int(summary.get("blocking_missing_requirements", 0) or 0) == 4,
        (
            f"objective_complete={summary.get('objective_complete')!r}, "
            f"satisfied={summary.get('satisfied_requirements')!r}, "
            f"blocking={summary.get('blocking_missing_requirements')!r}"
        ),
    )
    add_check(
        checks,
        "operator_packet_no_go_visible",
        operator.get("passed") is True
        and operator.get("not_external_evidence") is True
        and operator.get("start_state") == "DO_NOT_COLLECT_YET"
        and int(operator.get("blocking_missing_count", 0) or 0) >= 4,
        (
            f"start_state={operator.get('start_state')!r}, "
            f"blocking_missing_count={operator.get('blocking_missing_count')!r}"
        ),
    )
    add_check(
        checks,
        "operator_handoff_bundle_visible",
        handoff.get("passed") is True
        and handoff.get("not_external_evidence") is True
        and handoff.get("handoff_bundle_ready") is True
        and handoff.get("strict_evidence_ready") is False
        and handoff.get("start_state") == "DO_NOT_COLLECT_YET"
        and not handoff.get("forbidden_included_paths"),
        (
            f"files={handoff.get('included_file_count')!r}, "
            f"forbidden={handoff.get('forbidden_included_paths')!r}, "
            f"start_state={handoff.get('start_state')!r}"
        ),
    )
    add_check(
        checks,
        "materializer_guard_visible",
        materialization.get("passed") is True
        and materialization.get("write_enabled") is False
        and materialization.get("not_external_evidence") is True
        and str(materialization.get("operator_write_command", "")).endswith("--confirm-real-platform --write"),
        (
            f"write_enabled={materialization.get('write_enabled')!r}, "
            f"not_external_evidence={materialization.get('not_external_evidence')!r}"
        ),
    )
    claim_names = {str(claim.get("name", "")) for claim in ledger.get("permitted_claims", []) if isinstance(claim, dict)}
    add_check(
        checks,
        "ledger_tracks_new_visible_claims",
        {
            "external_operator_packet_claim",
            "external_operator_handoff_bundle_claim",
            "external_config_materialization_claim",
        }.issubset(claim_names),
        f"missing={sorted({'external_operator_packet_claim', 'external_operator_handoff_bundle_claim', 'external_config_materialization_claim'} - claim_names)}",
    )

    required_terms_by_file = {
        "README": [
            "adaptive physical world/action model for skill seams",
            "External config materialization plan",
            "External operator packet",
            "External operator handoff bundle",
            "17/21",
        ],
        "final_audit": [
            "External config materialization plan",
            "External operator packet",
            "External operator handoff bundle",
            "Haonan/Yilun outreach package",
            "17 satisfied, 4 blocking external gaps",
        ],
        "readiness_decision": [
            "guarded config materialization plan",
            "generated external operator packet",
            "external operator handoff bundle",
            "outreach package now frames Haonan's role as fit/falsification advice",
            "ICLR main ready: no",
        ],
        "readiness_audit": [
            "External config materialization plan",
            "External operator packet",
            "External operator handoff bundle",
            "outreach PDFs now reflect the operator-packet/no-go stance",
            "17/21 objective requirements satisfied",
        ],
        "version_log": [
            "scripts/materialize_external_configs.py",
            "scripts/build_external_operator_packet.py",
            "scripts/build_external_operator_handoff_bundle.py",
            "operator-packet/no-go stance",
        ],
        "child_status": [
            "external config materialization plan",
            "external operator packet",
            "external operator handoff bundle",
            "operator-packet-aligned Haonan/Yilun outreach package",
        ],
        "outreach": [
            "results/external_operator_packet.md",
            "do not frame Haonan as responsible for supplying the missing proof",
            "independent validation protocol/operator packet",
        ],
    }
    for name, terms in required_terms_by_file.items():
        ok, missing = contains_all(texts[name], terms)
        add_check(checks, f"{name}_current_visible_contribution_terms", ok, f"missing={missing}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "visible_contribution_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "audited_files": {name: rel(path) for name, path in files.items()},
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Visible Contribution Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        "",
        "This audit checks that the public-facing contribution docs describe the current package state: skill-seam world/action framing, guarded external config materialization, the no-go operator packet, the no-evidence operator handoff bundle, the Haonan/Yilun outreach stance, and the 17/21 readiness boundary.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Visible contribution audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    if not passed:
        for check in payload["failed_checks"]:
            print(f"FAILED {check['name']}: {check['detail']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
