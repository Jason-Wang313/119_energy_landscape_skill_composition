from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "related_work_audit.json"
OUT_MD = RESULTS / "related_work_audit.md"


REQUIRED_AREAS: dict[str, dict[str, Any]] = {
    "Classical energy and landscape control": {
        "citation_keys": [
            "khatib1986potential",
            "koditschek1989navigation",
            "ratliff2009chomp",
            "ijspeert2013dmp",
            "khansari2011stable",
        ],
        "boundary_terms": ["predictive seam interface", "not as a new low-level controller"],
    },
    "Composable Energy Policies": {
        "citation_keys": ["urain2021cep"],
        "boundary_terms": ["temporally ordered skill handoffs", "not to solve parallel multi-objective action composition"],
    },
    "Temporal abstraction, TAMP, and skill chaining": {
        "citation_keys": ["sutton1999options", "konidaris2009skillchaining", "kaelbling2011tamp", "garrett2021integrated"],
        "boundary_terms": ["physical consequence model", "skill edge"],
    },
    "Runtime Skill Composition and software contracts": {
        "citation_keys": ["pane2021runtime", "rizwan2025ezskiros"],
        "boundary_terms": ["software validity", "physical handoff validity"],
    },
    "Diffusion Policy and generative action representations": {
        "citation_keys": ["chi2023diffusionpolicy", "liu2026oat"],
        "boundary_terms": ["safe, repairable, or should be avoided", "not a replacement for action generation"],
    },
    "Robot foundation policies and datasets": {
        "citation_keys": ["florence2022implicit", "brohan2023rt1", "openx2023"],
        "boundary_terms": ["available skills", "trust a transition"],
    },
    "Policy composition and heterogeneous robot learning": {
        "citation_keys": ["wang2024poco"],
        "boundary_terms": ["transition-level test", "seam certification"],
    },
    "World/action models and hierarchical world models": {
        "citation_keys": ["du2019implicit", "hou2026worldmodel"],
        "boundary_terms": ["local world/action model", "pure controller is too narrow"],
    },
    "Language/Action Compositionality": {
        "citation_keys": ["vijayaraghavan2025compositionality"],
        "boundary_terms": ["physical seam", "chosen skill transition"],
    },
    "Sim-to-real and latent skill transfer": {
        "citation_keys": ["julian2020latent"],
        "boundary_terms": ["evaluating and repairing the handoff", "not learning the reusable skill manifold"],
    },
    "Closest outreach works": {
        "citation_keys": ["chen2026costream", "liu2026simpact", "liu2026oat", "wang2024poco"],
        "boundary_terms": ["compact validation layer", "not a request for Haonan to supply the whole paper"],
    },
    "External Validation Boundary": {
        "citation_keys": [],
        "boundary_terms": ["external-evidence audit", "claim remains bounded"],
    },
}


REQUIRED_MANUSCRIPT_BOUNDARIES = [
    "This paper does not propose a new controller or a new energy parameterization.",
    "not to compute a single reactive action satisfying simultaneous objectives",
    "not a universal world model, but a local world/action interface at a skill seam",
    "The seam critic adds this missing predictive physical test.",
    "This paper asks a complementary reliability question",
    "this paper is not a full behavior-composition stack, action tokenizer, foundation policy, or simulation world model",
    "Until those audits pass, the paper remains a local study with a bounded claim.",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def cite_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]+)\}", tex):
        for raw in match.group(1).split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return keys


def bib_keys(bib: str) -> list[str]:
    return re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib)


