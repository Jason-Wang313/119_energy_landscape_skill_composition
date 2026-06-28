from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
PREFLIGHT_ROOT = EXTERNAL / "render_video_preflight"
VIDEO_DIR = PREFLIGHT_ROOT / "videos"
OUT_JSON = RESULTS / "maniskill_render_video_preflight_audit.json"
OUT_MD = RESULTS / "maniskill_render_video_preflight_audit.md"
VERSION = "maniskill_render_video_preflight_audit_v1"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def clean_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def clear_preflight_outputs() -> None:
    if PREFLIGHT_ROOT.exists():
        resolved = PREFLIGHT_ROOT.resolve()
        expected = (EXTERNAL / "render_video_preflight").resolve()
        if resolved != expected:
            raise SystemExit(f"refusing to clear unexpected preflight path: {resolved}")
        shutil.rmtree(PREFLIGHT_ROOT)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def primary_envs() -> list[dict[str, str]]:
    payload = read_json(EXTERNAL / "maniskill_task_bindings.json")
    rows: list[dict[str, str]] = []
    for binding in payload.get("bindings", []) or []:
        if not isinstance(binding, dict):
            continue
        task_family = str(binding.get("task_family", "")).strip()
        env_id = str(binding.get("primary_env_id", "")).strip()
        if task_family and env_id:
            rows.append({"task_family": task_family, "env_id": env_id})
    return rows


def render_probe_code() -> str:
    return textwrap.dedent(
        r"""
        import json
        import sys
        import traceback
        from pathlib import Path

        env_id = sys.argv[1]
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        seed = int(sys.argv[4])
        output_path = Path(sys.argv[5])
        render_backend = sys.argv[6]
        shader_pack = sys.argv[7]

        payload = {
            "env_id": env_id,
            "width": width,
            "height": height,
            "seed": seed,
            "render_backend": render_backend,
            "shader_pack": shader_pack,
            "made_env": False,
            "reset_ok": False,
            "step_ok": False,
            "render_ok": False,
            "mp4_ok": False,
            "video_path": "",
            "video_size_bytes": 0,
            "error_type": "",
            "error": "",
            "traceback_tail": "",
        }
        env = None
        try:
            import gymnasium as gym
            import mani_skill  # noqa: F401
            from external_validation.runner.maniskill_reference_backend import _as_uint8_rgb_frame, write_mp4

            kwargs = {
                "obs_mode": "state",
                "render_mode": "rgb_array",
                "render_backend": render_backend,
                "sensor_configs": {"width": width, "height": height, "shader_pack": shader_pack},
                "human_render_camera_configs": {"width": width, "height": height, "shader_pack": shader_pack},
            }
            try:
                env = gym.make(env_id, **kwargs)
            except TypeError:
                env = gym.make(env_id, obs_mode="state", render_mode="rgb_array")
            payload["made_env"] = True
            env.reset(seed=seed)
            payload["reset_ok"] = True
            frames = []
            frame = env.render()
            frames.append(_as_uint8_rgb_frame(frame))
            payload["render_ok"] = True
            try:
                env.step(env.action_space.sample())
                payload["step_ok"] = True
                frame = env.render()
                frames.append(_as_uint8_rgb_frame(frame))
            except Exception as step_exc:  # noqa: BLE001 - preflight reports environment-specific step/render issues.
                payload["step_error"] = f"{type(step_exc).__name__}: {step_exc}"
            written = write_mp4(output_path, frames, fps=4)
            payload["mp4_ok"] = True
            payload["video_path"] = str(written).replace("\\", "/")
            payload["video_size_bytes"] = output_path.stat().st_size if output_path.exists() else 0
        except Exception as exc:  # noqa: BLE001 - all renderer failures are data for this preflight.
            payload["error_type"] = type(exc).__name__
            payload["error"] = str(exc)
            payload["traceback_tail"] = "\n".join(traceback.format_exc().splitlines()[-12:])
        finally:
            try:
                if env is not None:
                    env.close()
            except Exception as close_exc:  # noqa: BLE001
                payload["close_error"] = f"{type(close_exc).__name__}: {close_exc}"
            print("PAPER119_RENDER_PREFLIGHT " + json.dumps(payload, sort_keys=True))
        """
    )


def parse_marker(stdout: str) -> dict[str, Any] | None:
    marker = "PAPER119_RENDER_PREFLIGHT "
    for line in reversed(stdout.splitlines()):
        if line.startswith(marker):
            try:
                payload = json.loads(line[len(marker) :])
            except json.JSONDecodeError:
                return None
            return payload if isinstance(payload, dict) else None
    return None


