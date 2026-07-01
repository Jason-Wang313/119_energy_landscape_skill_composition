from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_BINDINGS = EXTERNAL / "maniskill_task_bindings.json"
OUT_JSON = RESULTS / "maniskill_fidelity_metadata_probe.json"
OUT_MD = RESULTS / "maniskill_fidelity_metadata_probe.md"

VERSION = "maniskill_fidelity_metadata_probe_v1"
SENTINEL = "PAPER119_MANISKILL_FIDELITY_METADATA "


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def clean_bindings(bindings: dict[str, Any]) -> list[dict[str, Any]]:
    raw = bindings.get("bindings", [])
    raw = raw if isinstance(raw, list) else []
    cleaned: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        task = str(item.get("task_family", "")).strip()
        primary = str(item.get("primary_env_id", "")).strip()
        support = item.get("support_env_ids", [])
        support = support if isinstance(support, list) else []
        if task and primary:
            cleaned.append(
                {
                    "task_family": task,
                    "primary_env_id": primary,
                    "support_env_ids": [str(env_id).strip() for env_id in support if str(env_id).strip()],
                    "binding_strength": str(item.get("binding_strength", "")).strip(),
                }
            )
    return cleaned


def metadata_code() -> str:
    return r'''
import json
import sys
import time
import traceback

sentinel = sys.argv[1]
env_id = sys.argv[2]


def scalar(value):
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def get_attr(obj, name):
    try:
        return scalar(getattr(obj, name))
    except Exception:
        return None


def stringify(value, limit=800):
    try:
        text = str(value)
    except Exception as exc:
        text = f"{type(exc).__name__}: {exc}"
    return text[:limit]


payload = {
    "env_id": env_id,
    "made_env": False,
    "reset_ok": False,
    "closed": False,
    "elapsed_seconds": None,
    "error_type": "",
    "error": "",
    "traceback_tail": "",
    "import_error": "",
    "required_asset_ids": [],
    "missing_asset_ids": [],
    "metadata": {},
}
started = time.time()
env = None
try:
    import gymnasium as gym
    import mani_skill  # noqa: F401
    from mani_skill.utils import assets
    from mani_skill.utils.registration import REGISTERED_ENVS
except Exception as exc:  # noqa: BLE001
    gym = None
    assets = None
    REGISTERED_ENVS = {}
    payload["import_error"] = f"{type(exc).__name__}: {exc}"

try:
    env_spec = REGISTERED_ENVS.get(env_id) if isinstance(REGISTERED_ENVS, dict) else None
    for asset_id in list(getattr(env_spec, "asset_download_ids", []) or []):
        asset_id = str(asset_id)
        payload["required_asset_ids"].append(asset_id)
        if assets is None:
            payload["missing_asset_ids"].append(asset_id)
        elif asset_id in assets.DATA_GROUPS:
            for data_source_id in assets.expand_data_group_into_individual_data_source_ids(asset_id):
                if not assets.is_data_source_downloaded(data_source_id):
                    payload["missing_asset_ids"].append(asset_id)
                    break
        elif asset_id in assets.DATA_SOURCES and not assets.is_data_source_downloaded(asset_id):
            payload["missing_asset_ids"].append(asset_id)
except Exception:
    pass

try:
    if gym is None:
        raise RuntimeError(payload["import_error"] or "gymnasium/mani_skill import failed")
    env = gym.make(env_id, obs_mode="state")
    payload["made_env"] = True
    obs, info = env.reset(seed=0)
    payload["reset_ok"] = True
    unwrapped = env.unwrapped
    scene = getattr(unwrapped, "scene", None)
    agent = getattr(unwrapped, "agent", None)
    controller = getattr(agent, "controller", None) if agent is not None else None
    controllers = getattr(agent, "controllers", {}) if agent is not None else {}
    controllers = controllers if isinstance(controllers, dict) else {}
    sim_freq = get_attr(unwrapped, "sim_freq")
    control_freq = get_attr(unwrapped, "control_freq")
    sim_timestep = get_attr(unwrapped, "sim_timestep")
    control_timestep = get_attr(unwrapped, "control_timestep")
    scene_timestep = get_attr(scene, "timestep") if scene is not None else None
    derived_substeps = None
    try:
        if sim_freq and control_freq:
            derived_substeps = float(sim_freq) / float(control_freq)
    except Exception:
        derived_substeps = None
    if derived_substeps is None:
        try:
            if sim_timestep and control_timestep:
                derived_substeps = float(control_timestep) / float(sim_timestep)
        except Exception:
            derived_substeps = None
    payload["metadata"] = {
        "env_class": type(unwrapped).__name__,
        "obs_mode": get_attr(unwrapped, "obs_mode"),
        "reward_mode": get_attr(unwrapped, "reward_mode"),
        "render_mode": get_attr(unwrapped, "render_mode"),
        "device": stringify(get_attr(unwrapped, "device"), 200),
        "num_envs": get_attr(unwrapped, "num_envs"),
        "sim_freq_hz": sim_freq,
        "control_freq_hz": control_freq,
        "sim_timestep_seconds": sim_timestep,
        "control_timestep_seconds": control_timestep,
        "scene_timestep_seconds": scene_timestep,
        "derived_substeps_per_control_step": derived_substeps,
        "scene_type": type(scene).__name__ if scene is not None else "",
        "scene_backend_type": type(getattr(scene, "px", None)).__name__ if scene is not None else "",
        "gpu_sim_enabled": get_attr(scene, "gpu_sim_enabled") if scene is not None else None,
        "observation_space": stringify(getattr(env, "observation_space", "")),
        "observation_type": type(obs).__name__,
        "observation_shape": stringify(getattr(obs, "shape", "")),
        "info_keys": sorted(str(key) for key in getattr(info, "keys", lambda: [])()),
        "agent_class": type(agent).__name__ if agent is not None else "",
        "agent_uid": get_attr(agent, "uid") if agent is not None else "",
        "robot_repr": stringify(getattr(agent, "robot", "")) if agent is not None else "",
        "controller_type": type(controller).__name__ if controller is not None else "",
        "controller_repr": stringify(controller),
        "available_controller_names": sorted(str(key) for key in controllers),
    }
except Exception as exc:  # noqa: BLE001
    payload["error_type"] = type(exc).__name__
    payload["error"] = str(exc)
    payload["traceback_tail"] = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-2000:]
finally:
    if env is not None:
        try:
            env.close()
            payload["closed"] = True
        except Exception as exc:  # noqa: BLE001
            payload["closed"] = False
            if not payload["error"]:
                payload["error_type"] = type(exc).__name__
                payload["error"] = str(exc)
    payload["required_asset_ids"] = sorted(set(payload["required_asset_ids"]))
    payload["missing_asset_ids"] = sorted(set(payload["missing_asset_ids"]))
    payload["elapsed_seconds"] = round(time.time() - started, 6)

print(sentinel + json.dumps(payload, sort_keys=True))
'''


