from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

DRAFT_JSON = EXTERNAL / "fidelity_acceptance_draft.json"
DRAFT_MD = EXTERNAL / "fidelity_acceptance_draft.md"
AUDIT_JSON = RESULTS / "external_fidelity_acceptance_draft_audit.json"
AUDIT_MD = RESULTS / "external_fidelity_acceptance_draft_audit.md"

DRAFT_VERSION = "paper119_fidelity_acceptance_draft_v1"
AUDIT_VERSION = "external_fidelity_acceptance_draft_audit_v1"
REAL_ACCEPTANCE_PATH = "external_validation/fidelity_acceptance.json"
REAL_MANIFEST_PATH = "external_validation/manifest.json"

REQUIRED_TASKS = {
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
}

DECLARED_SUPPORT_ASSET_IDS = ("oakink-v2", "ycb")

REMAINING_OPERATOR_INPUTS = [
    "independent_operator_identity",
    "accepted_external_collection_machine",
    "contact_solver_and_friction_model",
    "timestep_and_substeps_per_control_step",
    "paired_reset_replay_verification",
    "real_or_benchmark_calibration_basis",
    "task_binding_accept_or_replace_decision",
    "acceptance_gate_signoff",
    "manifest_declares_fidelity_acceptance_path",
    "real_rollout_logs_videos_and_release_hashes",
]

