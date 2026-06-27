from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
PAPER_PDF = PAPER / "main.pdf"
PAPER_TEX = PAPER / "main.tex"
PAPER_LOG = PAPER / "main.log"
CANONICAL_PDF = Path("C:/Users/wangz/Downloads/119.pdf")
OUT_JSON = RESULTS / "presentation_quality_audit.json"
OUT_MD = RESULTS / "presentation_quality_audit.md"


EXPECTED_SECTIONS = [
    "Motivation",
    "Problem Setup",
    "Skill Seams As Predictive Interfaces",
    "Evaluation Protocol",
    "Main Results",
    "Diagnostics, Ablations, And Fixed Risk",
    "Related Work And Boundary",
    "Scope And Validation",
]

EXPECTED_FIGURE_STEMS = [
    "skill_seam_action_model_overview_v5",
    "energy_landscape_composition_hard_success_v5",
    "energy_landscape_composition_utility_risk_v5",
    "energy_landscape_composition_ablation_v5",
    "energy_landscape_composition_stress_sweep_v5",
    "energy_landscape_composition_fixed_risk_v5",
    "energy_landscape_composition_fixed_coverage_v5",
]

FORBIDDEN_PDF_PHRASES = [
    "STRONG_REVISE",
    "STRONG REVISE",
    "not ICLR-main ready",
    "local CPU-only",
    "Terminal decision",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def run_text(command: list[str]) -> str:
    try:
        proc = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception as exc:
        fail(f"command failed: {' '.join(command)}: {exc}")
    return proc.stdout


def pdfinfo(path: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in run_text(["pdfinfo", str(path)]).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        info[key.strip()] = value.strip()
    return info


def pdf_text(path: Path) -> str:
    return run_text(["pdftotext", "-layout", str(path), "-"])


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def parse_underfulls(log_text: str) -> list[int]:
    return [int(value) for value in re.findall(r"Underfull \\hbox \(badness (\d+)\)", log_text)]


def alpha_compact(value: str) -> str:
    return re.sub(r"[^a-z]", "", value.lower())


def main() -> int:
    if not PAPER_PDF.exists():
        fail(f"missing {PAPER_PDF}")
    if not PAPER_TEX.exists():
        fail(f"missing {PAPER_TEX}")
    if not PAPER_LOG.exists():
        fail(f"missing {PAPER_LOG}")
    if not CANONICAL_PDF.exists():
        fail(f"missing canonical PDF {CANONICAL_PDF}")

    tex = PAPER_TEX.read_text(encoding="utf-8")
    log = PAPER_LOG.read_text(encoding="utf-8", errors="replace")
    info = pdfinfo(PAPER_PDF)
    text = pdf_text(PAPER_PDF)
    normalized_text = re.sub(r"\s+", " ", text)
    compact_text = alpha_compact(text)
    checks: list[dict[str, Any]] = []

    pages = int(info.get("Pages", "0"))
    size = PAPER_PDF.stat().st_size
    add_check(checks, "pdf_page_count", pages == 29, f"pages={pages}")
    add_check(checks, "pdf_letter_size", info.get("Page size", "").startswith("612 x 792 pts"), f"page_size={info.get('Page size')!r}")
    add_check(checks, "pdf_size_reasonable", 350_000 <= size <= 900_000, f"bytes={size}")
    add_check(checks, "canonical_matches_paper_pdf", sha256(PAPER_PDF) == sha256(CANONICAL_PDF), "paper/main.pdf vs Downloads/119.pdf")
    add_check(checks, "pdf_text_extractable", len(normalized_text) > 35_000, f"text_chars={len(normalized_text)}")

    for section in EXPECTED_SECTIONS:
        add_check(checks, f"section_present_{section}", f"\\section{{{section}}}" in tex, section)

    add_check(checks, "anonymous_submission", "\\author{Anonymous Authors}" in tex and "Anonymous authors" in text, "anonymous author line")
    add_check(checks, "title_visible", "predictiveskillseammodelsforrobotskillcomposition" in compact_text, "PDF title text")
    add_check(checks, "abstract_visible", "abstract" in compact_text and "boundedclaim" in compact_text, "abstract text")
    add_check(checks, "scope_boundary_visible", "externalrobotorhighfidelityvalidationremainsnecessary" in compact_text, "abstract boundary")
    add_check(checks, "remaining_evidence_visible", "remainingexternalevidence" in compact_text, "appendix scope section")

    missing_pdf_phrases = [phrase for phrase in FORBIDDEN_PDF_PHRASES if phrase in text or phrase in normalized_text]
    add_check(checks, "no_internal_status_leaks_in_pdf", not missing_pdf_phrases, f"leaks={missing_pdf_phrases}")
    add_check(checks, "hidden_links_configured", r"\hypersetup{hidelinks}" in tex, "hidelinks")
    add_check(checks, "hidden_link_wording", "Citation links are hidden and clickable" in tex and "Citation links are boxed" not in tex, "appendix wording")
    add_check(checks, "vector_figures_only_in_manuscript", ".png}" not in tex, "no PNG includes in main.tex")

    for stem in EXPECTED_FIGURE_STEMS:
        pdf_path = FIGURES / f"{stem}.pdf"
        png_path = FIGURES / f"{stem}.png"
        add_check(checks, f"figure_pdf_exists_{stem}", pdf_path.exists() and pdf_path.stat().st_size >= 15_000, f"{pdf_path} bytes={pdf_path.stat().st_size if pdf_path.exists() else 0}")
        add_check(checks, f"figure_png_companion_exists_{stem}", png_path.exists() and png_path.stat().st_size >= 50_000, f"{png_path} bytes={png_path.stat().st_size if png_path.exists() else 0}")
        add_check(checks, f"figure_pdf_referenced_{stem}", f"../figures/{stem}.pdf" in tex, stem)

    strict_patterns = {
        "undefined": r"Undefined|undefined|Citation.*undefined",
        "warnings": r"Warning",
        "overfull": r"Overfull",
        "fatal": r"Fatal|Emergency|Error",
    }
    for name, pattern in strict_patterns.items():
        hits = re.findall(pattern, log)
        add_check(checks, f"log_no_{name}", not hits, f"hits={len(hits)}")
    underfulls = parse_underfulls(log)
    add_check(checks, "log_underfull_count_bounded", len(underfulls) <= 3, f"underfull_count={len(underfulls)}")
    add_check(checks, "log_underfull_badness_bounded", (max(underfulls) if underfulls else 0) <= 4000, f"max_badness={max(underfulls) if underfulls else 0}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "presentation_quality_audit_v1",
        "passed": passed,
        "pdf": str(PAPER_PDF),
        "canonical_pdf": str(CANONICAL_PDF),
        "pages": pages,
        "pdf_bytes": size,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Presentation Quality Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"PDF pages: `{pages}`.",
        f"PDF size: `{size}` bytes.",
        "",
        "This audit checks presentation polish and artifact hygiene. It does not substitute for real external validation.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Presentation quality audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
