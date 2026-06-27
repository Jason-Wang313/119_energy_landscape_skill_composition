from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"

OUT_JSON = RESULTS / "manuscript_readability_audit.json"
OUT_MD = RESULTS / "manuscript_readability_audit.md"


REQUIRED_SECTIONS = [
    "Motivation",
    "Problem Setup",
    "Skill Seams As Predictive Interfaces",
    "Evaluation Protocol",
    "Main Results",
    "Diagnostics, Ablations, And Fixed Risk",
    "Related Work And Boundary",
    "Scope And Validation",
]

CORE_FRAME_TERMS = [
    "local world/action-modeling problem",
    "compact predictive interface between a skill library and a planner",
    "action-conditioned physical interface between a skill library and a planner",
    "world/action-model view at a deliberately local scale",
    "prediction-action-update loop",
    "accept, repair, probe, abstain",
    "choose a different transition",
    "planner-edge updates for future planning",
    "planner's edge beliefs",
]

BOUNDARY_TERMS = [
    "not a universal world model",
    "rather than a new low-level controller",
    "bounded claim",
    "local study",
    "external robot or high-fidelity validation",
    "deployment-level claims",
]

RELATED_BOUNDARY_TERMS = [
    "Composable Energy Policies",
    "Runtime Skill Composition",
    "World/action models and hierarchical world models",
    "Closest outreach works",
    "External Validation Boundary",
]

FORBIDDEN_TERMS = [
    "manual_related_work_not_full_paper_complete",
    "TODO",
    "FIXME",
    "citation needed",
    "not ICLR-main ready",
    "Paper 119",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def citation_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]+)\}", tex):
        for raw in match.group(1).split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return keys


def bibliography_keys(bib: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib))


def extract_abstract(tex: str) -> str:
    if "\\begin{abstract}" not in tex or "\\end{abstract}" not in tex:
        return ""
    return tex.split("\\begin{abstract}", 1)[1].split("\\end{abstract}", 1)[0].strip()


def main_body(tex: str) -> str:
    if "\\appendix" in tex:
        return tex.split("\\appendix", 1)[0]
    return tex


def latex_words(text: str) -> list[str]:
    cleaned = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    cleaned = re.sub(r"[^A-Za-z0-9_./-]+", " ", cleaned)
    return [word for word in cleaned.split() if word]


