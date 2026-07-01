from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
LEDGER = DOCS / "claim_evidence_ledger.json"
SUMMARY = RESULTS / "summary.json"
EXTERNAL_AUDIT = RESULTS / "external_evidence_audit.json"
ROLLOUT_METRICS = RESULTS / "external_rollout_metrics.json"
OUT_JSON = RESULTS / "claim_boundary_audit.json"
OUT_MD = RESULTS / "claim_boundary_audit.md"


FORBIDDEN_PATTERNS = [
    (r"\bICLR[- ]?main ready:\s*yes\b", "ICLR-main ready is claimed as yes"),
    (r"\bdeployment[- ]ready\b", "deployment-ready claim"),
    (r"\bhardware[- ]safe\b", "hardware-safe claim"),
    (r"\bstate[- ]of[- ]the[- ]art\s+real[- ]robot\b", "state-of-the-art real-robot claim"),
    (r"\breal[- ]robot validation passed\b", "real-robot validation passed claim"),
    (r"\bhigh[- ]fidelity validation passed\b", "high-fidelity validation passed claim"),
    (r"\bexternal evidence passed\b", "external evidence passed claim"),
    (r"\bsubmission_ready\s*=\s*true\b", "submission_ready=true text claim"),
    (r"Submission ready:\s*`true`", "external audit submission-ready true"),
]

NEGATED_CONTEXTS = (
    "not ",
    "no claim",
    "unsupported claim explicitly avoided",
    "must not",
    "should not",
    "cannot",
    "without",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path_value: str) -> Path:
    return ROOT / path_value


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def scan_forbidden(text: str, path: Path) -> list[str]:
    hits = []
    for pattern, reason in FORBIDDEN_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            prefix = text[max(0, match.start() - 80) : match.start()].lower()
            if any(context in prefix for context in NEGATED_CONTEXTS):
                continue
            hits.append(f"{path.relative_to(ROOT)}: {reason}: {snippet}")
    return hits


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []

    add_check(checks, "ledger_exists", LEDGER.exists(), str(LEDGER))
    ledger = read_json(LEDGER) if LEDGER.exists() else {}
    add_check(checks, "ledger_version", ledger.get("version") == "claim_evidence_ledger_v1", f"version={ledger.get('version')!r}")
    add_check(checks, "ledger_decision", ledger.get("current_decision") == "STRONG_REVISE", f"current_decision={ledger.get('current_decision')!r}")
    add_check(checks, "ledger_iclr_boundary", ledger.get("iclr_main_ready") is False, f"iclr_main_ready={ledger.get('iclr_main_ready')!r}")
    add_check(checks, "ledger_scope_boundary", ledger.get("scope_gate_pass") is False, f"scope_gate_pass={ledger.get('scope_gate_pass')!r}")

    summary = read_json(SUMMARY) if SUMMARY.exists() else {}
    add_check(checks, "summary_exists", SUMMARY.exists(), str(SUMMARY))
    add_check(checks, "summary_decision", summary.get("terminal_decision") == "STRONG_REVISE", f"terminal_decision={summary.get('terminal_decision')!r}")
    add_check(checks, "summary_not_iclr_ready", summary.get("iclr_main_ready") is False, f"iclr_main_ready={summary.get('iclr_main_ready')!r}")
    add_check(checks, "summary_scope_gate_false", summary.get("scope_gate_pass") is False, f"scope_gate_pass={summary.get('scope_gate_pass')!r}")

    external = read_json(EXTERNAL_AUDIT) if EXTERNAL_AUDIT.exists() else {}
    rollout = read_json(ROLLOUT_METRICS) if ROLLOUT_METRICS.exists() else {}
    add_check(checks, "external_audit_exists", EXTERNAL_AUDIT.exists(), str(EXTERNAL_AUDIT))
    add_check(checks, "external_not_ready", external.get("submission_ready") is False, f"submission_ready={external.get('submission_ready')!r}")
    add_check(checks, "rollout_metrics_exists", ROLLOUT_METRICS.exists(), str(ROLLOUT_METRICS))
    add_check(checks, "rollout_not_passed", rollout.get("passed") is False, f"passed={rollout.get('passed')!r}")

    missing_evidence = []
    for claim in ledger.get("permitted_claims", []):
        if not isinstance(claim, dict):
            continue
        for evidence in claim.get("evidence", []):
            if not rel(str(evidence)).exists():
                missing_evidence.append(f"{claim.get('name', '<unnamed>')}: {evidence}")
    add_check(checks, "permitted_claim_evidence_paths_exist", not missing_evidence, "; ".join(missing_evidence[:8]) if missing_evidence else "all evidence paths exist")

    missing_phrases = []
    for item in ledger.get("required_boundary_phrases", []):
        if not isinstance(item, dict):
            continue
        path = rel(str(item.get("file", "")))
        phrase = str(item.get("phrase", ""))
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if phrase not in text:
            missing_phrases.append(f"{item.get('file')}: {phrase}")
    add_check(checks, "required_boundary_phrases", not missing_phrases, "; ".join(missing_phrases[:8]) if missing_phrases else "all required boundary phrases present")

    forbidden_hits = []
    missing_audited = []
    for file_name in ledger.get("audited_text_files", []):
        path = rel(str(file_name))
        if not path.exists():
            missing_audited.append(str(file_name))
            continue
        forbidden_hits.extend(scan_forbidden(path.read_text(encoding="utf-8"), path))
    add_check(checks, "audited_text_files_exist", not missing_audited, "; ".join(missing_audited[:8]) if missing_audited else "all audited files exist")
    add_check(checks, "no_forbidden_overclaims", not forbidden_hits, "; ".join(forbidden_hits[:5]) if forbidden_hits else "no forbidden overclaim patterns found")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "claim_boundary_audit_v1",
        "passed": passed,
        "checks": checks,
        "forbidden_hits": forbidden_hits,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Claim Boundary Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = "PASS" if passed else "FAIL"
    print(f"Claim boundary audit: {status}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