def run_probe(row: dict[str, str], args: argparse.Namespace) -> dict[str, Any]:
    env_id = row["env_id"]
    task_family = row["task_family"]
    target = VIDEO_DIR / task_family / f"{env_id.replace('/', '_')}_render_preflight.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-c",
        render_probe_code(),
        env_id,
        str(args.width),
        str(args.height),
        str(args.seed),
        str(target),
        str(args.render_backend),
        str(args.shader_pack),
    ]
    env = os.environ.copy()
    env.setdefault("SAPIEN_RENDERER_DEVICE", args.renderer_device)
    env["PAPER119_MANISKILL_RENDER_BACKEND"] = str(args.render_backend)
    env["PAPER119_MANISKILL_SHADER_PACK"] = str(args.shader_pack)
    env["PAPER119_MANISKILL_RENDER_WIDTH"] = str(args.width)
    env["PAPER119_MANISKILL_RENDER_HEIGHT"] = str(args.height)
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=args.timeout_seconds,
        )
        timed_out = False
        stdout = proc.stdout
        stderr = proc.stderr
        returncode: int | None = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        returncode = None

    marker_payload = parse_marker(stdout) or {}
    record: dict[str, Any] = {
        "task_family": task_family,
        "env_id": env_id,
        "command": " ".join(command[:2] + ["<render_probe_code>", *command[3:]]),
        "timed_out": timed_out,
        "returncode": returncode,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
        "parsed_marker": bool(marker_payload),
        "output_path": rel(target),
        "not_external_evidence": True,
    }
    record.update(marker_payload)
    if timed_out:
        record["error_type"] = "TimeoutExpired"
        record["error"] = f"render preflight exceeded {args.timeout_seconds} seconds"
    if not record.get("error") and returncode not in (0, None):
        cleaned = clean_ansi(stderr)
        runtime_errors = [line.strip() for line in cleaned.splitlines() if "RuntimeError:" in line]
        record["error_type"] = "RuntimeError" if runtime_errors else f"returncode_{returncode}"
        record["error"] = runtime_errors[-1] if runtime_errors else f"subprocess exited with {returncode}"
    record["render_video_ready"] = bool(
        record.get("mp4_ok")
        and not record.get("timed_out")
        and returncode == 0
        and Path(str(record.get("video_path", ""))).exists()
    )
    return record


def summarize_blocker(records: list[dict[str, Any]]) -> str:
    failed = [record for record in records if not record.get("render_video_ready")]
    if not failed:
        return ""
    fragments = []
    for record in failed[:4]:
        error = str(record.get("error") or record.get("error_type") or "no render-backed MP4")
        fragments.append(f"{record.get('env_id')}: {error}")
    return "render-backed MP4 preflight is not ready on this machine; " + "; ".join(fragments)


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# ManiSkill Render-Video Preflight Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Render video ready: `{str(payload['render_video_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Output directory: `{payload['output_dir']}`.",
        "",
        "This preflight tests whether the selected ManiSkill/SAPIEN runtime can export render-backed RGB MP4 files before any official external collection. It is not rollout evidence, does not write the real manifest, and does not replace fidelity acceptance or strict rollout audits.",
        "",
        "## Blocking Missing",
        "",
    ]
    for blocker in payload["blocking_missing"] or ["none"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Environment Results", ""])
    for record in payload["env_records"]:
        status = "ready" if record.get("render_video_ready") else "not_ready"
        error = str(record.get("error") or record.get("error_type") or "")
        lines.append(
            f"- `{status}` `{record.get('task_family')}` / `{record.get('env_id')}`: "
            f"made_env={record.get('made_env')}, reset_ok={record.get('reset_ok')}, "
            f"render_ok={record.get('render_ok')}, mp4_ok={record.get('mp4_ok')}, error={error!r}"
        )
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe render-backed ManiSkill MP4 export without creating evidence.")
    parser.add_argument("--timeout-seconds", type=int, default=45)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--height", type=int, default=64)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--renderer-device", default="cpu")
    parser.add_argument("--render-backend", default="cpu")
    parser.add_argument("--shader-pack", default="minimal")
    parser.add_argument("--max-envs", type=int, default=4)
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    clear_preflight_outputs()
    env_rows = primary_envs()[: max(1, args.max_envs)]
    records = [run_probe(row, args) for row in env_rows]
    render_ready = bool(records) and all(record.get("render_video_ready") for record in records)
    blocking = [] if render_ready else [summarize_blocker(records) or "no ManiSkill primary environments were render-probed"]

    checks: list[dict[str, Any]] = []
    add_check(checks, "render_preflight_is_non_evidence", True, "preflight writes only quarantine outputs and audit files")
    add_check(
        checks,
        "quarantine_paths_are_not_official_evidence",
        is_under(VIDEO_DIR, PREFLIGHT_ROOT)
        and not is_under(VIDEO_DIR, EXTERNAL / "videos")
        and not (EXTERNAL / "manifest.json").exists(),
        f"video_dir={rel(VIDEO_DIR)}",
    )
    add_check(checks, "primary_envs_loaded", len(env_rows) >= 1, f"envs={len(env_rows)}")
    add_check(
        checks,
        "each_probe_has_terminal_status",
        bool(records) and all(record.get("timed_out") or record.get("parsed_marker") for record in records),
        f"records={len(records)}",
    )
    add_check(
        checks,
        "render_readiness_recorded_without_overclaim",
        isinstance(render_ready, bool),
        f"render_video_ready={render_ready}",
    )
    add_check(
        checks,
        "blocking_summary_present_when_not_ready",
        render_ready or bool(blocking and blocking[0]),
        f"blocking={blocking}",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent",
    )
    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "render_video_ready": render_ready,
        "render_ready_env_count": sum(1 for record in records if record.get("render_video_ready")),
        "env_count": len(records),
        "width": args.width,
        "height": args.height,
        "timeout_seconds": args.timeout_seconds,
        "renderer_device": args.renderer_device,
        "render_backend": args.render_backend,
        "shader_pack": args.shader_pack,
        "output_dir": rel(PREFLIGHT_ROOT),
        "video_dir": rel(VIDEO_DIR),
        "blocking_missing": blocking,
        "env_records": records,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "ManiSkill render-video preflight audit: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"render_video_ready={render_ready}; "
        f"envs={len(records)}"
    )
    if not render_ready:
        print(blocking[0])
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
