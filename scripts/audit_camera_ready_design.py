from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = ROOT / "results"
PAPER_PDF = PAPER / "main.pdf"
CANONICAL_PDF = Path("C:/Users/wangz/Downloads/119.pdf")
OUT_JSON = RESULTS / "camera_ready_design_audit.json"
OUT_MD = RESULTS / "camera_ready_design_audit.md"

EXPECTED_PAGES = 29
RENDER_DPI = 70
MIN_PAGE_WIDTH = 500
MIN_PAGE_HEIGHT = 700
MIN_PAGE_FOREGROUND = 0.010
MAX_PAGE_FOREGROUND = 0.350
MIN_MAIN_FOREGROUND = 0.075
MIN_PAGE_LUMINANCE_STD = 0.040
MIN_MAIN_LUMINANCE_STD = 0.090
MIN_EDGE_MARGIN_PX = 20
MAX_SPARSE_PAGES = 3


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_text(command: list[str]) -> str:
    try:
        proc = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception as exc:
        raise SystemExit(f"command failed: {' '.join(command)}: {exc}") from exc
    return proc.stdout


def pdf_page_count(path: Path) -> int:
    info = run_text(["pdfinfo", str(path)])
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise SystemExit(f"pdfinfo did not return a page count for {path}")


def pdf_text(path: Path, *, page: int | None = None) -> str:
    command = ["pdftotext"]
    if page is not None:
        command.extend(["-f", str(page), "-l", str(page)])
    command.extend(["-layout", str(path), "-"])
    return run_text(command)


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def render_pages(pdf_path: Path, output_dir: Path) -> list[Path]:
    prefix = output_dir / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(RENDER_DPI), str(pdf_path), str(prefix)],
        check=True,
        capture_output=True,
        text=True,
    )

    def page_number(path: Path) -> int:
        match = re.search(r"-(\d+)\.png$", path.name)
        return int(match.group(1)) if match else 0

    return sorted(output_dir.glob("page-*.png"), key=page_number)