def parse_matrix(matrix: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for raw in matrix.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        area = cells[0]
        if area in {"Area", "---"} or set(area) == {"-"}:
            continue
        rows[area] = {
            "prior_work": cells[1],
            "gap": cells[2],
            "boundary": cells[3],
            "citations": cells[4],
        }
    return rows


def section_after(tex: str, heading: str) -> str:
    marker = f"\\section{{{heading}}}"
    if marker not in tex:
        return ""
    return tex.split(marker, 1)[1]


def main() -> int:
    tex = read(PAPER / "main.tex")
    bib = read(PAPER / "references.bib")
    matrix_text = read(DOCS / "related_work_coverage_matrix.md")
    outreach = read(DOCS / "haonan_yilun_outreach_package.md")
    validation_protocol = read(DOCS / "independent_validation_protocol.md")

    cited = cite_keys(tex)
    bibliography_keys = bib_keys(bib)
    bibliography = set(bibliography_keys)
    duplicate_bib_keys = sorted({key for key in bibliography_keys if bibliography_keys.count(key) > 1})
    matrix_rows = parse_matrix(matrix_text)
    related_section = section_after(tex, "Related Work And Boundary")

    checks: list[dict[str, Any]] = []
    add_check(checks, "no_missing_citation_entries", not sorted(cited - bibliography), f"missing={sorted(cited - bibliography)}")
    add_check(checks, "no_duplicate_bib_keys", not duplicate_bib_keys, f"duplicates={duplicate_bib_keys}")
    add_check(checks, "related_work_section_exists", bool(related_section), "section=Related Work And Boundary")

    for area, spec in REQUIRED_AREAS.items():
        row = matrix_rows.get(area)
        add_check(checks, f"matrix_row_{area}", row is not None, area)
        if row is None:
            continue
        add_check(checks, f"matrix_gap_{area}", len(row["gap"]) >= 35, row["gap"])
        add_check(checks, f"matrix_boundary_{area}", len(row["boundary"]) >= 30, row["boundary"])
        add_check(checks, f"matrix_citations_{area}", bool(row["citations"]), row["citations"])
        missing_terms = [term for term in spec["boundary_terms"] if term.lower() not in row["gap"].lower() + " " + row["boundary"].lower()]
        add_check(checks, f"matrix_boundary_terms_{area}", not missing_terms, f"missing_terms={missing_terms}")
        missing_tex_keys = [key for key in spec["citation_keys"] if key not in cited]
        missing_bib_keys = [key for key in spec["citation_keys"] if key not in bibliography]
        add_check(checks, f"manuscript_cites_{area}", not missing_tex_keys, f"missing={missing_tex_keys}")
        add_check(checks, f"bibliography_has_{area}", not missing_bib_keys, f"missing={missing_bib_keys}")

    missing_manuscript_boundaries = [phrase for phrase in REQUIRED_MANUSCRIPT_BOUNDARIES if phrase not in tex]
    add_check(
        checks,
        "manuscript_boundary_sentences",
        not missing_manuscript_boundaries,
        "; ".join(missing_manuscript_boundaries) if missing_manuscript_boundaries else "all boundary sentences present",
    )
    add_check(
        checks,
        "reviewer_facing_novelty_boundary_present",
        "Reviewer-facing novelty boundary" in matrix_text
        and "not primarily a contact-rich manipulation paper" in matrix_text
        and "local world/action model at the seam" in matrix_text,
        "matrix final novelty boundary",
    )
    add_check(
        checks,
        "outreach_boundary_present",
        "not a request for Haonan to supply the whole paper" in matrix_text
        and "not another behavior module, but a seam critic" in outreach,
        "Haonan/Yilun boundary",
    )
    add_check(
        checks,
        "validation_protocol_boundary_present",
        "Do not imply that Haonan's job is to supply the missing proof." in validation_protocol
        and "without relying on Haonan Chen" in validation_protocol,
        "independent validation protocol",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "related_work_audit_v1",
        "passed": passed,
        "required_areas": sorted(REQUIRED_AREAS),
        "cited_keys": sorted(cited),
        "bibliography_keys": sorted(bibliography),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Related Work Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "",
        "This audit checks citation coverage, novelty-boundary rows, and outreach/validation boundaries.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Related work audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
