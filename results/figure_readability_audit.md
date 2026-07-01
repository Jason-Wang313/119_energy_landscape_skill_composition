# Figure Readability Audit

Passed: `true`.
Not evidence: `true`.
Figures checked: `7`.

This audit checks raster companions for figure readability: render resolution, foreground density, contrast, edge margins, color detail, and manuscript references. It does not substitute for external validation.

## Figure Metrics

- `skill_seam_action_model_overview_v5`: `2026x972`, foreground `0.3570`, dark `0.0659`, std `0.1318`, min margin `55` px
- `energy_landscape_composition_hard_success_v5`: `1952x1204`, foreground `0.2402`, dark `0.2280`, std `0.1867`, min margin `26` px
- `energy_landscape_composition_utility_risk_v5`: `1543x1144`, foreground `0.0445`, dark `0.0324`, std `0.1213`, min margin `24` px
- `energy_landscape_composition_ablation_v5`: `1875x1104`, foreground `0.1777`, dark `0.1648`, std `0.1768`, min margin `26` px
- `energy_landscape_composition_stress_sweep_v5`: `1559x1144`, foreground `0.2706`, dark `0.0651`, std `0.1379`, min margin `24` px
- `energy_landscape_composition_fixed_risk_v5`: `1581x1104`, foreground `0.0944`, dark `0.0520`, std `0.1384`, min margin `23` px
- `energy_landscape_composition_fixed_coverage_v5`: `1539x1104`, foreground `0.0831`, dark `0.0510`, std `0.1381`, min margin `24` px

## Checks