def section_positions(tex: str) -> list[int]:
    return [tex.find(f"\\section{{{section}}}") for section in REQUIRED_SECTIONS]


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    tex = read(PAPER / "main.tex")
    bib = read(PAPER / "references.bib")
    matrix = read(DOCS / "related_work_coverage_matrix.md")
    summary = json.loads(read(RESULTS / "summary.json"))
    related_audit = json.loads(read(RESULTS / "related_work_audit.json"))
    reference_audit = json.loads(read(RESULTS / "reference_integrity_audit.json"))
    number_audit = json.loads(read(RESULTS / "manuscript_number_audit.json"))

    body = main_body(tex)
    abstract = extract_abstract(tex)
    checks: list[dict[str, Any]] = []

    add_check(checks, "abstract_exists", bool(abstract), f"words={len(latex_words(abstract))}")
    abstract_words = len(latex_words(abstract))
    add_check(checks, "abstract_length_conference_reasonable", 130 <= abstract_words <= 260, f"words={abstract_words}")

    positions = section_positions(body)
    add_check(checks, "required_sections_present", all(pos >= 0 for pos in positions), f"positions={positions}")
    add_check(checks, "required_sections_in_order", positions == sorted(positions) and all(pos >= 0 for pos in positions), f"positions={positions}")

    for term in CORE_FRAME_TERMS:
        add_check(checks, f"core_frame_term_{term[:32]}", term in body, term)
    for term in BOUNDARY_TERMS:
        add_check(checks, f"boundary_term_{term[:32]}", term in body, term)
    for term in RELATED_BOUNDARY_TERMS:
        add_check(checks, f"matrix_term_{term[:32]}", term in matrix, term)

    exact_identity_count = body.count("adaptive physical world/action models for embodied agents")
    wam_phrase_count = (
        body.count("world/action model")
        + body.count("world/action-model")
        + body.count("world/action interface")
    )
    contact_rich_count = body.lower().count("contact-rich")
    add_check(checks, "identity_phrase_not_forced", exact_identity_count <= 1, f"count={exact_identity_count}")
    add_check(checks, "world_action_framing_not_overdone", 4 <= wam_phrase_count <= 12, f"count={wam_phrase_count}")
    add_check(checks, "contact_rich_is_not_the_identity", contact_rich_count <= 2, f"contact-rich count={contact_rich_count}")
    add_check(
        checks,
        "contact_positioning_is_testbed",
        "they are a testbed for the seam model, not the identity of the paper" in body,
        "contact-rich examples are positioned as a testbed",
    )

    forbidden_hits = [term for term in FORBIDDEN_TERMS if term.lower() in body.lower()]
    add_check(checks, "no_stale_internal_or_manual_polish_terms", not forbidden_hits, f"hits={forbidden_hits}")

    missing_scope = summary.get("missing_scope_evidence", [])
    add_check(
        checks,
        "summary_scope_blockers_are_external_only",
        not any("manual_related_work" in item for item in missing_scope),
        f"missing_scope_evidence={missing_scope}",
    )

    cited = citation_keys(tex)
    bib_keys = bibliography_keys(bib)
    add_check(checks, "all_citations_have_bib_entries", not sorted(cited - bib_keys), f"missing={sorted(cited - bib_keys)}")
    add_check(checks, "bibliography_has_enough_entries", len(bib_keys) >= 25, f"entries={len(bib_keys)}")
    add_check(checks, "related_work_audit_passed", related_audit.get("passed") is True, "results/related_work_audit.json")
    add_check(checks, "reference_integrity_audit_passed", reference_audit.get("passed") is True, "results/reference_integrity_audit.json")
    add_check(checks, "number_audit_passed", number_audit.get("passed") is True, "results/manuscript_number_audit.json")

    after_abstract = body.split("\\end{abstract}", 1)[1] if "\\end{abstract}" in body else body
    paragraphs = []
    for raw in after_abstract.splitlines():
        paragraph = raw.strip()
        if not paragraph:
            continue
        if paragraph.startswith(("\\section", "\\subsection", "\\begin", "\\end", "\\[", "\\]", "\\paragraph", "\\clearpage")):
            continue
        if paragraph.startswith(("\\title", "\\author", "\\documentclass", "\\usepackage", "\\input", "\\hypersetup", "\\setlist", "\\raggedbottom", "\\maketitle")):
            continue
        paragraphs.append(paragraph)
    long_paragraphs = []
    for index, paragraph in enumerate(paragraphs, start=1):
        words = latex_words(paragraph)
        if len(words) > 190:
            long_paragraphs.append({"index": index, "words": len(words), "start": paragraph[:80]})
    add_check(checks, "main_body_paragraphs_not_overlong", not long_paragraphs, f"long={long_paragraphs[:5]}")

    main_pages_note = "current evidence supports a bounded claim"
    add_check(checks, "abstract_is_bounded", main_pages_note in abstract.lower(), main_pages_note)
    add_check(
        checks,
        "scope_section_demands_external_evidence",
        "raw-rollout validator must recompute" in body and "Until those audits pass" in body,
        "scope section has evidence contract",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "manuscript_readability_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "abstract_words": abstract_words,
        "main_body_paragraphs": len(paragraphs),
        "world_action_phrase_count": wam_phrase_count,
        "contact_rich_count": contact_rich_count,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Manuscript Readability Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Abstract words: `{abstract_words}`.",
        f"World/action phrase count: `{wam_phrase_count}`.",
        f"Contact-rich phrase count: `{contact_rich_count}`.",
        "",
        "This audit checks that the generated manuscript is naturally framed around a bounded skill-seam world/action model, keeps contact-rich manipulation as a testbed rather than the identity, and has machine-audited related-work/reference coverage. It is not external robot evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Manuscript readability audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
