from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_BINDINGS = EXTERNAL / "maniskill_task_bindings.json"
DEFAULT_CONFIG_DIR = EXTERNAL / "configs"
OUT_JSON = RESULTS / "maniskill_task_binding_probe.json"
OUT_MD = RESULTS / "maniskill_task_binding_probe.md"

VERSION = "maniskill_task_binding_probe_v1"


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


def distribution_version(name: str) -> str:
    for candidate in (name, name.replace("_", "-")):
        try:
            return importlib.metadata.version(candidate)
        except importlib.metadata.PackageNotFoundError:
            continue
    return ""


def inspect_registry() -> dict[str, Any]:
    status: dict[str, Any] = {
        "gymnasium_available": importlib.util.find_spec("gymnasium") is not None,
        "mani_skill_available": importlib.util.find_spec("mani_skill") is not None,
        "gymnasium_version": distribution_version("gymnasium"),
        "mani_skill_version": distribution_version("mani_skill"),
        "registry_inspected": False,
        "registry_env_ids": [],
        "import_error": "",
    }
    if not status["gymnasium_available"] or not status["mani_skill_available"]:
        return status
    try:
        import gymnasium as gym  # type: ignore
        import mani_skill  # noqa: F401  # type: ignore

        status["registry_env_ids"] = sorted(str(env_id) for env_id in gym.registry.keys())
        status["registry_inspected"] = True
    except Exception as exc:  # noqa: BLE001 - environment-dependent renderer/import failures are reported, not hidden.
        status["import_error"] = f"{type(exc).__name__}: {exc}"
    return status


def config_payloads(config_dir: Path) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    if not config_dir.exists():
        return payloads
    for path in sorted(config_dir.glob("*.json")):
        payload = read_json(path)
        task = str(payload.get("task_family", path.stem)).strip()
        if task:
            payloads[task] = payload
    return payloads


