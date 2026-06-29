from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

SWEEP_ROOT = EXTERNAL / "render_resource_sweep"
SWEEP_VIDEO_DIR = SWEEP_ROOT / "videos"
OUT_JSON = RESULTS / "maniskill_render_resource_sweep.json"
OUT_MD = RESULTS / "maniskill_render_resource_sweep.md"
OUT_CSV = EXTERNAL / "render_resource_sweep_work_orders.csv"
VERSION = "maniskill_render_resource_sweep_v1"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def load_preflight_module() -> Any:
    path = SCRIPTS / "audit_maniskill_render_video_preflight.py"
    spec = importlib.util.spec_from_file_location("paper119_render_preflight", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {rel(path)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clear_sweep_outputs() -> None:
    if SWEEP_ROOT.exists():
        resolved = SWEEP_ROOT.resolve()
        expected = (EXTERNAL / "render_resource_sweep").resolve()
        if resolved != expected:
            raise SystemExit(f"refusing to clear unexpected sweep path: {resolved}")
        shutil.rmtree(SWEEP_ROOT)
    SWEEP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def parse_sweep_spec(spec: str) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, int]] = set()
    for raw_item in spec.split(","):
        item = raw_item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) == 3:
            backend, shader_pack, resolution = parts
        elif len(parts) == 2:
            backend, resolution = parts
            shader_pack = "minimal"
        else:
            raise SystemExit(f"invalid sweep spec item: {item!r}; expected backend:shader:WxH")
        if "x" not in resolution.lower():
            raise SystemExit(f"invalid resolution in sweep spec item: {item!r}")
        width_raw, height_raw = resolution.lower().split("x", 1)
        width = int(width_raw)
        height = int(height_raw)
        key = (backend.strip(), shader_pack.strip(), width, height)
        if not key[0] or not key[1] or width < 1 or height < 1 or key in seen:
            continue
        seen.add(key)
        profiles.append(
            {
                "render_backend": key[0],
                "shader_pack": key[1],
                "width": width,
                "height": height,
                "profile": f"{key[0]}/{key[1]}/{width}x{height}",
            }
        )
    if not profiles:
        raise SystemExit("sweep spec produced no profiles")
    return profiles