def text_tail(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[-limit:]
    return str(value)[-limit:]


def parse_payload(stdout: Any) -> dict[str, Any] | None:
    text = text_tail(stdout, limit=20000)
    for line in reversed(text.splitlines()):
        if SENTINEL in line:
            try:
                return json.loads(line.split(SENTINEL, 1)[1])
            except json.JSONDecodeError:
                return None
    return None


def run_metadata_probe(env_id: str, *, timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", metadata_code(), SENTINEL, env_id],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        parsed = parse_payload(exc.stdout)
        if parsed is not None:
            parsed["subprocess_timeout"] = True
            parsed["subprocess_returncode"] = None
            parsed["stdout_tail"] = text_tail(exc.stdout)
            parsed["stderr_tail"] = text_tail(exc.stderr)
            parsed["timed_out_after_result"] = True
            return parsed
        return {
            "env_id": env_id,
            "made_env": False,
            "reset_ok": False,
            "closed": False,
            "elapsed_seconds": None,
            "error_type": "TimeoutExpired",
            "error": f"timed out after {timeout}s",
            "traceback_tail": "",
            "required_asset_ids": [],
            "missing_asset_ids": [],
            "metadata": {},
            "subprocess_timeout": True,
            "subprocess_returncode": None,
            "stdout_tail": text_tail(exc.stdout),
            "stderr_tail": text_tail(exc.stderr),
        }
    parsed = parse_payload(proc.stdout)
    if parsed is None:
        return {
            "env_id": env_id,
            "made_env": False,
            "reset_ok": False,
            "closed": False,
            "elapsed_seconds": None,
            "error_type": "MissingProbeResult",
            "error": "subprocess did not emit the expected probe result",
            "traceback_tail": "",
            "required_asset_ids": [],
            "missing_asset_ids": [],
            "metadata": {},
            "subprocess_timeout": False,
            "subprocess_returncode": proc.returncode,
            "stdout_tail": text_tail(proc.stdout),
            "stderr_tail": text_tail(proc.stderr),
        }
    parsed["subprocess_timeout"] = False
    parsed["subprocess_returncode"] = proc.returncode
    parsed["stdout_tail"] = text_tail(proc.stdout)
    parsed["stderr_tail"] = text_tail(proc.stderr)
    return parsed


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def rounded_unique(values: list[Any], *, ndigits: int = 8) -> list[Any]:
    out = []
    for value in values:
        if value in ("", None):
            continue
        try:
            value = round(float(value), ndigits)
        except Exception:
            pass
        if value not in out:
            out.append(value)
    return out


def summarize_primary_timing(records: list[dict[str, Any]], primary_envs: set[str]) -> dict[str, Any]:
    primary = [record for record in records if record.get("env_id") in primary_envs and record.get("reset_ok") is True]
    metadata = [record.get("metadata", {}) for record in primary if isinstance(record.get("metadata"), dict)]
    return {
        "primary_metadata_env_count": len(metadata),
        "sim_freq_hz_values": rounded_unique([item.get("sim_freq_hz") for item in metadata]),
        "control_freq_hz_values": rounded_unique([item.get("control_freq_hz") for item in metadata]),
        "sim_timestep_seconds_values": rounded_unique([item.get("sim_timestep_seconds") for item in metadata]),
        "control_timestep_seconds_values": rounded_unique([item.get("control_timestep_seconds") for item in metadata]),
        "scene_timestep_seconds_values": rounded_unique([item.get("scene_timestep_seconds") for item in metadata]),
        "derived_substeps_per_control_step_values": rounded_unique([item.get("derived_substeps_per_control_step") for item in metadata]),
        "scene_backend_types": sorted({str(item.get("scene_backend_type", "")) for item in metadata if item.get("scene_backend_type")}),
        "agent_uids": sorted({str(item.get("agent_uid", "")) for item in metadata if item.get("agent_uid")}),
        "controller_types": sorted({str(item.get("controller_type", "")) for item in metadata if item.get("controller_type")}),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    binding_file = read_json(args.binding_file)
    bindings = clean_bindings(binding_file)
    env_to_roles: dict[str, dict[str, list[str]]] = {}
    for binding in bindings:
        primary = binding["primary_env_id"]
        env_to_roles.setdefault(primary, {"primary_for": [], "support_for": []})["primary_for"].append(binding["task_family"])
        for env_id in binding["support_env_ids"]:
            env_to_roles.setdefault(env_id, {"primary_for": [], "support_for": []})["support_for"].append(binding["task_family"])

    records: list[dict[str, Any]] = []
    for env_id in sorted(env_to_roles):
        record = run_metadata_probe(env_id, timeout=args.timeout_seconds)
        record["primary_for"] = sorted(env_to_roles[env_id]["primary_for"])
        record["support_for"] = sorted(env_to_roles[env_id]["support_for"])
        records.append(record)

    primary_envs = {binding["primary_env_id"] for binding in bindings}
    primary_records = [record for record in records if record.get("env_id") in primary_envs]
    primary_metadata_missing = sorted(record["env_id"] for record in primary_records if record.get("reset_ok") is not True)
    support_metadata_missing = sorted(
        record["env_id"] for record in records if record.get("env_id") not in primary_envs and record.get("reset_ok") is not True
    )
    timing_summary = summarize_primary_timing(records, primary_envs)
    missing_asset_ids = sorted({asset for record in records for asset in record.get("missing_asset_ids", []) or []})

    checks: list[dict[str, Any]] = []
    add_check(checks, "probe_is_non_evidence", True, "not_external_evidence=True")
    add_check(
        checks,
        "binding_file_ready",
        binding_file.get("version") == "maniskill_task_bindings_v1"
        and binding_file.get("not_external_evidence") is True
        and len(bindings) >= 4,
        f"version={binding_file.get('version')!r}, bindings={len(bindings)}",
    )
    add_check(
        checks,
        "metadata_attempted_all_bound_envs",
        len(records) == len(env_to_roles) and len(records) >= 4,
        f"attempted={len(records)}, expected={len(env_to_roles)}",
    )
    add_check(
        checks,
        "primary_metadata_readiness_reported",
        isinstance(primary_metadata_missing, list),
        f"primary_metadata_missing={primary_metadata_missing}",
    )
    add_check(
        checks,
        "timing_summary_reported",
        isinstance(timing_summary.get("sim_timestep_seconds_values"), list)
        and isinstance(timing_summary.get("derived_substeps_per_control_step_values"), list),
        json.dumps(timing_summary, sort_keys=True),
    )
    add_check(
        checks,
        "asset_requirements_reported",
        isinstance(missing_asset_ids, list)
        and all("required_asset_ids" in record and "missing_asset_ids" in record for record in records),
        f"missing_asset_ids={missing_asset_ids}",
    )
    add_check(
        checks,
        "strict_evidence_remains_false",
        True,
        "metadata probing cannot satisfy fidelity acceptance, rollout logs, videos, or manifest evidence",
    )

    passed = all(check["passed"] for check in checks)
    strict_metadata_ready = passed and not primary_metadata_missing
    return {
        "version": VERSION,
        "passed": passed,
        "strict": bool(args.strict),
        "not_external_evidence": True,
        "metadata_probe_ready": passed,
        "strict_metadata_ready": strict_metadata_ready,
        "accepted_fidelity_ready": False,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "binding_file": rel(args.binding_file),
        "timeout_seconds": int(args.timeout_seconds),
        "env_count": len(records),
        "primary_env_count": len(primary_records),
        "primary_metadata_missing": primary_metadata_missing,
        "support_metadata_missing": support_metadata_missing,
        "missing_asset_ids": missing_asset_ids,
        "primary_timing_summary": timing_summary,
        "env_records": records,
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# ManiSkill Fidelity Metadata Probe",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Metadata probe ready: `{str(payload['metadata_probe_ready']).lower()}`.",
        f"Strict metadata ready: `{str(payload['strict_metadata_ready']).lower()}`.",
        f"Accepted fidelity ready: `{str(payload['accepted_fidelity_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "This probe records platform timing, scene/backend, observation, controller, and asset metadata for the bound ManiSkill/SAPIEN task candidates. It is not rollout evidence and does not replace independent operator fidelity acceptance.",
        "",
        "## Primary Timing Summary",
        "",
        f"- sim_freq_hz_values: `{payload['primary_timing_summary']['sim_freq_hz_values']}`",
        f"- control_freq_hz_values: `{payload['primary_timing_summary']['control_freq_hz_values']}`",
        f"- sim_timestep_seconds_values: `{payload['primary_timing_summary']['sim_timestep_seconds_values']}`",
        f"- control_timestep_seconds_values: `{payload['primary_timing_summary']['control_timestep_seconds_values']}`",
        f"- derived_substeps_per_control_step_values: `{payload['primary_timing_summary']['derived_substeps_per_control_step_values']}`",
        f"- scene_backend_types: `{payload['primary_timing_summary']['scene_backend_types']}`",
        "",
        "## Environment Records",
        "",
        "| Env ID | Primary for | Support for | Reset | sim dt | control dt | substeps | backend | agent | info keys | Missing assets |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for record in payload["env_records"]:
        metadata = record.get("metadata", {}) if isinstance(record.get("metadata"), dict) else {}
        primary = ", ".join(record.get("primary_for", []) or []) or "none"
        support = ", ".join(record.get("support_for", []) or []) or "none"
        info_keys = ", ".join(metadata.get("info_keys", []) or []) or "none"
        missing_assets = ", ".join(record.get("missing_asset_ids", []) or []) or "none"
        lines.append(
            f"| `{record['env_id']}` | `{primary}` | `{support}` | `{record.get('reset_ok')}` | "
            f"`{metadata.get('sim_timestep_seconds', '')}` | `{metadata.get('control_timestep_seconds', '')}` | "
            f"`{metadata.get('derived_substeps_per_control_step', '')}` | `{metadata.get('scene_backend_type', '')}` | "
            f"`{metadata.get('agent_uid', '')}` | `{info_keys}` | `{missing_assets}` |"
        )
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-evidence ManiSkill/SAPIEN fidelity metadata probe.")
    parser.add_argument("--binding-file", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless every primary bound env emits reset metadata.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "ManiSkill fidelity metadata probe: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"strict_metadata_ready={payload['strict_metadata_ready']}; "
        f"primary_metadata_missing={payload['primary_metadata_missing']}; "
        f"not_evidence={payload['not_external_evidence']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] and (not args.strict or payload["strict_metadata_ready"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