- `pass` `main_tex_exists`: paper/main.tex
- `pass` `main_uses_vector_figures`: no PNG includes in main.tex
- `pass` `skill_seam_action_model_overview_v5_png_exists`: figures/skill_seam_action_model_overview_v5.png
- `pass` `skill_seam_action_model_overview_v5_pdf_exists`: figures/skill_seam_action_model_overview_v5.pdf
- `pass` `skill_seam_action_model_overview_v5_png_size`: bytes=143735
- `pass` `skill_seam_action_model_overview_v5_pdf_size`: bytes=22161
- `pass` `skill_seam_action_model_overview_v5_render_resolution`: 2026x972
- `pass` `skill_seam_action_model_overview_v5_foreground_fraction`: foreground_fraction=0.3570
- `pass` `skill_seam_action_model_overview_v5_dark_fraction`: dark_fraction=0.0659
- `pass` `skill_seam_action_model_overview_v5_luminance_contrast`: std=0.1318, p99=1.0000
- `pass` `skill_seam_action_model_overview_v5_not_edge_clipped`: margins={'left': 71, 'top': 85, 'right': 110, 'bottom': 55, 'minimum': 55}
- `pass` `skill_seam_action_model_overview_v5_color_detail`: unique_quantized_colors=92
- `pass` `skill_seam_action_model_overview_v5_referenced_in_manuscript`: skill_seam_action_model_overview_v5
- `pass` `energy_landscape_composition_hard_success_v5_png_exists`: figures/energy_landscape_composition_hard_success_v5.png
- `pass` `energy_landscape_composition_hard_success_v5_pdf_exists`: figures/energy_landscape_composition_hard_success_v5.pdf
- `pass` `energy_landscape_composition_hard_success_v5_png_size`: bytes=130382
- `pass` `energy_landscape_composition_hard_success_v5_pdf_size`: bytes=27319
- `pass` `energy_landscape_composition_hard_success_v5_render_resolution`: 1952x1204
- `pass` `energy_landscape_composition_hard_success_v5_foreground_fraction`: foreground_fraction=0.2402
- `pass` `energy_landscape_composition_hard_success_v5_dark_fraction`: dark_fraction=0.2280
- `pass` `energy_landscape_composition_hard_success_v5_luminance_contrast`: std=0.1867, p99=1.0000
- `pass` `energy_landscape_composition_hard_success_v5_not_edge_clipped`: margins={'left': 28, 'top': 26, 'right': 27, 'bottom': 32, 'minimum': 26}
- `pass` `energy_landscape_composition_hard_success_v5_color_detail`: unique_quantized_colors=53
- `pass` `energy_landscape_composition_hard_success_v5_referenced_in_manuscript`: energy_landscape_composition_hard_success_v5
- `pass` `energy_landscape_composition_utility_risk_v5_png_exists`: figures/energy_landscape_composition_utility_risk_v5.png
- `pass` `energy_landscape_composition_utility_risk_v5_pdf_exists`: figures/energy_landscape_composition_utility_risk_v5.pdf
- `pass` `energy_landscape_composition_utility_risk_v5_png_size`: bytes=106021
- `pass` `energy_landscape_composition_utility_risk_v5_pdf_size`: bytes=25701
- `pass` `energy_landscape_composition_utility_risk_v5_render_resolution`: 1543x1144
- `pass` `energy_landscape_composition_utility_risk_v5_foreground_fraction`: foreground_fraction=0.0445
- `pass` `energy_landscape_composition_utility_risk_v5_dark_fraction`: dark_fraction=0.0324
- `pass` `energy_landscape_composition_utility_risk_v5_luminance_contrast`: std=0.1213, p99=1.0000
- `pass` `energy_landscape_composition_utility_risk_v5_not_edge_clipped`: margins={'left': 25, 'top': 26, 'right': 24, 'bottom': 28, 'minimum': 24}
- `pass` `energy_landscape_composition_utility_risk_v5_color_detail`: unique_quantized_colors=80
- `pass` `energy_landscape_composition_utility_risk_v5_referenced_in_manuscript`: energy_landscape_composition_utility_risk_v5
- `pass` `energy_landscape_composition_ablation_v5_png_exists`: figures/energy_landscape_composition_ablation_v5.png
- `pass` `energy_landscape_composition_ablation_v5_pdf_exists`: figures/energy_landscape_composition_ablation_v5.pdf
- `pass` `energy_landscape_composition_ablation_v5_png_size`: bytes=104956
- `pass` `energy_landscape_composition_ablation_v5_pdf_size`: bytes=21977
- `pass` `energy_landscape_composition_ablation_v5_render_resolution`: 1875x1104
- `pass` `energy_landscape_composition_ablation_v5_foreground_fraction`: foreground_fraction=0.1777
- `pass` `energy_landscape_composition_ablation_v5_dark_fraction`: dark_fraction=0.1648
- `pass` `energy_landscape_composition_ablation_v5_luminance_contrast`: std=0.1768, p99=1.0000
- `pass` `energy_landscape_composition_ablation_v5_not_edge_clipped`: margins={'left': 28, 'top': 26, 'right': 28, 'bottom': 26, 'minimum': 26}
- `pass` `energy_landscape_composition_ablation_v5_color_detail`: unique_quantized_colors=33
- `pass` `energy_landscape_composition_ablation_v5_referenced_in_manuscript`: energy_landscape_composition_ablation_v5
- `pass` `energy_landscape_composition_stress_sweep_v5_png_exists`: figures/energy_landscape_composition_stress_sweep_v5.png
- `pass` `energy_landscape_composition_stress_sweep_v5_pdf_exists`: figures/energy_landscape_composition_stress_sweep_v5.pdf
- `pass` `energy_landscape_composition_stress_sweep_v5_png_size`: bytes=128259
- `pass` `energy_landscape_composition_stress_sweep_v5_pdf_size`: bytes=25642
- `pass` `energy_landscape_composition_stress_sweep_v5_render_resolution`: 1559x1144
- `pass` `energy_landscape_composition_stress_sweep_v5_foreground_fraction`: foreground_fraction=0.2706
- `pass` `energy_landscape_composition_stress_sweep_v5_dark_fraction`: dark_fraction=0.0651
- `pass` `energy_landscape_composition_stress_sweep_v5_luminance_contrast`: std=0.1379, p99=1.0000
- `pass` `energy_landscape_composition_stress_sweep_v5_not_edge_clipped`: margins={'left': 34, 'top': 26, 'right': 24, 'bottom': 25, 'minimum': 24}
- `pass` `energy_landscape_composition_stress_sweep_v5_color_detail`: unique_quantized_colors=81
- `pass` `energy_landscape_composition_stress_sweep_v5_referenced_in_manuscript`: energy_landscape_composition_stress_sweep_v5
- `pass` `energy_landscape_composition_fixed_risk_v5_png_exists`: figures/energy_landscape_composition_fixed_risk_v5.png
- `pass` `energy_landscape_composition_fixed_risk_v5_pdf_exists`: figures/energy_landscape_composition_fixed_risk_v5.pdf
- `pass` `energy_landscape_composition_fixed_risk_v5_png_size`: bytes=124966
- `pass` `energy_landscape_composition_fixed_risk_v5_pdf_size`: bytes=26259
- `pass` `energy_landscape_composition_fixed_risk_v5_render_resolution`: 1581x1104
- `pass` `energy_landscape_composition_fixed_risk_v5_foreground_fraction`: foreground_fraction=0.0944
- `pass` `energy_landscape_composition_fixed_risk_v5_dark_fraction`: dark_fraction=0.0520
- `pass` `energy_landscape_composition_fixed_risk_v5_luminance_contrast`: std=0.1384, p99=1.0000
- `pass` `energy_landscape_composition_fixed_risk_v5_not_edge_clipped`: margins={'left': 25, 'top': 26, 'right': 23, 'bottom': 26, 'minimum': 23}
- `pass` `energy_landscape_composition_fixed_risk_v5_color_detail`: unique_quantized_colors=94
- `pass` `energy_landscape_composition_fixed_risk_v5_referenced_in_manuscript`: energy_landscape_composition_fixed_risk_v5
- `pass` `energy_landscape_composition_fixed_coverage_v5_png_exists`: figures/energy_landscape_composition_fixed_coverage_v5.png
- `pass` `energy_landscape_composition_fixed_coverage_v5_pdf_exists`: figures/energy_landscape_composition_fixed_coverage_v5.pdf
- `pass` `energy_landscape_composition_fixed_coverage_v5_png_size`: bytes=123927
- `pass` `energy_landscape_composition_fixed_coverage_v5_pdf_size`: bytes=25951
- `pass` `energy_landscape_composition_fixed_coverage_v5_render_resolution`: 1539x1104
- `pass` `energy_landscape_composition_fixed_coverage_v5_foreground_fraction`: foreground_fraction=0.0831
- `pass` `energy_landscape_composition_fixed_coverage_v5_dark_fraction`: dark_fraction=0.0510
- `pass` `energy_landscape_composition_fixed_coverage_v5_luminance_contrast`: std=0.1381, p99=1.0000
- `pass` `energy_landscape_composition_fixed_coverage_v5_not_edge_clipped`: margins={'left': 34, 'top': 26, 'right': 24, 'bottom': 26, 'minimum': 24}
- `pass` `energy_landscape_composition_fixed_coverage_v5_color_detail`: unique_quantized_colors=98
- `pass` `energy_landscape_composition_fixed_coverage_v5_referenced_in_manuscript`: energy_landscape_composition_fixed_coverage_v5
- `pass` `all_expected_figures_checked`: figures=7
