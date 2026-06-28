from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "platform_onboarding_packet.json"
PACKET_MD = EXTERNAL / "platform_onboarding_packet.md"
AUDIT_JSON = RESULTS / "external_platform_onboarding_audit.json"
AUDIT_MD = RESULTS / "external_platform_onboarding_audit.md"

PACKET_VERSION = "external_platform_onboarding_v1"
AUDIT_VERSION = "external_platform_onboarding_audit_v1"
SOURCE_CHECK_DATE = "2026-06-27"

READINESS_BLOCKERS = [
    "manifest_backed_external_evidence",
    "raw_jsonl_metric_recompute",
    "real_task_configs",
    "independent_non_oracle_baselines",
]

PRIMARY_OFFICIAL_SOURCES = [
    {
        "name": "ManiSkill installation docs",
        "url": "https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html",
        "operator_note": "Official docs state the package is installed with pip and a system-compatible torch build.",
    },
    {
        "name": "SAPIEN documentation",
        "url": "https://sapien.ucsd.edu/docs/latest/index.html",
        "operator_note": "Record the exact SAPIEN version, renderer, contact solver settings, and GPU/Vulkan path used by the backend.",
    },
]

SECONDARY_OFFICIAL_SOURCES = [
    {
        "route_id": "mujoco_robosuite_cross_engine",
        "name": "robosuite installation docs",
        "url": "https://robosuite.ai/docs/installation.html",
    },
    {
        "route_id": "isaac_sim_lab_secondary",
        "name": "Isaac Sim installation docs",
        "url": "https://docs.isaacsim.omniverse.nvidia.com/6.0.0/installation/index.html",
    },
    {
        "route_id": "isaac_sim_lab_secondary",
        "name": "Isaac Lab local installation docs",
        "url": "https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html",
    },
]

PRIMARY_PROVENANCE_FIELDS = [
    "platform_name",
    "platform_version",
    "maniskill_version",
    "sapien_version",
    "python_version",
    "operating_system",
    "gpu_model",
    "gpu_driver",
    "vulkan_or_renderer_device",
    "physics_timestep",
    "contact_solver",
    "friction_model",
    "compliance_or_contact_regularization",
    "camera_intrinsics_and_resolution",
    "state_observation_keys",
    "contact_signal_keys",
    "asset_sources",
    "task_config_sha256",
    "backend_module_sha256",
    "skill_library_hash",
    "code_commit",
]

STRICT_COMMANDS = [
    r"python scripts\build_external_platform_onboarding.py",
    r"python scripts\probe_external_platform.py --strict",
    r"python scripts\probe_maniskill_task_bindings.py --strict",
    r"python scripts\probe_maniskill_env_smoke.py --strict",
    r"python scripts\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --alias-map external_validation\method_alias_map.json",
    r"python scripts\materialize_external_configs.py --platform-type high_fidelity_sim --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write",
    r"python scripts\audit_external_fidelity_acceptance.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence.py --strict",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path.relative_to(ROOT).as_posix()}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def route_by_id(route_audit: dict[str, Any], route_id: str) -> dict[str, Any]:
    for route in route_audit.get("routes", []) or []:
        if route.get("route_id") == route_id:
            return route
    return {}


def planned_tasks(collection_plan: dict[str, Any]) -> list[str]:
    return [
        str(task.get("task_family"))
        for task in collection_plan.get("tasks", []) or []
        if isinstance(task, dict) and task.get("task_family")
    ]