def page_metrics(path: Path, page: int) -> dict[str, Any]:
    arr = mpimg.imread(path).astype(float)
    if arr.ndim != 3 or arr.shape[2] not in {3, 4}:
        raise SystemExit(f"unexpected rendered page shape for {path}: {arr.shape}")
    rgb = arr[:, :, :3]
    if arr.shape[2] == 4:
        alpha = arr[:, :, 3:4]
        rgb = rgb * alpha + (1.0 - alpha)
    rgb = np.clip(rgb, 0.0, 1.0)
    gray = rgb.mean(axis=2)
    foreground = np.abs(rgb - 1.0).max(axis=2) > 0.035
    ys, xs = np.where(foreground)
    height, width = foreground.shape
    if len(xs) == 0:
        margins = {"left": 0, "top": 0, "right": 0, "bottom": 0, "minimum": 0}
    else:
        margins = {
            "left": int(xs.min()),
            "top": int(ys.min()),
            "right": int(width - 1 - xs.max()),
            "bottom": int(height - 1 - ys.max()),
        }
        margins["minimum"] = min(margins.values())
    return {
        "page": page,
        "width": int(width),
        "height": int(height),
        "foreground_fraction": float(foreground.mean()),
        "luminance_std": float(gray.std()),
        "edge_margins_px": margins,
    }


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []

    add_check(checks, "paper_pdf_exists", PAPER_PDF.exists(), str(PAPER_PDF))
    add_check(checks, "canonical_pdf_exists", CANONICAL_PDF.exists(), str(CANONICAL_PDF))
    if not PAPER_PDF.exists() or not CANONICAL_PDF.exists():
        payload = {
            "version": "camera_ready_design_audit_v1",
            "passed": False,
            "not_external_evidence": True,
            "checks": checks,
            "failed_checks": [check for check in checks if not check["passed"]],
        }
        OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 1

    add_check(checks, "canonical_matches_paper_pdf", sha256(PAPER_PDF) == sha256(CANONICAL_PDF), "paper/main.pdf vs Downloads/119.pdf")
    pages = pdf_page_count(PAPER_PDF)
    add_check(checks, "page_count_exact", pages == EXPECTED_PAGES, f"pages={pages}")

    with tempfile.TemporaryDirectory(prefix="paper119_camera_ready_") as tmp_name:
        rendered = render_pages(PAPER_PDF, Path(tmp_name))
        metrics = [page_metrics(path, index + 1) for index, path in enumerate(rendered)]

    add_check(checks, "rendered_page_count_exact", len(metrics) == pages == EXPECTED_PAGES, f"rendered={len(metrics)}, pages={pages}")
    low_resolution = [item["page"] for item in metrics if item["width"] < MIN_PAGE_WIDTH or item["height"] < MIN_PAGE_HEIGHT]
    add_check(checks, "render_resolution_ok", not low_resolution, f"low_resolution_pages={low_resolution}")
    blank_pages = [item["page"] for item in metrics if item["foreground_fraction"] < MIN_PAGE_FOREGROUND]
    add_check(checks, "no_blank_pages", not blank_pages, f"blank_pages={blank_pages}")
    overfull_visual_pages = [item["page"] for item in metrics if item["foreground_fraction"] > MAX_PAGE_FOREGROUND]
    add_check(checks, "no_overdense_pages", not overfull_visual_pages, f"overdense_pages={overfull_visual_pages}")
    clipped_pages = [item["page"] for item in metrics if item["edge_margins_px"]["minimum"] < MIN_EDGE_MARGIN_PX]
    add_check(checks, "no_edge_clipped_pages", not clipped_pages, f"clipped_pages={clipped_pages}")
    weak_contrast_pages = [item["page"] for item in metrics if item["luminance_std"] < MIN_PAGE_LUMINANCE_STD]
    add_check(checks, "page_contrast_ok", not weak_contrast_pages, f"weak_contrast_pages={weak_contrast_pages}")

    main_pages = [item for item in metrics if 1 <= item["page"] <= 8]
    weak_main_density = [item["page"] for item in main_pages if item["foreground_fraction"] < MIN_MAIN_FOREGROUND]
    weak_main_contrast = [item["page"] for item in main_pages if item["luminance_std"] < MIN_MAIN_LUMINANCE_STD]
    sparse_pages = [item["page"] for item in metrics if item["foreground_fraction"] < 0.030]
    add_check(checks, "main_pages_have_enough_content", not weak_main_density, f"weak_main_density={weak_main_density}")
    add_check(checks, "main_pages_have_enough_contrast", not weak_main_contrast, f"weak_main_contrast={weak_main_contrast}")
    add_check(checks, "sparse_appendix_pages_bounded", len(sparse_pages) <= MAX_SPARSE_PAGES, f"sparse_pages={sparse_pages}")

    full_text = compact(pdf_text(PAPER_PDF))
    page_texts = {page: compact(pdf_text(PAPER_PDF, page=page)) for page in (1, 5, 6, 7, 8)}
    scope_boundary_ok = (
        "externalrobotor" in full_text
        and "highfidelityvalidationremains" in full_text
        and "necessarybeforedeploymentlevelclaims" in full_text
        and "untilthoseaudits" in full_text
        and "pass" in full_text
        and "thepaperremains" in full_text
        and "localstudy" in full_text
        and "boundedclaim" in full_text
    )
    text_anchors = {
        "title_and_abstract": "skillseamworldactionmodels" in page_texts[1]
        and "robotskillcomposition" in page_texts[1]
        and "abstract" in page_texts[1],
        "decision_quality_page": any("comparativedecisionqualityaudit" in page_texts[page] for page in (5, 6)),
        "predictive_calibration_page": "predictivecalibrationtable" in page_texts[7],
        "stress_and_fixed_risk_page": "stresssweep" in page_texts[8] and "fixedrisk" in page_texts[8],
        "scope_boundary_full_text": scope_boundary_ok,
    }
    for name, ok in text_anchors.items():
        add_check(checks, f"text_anchor_{name}", ok, name)

    density_values = [item["foreground_fraction"] for item in metrics]
    margin_values = [item["edge_margins_px"]["minimum"] for item in metrics]
    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "camera_ready_design_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "pages": pages,
        "render_dpi": RENDER_DPI,
        "density_summary": {
            "minimum": min(density_values) if density_values else None,
            "maximum": max(density_values) if density_values else None,
            "mean": float(sum(density_values) / len(density_values)) if density_values else None,
            "sparse_pages": sparse_pages,
        },
        "minimum_edge_margin_px": min(margin_values) if margin_values else None,
        "page_metrics": metrics,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Camera-Ready Design Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Pages: `{pages}`.",
        f"Render DPI: `{RENDER_DPI}`.",
        f"Foreground density range: `{payload['density_summary']['minimum']:.4f}` to `{payload['density_summary']['maximum']:.4f}`.",
        f"Minimum edge margin: `{payload['minimum_edge_margin_px']}` px.",
        "",
        "This audit renders every PDF page and checks for nonblank pages, reasonable density, page margins, contrast, and selected text anchors. It is a camera-ready presentation check only; it does not substitute for external validation.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = "PASS" if passed else "FAIL"
    print(f"Camera-ready design audit: {status}; pages={pages}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
