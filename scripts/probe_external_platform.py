from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"
OUT_JSON = RESULTS / "external_platform_probe.json"
OUT_MD = RESULTS / "external_platform_probe.md"

VERSION = "external_platform_probe_v1"
PRIMARY_ROUTE = "maniskill_sapien_primary"
PRIMARY_PACKAGES = {"mani_skill", "sapien", "torch", "gymnasium"}
PACKAGE_SPECS = [
    {
        "name": "mani_skill",
        "module": "mani_skill",
        "distributions": ["mani_skill", "mani-skill", "mani_skill2", "mani-skill2"],
        "route": "primary",
    },
    {
        "name": "sapien",
        "module": "sapien",
        "distributions": ["sapien", "sapien-python"],
        "route": "primary",
    },
    {
        "name": "torch",
        "module": "torch",
        "distributions": ["torch"],
        "route": "primary",
    },
    {
        "name": "gymnasium",
        "module": "gymnasium",
        "distributions": ["gymnasium"],
        "route": "primary",
    },
    {
        "name": "mujoco",
        "module": "mujoco",
        "distributions": ["mujoco"],
        "route": "secondary",
    },
    {
        "name": "robosuite",
        "module": "robosuite",
        "distributions": ["robosuite"],
        "route": "secondary",
    },
    {
        "name": "isaacsim",
        "module": "isaacsim",
        "distributions": ["isaacsim", "isaac-sim"],
        "route": "secondary",
    },
    {
        "name": "isaaclab",
        "module": "isaaclab",
        "distributions": ["isaaclab", "isaac-lab"],
        "route": "secondary",
    },
]
HASH_PATHS = [
    EXTERNAL / "fidelity_acceptance_template.json",
    EXTERNAL / "config_schema_v1.json",
    EXTERNAL / "maniskill_task_bindings.json",
    EXTERNAL / "runner" / "backend_contract.py",
    EXTERNAL / "runner" / "real_collection_runner.py",
    EXTERNAL / "runner" / "backend_templates" / "maniskill_backend.py",
    EXTERNAL / "configs" / "peg_place_regrasp.json",
    EXTERNAL / "configs" / "drawer_to_pick_transfer.json",
    EXTERNAL / "configs" / "door_open_navigation.json",
    EXTERNAL / "configs" / "cable_route_insert.json",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run_command(command: list[str], *, timeout: int = 15, max_chars: int = 5000) -> dict[str, Any]:
    executable = command[0]
    if shutil.which(executable) is None:
        return {
            "command": command,
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"{executable} not found on PATH",
        }
    try:
        proc = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[:max_chars],
            "stderr": f"timed out after {timeout}s",
        }
    return {
        "command": command,
        "available": True,
        "returncode": proc.returncode,
        "stdout": proc.stdout[:max_chars],
        "stderr": proc.stderr[:max_chars],
    }


def distribution_version(candidates: list[str]) -> str | None:
    for name in candidates:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def package_status(spec: dict[str, Any]) -> dict[str, Any]:
    module = str(spec["module"])
    module_available = importlib.util.find_spec(module) is not None
    version = distribution_version(list(spec.get("distributions", []) or []))
    status: dict[str, Any] = {
        "module": module,
        "module_available": module_available,
        "distribution_version": version,
        "route": spec["route"],
    }
    if module == "torch" and module_available:
        try:
            import torch  # type: ignore

            status["torch_version"] = getattr(torch, "__version__", version)
            status["torch_cuda_version"] = getattr(getattr(torch, "version", None), "cuda", None)
            status["torch_cuda_available"] = bool(torch.cuda.is_available())
            status["torch_cuda_device_count"] = int(torch.cuda.device_count())
            if torch.cuda.is_available():
                status["torch_cuda_device_names"] = [
                    torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
                ]
        except Exception as exc:  # pragma: no cover - environment dependent
            status["torch_probe_error"] = repr(exc)
    return status


