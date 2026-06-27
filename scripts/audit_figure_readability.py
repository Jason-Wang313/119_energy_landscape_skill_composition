from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "figure_readability_audit.json"
OUT_MD = RESULTS / "figure_readability_audit.md"

EXPECTED_FIGURE_STEMS = [
    "skill_seam_action_model_overview_v5",
    "energy_landscape_composition_hard_success_v5",
    "energy_landscape_composition_utility_risk_v5",
    "energy_landscape_composition_ablation_v5",
    "energy_landscape_composition_stress_sweep_v5",
    "energy_landscape_composition_fixed_risk_v5",
    "energy_landscape_composition_fixed_coverage_v5",
]

MIN_WIDTH = 1500
MIN_HEIGHT = 900
MIN_PNG_BYTES = 50_000
MIN_PDF_BYTES = 15_000
MIN_FOREGROUND_FRACTION = 0.030
MAX_FOREGROUND_FRACTION = 0.600
MIN_DARK_FRACTION = 0.020
MIN_LUMINANCE_STD = 0.100
MIN_EDGE_MARGIN_PX = 18


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_rgb(path: Path) -> np.ndarray:
    arr = mpimg.imread(path).astype(float)
    if arr.ndim != 3 or arr.shape[2] not in {3, 4}:
        raise SystemExit(f"unexpected image shape for {path}: {arr.shape}")
    rgb = arr[:, :, :3]
    if arr.shape[2] == 4:
        alpha = arr[:, :, 3:4]
        rgb = rgb * alpha + (1.0 - alpha)
    return np.clip(rgb, 0.0, 1.0)


def figure_metrics(path: Path) -> dict[str, Any]:
    rgb = load_rgb(path)
    height, width = rgb.shape[:2]
    gray = rgb.mean(axis=2)
    foreground = np.abs(rgb - 1.0).max(axis=2) > 0.025
    ys, xs = np.where(foreground)
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
    quantized = np.floor(rgb.reshape(-1, 3) * 12).astype(int)
    foreground_pixels = quantized[foreground.reshape(-1)]
    unique_foreground_colors = int(len({tuple(row) for row in foreground_pixels[:: max(1, len(foreground_pixels) // 20_000)]}))
    p01, p99 = np.quantile(gray, [0.01, 0.99])
    return {
        "width": int(width),
        "height": int(height),
        "bytes": int(path.stat().st_size),
        "foreground_fraction": float(foreground.mean()),
        "dark_fraction": float((gray < 0.90).mean()),
        "luminance_std": float(gray.std()),
        "luminance_p01": float(p01),
        "luminance_p99": float(p99),
        "edge_margins_px": margins,
        "unique_foreground_colors_quantized": unique_foreground_colors,
    }


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []
    figures: list[dict[str, Any]] = []
    tex_path = PAPER / "main.tex"
    tex = tex_path.read_text(encoding="utf-8") if tex_path.exists() else ""

    add_check(checks, "main_tex_exists", tex_path.exists(), rel(tex_path))
    add_check(checks, "main_uses_vector_figures", ".png}" not in tex, "no PNG includes in main.tex")

    for stem in EXPECTED_FIGURE_STEMS:
        png_path = FIGURES / f"{stem}.png"
        pdf_path = FIGURES / f"{stem}.pdf"
        add_check(checks, f"{stem}_png_exists", png_path.exists(), rel(png_path))
        add_check(checks, f"{stem}_pdf_exists", pdf_path.exists(), rel(pdf_path))
        if not png_path.exists() or not pdf_path.exists():
            continue
        metrics = figure_metrics(png_path)
        metrics["stem"] = stem
        metrics["png"] = rel(png_path)
        metrics["pdf"] = rel(pdf_path)
        metrics["pdf_bytes"] = int(pdf_path.stat().st_size)
        figures.append(metrics)

        add_check(checks, f"{stem}_png_size", metrics["bytes"] >= MIN_PNG_BYTES, f"bytes={metrics['bytes']}")
        add_check(checks, f"{stem}_pdf_size", metrics["pdf_bytes"] >= MIN_PDF_BYTES, f"bytes={metrics['pdf_bytes']}")
        add_check(
            checks,
            f"{stem}_render_resolution",
            metrics["width"] >= MIN_WIDTH and metrics["height"] >= MIN_HEIGHT,
            f"{metrics['width']}x{metrics['height']}",
        )
        add_check(
            checks,
            f"{stem}_foreground_fraction",
            MIN_FOREGROUND_FRACTION <= metrics["foreground_fraction"] <= MAX_FOREGROUND_FRACTION,
            f"foreground_fraction={metrics['foreground_fraction']:.4f}",
        )
        add_check(
            checks,
            f"{stem}_dark_fraction",
            metrics["dark_fraction"] >= MIN_DARK_FRACTION,
            f"dark_fraction={metrics['dark_fraction']:.4f}",
        )
        add_check(
            checks,
            f"{stem}_luminance_contrast",
            metrics["luminance_std"] >= MIN_LUMINANCE_STD and metrics["luminance_p99"] >= 0.98,
            f"std={metrics['luminance_std']:.4f}, p99={metrics['luminance_p99']:.4f}",
        )
        add_check(
            checks,
            f"{stem}_not_edge_clipped",
            metrics["edge_margins_px"]["minimum"] >= MIN_EDGE_MARGIN_PX,
            f"margins={metrics['edge_margins_px']}",
        )
        add_check(
            checks,
            f"{stem}_color_detail",
            metrics["unique_foreground_colors_quantized"] >= 8,
            f"unique_quantized_colors={metrics['unique_foreground_colors_quantized']}",
        )
        add_check(
            checks,
            f"{stem}_referenced_in_manuscript",
            f"../figures/{stem}.pdf" in tex,
            stem,
        )

    add_check(checks, "all_expected_figures_checked", len(figures) == len(EXPECTED_FIGURE_STEMS), f"figures={len(figures)}")
    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "figure_readability_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "figure_count": len(figures),
        "thresholds": {
            "min_width": MIN_WIDTH,
            "min_height": MIN_HEIGHT,
            "min_png_bytes": MIN_PNG_BYTES,
            "min_pdf_bytes": MIN_PDF_BYTES,
            "min_foreground_fraction": MIN_FOREGROUND_FRACTION,
            "max_foreground_fraction": MAX_FOREGROUND_FRACTION,
            "min_dark_fraction": MIN_DARK_FRACTION,
            "min_luminance_std": MIN_LUMINANCE_STD,
            "min_edge_margin_px": MIN_EDGE_MARGIN_PX,
        },
        "figures": figures,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Figure Readability Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Figures checked: `{len(figures)}`.",
        "",
        "This audit checks raster companions for figure readability: render resolution, foreground density, contrast, edge margins, color detail, and manuscript references. It does not substitute for external validation.",
        "",
        "## Figure Metrics",
        "",
    ]
    for item in figures:
        lines.append(
            "- `{stem}`: `{width}x{height}`, foreground `{foreground_fraction:.4f}`, dark `{dark_fraction:.4f}`, "
            "std `{luminance_std:.4f}`, min margin `{margin}` px".format(
                stem=item["stem"],
                width=item["width"],
                height=item["height"],
                foreground_fraction=item["foreground_fraction"],
                dark_fraction=item["dark_fraction"],
                luminance_std=item["luminance_std"],
                margin=item["edge_margins_px"]["minimum"],
            )
        )
    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    status = "PASS" if passed else "FAIL"
    print(f"Figure readability audit: {status}; figures={len(figures)}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
