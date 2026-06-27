from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_BINDINGS = EXTERNAL / "maniskill_task_bindings.json"
OUT_JSON = RESULTS / "maniskill_env_smoke_probe.json"
OUT_MD = RESULTS / "maniskill_env_smoke_probe.md"

VERSION = "maniskill_env_smoke_probe_v1"
SENTINEL = "PAPER119_ENV_SMOKE_RESULT "


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def clean_bindings(bindings: dict[str, Any]) -> list[dict[str, Any]]:
    raw = bindings.get("bindings", [])
    if not isinstance(raw, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        task = str(item.get("task_family", "")).strip()
        primary = str(item.get("primary_env_id", "")).strip()
        if not task or not primary:
            continue
        support = item.get("support_env_ids", [])
        support = support if isinstance(support, list) else []
        cleaned.append(
            {
                "task_family": task,
                "primary_env_id": primary,
                "support_env_ids": [str(env_id).strip() for env_id in support if str(env_id).strip()],
                "binding_strength": str(item.get("binding_strength", "")).strip(),
            }
        )
    return cleaned


def smoke_code() -> str:
    return r'''
import json
import sys
import time
import traceback

sentinel = sys.argv[1]
env_ids = sys.argv[2:]
records = []
try:
    import gymnasium as gym
    import mani_skill  # noqa: F401
    from mani_skill.utils import assets
    from mani_skill.utils.registration import REGISTERED_ENVS
    import_error = ""
except Exception as exc:  # noqa: BLE001
    gym = None
    assets = None
    REGISTERED_ENVS = {}
    import_error = f"{type(exc).__name__}: {exc}"

for env_id in env_ids:
    started = time.time()
    required_asset_ids = []
    missing_asset_ids = []
    try:
        env_spec = REGISTERED_ENVS.get(env_id) if isinstance(REGISTERED_ENVS, dict) else None
        for asset_id in list(getattr(env_spec, "asset_download_ids", []) or []):
            required_asset_ids.append(str(asset_id))
            if assets is None:
                missing_asset_ids.append(str(asset_id))
                continue
            if asset_id in assets.DATA_GROUPS:
                for data_source_id in assets.expand_data_group_into_individual_data_source_ids(asset_id):
                    if not assets.is_data_source_downloaded(data_source_id):
                        missing_asset_ids.append(str(asset_id))
                        break
            elif asset_id in assets.DATA_SOURCES and not assets.is_data_source_downloaded(asset_id):
                missing_asset_ids.append(str(asset_id))
    except Exception:
        pass
    payload = {
        "env_id": env_id,
        "made_env": False,
        "reset_ok": False,
        "closed": False,
        "elapsed_seconds": None,
        "observation_space": "",
        "observation_type": "",
        "observation_shape": "",
        "info_keys": [],
        "required_asset_ids": sorted(set(required_asset_ids)),
        "missing_asset_ids": sorted(set(missing_asset_ids)),
        "error_type": "",
        "error": "",
        "traceback_tail": "",
    }
    env = None
    try:
        if gym is None:
            raise RuntimeError(import_error or "gymnasium/mani_skill import failed")
        env = gym.make(env_id, obs_mode="state")
        payload["made_env"] = True
        payload["observation_space"] = str(getattr(env, "observation_space", ""))
        obs, info = env.reset(seed=0)
        payload["reset_ok"] = True
        payload["observation_type"] = type(obs).__name__
        payload["observation_shape"] = str(getattr(obs, "shape", ""))
        payload["info_keys"] = sorted(str(key) for key in getattr(info, "keys", lambda: [])())
    except Exception as exc:  # noqa: BLE001
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        payload["traceback_tail"] = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-2000:]
    if env is not None:
        try:
            env.close()
            payload["closed"] = True
        except Exception as exc:  # noqa: BLE001
            payload["closed"] = False
            if not payload["error"]:
                payload["error_type"] = type(exc).__name__
                payload["error"] = str(exc)
    payload["elapsed_seconds"] = round(time.time() - started, 6)
    records.append(payload)
print(sentinel + json.dumps({"records": records}, sort_keys=True))
'''


def text_tail(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[-limit:]
    return str(value)[-limit:]


def parse_probe_payload(stdout: Any) -> dict[str, Any] | None:
    stdout_text = text_tail(stdout, limit=20000)
    for line in reversed(stdout_text.splitlines()):
        if SENTINEL in line:
            try:
                return json.loads(line.split(SENTINEL, 1)[1])
            except json.JSONDecodeError:
                return None
    return None


def normalize_probe_records(
    env_ids: list[str],
    records: Any,
    *,
    returncode: int | None,
    subprocess_timeout: bool,
    stdout_tail: str = "",
    stderr_tail: str = "",
    timed_out_after_result: bool = False,
) -> list[dict[str, Any]]:
    records = records if isinstance(records, list) else []
    by_id = {str(record.get("env_id", "")): record for record in records if isinstance(record, dict)}
    normalized = []
    for env_id in env_ids:
        record = by_id.get(env_id) or {
            "env_id": env_id,
            "made_env": False,
            "reset_ok": False,
            "closed": False,
            "error_type": "MissingEnvResult",
            "error": "subprocess did not emit a record for this env",
        }
        record.update(
            {
                "subprocess_returncode": returncode,
                "subprocess_timeout": subprocess_timeout,
                "stdout_tail": stdout_tail,
                "stderr_tail": stderr_tail,
            }
        )
        if timed_out_after_result:
            record["timed_out_after_result"] = True
        normalized.append(record)
    return normalized


def run_env_smoke_batch(env_ids: list[str], *, timeout: int) -> list[dict[str, Any]]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", smoke_code(), SENTINEL, *env_ids],
            input="",
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout_tail = text_tail(exc.stdout)
        stderr_tail = text_tail(exc.stderr)
        payload = parse_probe_payload(exc.stdout)
        if payload is not None:
            return normalize_probe_records(
                env_ids,
                payload.get("records", []),
                returncode=None,
                subprocess_timeout=True,
                stdout_tail=stdout_tail,
                stderr_tail=stderr_tail,
                timed_out_after_result=True,
            )
        return [{
            "env_id": env_id,
            "subprocess_returncode": None,
            "subprocess_timeout": True,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "made_env": False,
            "reset_ok": False,
            "closed": False,
            "error_type": "TimeoutExpired",
            "error": f"timed out after {timeout}s",
        } for env_id in env_ids]
    payload = parse_probe_payload(proc.stdout)
    if payload is None:
        return [{
            "env_id": env_id,
            "made_env": False,
            "reset_ok": False,
            "closed": False,
            "error_type": "MissingProbeResult",
            "error": "subprocess did not emit the expected probe result",
            "subprocess_returncode": proc.returncode,
            "subprocess_timeout": False,
            "stdout_tail": text_tail(proc.stdout),
            "stderr_tail": text_tail(proc.stderr),
        } for env_id in env_ids]
    return normalize_probe_records(
        env_ids,
        payload.get("records", []),
        returncode=proc.returncode,
        subprocess_timeout=False,
        stderr_tail=text_tail(proc.stderr),
    )


def run_env_smokes(env_ids: list[str], *, timeout: int) -> list[dict[str, Any]]:
    """Run each environment in its own subprocess.

    A missing asset or slow constructor for one ManiSkill environment should not
    make every other bound environment look broken. Per-env isolation also keeps
    stdout/stderr tails attributable to the actual failing candidate.
    """
    records: list[dict[str, Any]] = []
    for env_id in env_ids:
        records.extend(run_env_smoke_batch([env_id], timeout=timeout))
    return records


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    binding_file = read_json(args.binding_file)
    bindings = clean_bindings(binding_file)
    env_to_tasks: dict[str, list[str]] = {}
    for binding in bindings:
        for env_id in [binding["primary_env_id"], *binding["support_env_ids"]]:
            env_to_tasks.setdefault(env_id, []).append(binding["task_family"])

    env_records = []
    for smoke in run_env_smokes(sorted(env_to_tasks), timeout=args.timeout_seconds):
        env_id = str(smoke.get("env_id", ""))
        env_records.append(
            {
                **smoke,
                "task_families": sorted(env_to_tasks[env_id]),
                "is_primary_for": sorted(
                    binding["task_family"]
                    for binding in bindings
                    if binding["primary_env_id"] == env_id
                ),
                "is_support_for": sorted(
                    binding["task_family"]
                    for binding in bindings
                    if env_id in binding["support_env_ids"]
                ),
            }
        )

    primary_envs = {binding["primary_env_id"] for binding in bindings}
    primary_records = [record for record in env_records if record["env_id"] in primary_envs]
    primary_reset_missing = sorted(record["env_id"] for record in primary_records if record.get("reset_ok") is not True)
    support_reset_missing = sorted(
        record["env_id"] for record in env_records if record["env_id"] not in primary_envs and record.get("reset_ok") is not True
    )
    asset_related_failures = []
    missing_asset_ids_by_env: dict[str, list[str]] = {}
    for record in env_records:
        env_id = str(record["env_id"])
        record_text = " ".join(
            str(record.get(key, ""))
            for key in ("error_type", "error", "traceback_tail", "stdout_tail", "stderr_tail")
        ).lower()
        missing_asset_ids = sorted(str(asset_id) for asset_id in record.get("missing_asset_ids", []) or [])
        if missing_asset_ids:
            missing_asset_ids_by_env[env_id] = missing_asset_ids
        explicit_asset_failure = any(term in record_text for term in ("asset", "dataset", "partnet"))
        cabinet_prompt_failure = env_id.startswith("OpenCabinet") and "eof when reading a line" in record_text
        if missing_asset_ids or explicit_asset_failure or cabinet_prompt_failure:
            asset_related_failures.append(env_id)
    asset_related_failures = sorted(asset_related_failures)
    missing_asset_ids_all = sorted({asset_id for ids in missing_asset_ids_by_env.values() for asset_id in ids})
    asset_install_hints = [f"python -m mani_skill.utils.download_asset {asset_id} -y" for asset_id in missing_asset_ids_all]
    if not asset_install_hints:
        asset_install_hints = ["python -m mani_skill.utils.download_asset partnet_mobility_cabinet -y"]

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
        "smoke_attempted_all_bound_envs",
        len(env_records) == len(env_to_tasks) and len(env_records) >= 4,
        f"attempted={len(env_records)}, expected={len(env_to_tasks)}",
    )
    add_check(
        checks,
        "primary_reset_readiness_reported",
        isinstance(primary_reset_missing, list),
        f"primary_reset_missing={primary_reset_missing}",
    )
    add_check(
        checks,
        "asset_failures_reported",
        isinstance(asset_related_failures, list),
        f"asset_related_failures={asset_related_failures}, missing_asset_ids={missing_asset_ids_all}",
    )
    add_check(
        checks,
        "strict_evidence_remains_false",
        True,
        "environment construction/reset smoke tests are not rollout evidence",
    )

    passed = all(check["passed"] for check in checks)
    strict_env_smoke_ready = passed and not primary_reset_missing
    return {
        "version": VERSION,
        "passed": passed,
        "strict": bool(args.strict),
        "not_external_evidence": True,
        "env_smoke_probe_ready": passed,
        "strict_env_smoke_ready": strict_env_smoke_ready,
        "accepted_fidelity_ready": False,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "binding_file": rel(args.binding_file),
        "timeout_seconds": int(args.timeout_seconds),
        "env_count": len(env_records),
        "primary_env_count": len(primary_records),
        "primary_reset_missing": primary_reset_missing,
        "support_reset_missing": support_reset_missing,
        "asset_related_failures": asset_related_failures,
        "missing_asset_ids": missing_asset_ids_all,
        "missing_asset_ids_by_env": missing_asset_ids_by_env,
        "asset_install_hints": asset_install_hints,
        "asset_install_hint": "; ".join(asset_install_hints),
        "env_records": env_records,
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# ManiSkill Environment Smoke Probe",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Environment smoke probe ready: `{str(payload['env_smoke_probe_ready']).lower()}`.",
        f"Strict env smoke ready: `{str(payload['strict_env_smoke_ready']).lower()}`.",
        f"Accepted fidelity ready: `{str(payload['accepted_fidelity_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "This probe attempts construction and reset for the ManiSkill/SAPIEN environment candidates bound to Paper 119 task families. It is not rollout evidence and does not replace backend qualification, operator fidelity acceptance, videos, logs, manifests, or strict evidence audits.",
        "",
        f"Asset install hint: `{payload['asset_install_hint']}`",
        f"Missing asset IDs: `{payload.get('missing_asset_ids', [])}`",
        "",
        "## Environment Records",
        "",
        "| Env ID | Primary for | Support for | Missing assets | Made | Reset | Error |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in payload["env_records"]:
        primary = ", ".join(record.get("is_primary_for", [])) or "none"
        support = ", ".join(record.get("is_support_for", [])) or "none"
        missing_assets = ", ".join(record.get("missing_asset_ids", []) or []) or "none"
        error = str(record.get("error") or record.get("error_type") or "")
        error = error.replace("\n", " ")[:120]
        lines.append(
            f"| `{record['env_id']}` | `{primary}` | `{support}` | `{missing_assets}` | `{record.get('made_env')}` | `{record.get('reset_ok')}` | {error} |"
        )
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-evidence ManiSkill environment construction/reset smoke probe.")
    parser.add_argument("--binding-file", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless every primary bound environment constructs and resets.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "ManiSkill env smoke probe: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"strict_env_smoke_ready={payload['strict_env_smoke_ready']}; "
        f"primary_reset_missing={payload['primary_reset_missing']}; "
        f"not_evidence={payload['not_external_evidence']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] and (not args.strict or payload["strict_env_smoke_ready"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
