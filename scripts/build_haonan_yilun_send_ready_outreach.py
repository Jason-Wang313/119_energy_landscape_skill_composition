from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
OUTREACH = ROOT / "outreach"

OUT_DOC = DOCS / "haonan_yilun_send_ready_outreach.md"
OUT_JSON = RESULTS / "haonan_yilun_send_ready_outreach_audit.json"
OUT_MD = RESULTS / "haonan_yilun_send_ready_outreach_audit.md"

VERSION = "haonan_yilun_send_ready_outreach_v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9_']+", text))


def contains_forbidden(text: str, forbidden: list[str]) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in forbidden if phrase.lower() in lowered]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    summary = read_json(RESULTS / "summary.json")
    gap = read_json(RESULTS / "submission_readiness_gap_audit.json")
    closure = read_json(RESULTS / "external_evidence_closure_brief.json")
    reviewer = read_json(RESULTS / "reviewer_response_packet_audit.json")
    visible = read_json(RESULTS / "visible_contribution_audit.json")

    total_requirements = int(gap.get("satisfied_requirements", 0) or 0) + int(gap.get("missing_requirements", 0) or 0)
    satisfied = int(gap.get("satisfied_requirements", 0) or 0)
    blockers = int(gap.get("blocking_missing_requirements", 0) or 0)

    first_email = """Subject: Seam certification for compositional robot behaviors

Hi Haonan,

I'm Jason Wang, an independent researcher working on adaptive physical world/action models for robot behavior composition.

I have a submission-shaped project on local skill-seam certification: before chaining two skills, the model predicts whether the next skill's basin can take over, whether a small repair/probe is enough, or whether the transition should be rejected. The strongest local evidence is on hard handoff regimes where naive sequencing looks feasible but fails through basin mismatch, high-energy barriers, or contact-mode discontinuity.

I thought of CoStream because it makes behavior composition the right object of study. My project is complementary: not another behavior module, but a seam critic for deciding when composed behaviors should be accepted, repaired, probed, or abstained from.

The current package is honest about its boundary: it has a clean local draft and validation protocol, but still needs independent real or accepted high-fidelity validation. I would value your advice on whether this seam-certification layer is scientifically useful to test in a behavior-composition stack.

Would you be open to a short chat?

Best,
Jason"""

    followup_email = """Subject: Re: Seam certification for compositional robot behaviors

Hi Haonan,

Just a brief follow-up. I made a one-page memo and a four-page technical preview for the seam-certification idea. The core question is whether a behavior-composition stack benefits from a separate handoff critic that can accept, repair, probe, or reject seams before execution.

No worries if now is not a good time. I would still appreciate any quick pointer on whether this direction seems useful or misguided.

Best,
Jason"""

    positive_reply = """Thanks, that would be great.

The cleanest next step from my side is to send the one-page memo and four-page preview, then ask one falsification question: which behavior-composition setting would be the cleanest test for a seam critic? I can own implementation, analysis, writing, and ablations around the seam layer. I would not want to treat you as responsible for supplying the missing proof; the current validation packet is there so the proof burden is explicit and independently checkable."""

    attachment_sequence = [
        {
            "stage": "first_email",
            "send": [
                "outreach/paper119_one_page_memo.pdf",
                "outreach/paper119_four_page_preview.pdf",
            ],
            "do_not_send": [
                "full generated PDF as the only artifact",
                "operator-release bundle",
                "long validation artifact catalog",
                "many Haonan/Yilun paper references",
            ],
        },
        {
            "stage": "after_interest",
            "send": [
                "docs/external_evidence_closure_brief.md",
                "results/external_operator_packet.md",
                "external_validation/operator_release_bundle_README.md",
            ],
            "do_not_send": [
                "raw logs or videos before real evidence exists",
                "any claim that strict external evidence has passed",
            ],
        },
    ]

    constraints = {
        "primary_first_email_anchor": "CoStream",
        "secondary_first_email_anchor": "none",
        "max_first_email_words": 190,
        "haonan_role": "fit/falsification advice and possible collaboration, not supplier of the missing proof",
        "yilun_route": "only discuss Yilun if Haonan engages on the scientific fit; do not mention access as a motive",
        "current_status_line": f"{satisfied}/{total_requirements} readiness, {blockers} blocking external-evidence gaps, STRONG_REVISE",
    }

    first_email_words = word_count(first_email)

    body_lines = [
        "# Haonan/Yilun Send-Ready Outreach",
        "",
        "Not evidence: `true`.",
        f"Current decision: `{summary.get('terminal_decision')}`.",
        f"Readiness: `{satisfied}/{total_requirements}` requirements satisfied; `{blockers}` blocking external-evidence gaps.",
        f"First-email word count: `{first_email_words}`.",
        "",
        "Purpose: keep the actual first contact crisp, honest, and aligned with the strengthened Paper 119 package. This document is the send-ready layer; the longer outreach package remains the private reasoning layer.",
        "",
        "## Send Rule",
        "",
        "- Lead with Paper 119 as a skill-seam world/action model for behavior composition.",
        "- Mention CoStream as the primary fit anchor in the first email.",
        "- Mention no secondary paper in the first email. If a later technical reply needs one, use exactly one of OAT or SIMPACT.",
        "- Send the one-page memo and four-page preview first.",
        "- Keep the External evidence closure brief and operator packet as follow-up artifacts only.",
        "- Do not pitch Haonan as responsible for supplying the missing proof.",
        "- Do not mention Yilun as the outreach motive.",
        "",
        "## First Email",
        "",
        "```text",
        first_email,
        "```",
        "",
        "## Follow-Up",
        "",
        "```text",
        followup_email,
        "```",
        "",
        "## If He Responds Positively",
        "",
        "```text",
        positive_reply,
        "```",
        "",
        "## Attachment Sequence",
        "",
    ]
    for stage in attachment_sequence:
        body_lines.extend([f"### {stage['stage']}", "", "Send:"])
        for item in stage["send"]:
            body_lines.append(f"- `{item}`")
        body_lines.extend(["", "Do not send:"])
        for item in stage["do_not_send"]:
            body_lines.append(f"- {item}")
        body_lines.append("")

    body_lines.extend(
        [
            "## Guardrails",
            "",
            "- The ask is whether the seam critic is worth testing, not whether Haonan will provide the validation layer.",
            "- The claim is a bounded local mechanism claim until independent real or accepted high-fidelity evidence exists.",
            "- The agenda identity is adaptive physical world/action models for embodied agents; contact-rich manipulation is a testbed only.",
            "- The outreach success criterion is a scientifically useful falsification path, not access theater.",
            "",
            "## Machine-Checked Constraints",
            "",
        ]
    )
    for key, value in constraints.items():
        body_lines.append(f"- `{key}`: {value}")
    body = "\n".join(body_lines) + "\n"
    OUT_DOC.write_text(body, encoding="utf-8")

    forbidden_first_contact = [
        "all that is left is for you to do",
        "please do the real validation",
        "get to yilun",
        "already main-conference ready",
        "external evidence passed",
        "main ready: yes",
        "submission_ready=true",
    ]
    first_email_forbidden = contains_forbidden(first_email + "\n" + followup_email + "\n" + positive_reply, forbidden_first_contact)
    first_email_secondary_hits = [term for term in ("OAT", "SIMPACT", "Yilun") if term in first_email]

    checks: list[dict[str, Any]] = []
    add_check(checks, "not_external_evidence_declared", "Not evidence: `true`." in body, "document declares non-evidence")
    add_check(checks, "readiness_boundary_current", satisfied == 17 and blockers == 4 and gap.get("objective_complete") is False, f"satisfied={satisfied}, blockers={blockers}, objective_complete={gap.get('objective_complete')!r}")
    add_check(checks, "decision_boundary_current", summary.get("terminal_decision") == "STRONG_REVISE", f"decision={summary.get('terminal_decision')!r}")
    add_check(checks, "closure_route_not_haonan_dependent", closure.get("haonan_dependency") is False and closure.get("strict_external_evidence_ready") is False, f"haonan_dependency={closure.get('haonan_dependency')!r}, strict={closure.get('strict_external_evidence_ready')!r}")
    add_check(checks, "reviewer_packet_available", reviewer.get("passed") is True and reviewer.get("not_external_evidence") is True, f"passed={reviewer.get('passed')!r}")
    add_check(checks, "visible_contribution_current", visible.get("passed") is True, f"passed={visible.get('passed')!r}")
    add_check(checks, "first_email_concise", first_email_words <= constraints["max_first_email_words"], f"words={first_email_words}")
    add_check(checks, "first_email_uses_one_primary_anchor", first_email.count("CoStream") == 1 and not first_email_secondary_hits, f"CoStream={first_email.count('CoStream')}, secondary_hits={first_email_secondary_hits}")
    add_check(checks, "first_contact_forbidden_phrases_absent", not first_email_forbidden, f"hits={first_email_forbidden}")
    add_check(checks, "haonan_not_proof_supplier", "Do not pitch Haonan as responsible for supplying the missing proof." in body and "not supplier of the missing proof" in constraints["haonan_role"], "proof-burden boundary present")
    add_check(checks, "yilun_access_motive_absent", "Do not mention Yilun as the outreach motive." in body and "access" not in first_email.lower(), "Yilun access motive excluded from first email")
    add_check(checks, "first_wave_attachments_exist", all((ROOT / item).exists() for item in attachment_sequence[0]["send"]), f"send={attachment_sequence[0]['send']}")
    add_check(checks, "followup_artifacts_exist", all((ROOT / item).exists() for item in attachment_sequence[1]["send"]), f"send={attachment_sequence[1]['send']}")
    add_check(checks, "agenda_identity_visible", "adaptive physical world/action models for embodied agents" in body, "agenda phrase present")
    add_check(checks, "private_reasoning_layer_preserved", (DOCS / "haonan_yilun_outreach_package.md").exists(), "long package remains available")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "current_decision": summary.get("terminal_decision"),
        "readiness": {
            "satisfied_requirements": satisfied,
            "total_requirements": total_requirements,
            "blocking_missing_requirements": blockers,
        },
        "packet": rel(OUT_DOC),
        "primary_first_email_anchor": constraints["primary_first_email_anchor"],
        "secondary_first_email_anchor": constraints["secondary_first_email_anchor"],
        "first_email_word_count": first_email_words,
        "attachment_sequence": attachment_sequence,
        "constraints": constraints,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit_lines = [
        "# Haonan/Yilun Send-Ready Outreach Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        f"Packet: `{rel(OUT_DOC)}`.",
        f"First-email words: `{first_email_words}`.",
        "",
        "This audit checks that the send-ready outreach layer stays concise, uses CoStream as the only first-email paper anchor, preserves the 17/21 STRONG_REVISE boundary, and does not frame Haonan as responsible for the missing proof.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        audit_lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print(f"Haonan/Yilun send-ready outreach audit: {'PASS' if passed else 'FAIL'}; first_email_words={first_email_words}; checks={len(checks)}")
    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