def work_orders(payload: dict[str, Any]) -> list[dict[str, str]]:
    failure_classes = ", ".join(payload["renderer_failure_classes"]) or "none"
    profiles = ", ".join(record["profile"] for record in payload["records"]) or "none"
    return [
        {
            "id": "resource_min_resolution_retest",
            "owner": "independent_operator",
            "status": "blocked_until_renderer_resource_path_passes",
            "command": "python scripts\\audit_maniskill_render_resource_sweep.py --timeout-seconds 45 --max-envs 1",
            "acceptance": "at least one accepted renderer profile writes a render-backed RGB MP4 without diagnostic fallback",
            "notes": f"profiles={profiles}; failure_classes={failure_classes}",
        },
        {
            "id": "accepted_machine_driver_probe",
            "owner": "independent_operator",
            "status": "required_before_fidelity_acceptance",
            "command": "python scripts\\probe_external_platform.py --strict",
            "acceptance": "record exact GPU/Vulkan/SAPIEN/ManiSkill provenance for the collection machine",
            "notes": "compare driver/runtime provenance against this local failing machine",
        },
        {
            "id": "render_backed_video_gate",
            "owner": "jason_or_operator",
            "status": "must_remain_enforced",
            "command": "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix",
            "acceptance": "all four primary task families write render-backed MP4s on the accepted machine",
            "notes": "resource sweep cannot replace the four-task render preflight",
        },
        {
            "id": "diagnostic_fallback_exclusion",
            "owner": "jason_or_operator",
            "status": "must_remain_enforced",
            "command": "python scripts\\validate_external_rollouts.py --strict --write-results",
            "acceptance": "diagnostic fallback sidecars and quarantined sweep media are absent from external_validation/manifest.json",
            "notes": "sweep outputs stay under external_validation/render_resource_sweep",
        },
    ]


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "owner", "status", "command", "acceptance", "notes"])
        writer.writeheader()
        writer.writerows(payload["work_orders"])

    lines = [
        "# ManiSkill Render Resource Sweep",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Any render-backed MP4 ready: `{str(payload['any_render_video_ready']).lower()}`.",
        f"Descriptor-pool failure persists at minimum resolution: `{str(payload['descriptor_pool_failure_persists_at_minimum_resolution']).lower()}`.",
        f"Sweep root: `{payload['sweep_root']}`.",
        "",
        "This bounded sweep retests the first primary ManiSkill task at minimal resolution across renderer profiles. It is non-evidence, writes only quarantined outputs, and cannot replace the four-task render-video preflight.",
        "",
        "## Records",
        "",
    ]
    for record in payload["records"]:
        status = "ready" if record.get("render_video_ready") else "not_ready"
        lines.append(
            f"- `{status}` `{record.get('profile')}` / `{record.get('env_id')}`: "
            f"made_env={record.get('made_env')}, reset_ok={record.get('reset_ok')}, "
            f"render_ok={record.get('render_ok')}, mp4_ok={record.get('mp4_ok')}, "
            f"error={record.get('error')!r}, failure_stage={record.get('failure_progress_stage')!r}, "
            f"terminal_stage={record.get('terminal_progress_stage')!r}"
        )
    lines.extend(["", "## Work Orders", ""])
    for item in payload["work_orders"]:
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"- Owner: `{item['owner']}`")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Command: `{item['command']}`")
        lines.append(f"- Acceptance: {item['acceptance']}")
        lines.append(f"- Notes: {item['notes']}")
        lines.append("")
    lines.extend(["## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a bounded non-evidence ManiSkill render resource sweep.")
    parser.add_argument("--timeout-seconds", type=int, default=45)
    parser.add_argument("--max-envs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--renderer-device", default="cpu")
    parser.add_argument(
        "--sweep-spec",
        default="cpu:minimal:16x16,gpu:minimal:16x16,sapien_cuda:minimal:16x16",
        help="Comma-separated backend:shader:WxH profiles.",
    )
    args = parser.parse_args()

    module = load_preflight_module()
    module.VIDEO_DIR = SWEEP_VIDEO_DIR
    clear_sweep_outputs()
    profiles = parse_sweep_spec(args.sweep_spec)
    env_rows = module.primary_envs()[: max(1, int(args.max_envs))]

    records: list[dict[str, Any]] = []
    for profile in profiles:
        for row in env_rows:
            probe_args = argparse.Namespace(
                timeout_seconds=int(args.timeout_seconds),
                width=int(profile["width"]),
                height=int(profile["height"]),
                seed=int(args.seed),
                renderer_device=str(args.renderer_device),
                render_backend=str(profile["render_backend"]),
                shader_pack=str(profile["shader_pack"]),
                profile_label=f"resource_{profile['render_backend']}_{profile['shader_pack']}_{profile['width']}x{profile['height']}",
            )
            record = module.run_probe(row, probe_args)
            record["resource_sweep"] = True
            record["profile"] = str(profile["profile"])
            record["renderer_failure_class"] = "" if record.get("render_video_ready") else module.classify_render_failure(record)
            records.append(record)

    failure_classes = sorted({str(record.get("renderer_failure_class")) for record in records if record.get("renderer_failure_class")})
    failure_stages = sorted(
        {
            str(record.get("failure_progress_stage"))
            for record in records
            if not record.get("render_video_ready") and record.get("failure_progress_stage")
        }
    )
    any_ready = any(record.get("render_video_ready") for record in records)
    descriptor_pool_persists = (
        "vulkan_descriptor_pool_exhaustion" in failure_classes
        and not any_ready
        and all(int(record.get("width", 0) or 0) <= 16 and int(record.get("height", 0) or 0) <= 16 for record in records)
    )
    checks: list[dict[str, Any]] = []
    add_check(checks, "resource_sweep_is_non_evidence", True, "sweep writes only quarantine outputs and audit files")
    add_check(checks, "profiles_loaded", len(profiles) >= 3, f"profiles={len(profiles)}")
    add_check(checks, "primary_env_loaded", len(env_rows) >= 1, f"env_rows={env_rows}")
    add_check(
        checks,
        "each_probe_has_terminal_status",
        bool(records) and all(record.get("timed_out") or record.get("parsed_marker") for record in records),
        f"records={len(records)}",
    )
    add_check(
        checks,
        "quarantine_paths_are_not_official_evidence",
        all(str(record.get("output_path", "")).startswith("external_validation/render_resource_sweep/") for record in records),
        f"sweep_root={rel(SWEEP_ROOT)}",
    )
    add_check(
        checks,
        "descriptor_pool_failure_classified_or_render_ready",
        any_ready or "vulkan_descriptor_pool_exhaustion" in failure_classes,
        f"any_ready={any_ready}, classes={failure_classes}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent",
    )
    passed = all(check["passed"] for check in checks)
    payload: dict[str, Any] = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "sweep_root": rel(SWEEP_ROOT),
        "video_dir": rel(SWEEP_VIDEO_DIR),
        "timeout_seconds": int(args.timeout_seconds),
        "max_envs": int(args.max_envs),
        "sweep_spec": str(args.sweep_spec),
        "records": records,
        "record_count": len(records),
        "any_render_video_ready": any_ready,
        "descriptor_pool_failure_persists_at_minimum_resolution": descriptor_pool_persists,
        "renderer_failure_classes": failure_classes,
        "renderer_failure_stages": failure_stages,
        "work_orders": work_orders(
            {
                "renderer_failure_classes": failure_classes,
                "records": records,
            }
        ),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    write_outputs(payload)
    print(
        "ManiSkill render resource sweep: "
        f"{'PASS' if passed else 'FAIL'}; any_ready={any_ready}; records={len(records)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