def task_binding_by_task(task_binding_probe: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = task_binding_probe.get("task_records", [])
    if not isinstance(records, list):
        return {}
    return {
        str(record.get("task_family")): record
        for record in records
        if isinstance(record, dict) and record.get("task_family")
    }


def build_packet(
    collection_plan: dict[str, Any],
    route_audit: dict[str, Any],
    analysis_audit: dict[str, Any],
    platform_probe: dict[str, Any],
    task_binding_probe: dict[str, Any],
    env_smoke_probe: dict[str, Any],
) -> dict[str, Any]:
    primary_route = route_by_id(route_audit, "maniskill_sapien_primary")
    tasks = planned_tasks(collection_plan)
    bindings_by_task = task_binding_by_task(task_binding_probe)
    task_onboarding = [
        {
            "task_family": task,
            "backend_task_binding": {
                "primary_env_id": bindings_by_task.get(task, {}).get("primary_env_id", ""),
                "support_env_ids": bindings_by_task.get(task, {}).get("support_env_ids", []),
                "binding_strength": bindings_by_task.get(task, {}).get("binding_strength", ""),
                "primary_env_available": bindings_by_task.get(task, {}).get("primary_env_available"),
                "requires_operator_fidelity_acceptance": bindings_by_task.get(task, {}).get("requires_operator_fidelity_acceptance", True),
            },
            "required_operator_files": [
                f"external_validation/configs/{task}.json",
                f"external_validation/logs/{task}.jsonl",
                f"external_validation/videos/{task}/",
            ],
            "must_document": [
                "reset sampler and paired initial-state hash rule",
                "terminal sample set construction",
                "camera/state/contact observation channels exposed to every method",
                "video export path and hash coverage",
                "task-specific fidelity risks and accepted approximations",
            ],
        }
        for task in tasks
    ]
    return {
        "version": PACKET_VERSION,
        "not_external_evidence": True,
        "platform_onboarding_ready": True,
        "strict_evidence_ready": False,
        "source_check_date": SOURCE_CHECK_DATE,
        "purpose": "Operator-facing onboarding contract for executing the non-Haonan public-simulator validation route without loosening the external evidence gates.",
        "source_reports": [
            rel(RESULTS / "external_collection_plan.json"),
            rel(RESULTS / "independent_validation_route_audit.json"),
            rel(RESULTS / "external_analysis_plan_audit.json"),
            rel(RESULTS / "external_platform_probe.json"),
            rel(EXTERNAL / "maniskill_task_bindings.json"),
            rel(RESULTS / "maniskill_task_binding_probe.json"),
            rel(RESULTS / "maniskill_env_smoke_probe.json"),
        ],
        "primary_route": primary_route.get("route_id", "maniskill_sapien_primary"),
        "primary_platform_family": primary_route.get("platform_family", "ManiSkill/SAPIEN"),
        "primary_route_independent_of_haonan": primary_route.get("independent_of_haonan") is True,
        "planned_records": collection_plan.get("total_required_records"),
        "planned_tasks": tasks,
        "readiness_blockers_addressed": READINESS_BLOCKERS,
        "official_sources": {
            "primary": PRIMARY_OFFICIAL_SOURCES,
            "secondary": SECONDARY_OFFICIAL_SOURCES,
        },
        "primary_install_probe": {
            "install_command_from_official_docs": "python -m pip install --upgrade mani_skill; python -m pip install torch torchvision torchaudio",
            "version_capture_command": "python -c \"import platform, torch, mani_skill, sapien; print(platform.platform()); print(torch.__version__); print(getattr(mani_skill, '__version__', 'unknown')); print(getattr(sapien, '__version__', 'unknown'))\"",
            "machine_probe_command": r"python scripts\probe_external_platform.py",
            "strict_machine_probe_command": r"python scripts\probe_external_platform.py --strict",
            "task_binding_probe_command": r"python scripts\probe_maniskill_task_bindings.py",
            "strict_task_binding_probe_command": r"python scripts\probe_maniskill_task_bindings.py --strict",
            "env_smoke_probe_command": r"python scripts\probe_maniskill_env_smoke.py",
            "strict_env_smoke_probe_command": r"python scripts\probe_maniskill_env_smoke.py --strict",
            "latest_task_binding_probe_report": "results/maniskill_task_binding_probe.json",
            "latest_task_binding_install_ready": task_binding_probe.get("strict_task_binding_install_ready") is True,
            "latest_task_binding_missing_env_ids": list(task_binding_probe.get("primary_missing_env_ids", []) or []),
            "latest_env_smoke_probe_report": "results/maniskill_env_smoke_probe.json",
            "latest_env_smoke_ready": env_smoke_probe.get("strict_env_smoke_ready") is True,
            "latest_env_smoke_primary_reset_missing": list(env_smoke_probe.get("primary_reset_missing", []) or []),
            "latest_env_smoke_support_reset_missing": list(env_smoke_probe.get("support_reset_missing", []) or []),
            "latest_env_smoke_missing_asset_ids": list(env_smoke_probe.get("missing_asset_ids", []) or []),
            "latest_env_smoke_missing_asset_ids_by_env": dict(env_smoke_probe.get("missing_asset_ids_by_env", {}) or {}),
            "latest_env_smoke_asset_install_hints": list(env_smoke_probe.get("asset_install_hints", []) or []),
            "latest_env_smoke_asset_install_hint": env_smoke_probe.get("asset_install_hint", ""),
            "latest_probe_report": "results/external_platform_probe.json",
            "latest_probe_install_ready": platform_probe.get("primary_route_install_ready") is True,
            "latest_probe_missing_packages": list(platform_probe.get("primary_route_missing_packages", []) or []),
            "local_status": "probe is non-evidence; operator must rerun it on the selected GPU workstation and record exact versions in fidelity_acceptance.json",
        },
        "required_platform_provenance_fields": PRIMARY_PROVENANCE_FIELDS,
        "task_onboarding": task_onboarding,
        "backend_requirements": [
            "implement external_validation.runner.backend_contract.ExternalCollectionBackend",
            "return non-placeholder platform_provenance with the required provenance fields",
            "load manifest-declared task configs from external_validation/configs",
            "preserve paired reset identity for every method panel",
            "export videos under external_validation/videos and log paths under external_validation/logs",
            "report policy_or_config_hash for every method execution",
            "raise rather than silently substituting scaffold/template implementations",
        ],
        "pilot_sequence": [
            "Run the dry-run packet check without writing logs or videos.",
            "Run strict backend qualification against the non-template backend module.",
            "Materialize real task configs only with --confirm-real-platform --write after platform values are known.",
            "Materialize external_validation/fidelity_acceptance.json only through scripts\\materialize_fidelity_acceptance.py after independent operator signoff and real evidence confirmations.",
            "Run strict collection readiness with a specific immutable run id and explicit alias unsealing.",
            "Collect the full 1,440-record blinded paired-reset panel only after strict readiness passes.",
            "Build the manifest and run strict rollout, pairing, release-package, and evidence audits from raw logs.",
        ],
        "strict_commands": STRICT_COMMANDS,
        "analysis_plan_dependency": {
            "analysis_plan_ready": analysis_audit.get("analysis_plan_ready") is True,
            "strict_evidence_ready": analysis_audit.get("strict_evidence_ready") is True,
            "note": "The analysis plan locks thresholds and exclusions before rollout collection; this onboarding packet only prepares the platform path.",
        },
    }


def audit_packet(
    packet: dict[str, Any],
    collection_plan: dict[str, Any],
    route_audit: dict[str, Any],
    platform_probe: dict[str, Any],
    task_binding_probe: dict[str, Any],
    env_smoke_probe: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    route_checks = {check.get("name"): check.get("passed") for check in route_audit.get("checks", []) or []}
    task_set = set(packet.get("planned_tasks", []) or [])
    provenance = set(packet.get("required_platform_provenance_fields", []) or [])
    command_text = "\n".join(packet.get("strict_commands", []) or [])
    source_urls = [
        source.get("url", "")
        for group in packet.get("official_sources", {}).values()
        for source in group
        if isinstance(source, dict)
    ]

    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True
        and packet.get("platform_onboarding_ready") is True
        and packet.get("strict_evidence_ready") is False,
        (
            f"not_external_evidence={packet.get('not_external_evidence')!r}, "
            f"strict_evidence_ready={packet.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "primary_route_matches_independent_plan",
        packet.get("primary_route") == "maniskill_sapien_primary"
        and packet.get("primary_route_independent_of_haonan") is True
        and route_checks.get("primary_route_independent_of_haonan") is True,
        f"primary_route={packet.get('primary_route')!r}",
    )
    add_check(
        checks,
        "task_onboarding_covers_collection_plan",
        len(task_set) >= 4 and task_set == set(planned_tasks(collection_plan)),
        f"tasks={sorted(task_set)}",
    )
    add_check(
        checks,
        "record_budget_preserved",
        int(packet.get("planned_records", 0) or 0) >= 1440
        and packet.get("planned_records") == collection_plan.get("total_required_records"),
        f"planned_records={packet.get('planned_records')!r}",
    )
    add_check(
        checks,
        "all_remaining_blockers_addressed",
        set(READINESS_BLOCKERS).issubset(set(packet.get("readiness_blockers_addressed", []) or [])),
        f"addressed={packet.get('readiness_blockers_addressed')!r}",
    )
    add_check(
        checks,
        "official_sources_are_primary_and_currently_checked",
        SOURCE_CHECK_DATE == packet.get("source_check_date")
        and any("maniskill.readthedocs.io" in url for url in source_urls)
        and any("sapien.ucsd.edu" in url for url in source_urls)
        and any("robosuite.ai" in url for url in source_urls)
        and any("isaac" in url for url in source_urls),
        f"source_urls={source_urls}",
    )
    add_check(
        checks,
        "platform_provenance_fields_cover_fidelity_hashes_and_observations",
        {
            "contact_solver",
            "friction_model",
            "camera_intrinsics_and_resolution",
            "state_observation_keys",
            "contact_signal_keys",
            "task_config_sha256",
            "backend_module_sha256",
            "skill_library_hash",
            "code_commit",
        }.issubset(provenance),
        f"missing={sorted({'contact_solver', 'friction_model', 'camera_intrinsics_and_resolution', 'state_observation_keys', 'contact_signal_keys', 'task_config_sha256', 'backend_module_sha256', 'skill_library_hash', 'code_commit'} - provenance)}",
    )
    install_probe = packet.get("primary_install_probe", {})
    install_probe = install_probe if isinstance(install_probe, dict) else {}
    add_check(
        checks,
        "platform_probe_report_ready",
        platform_probe.get("version") == "external_platform_probe_v1"
        and platform_probe.get("passed") is True
        and platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_fidelity_evidence_ready") is False
        and platform_probe.get("strict_external_evidence_ready") is False
        and platform_probe.get("primary_route") == "maniskill_sapien_primary",
        (
            f"primary_route_install_ready={platform_probe.get('primary_route_install_ready')!r}, "
            f"missing={platform_probe.get('primary_route_missing_packages')!r}"
        ),
    )
    add_check(
        checks,
        "primary_install_probe_has_machine_probe_command",
        "probe_external_platform.py" in str(install_probe.get("machine_probe_command", ""))
        and "probe_external_platform.py --strict" in str(install_probe.get("strict_machine_probe_command", ""))
        and "probe_maniskill_task_bindings.py" in str(install_probe.get("task_binding_probe_command", ""))
        and "probe_maniskill_task_bindings.py --strict" in str(install_probe.get("strict_task_binding_probe_command", ""))
        and "probe_maniskill_env_smoke.py" in str(install_probe.get("env_smoke_probe_command", ""))
        and "probe_maniskill_env_smoke.py --strict" in str(install_probe.get("strict_env_smoke_probe_command", "")),
        f"install_probe={install_probe}",
    )
    task_binding_checks = {check.get("name"): check.get("passed") for check in task_binding_probe.get("checks", []) or []}
    task_bindings = [
        task.get("backend_task_binding", {})
        for task in packet.get("task_onboarding", []) or []
        if isinstance(task, dict)
    ]
    add_check(
        checks,
        "task_binding_probe_report_ready",
        task_binding_probe.get("version") == "maniskill_task_binding_probe_v1"
        and task_binding_probe.get("passed") is True
        and task_binding_probe.get("not_external_evidence") is True
        and task_binding_probe.get("task_binding_probe_ready") is True
        and task_binding_probe.get("accepted_task_binding_ready") is False
        and task_binding_probe.get("strict_external_evidence_ready") is False
        and task_binding_checks.get("task_bindings_cover_configs") is True
        and task_binding_checks.get("configs_embed_backend_task_bindings") is True
        and all(binding.get("primary_env_id") for binding in task_bindings if isinstance(binding, dict)),
        (
            f"strict_task_binding_install_ready={task_binding_probe.get('strict_task_binding_install_ready')!r}, "
            f"missing={task_binding_probe.get('primary_missing_env_ids')!r}"
        ),
    )
    env_smoke_checks = {check.get("name"): check.get("passed") for check in env_smoke_probe.get("checks", []) or []}
    add_check(
        checks,
        "env_smoke_probe_report_ready",
        env_smoke_probe.get("version") == "maniskill_env_smoke_probe_v1"
        and env_smoke_probe.get("passed") is True
        and env_smoke_probe.get("not_external_evidence") is True
        and env_smoke_probe.get("env_smoke_probe_ready") is True
        and env_smoke_probe.get("accepted_fidelity_ready") is False
        and env_smoke_probe.get("strict_fidelity_evidence_ready") is False
        and env_smoke_probe.get("strict_external_evidence_ready") is False
        and env_smoke_checks.get("smoke_attempted_all_bound_envs") is True
        and env_smoke_checks.get("primary_reset_readiness_reported") is True,
        (
            f"strict_env_smoke_ready={env_smoke_probe.get('strict_env_smoke_ready')!r}, "
            f"primary_reset_missing={env_smoke_probe.get('primary_reset_missing')!r}"
        ),
    )
    for fragment in (
        "build_external_platform_onboarding.py",
        "probe_external_platform.py --strict",
        "probe_maniskill_task_bindings.py --strict",
        "probe_maniskill_env_smoke.py --strict",
        "audit_external_backend_contract.py --strict",
        "materialize_external_configs.py",
        "validate_external_configs.py --strict",
        "materialize_fidelity_acceptance.py",
        "audit_external_fidelity_acceptance.py --strict",
        "audit_external_collection_readiness.py --strict",
        "real_collection_runner.py",
        "build_external_manifest.py --write --check-video-paths",
        "validate_external_rollouts.py",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_release_package.py --strict",
        "audit_external_evidence.py --strict",
    ):
        add_check(
            checks,
            f"strict_command_includes_{fragment.split('.')[0].replace(' ', '_').replace('-', '_')}",
            fragment in command_text,
            fragment,
        )
    add_check(
        checks,
        "pilot_sequence_preserves_gate_order",
        "strict backend qualification" in " ".join(packet.get("pilot_sequence", []))
        and "strict collection readiness" in " ".join(packet.get("pilot_sequence", []))
        and "1,440-record" in " ".join(packet.get("pilot_sequence", [])),
        f"pilot_sequence={packet.get('pilot_sequence')!r}",
    )
    add_check(
        checks,
        "packet_files_written",
        PACKET_JSON.exists() and PACKET_MD.exists(),
        f"packet_json={PACKET_JSON.exists()}, packet_md={PACKET_MD.exists()}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": AUDIT_VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "platform_onboarding_ready": passed,
        "strict_evidence_ready": False,
        "source_packet": rel(PACKET_JSON),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_packet_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Platform Onboarding Packet",
        "",
        "Not evidence: `true`.",
        f"Source check date: `{packet['source_check_date']}`.",
        f"Primary route: `{packet['primary_route']}`.",
        f"Primary platform family: `{packet['primary_platform_family']}`.",
        f"Planned records: `{packet['planned_records']}`.",
        "",
        "This packet turns the non-Haonan public-simulator route into an operator onboarding contract. Package and registry probes are non-evidence; this packet does not claim that any simulator task rollout has been run locally. The operator must record actual installed versions, platform provenance, configs, videos, logs, hashes, and backend implementations before any result can count as evidence.",
        "",
        "## Official Sources Checked",
        "",
    ]
    for source in packet["official_sources"]["primary"] + packet["official_sources"]["secondary"]:
        route = f" `{source['route_id']}`" if "route_id" in source else ""
        lines.append(f"-{route} {source['name']}: {source['url']}")
    lines.extend(
        [
            "",
            "## Primary Install Probe",
            "",
            f"- Install command from official docs: `{packet['primary_install_probe']['install_command_from_official_docs']}`",
            f"- Version capture command: `{packet['primary_install_probe']['version_capture_command']}`",
            f"- Machine probe command: `{packet['primary_install_probe']['machine_probe_command']}`",
            f"- Strict machine probe command: `{packet['primary_install_probe']['strict_machine_probe_command']}`",
            f"- Task binding probe command: `{packet['primary_install_probe']['task_binding_probe_command']}`",
            f"- Strict task binding probe command: `{packet['primary_install_probe']['strict_task_binding_probe_command']}`",
            f"- Env smoke probe command: `{packet['primary_install_probe']['env_smoke_probe_command']}`",
            f"- Strict env smoke probe command: `{packet['primary_install_probe']['strict_env_smoke_probe_command']}`",
            f"- Latest task binding probe report: `{packet['primary_install_probe']['latest_task_binding_probe_report']}`",
            f"- Latest task binding install ready: `{str(packet['primary_install_probe']['latest_task_binding_install_ready']).lower()}`",
            f"- Latest task binding missing env IDs: `{packet['primary_install_probe']['latest_task_binding_missing_env_ids']}`",
            f"- Latest env smoke probe report: `{packet['primary_install_probe']['latest_env_smoke_probe_report']}`",
            f"- Latest env smoke ready: `{str(packet['primary_install_probe']['latest_env_smoke_ready']).lower()}`",
            f"- Latest env smoke primary reset missing: `{packet['primary_install_probe']['latest_env_smoke_primary_reset_missing']}`",
            f"- Latest env smoke support reset missing: `{packet['primary_install_probe']['latest_env_smoke_support_reset_missing']}`",
            f"- Latest env smoke missing asset IDs: `{packet['primary_install_probe']['latest_env_smoke_missing_asset_ids']}`",
            f"- Latest env smoke missing asset IDs by env: `{packet['primary_install_probe']['latest_env_smoke_missing_asset_ids_by_env']}`",
            f"- Latest env smoke asset install hint: `{packet['primary_install_probe']['latest_env_smoke_asset_install_hint']}`",
            f"- Latest probe report: `{packet['primary_install_probe']['latest_probe_report']}`",
            f"- Latest probe install ready: `{str(packet['primary_install_probe']['latest_probe_install_ready']).lower()}`",
            f"- Latest probe missing packages: `{packet['primary_install_probe']['latest_probe_missing_packages']}`",
            f"- Local status: {packet['primary_install_probe']['local_status']}",
            "",
            "## Required Platform Provenance",
            "",
        ]
    )
    for field in packet["required_platform_provenance_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Task Onboarding", ""])
    for task in packet["task_onboarding"]:
        lines.append(f"### `{task['task_family']}`")
        lines.append("")
        binding = task.get("backend_task_binding", {})
        lines.append("Backend task binding:")
        lines.append(f"- Primary env ID: `{binding.get('primary_env_id', '')}`")
        lines.append(f"- Support env IDs: `{binding.get('support_env_ids', [])}`")
        lines.append(f"- Binding strength: `{binding.get('binding_strength', '')}`")
        lines.append(f"- Primary env available in latest probe: `{binding.get('primary_env_available')}`")
        lines.append(f"- Operator fidelity acceptance required: `{str(binding.get('requires_operator_fidelity_acceptance', True)).lower()}`")
        lines.append("")
        lines.append("Required operator files:")
        for item in task["required_operator_files"]:
            lines.append(f"- `{item}`")
        lines.append("")
        lines.append("Must document:")
        for item in task["must_document"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["## Backend Requirements", ""])
    for item in packet["backend_requirements"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Pilot Sequence", ""])
    for idx, item in enumerate(packet["pilot_sequence"], start=1):
        lines.append(f"{idx}. {item}")
    lines.extend(["", "## Strict Commands", ""])
    for command in packet["strict_commands"]:
        lines.append(f"- `{command}`")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Platform Onboarding Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Platform onboarding ready: `{str(audit['platform_onboarding_ready']).lower()}`.",
        f"Strict evidence ready: `{str(audit['strict_evidence_ready']).lower()}`.",
        "",
        "This audit checks that the public-simulator onboarding packet is specific enough for an independent operator while still remaining non-evidence.",
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
    collection_plan = read_json(RESULTS / "external_collection_plan.json")
    route_audit = read_json(RESULTS / "independent_validation_route_audit.json")
    analysis_audit = read_json(RESULTS / "external_analysis_plan_audit.json")
    platform_probe = read_json(RESULTS / "external_platform_probe.json")
    task_binding_probe = read_json(RESULTS / "maniskill_task_binding_probe.json")
    env_smoke_probe = read_json(RESULTS / "maniskill_env_smoke_probe.json")

    packet = build_packet(collection_plan, route_audit, analysis_audit, platform_probe, task_binding_probe, env_smoke_probe)
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_packet_md(packet)
    audit = audit_packet(packet, collection_plan, route_audit, platform_probe, task_binding_probe, env_smoke_probe)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    print(
        "External platform onboarding: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"primary={packet['primary_route']}; not_evidence=true"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