def clean_bindings(bindings: dict[str, Any]) -> list[dict[str, Any]]:
    raw = bindings.get("bindings", [])
    if not isinstance(raw, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        task_family = str(item.get("task_family", "")).strip()
        primary_env_id = str(item.get("primary_env_id", "")).strip()
        if not task_family or not primary_env_id:
            continue
        support_env_ids = item.get("support_env_ids", [])
        if not isinstance(support_env_ids, list):
            support_env_ids = []
        cleaned.append(
            {
                "task_family": task_family,
                "primary_env_id": primary_env_id,
                "support_env_ids": [str(env_id).strip() for env_id in support_env_ids if str(env_id).strip()],
                "binding_strength": str(item.get("binding_strength", "")).strip(),
                "requires_operator_fidelity_acceptance": item.get("requires_operator_fidelity_acceptance") is True,
                "rationale": str(item.get("rationale", "")).strip(),
            }
        )
    return cleaned


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    binding_file = read_json(args.binding_file)
    bindings = clean_bindings(binding_file)
    configs = config_payloads(args.config_dir)
    registry = inspect_registry()
    registry_envs = set(registry.get("registry_env_ids", []) or [])

    task_records: list[dict[str, Any]] = []
    for binding in bindings:
        task = binding["task_family"]
        config = configs.get(task, {})
        config_binding = config.get("backend_task_binding", {}) if isinstance(config, dict) else {}
        config_binding = config_binding if isinstance(config_binding, dict) else {}
        all_env_ids = [binding["primary_env_id"], *binding["support_env_ids"]]
        available = {env_id: (env_id in registry_envs if registry.get("registry_inspected") else None) for env_id in all_env_ids}
        task_records.append(
            {
                **binding,
                "config_path": rel(args.config_dir / f"{task}.json"),
                "config_exists": bool(config),
                "config_has_backend_task_binding": bool(config_binding),
                "config_primary_env_id": config_binding.get("primary_env_id", ""),
                "config_binding_matches_probe": config_binding.get("primary_env_id") == binding["primary_env_id"],
                "env_availability": available,
                "primary_env_available": available[binding["primary_env_id"]],
            }
        )

    collection_tasks = sorted(configs)
    binding_tasks = sorted(record["task_family"] for record in task_records)
    missing_task_bindings = sorted(set(collection_tasks) - set(binding_tasks))
    missing_configs = sorted(set(binding_tasks) - set(collection_tasks))
    primary_missing = sorted(
        record["primary_env_id"]
        for record in task_records
        if record["primary_env_available"] is False
    )
    records_needing_acceptance = sorted(
        record["task_family"]
        for record in task_records
        if record.get("requires_operator_fidelity_acceptance") is True
    )

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
        "task_bindings_cover_configs",
        not missing_task_bindings and not missing_configs and len(task_records) >= 4,
        f"missing_task_bindings={missing_task_bindings}, missing_configs={missing_configs}",
    )
    add_check(
        checks,
        "configs_embed_backend_task_bindings",
        all(record["config_has_backend_task_binding"] and record["config_binding_matches_probe"] for record in task_records),
        f"missing_or_mismatched={[record['task_family'] for record in task_records if not (record['config_has_backend_task_binding'] and record['config_binding_matches_probe'])]}",
    )
    add_check(
        checks,
        "registry_availability_reported",
        isinstance(registry.get("registry_inspected"), bool),
        f"registry_inspected={registry.get('registry_inspected')!r}, import_error={registry.get('import_error')!r}",
    )
    add_check(
        checks,
        "primary_env_availability_reported",
        all(record["primary_env_available"] in {True, False, None} for record in task_records),
        f"primary_missing={primary_missing}",
    )
    add_check(
        checks,
        "non_direct_bindings_require_operator_acceptance",
        all(
            record["requires_operator_fidelity_acceptance"] is True
            for record in task_records
            if record["binding_strength"] != "direct_contact_candidate"
        ),
        f"records_needing_acceptance={records_needing_acceptance}",
    )
    add_check(
        checks,
        "strict_evidence_remains_false",
        True,
        "task binding and registry inspection cannot satisfy fidelity acceptance or rollout evidence",
    )

    passed = all(check["passed"] for check in checks)
    strict_ready = (
        passed
        and registry.get("registry_inspected") is True
        and all(record["primary_env_available"] is True for record in task_records)
    )
    return {
        "version": VERSION,
        "passed": passed,
        "strict": bool(args.strict),
        "not_external_evidence": True,
        "task_binding_probe_ready": passed,
        "accepted_task_binding_ready": False,
        "strict_task_binding_install_ready": strict_ready,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "primary_route": binding_file.get("primary_route", "maniskill_sapien_primary"),
        "binding_file": rel(args.binding_file),
        "config_dir": rel(args.config_dir),
        "registry": registry,
        "task_records": task_records,
        "primary_missing_env_ids": primary_missing,
        "operator_acceptance_required_for": records_needing_acceptance,
        "checks": checks,
    }


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# ManiSkill Task Binding Probe",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Primary route: `{payload['primary_route']}`.",
        f"Registry inspected: `{str(payload['registry'].get('registry_inspected')).lower()}`.",
        f"Strict task-binding install ready: `{str(payload['strict_task_binding_install_ready']).lower()}`.",
        f"Accepted task binding ready: `{str(payload['accepted_task_binding_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "This probe binds Paper 119 task families to concrete ManiSkill/SAPIEN environment candidates and, when ManiSkill is installed, checks the local Gymnasium registry. It is not rollout evidence and does not replace operator fidelity acceptance.",
        "",
        "## Task Bindings",
        "",
        "| Task | Primary env | Support envs | Strength | Available |",
        "|---|---|---|---|---|",
    ]
    for record in payload["task_records"]:
        support = ", ".join(record["support_env_ids"]) if record["support_env_ids"] else "none"
        available = record["primary_env_available"]
        lines.append(
            f"| `{record['task_family']}` | `{record['primary_env_id']}` | `{support}` | `{record['binding_strength']}` | `{available}` |"
        )
    if payload.get("primary_missing_env_ids"):
        lines.extend(["", "## Missing Primary Env IDs", ""])
        for env_id in payload["primary_missing_env_ids"]:
            lines.append(f"- `{env_id}`")
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe ManiSkill task bindings for Paper 119 external validation.")
    parser.add_argument("--binding-file", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--config-dir", type=Path, default=DEFAULT_CONFIG_DIR)
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless all primary env IDs are visible in the installed ManiSkill registry.")
    args = parser.parse_args()

    RESULTS.mkdir(exist_ok=True)
    payload = build_payload(args)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "ManiSkill task binding probe: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"registry_inspected={payload['registry'].get('registry_inspected')}; "
        f"strict_install_ready={payload['strict_task_binding_install_ready']}; "
        f"not_evidence={payload['not_external_evidence']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] and (not args.strict or payload["strict_task_binding_install_ready"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