PROMOTION_COMMANDS = [
    "copy external_validation\\fidelity_acceptance_draft.json external_validation\\fidelity_acceptance.json",
    "edit external_validation\\fidelity_acceptance.json: change version to paper119_fidelity_acceptance_v1, remove draft_only, fill every remaining operator input, and set gates only after evidence exists",
    "ensure external_validation/manifest.json declares fidelity_acceptance_path=external_validation/fidelity_acceptance.json together with real logs, videos, configs, checkpoints, and method hashes",
    "python scripts\\build_external_manifest.py --write --check-video-paths",
    "python scripts\\audit_external_fidelity_acceptance.py --strict",
    "python scripts\\audit_external_collection_readiness.py --strict --backend-module external_validation\\runner\\maniskill_reference_backend.py --task-config-dir external_validation\\configs --run-id <specific_run_id> --unsealed-alias-map",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def has_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_tree(path: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(child for child in path.rglob("*") if child.is_file())
    for child in files:
        digest.update(child.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(child).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest().upper()


def run_git(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def env_status_by_id(env_smoke: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = env_smoke.get("env_records", [])
    records = records if isinstance(records, list) else []
    return {
        str(record.get("env_id", "")): record
        for record in records
        if isinstance(record, dict) and str(record.get("env_id", ""))
    }


def task_bindings(binding_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bindings = binding_payload.get("bindings", [])
    bindings = bindings if isinstance(bindings, list) else []
    return {
        str(binding.get("task_family", "")): binding
        for binding in bindings
        if isinstance(binding, dict) and str(binding.get("task_family", ""))
    }


def config_hashes(platform_probe: dict[str, Any]) -> dict[str, str]:
    tracked = platform_probe.get("tracked_hashes", {})
    tracked = tracked if isinstance(tracked, dict) else {}
    hashes: dict[str, str] = {}
    for task in sorted(REQUIRED_TASKS):
        path = f"external_validation/configs/{task}.json"
        record = tracked.get(path, {})
        if isinstance(record, dict) and has_sha(record.get("sha256")):
            hashes[task] = str(record["sha256"]).upper()
    return hashes


def build_task_fidelity(
    template: dict[str, Any],
    binding_payload: dict[str, Any],
    env_smoke: dict[str, Any],
    config_hash_by_task: dict[str, str],
) -> list[dict[str, Any]]:
    template_tasks = template.get("task_fidelity", [])
    template_tasks = template_tasks if isinstance(template_tasks, list) else []
    bindings = task_bindings(binding_payload)
    envs = env_status_by_id(env_smoke)
    result: list[dict[str, Any]] = []
    for item in template_tasks:
        if not isinstance(item, dict):
            continue
        task = str(item.get("task_family", ""))
        binding = bindings.get(task, {})
        primary_env_id = str(binding.get("primary_env_id", ""))
        env_record = envs.get(primary_env_id, {})
        support_env_ids = list(binding.get("support_env_ids", []) or [])
        support_status = {
            env_id: {
                "reset_ok": bool(envs.get(env_id, {}).get("reset_ok")),
                "missing_asset_ids": list(envs.get(env_id, {}).get("missing_asset_ids", []) or []),
            }
            for env_id in support_env_ids
        }
        merged = dict(item)
        merged.update(
            {
                "primary_env_id": primary_env_id,
                "support_env_ids": support_env_ids,
                "binding_strength": binding.get("binding_strength", ""),
                "binding_rationale": binding.get("rationale", ""),
                "requires_operator_fidelity_acceptance": True,
                "primary_env_smoke_recorded": bool(env_record),
                "primary_env_reset_ok": bool(env_record.get("reset_ok")),
                "primary_observation_shape": env_record.get("observation_shape", ""),
                "primary_info_keys": list(env_record.get("info_keys", []) or []),
                "support_env_status": support_status,
                "config_path": f"external_validation/configs/{task}.json",
                "config_sha256": config_hash_by_task.get(task, ""),
            }
        )
        result.append(merged)
    return result


def build_draft() -> dict[str, Any]:
    template = read_json(EXTERNAL / "fidelity_acceptance_template.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    backend = read_json(RESULTS / "maniskill_backend_readiness_audit.json")
    reference_preflight = read_json(RESULTS / "maniskill_reference_collection_preflight_audit.json")
    env_smoke = read_json(RESULTS / "maniskill_env_smoke_probe.json")
    bindings = read_json(EXTERNAL / "maniskill_task_bindings.json")

    backend_platform = backend.get("platform_provenance", {})
    backend_platform = backend_platform if isinstance(backend_platform, dict) else {}
    packages = platform_probe.get("packages", {})
    packages = packages if isinstance(packages, dict) else {}
    config_hash_by_task = config_hashes(platform_probe)
    tracked_hashes = platform_probe.get("tracked_hashes", {})
    tracked_hashes = tracked_hashes if isinstance(tracked_hashes, dict) else {}
    repo = platform_probe.get("repo", {})
    repo = repo if isinstance(repo, dict) else {}
    current_commit = run_git(["rev-parse", "HEAD"]) or str(repo.get("commit", ""))
    dirty_status = [line for line in run_git(["status", "--short"]).splitlines() if line.strip()]
    backend_hash = str(backend_platform.get("backend_module_sha256", "")).upper()
    skill_library_hash = sha256_tree(EXTERNAL / "baselines")
    detected_missing_asset_ids = sorted(set(env_smoke.get("missing_asset_ids", []) or []))
    support_asset_ids = sorted(set(detected_missing_asset_ids).union(DECLARED_SUPPORT_ASSET_IDS))

    platform = {
        "platform_type": "high_fidelity_sim",
        "platform_name": backend_platform.get("platform_name", "ManiSkill-SAPIEN-reference-backend"),
        "platform_version": (
            f"ManiSkill {packages.get('mani_skill', {}).get('distribution_version') or backend_platform.get('maniskill_version', 'unknown')}; "
            f"SAPIEN {packages.get('sapien', {}).get('distribution_version') or backend_platform.get('sapien_version', 'unknown')}"
        ),
        "physics_engine": f"SAPIEN {packages.get('sapien', {}).get('distribution_version') or backend_platform.get('sapien_version', 'unknown')} via ManiSkill",
        "contact_solver": "OPERATOR_VERIFY_CONTACT_SOLVER_AND_FRICTION_BEFORE_ACCEPTANCE",
        "timestep_seconds": "OPERATOR_VERIFY_TIMESTEP_SECONDS_BEFORE_ACCEPTANCE",
        "substeps_per_control_step": "OPERATOR_VERIFY_SUBSTEPS_BEFORE_ACCEPTANCE",
        "robot_model_source": "ManiSkill/SAPIEN task assets and Panda robot definitions; operator must record exact selected-task asset provenance before acceptance",
        "asset_sources": [
            "ManiSkill primary task assets for PegInsertionSide-v1, OpenCabinetDrawer-v1, OpenCabinetDoor-v1, and PullCubeTool-v1",
            "PartNet Mobility cabinet asset for OpenCabinetDrawer-v1/OpenCabinetDoor-v1 when required",
            f"Support assets not yet accepted for evidence: {', '.join(support_asset_ids)}",
        ],
        "sensor_modalities": ["state", "camera", "contact_or_force"],
        "state_observation_channels": [
            "terminal_state",
            "object_pose",
            "robot_pose",
            "task_info_success_or_contact_keys",
        ],
        "contact_or_force_channels": [
            "contact_events_or_task_contact_proxy",
            "normal_force_or_proxy_to_be_verified_by_operator",
        ],
    }

    qualification = dict(template.get("qualification", {}) or {})
    qualification.update(
        {
            "operator_independence_statement": "DRAFT ONLY: independent operator/lab must fill this after confirming they are not Jason, Haonan Chen, Yilun Du, or another target collaborator.",
            "contact_dynamics_justification": "DRAFT ONLY: primary ManiSkill/SAPIEN task bindings reset locally, but accepted contact/friction/substep details must be written by the operator before rollouts count.",
            "paired_reset_replay_test": "DRAFT ONLY: strict collection requires replaying the same scene, seed, skill pair, initial_state_hash, and terminal sample set across every method panel.",
            "real_or_benchmark_calibration_basis": "DRAFT ONLY: operator must name the real robot benchmark, simulator benchmark, calibration suite, or published environment standard used to justify high-fidelity status.",
            "known_limitations": "DRAFT ONLY: current local probe uses CPU fallback rendering; support assets oakink-v2/ycb are not needed for the primary route but remain explicit support-environment blockers.",
        }
    )

    gates = []
    for gate in template.get("acceptance_gates", []) or []:
        if not isinstance(gate, dict):
            continue
        new_gate = dict(gate)
        new_gate["status"] = "draft_unaccepted"
        new_gate["evidence"] = f"DRAFT ONLY: {gate.get('evidence', '')}"
        gates.append(new_gate)

    return {
        "version": DRAFT_VERSION,
        "not_external_evidence": True,
        "draft_only": True,
        "acceptance_ready": False,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "promotion_ready": False,
        "route": "high_fidelity_sim",
        "real_acceptance_path": REAL_ACCEPTANCE_PATH,
        "real_manifest_path": REAL_MANIFEST_PATH,
        "purpose": "Operator-editable draft for the tracked ManiSkill/SAPIEN route. This file pre-fills reproducible provenance anchors but cannot satisfy fidelity acceptance until independently completed, renamed, manifest-declared, and strict-audited.",
        "platform": platform,
        "qualification": qualification,
        "task_fidelity": build_task_fidelity(template, bindings, env_smoke, config_hash_by_task),
        "provenance": {
            "operator_name_or_lab": "DRAFT_OPERATOR_TO_FILL",
            "operator_not_target_collaborator": False,
            "date_locked": "DRAFT_NOT_LOCKED",
            "code_commit": current_commit,
            "repo_dirty_status_lines": dirty_status,
            "skill_library_hash": skill_library_hash,
            "backend_module": "external_validation/runner/maniskill_reference_backend.py",
            "backend_module_hash": backend_hash,
            "manifest_path": REAL_MANIFEST_PATH,
            "artifact_hash_policy": "sha256",
            "primary_route_install_ready": platform_probe.get("primary_route_install_ready") is True,
            "primary_env_smoke_recorded": env_smoke.get("env_smoke_probe_ready") is True,
            "primary_env_smoke_ready": env_smoke.get("strict_env_smoke_ready") is True,
            "primary_reset_missing": list(env_smoke.get("primary_reset_missing", []) or []),
            "reference_collection_preflight_blocking": list(reference_preflight.get("collection_blocking_missing", []) or []),
        },
        "prefilled_hashes": {
            "task_config_hashes": config_hash_by_task,
            "backend_module_sha256": backend_hash,
            "skill_library_hash": skill_library_hash,
            "tracked_probe_hashes": tracked_hashes,
        },
        "remaining_operator_inputs": REMAINING_OPERATOR_INPUTS,
        "acceptance_gates": gates,
        "promotion_commands": PROMOTION_COMMANDS,
        "source_reports": [
            "external_validation/fidelity_acceptance_template.json",
            "results/external_platform_probe.json",
            "results/maniskill_backend_readiness_audit.json",
            "results/maniskill_reference_collection_preflight_audit.json",
            "results/maniskill_env_smoke_probe.json",
            "external_validation/maniskill_task_bindings.json",
        ],
    }


def audit_draft(draft: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    task_fidelity = draft.get("task_fidelity", []) if isinstance(draft.get("task_fidelity"), list) else []
    task_names = {str(task.get("task_family", "")) for task in task_fidelity if isinstance(task, dict)}
    config_hashes = draft.get("prefilled_hashes", {}).get("task_config_hashes", {})
    config_hashes = config_hashes if isinstance(config_hashes, dict) else {}
    provenance = draft.get("provenance", {}) if isinstance(draft.get("provenance"), dict) else {}
    remaining = set(draft.get("remaining_operator_inputs", []) or [])
    gates = draft.get("acceptance_gates", []) if isinstance(draft.get("acceptance_gates"), list) else []
    command_text = "\n".join(draft.get("promotion_commands", []) or [])

    add_check(
        checks,
        "draft_is_non_evidence_and_fail_closed",
        draft.get("version") == DRAFT_VERSION
        and draft.get("not_external_evidence") is True
        and draft.get("draft_only") is True
        and draft.get("acceptance_ready") is False
        and draft.get("strict_fidelity_evidence_ready") is False
        and draft.get("strict_external_evidence_ready") is False
        and draft.get("promotion_ready") is False
        and draft.get("real_acceptance_path") == REAL_ACCEPTANCE_PATH,
        (
            f"version={draft.get('version')!r}, "
            f"draft_only={draft.get('draft_only')!r}, "
            f"acceptance_ready={draft.get('acceptance_ready')!r}"
        ),
    )
    add_check(
        checks,
        "candidate_platform_prefilled_from_reference_route",
        draft.get("platform", {}).get("platform_type") == "high_fidelity_sim"
        and "ManiSkill" in str(draft.get("platform", {}).get("platform_version", ""))
        and "SAPIEN" in str(draft.get("platform", {}).get("physics_engine", ""))
        and isinstance(provenance.get("primary_route_install_ready"), bool)
        and provenance.get("primary_env_smoke_recorded") is True,
        (
            f"platform_version={draft.get('platform', {}).get('platform_version')!r}, "
            f"primary_route_install_ready={provenance.get('primary_route_install_ready')!r}, "
            f"primary_env_smoke_recorded={provenance.get('primary_env_smoke_recorded')!r}, "
            f"primary_env_smoke_ready={provenance.get('primary_env_smoke_ready')!r}"
        ),
    )
    add_check(
        checks,
        "all_core_tasks_have_primary_env_status_and_config_hash",
        REQUIRED_TASKS <= task_names
        and all(
            isinstance(task, dict)
            and task.get("primary_env_smoke_recorded") is True
            and has_sha(task.get("config_sha256"))
            for task in task_fidelity
            if task.get("task_family") in REQUIRED_TASKS
        )
        and all(has_sha(config_hashes.get(task)) for task in REQUIRED_TASKS),
        f"tasks={sorted(task_names)}, hashes={config_hashes}",
    )
    add_check(
        checks,
        "support_asset_blockers_remain_visible",
        "oakink-v2" in " ".join(draft.get("platform", {}).get("asset_sources", []) or [])
        and "ycb" in " ".join(draft.get("platform", {}).get("asset_sources", []) or []),
        f"asset_sources={draft.get('platform', {}).get('asset_sources')!r}",
    )
    add_check(
        checks,
        "candidate_hashes_prefilled",
        has_sha(provenance.get("skill_library_hash"))
        and has_sha(provenance.get("backend_module_hash"))
        and has_sha(draft.get("prefilled_hashes", {}).get("skill_library_hash"))
        and has_sha(draft.get("prefilled_hashes", {}).get("backend_module_sha256"))
        and bool(provenance.get("code_commit")),
        (
            f"code_commit={provenance.get('code_commit')!r}, "
            f"skill_hash={provenance.get('skill_library_hash')!r}, "
            f"backend_hash={provenance.get('backend_module_hash')!r}"
        ),
    )
    add_check(
        checks,
        "remaining_operator_inputs_cover_fidelity_gate",
        set(REMAINING_OPERATOR_INPUTS) <= remaining,
        f"missing={sorted(set(REMAINING_OPERATOR_INPUTS) - remaining)}",
    )
    add_check(
        checks,
        "acceptance_gates_remain_unaccepted",
        len(gates) >= 5 and all(isinstance(gate, dict) and gate.get("status") == "draft_unaccepted" for gate in gates),
        f"gate_statuses={[gate.get('status') for gate in gates if isinstance(gate, dict)]}",
    )
    add_check(
        checks,
        "promotion_commands_require_real_file_manifest_and_strict_audits",
        REAL_ACCEPTANCE_PATH in command_text
        and REAL_MANIFEST_PATH in command_text
        and "paper119_fidelity_acceptance_v1" in command_text
        and "audit_external_fidelity_acceptance.py --strict" in command_text
        and "audit_external_collection_readiness.py --strict" in command_text,
        command_text,
    )
    add_check(
        checks,
        "no_real_acceptance_or_manifest_written",
        not (EXTERNAL / "fidelity_acceptance.json").exists()
        and not (EXTERNAL / "manifest.json").exists(),
        (
            f"acceptance_exists={(EXTERNAL / 'fidelity_acceptance.json').exists()}, "
            f"manifest_exists={(EXTERNAL / 'manifest.json').exists()}"
        ),
    )
    add_check(
        checks,
        "draft_files_written",
        DRAFT_JSON.exists() and DRAFT_MD.exists(),
        f"draft_json={DRAFT_JSON.exists()}, draft_md={DRAFT_MD.exists()}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "draft_ready": True,
        "acceptance_ready": False,
        "strict_fidelity_evidence_ready": False,
        "strict_external_evidence_ready": False,
        "remaining_operator_input_count": len(REMAINING_OPERATOR_INPUTS),
        "draft_path": rel(DRAFT_JSON),
        "draft_md_path": rel(DRAFT_MD),
        "real_acceptance_path": REAL_ACCEPTANCE_PATH,
        "real_manifest_path": REAL_MANIFEST_PATH,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_draft_md(draft: dict[str, Any]) -> None:
    platform = draft["platform"]
    provenance = draft["provenance"]
    lines = [
        "# External Fidelity Acceptance Draft",
        "",
        "Draft ready: `true`.",
        "Not evidence: `true`.",
        "Acceptance ready: `false`.",
        "Strict fidelity evidence ready: `false`.",
        "",
        "This is an operator-editable draft for the tracked ManiSkill/SAPIEN route. It pre-fills reproducible anchors from the current platform probe, backend readiness audit, task bindings, config hashes, and environment smoke probe. It is deliberately not accepted evidence.",
        "",
        "## Candidate Platform Snapshot",
        "",
        f"- Platform: `{platform['platform_name']}`",
        f"- Version: `{platform['platform_version']}`",
        f"- Physics engine: `{platform['physics_engine']}`",
        f"- Backend hash: `{provenance['backend_module_hash']}`",
        f"- Candidate skill-library hash: `{provenance['skill_library_hash']}`",
        f"- Code commit captured in draft: `{provenance['code_commit']}`",
        f"- Primary route install ready: `{str(provenance['primary_route_install_ready']).lower()}`",
        f"- Primary env smoke recorded: `{str(provenance['primary_env_smoke_recorded']).lower()}`",
        f"- Primary env smoke ready: `{str(provenance['primary_env_smoke_ready']).lower()}`",
        f"- Primary reset missing: `{provenance['primary_reset_missing']}`",
        "",
        "## Remaining Operator Inputs",
        "",
    ]
    for item in draft["remaining_operator_inputs"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Task Bindings", ""])
    for task in draft["task_fidelity"]:
        lines.append(
            f"- `{task['task_family']}`: primary `{task['primary_env_id']}`, "
            f"reset_ok=`{str(task['primary_env_reset_ok']).lower()}`, config_sha256=`{task['config_sha256']}`"
        )
    lines.extend(["", "## Acceptance Gates", ""])
    for gate in draft["acceptance_gates"]:
        lines.append(f"- `{gate['name']}`: `{gate['status']}`")
    lines.extend(["", "## Promotion Commands", ""])
    for command in draft["promotion_commands"]:
        lines.append(f"- `{command}`")
    DRAFT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Fidelity Acceptance Draft Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Draft ready: `{str(audit['draft_ready']).lower()}`.",
        f"Acceptance ready: `{str(audit['acceptance_ready']).lower()}`.",
        f"Remaining operator inputs: `{audit['remaining_operator_input_count']}`.",
        "",
        "This audit checks that the draft is useful as an operator intake artifact while remaining impossible to count as accepted fidelity evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    draft = build_draft()
    DRAFT_JSON.write_text(json.dumps(draft, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_draft_md(draft)

    audit = audit_draft(draft)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External fidelity acceptance draft: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"remaining_operator_inputs={audit['remaining_operator_input_count']}; "
        "not_evidence=True"
    )
    print(f"Wrote {DRAFT_JSON}")
    print(f"Wrote {DRAFT_MD}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