def repo_state() -> dict[str, Any]:
    commit = run_command(["git", "rev-parse", "HEAD"], timeout=10)
    branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=10)
    status = run_command(["git", "status", "--short"], timeout=10, max_chars=2000)
    return {
        "commit": commit["stdout"].strip() if commit.get("returncode") == 0 else "",
        "branch": branch["stdout"].strip() if branch.get("returncode") == 0 else "",
        "dirty_status_lines": [
            line for line in str(status.get("stdout", "")).splitlines() if line.strip()
        ],
        "git_commands": {
            "rev_parse_head": commit,
            "rev_parse_branch": branch,
            "status_short": status,
        },
    }


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_payload() -> dict[str, Any]:
    packages = {spec["name"]: package_status(spec) for spec in PACKAGE_SPECS}
    primary_missing = sorted(
        name for name in PRIMARY_PACKAGES if not packages.get(name, {}).get("module_available")
    )
    primary_route_install_ready = not primary_missing
    commands = {
        "nvidia_smi": run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
            timeout=15,
        ),
        "vulkaninfo_summary": run_command(["vulkaninfo", "--summary"], timeout=15),
    }
    hashes = {
        rel(path): {
            "exists": path.exists(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        }
        for path in HASH_PATHS
    }
    environment = {
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "relevant_environment_variables": {
            key: os.environ.get(key, "")
            for key in (
                "CUDA_VISIBLE_DEVICES",
                "NVIDIA_VISIBLE_DEVICES",
                "VK_ICD_FILENAMES",
                "SAPIEN_RENDERER_DEVICE",
                "PYTHONPATH",
            )
            if os.environ.get(key)
        },
    }
    repo = repo_state()

    checks: list[dict[str, Any]] = []
    add_check(checks, "probe_is_non_evidence", True, "not_external_evidence=True")
    add_check(checks, "primary_route_declared", PRIMARY_ROUTE == "maniskill_sapien_primary", PRIMARY_ROUTE)
    add_check(
        checks,
        "primary_packages_checked",
        PRIMARY_PACKAGES <= set(packages),
        f"checked={sorted(packages)}",
    )
    add_check(
        checks,
        "primary_install_readiness_reported",
        isinstance(primary_route_install_ready, bool),
        f"primary_missing={primary_missing}",
    )
    add_check(
        checks,
        "repo_commit_reported",
        bool(repo.get("commit")),
        f"commit={repo.get('commit')!r}",
    )
    add_check(
        checks,
        "required_hashes_recorded",
        all(record.get("exists") and record.get("sha256") for record in hashes.values()),
        f"missing={[path for path, record in hashes.items() if not record.get('sha256')]}",
    )
    add_check(
        checks,
        "gpu_renderer_commands_attempted",
        {"nvidia_smi", "vulkaninfo_summary"} <= set(commands),
        f"commands={sorted(commands)}",
    )
    add_check(
        checks,
        "strict_evidence_remains_false",
        True,
        "probe cannot satisfy external fidelity or rollout evidence",
    )

    return {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "platform_probe_ready": all(check["passed"] for check in checks),
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "primary_route": PRIMARY_ROUTE,
        "primary_route_install_ready": primary_route_install_ready,
        "primary_route_missing_packages": primary_missing,
        "environment": environment,
        "packages": packages,
        "gpu_renderer_probe": commands,
        "repo": repo,
        "tracked_hashes": hashes,
        "operator_next_steps": [
            "Run this probe on the selected external GPU workstation.",
            "If primary_route_install_ready is false, install/repair ManiSkill, SAPIEN, Torch, and Gymnasium before backend qualification.",
            "Copy exact package, GPU, renderer, code commit, config hash, and backend hash values into external_validation/fidelity_acceptance.json.",
            "Then run python scripts\\audit_external_fidelity_acceptance.py --strict and python scripts\\audit_external_collection_readiness.py --strict with the real backend.",
        ],
        "strict_operator_command": "python scripts\\probe_external_platform.py --strict",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_md(payload: dict[str, Any], md_out: Path) -> None:
    packages = payload["packages"]
    lines = [
        "# External Platform Probe",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Primary route: `{payload['primary_route']}`.",
        f"Primary route install ready: `{str(payload['primary_route_install_ready']).lower()}`.",
        f"Strict fidelity evidence ready: `{str(payload['strict_fidelity_evidence_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "This probe records operator-machine environment facts for the independent public-simulator route. It is not rollout evidence and cannot make the paper submission-ready by itself.",
        "",
        "## Primary Package Status",
        "",
    ]
    for name in sorted(PRIMARY_PACKAGES):
        item = packages.get(name, {})
        lines.append(
            f"- `{name}`: module_available=`{str(item.get('module_available')).lower()}`, "
            f"version=`{item.get('distribution_version') or item.get('torch_version') or 'unknown'}`"
        )
    if payload["primary_route_missing_packages"]:
        lines.extend(["", "Missing primary packages:"])
        for name in payload["primary_route_missing_packages"]:
            lines.append(f"- `{name}`")
    lines.extend(["", "## Environment", ""])
    env = payload["environment"]
    for key in ("python_executable", "python_version", "platform", "machine"):
        lines.append(f"- `{key}`: `{env.get(key, '')}`")
    lines.extend(["", "## GPU/Renderer Commands", ""])
    for name, result in payload["gpu_renderer_probe"].items():
        lines.append(
            f"- `{name}`: available=`{str(result.get('available')).lower()}`, returncode=`{result.get('returncode')}`"
        )
    lines.extend(["", "## Operator Next Steps", ""])
    for step in payload["operator_next_steps"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit nonzero unless the primary ManiSkill/SAPIEN route appears installed")
    parser.add_argument("--json-out", default=str(OUT_JSON))
    parser.add_argument("--md-out", default=str(OUT_MD))
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload()
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload, md_out)

    print(
        "External platform probe: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"primary_route_install_ready={payload['primary_route_install_ready']}; "
        f"not_evidence=True"
    )
    print(f"Wrote {json_out}")
    print(f"Wrote {md_out}")
    if not payload["passed"]:
        return 1
    if args.strict and not payload["primary_route_install_ready"]:
        print("Strict platform probe failed: primary ManiSkill/SAPIEN route is not install-ready on this machine.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
