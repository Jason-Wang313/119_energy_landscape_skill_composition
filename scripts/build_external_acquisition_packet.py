from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
EXTERNAL = ROOT / "external_validation"

OUT_JSON = RESULTS / "external_acquisition_packet.json"
OUT_MD = RESULTS / "external_acquisition_packet.md"


MISSING_REQUIREMENT_ACTIONS = {
    "Independent real-robot or accepted high-fidelity external validation evidence": [
        "platform_probe",
        "task_binding_probe",
        "env_smoke_probe",
        "platform_onboarding",
        "fidelity_provenance_packet",
        "backend_integration_packet",
        "maniskill_reference_backend_audit",
        "maniskill_reference_collection_preflight",
        "rollout_evidence_packet",
        "backend_module",
        "platform_fidelity",
        "pilot_smoke_packet",
        "run_collection",
        "manifest_and_release",
    ],
    "External rollout metrics recomputed from raw JSONL logs": [
        "rollout_evidence_packet",
        "run_collection",
        "strict_rollout_recompute",
    ],
    "Manifest-declared real task configs replace non-evidence templates": [
        "config_manifest_packet",
        "real_task_configs",
        "manifest_and_release",
    ],
    "Manifest-declared independent non-oracle baseline evidence and fairness contract": [
        "method_implementation_packet",
        "real_method_implementations",
        "strict_adapter_evidence",
    ],
}

EXPECTED_MISSING_REQUIREMENTS = list(MISSING_REQUIREMENT_ACTIONS)


ACTION_CATALOG = {
    "platform_probe": {
        "title": "Probe the selected external platform machine",
        "operator_input": "run the non-evidence probe on the GPU workstation or accepted robot/simulator machine before backend qualification",
        "artifacts": [
            "results/external_platform_probe.json",
            "results/external_platform_probe.md",
        ],
        "commands": [
            "python scripts\\probe_external_platform.py",
            "python scripts\\probe_external_platform.py --strict",
        ],
        "closes": ["platform package, GPU, renderer, code, config, and backend hash provenance before fidelity acceptance"],
    },
    "task_binding_probe": {
        "title": "Probe ManiSkill task-family bindings",
        "operator_input": "bind each Paper 119 task family to concrete ManiSkill/SAPIEN environment candidates and inspect the local registry when available",
        "artifacts": [
            "external_validation/maniskill_task_bindings.json",
            "results/maniskill_task_binding_probe.json",
            "results/maniskill_task_binding_probe.md",
        ],
        "commands": [
            "python scripts\\probe_maniskill_task_bindings.py",
            "python scripts\\probe_maniskill_task_bindings.py --strict",
        ],
        "closes": ["task-family to public-simulator environment binding before operator fidelity acceptance"],
    },
    "env_smoke_probe": {
        "title": "Smoke-test bound ManiSkill environments",
        "operator_input": "construct and reset the bound public-simulator environment candidates without writing rollout logs or videos",
        "artifacts": [
            "results/maniskill_env_smoke_probe.json",
            "results/maniskill_env_smoke_probe.md",
        ],
        "commands": [
            "python scripts\\probe_maniskill_env_smoke.py",
            "python scripts\\probe_maniskill_env_smoke.py --strict",
        ],
        "closes": ["environment construction/reset and missing-asset readiness before backend qualification"],
    },
    "platform_onboarding": {
        "title": "Onboard the public simulator platform",
        "operator_input": "GPU workstation or accepted robot/simulator platform plus recorded version/provenance fields",
        "artifacts": [
            "external_validation/platform_onboarding_packet.md",
            "external_validation/platform_onboarding_packet.json",
            "results/external_platform_probe.json",
            "results/maniskill_task_binding_probe.json",
            "results/maniskill_env_smoke_probe.json",
            "results/external_platform_onboarding_audit.json",
        ],
        "commands": [
            "python scripts\\probe_external_platform.py",
            "python scripts\\probe_maniskill_task_bindings.py",
            "python scripts\\probe_maniskill_env_smoke.py",
            "python scripts\\build_external_platform_onboarding.py",
            "python scripts\\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json",
            "python scripts\\audit_external_fidelity_acceptance.py --strict",
        ],
        "closes": ["platform onboarding for independent high-fidelity or robot evidence capture"],
    },
    "backend_module": {
        "title": "Select a non-template backend module",
        "operator_input": "--backend-module <module_or_path>",
        "artifacts": ["external_validation/runner/backends/<real_backend>.py"],
        "commands": [
            "python scripts\\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json",
            "python scripts\\audit_external_collection_readiness.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --run-id <specific_run_id> --unsealed-alias-map",
        ],
        "closes": ["actual collection backend readiness"],
    },
    "backend_integration_packet": {
        "title": "Use the backend integration packet as the public-simulator backend checklist",
        "operator_input": "complete the non-template backend work orders with real module, provenance, task binding, hashes, logs, and videos",
        "artifacts": [
            "external_validation/backend_integration_packet.md",
            "external_validation/backend_integration_work_orders.csv",
            "results/external_backend_integration_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_backend_integration_packet.py",
            "python scripts\\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json",
        ],
        "closes": ["actual collection backend readiness"],
    },
    "maniskill_reference_backend_audit": {
        "title": "Audit the repository ManiSkill/SAPIEN reference backend candidate",
        "operator_input": "use the tracked reference backend to inspect API/config/adapter wiring before replacing or wrapping it with a real evidence backend",
        "artifacts": [
            "external_validation/runner/maniskill_reference_backend.py",
            "results/maniskill_backend_readiness_audit.json",
            "results/maniskill_backend_readiness_audit.md",
        ],
        "commands": [
            "python scripts\\audit_maniskill_backend_readiness.py",
        ],
        "closes": ["reference backend contract plus MP4-writer qualification only; official collection still requires accepted fidelity, renderable per-episode videos, logs, manifests, and strict evidence gates"],
    },
    "maniskill_reference_collection_preflight": {
        "title": "Audit explicit reference-backend collection preflight",
        "operator_input": "use the tracked reference backend with prepared configs, an explicit run id, and unsealed aliases to verify that preflight reaches the fidelity gate",
        "artifacts": [
            "results/maniskill_reference_collection_preflight_audit.json",
            "results/maniskill_reference_collection_preflight_audit.md",
            "external_validation/runner/maniskill_reference_backend.py",
        ],
        "commands": [
            "python scripts\\audit_maniskill_reference_collection_preflight.py",
        ],
        "closes": ["reference backend/config/run-id/alias preflight to fidelity acceptance only; official collection still requires accepted fidelity, logs, videos, manifest, and strict evidence gates"],
    },
    "real_task_configs": {
        "title": "Create real manifest-declared task configs",
        "operator_input": "external_validation/configs/<task_family>.json for each task family",
        "artifacts": [
            "external_validation/configs/peg_place_regrasp.json",
            "external_validation/configs/drawer_to_pick_transfer.json",
            "external_validation/configs/door_open_navigation.json",
            "external_validation/configs/cable_route_insert.json",
        ],
        "commands": [
            "python scripts\\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
            "python scripts\\validate_external_configs.py --strict",
        ],
        "closes": ["Manifest-declared real task configs replace non-evidence templates"],
    },
    "config_manifest_packet": {
        "title": "Use the config manifest packet as the task-config evidence checklist",
        "operator_input": "manifest-declare prepared configs with hashes only after real platform, log, and video artifacts exist",
        "artifacts": [
            "external_validation/config_manifest_packet.md",
            "external_validation/config_manifest_work_orders.csv",
            "results/external_config_manifest_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_config_manifest_packet.py",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\validate_external_configs.py --strict",
        ],
        "closes": ["Manifest-declared real task configs replace non-evidence templates"],
    },
    "rollout_evidence_packet": {
        "title": "Use the rollout evidence packet as the raw-log evidence checklist",
        "operator_input": "complete the rollout work orders with manifest-declared JSONL logs, videos, config hashes, method hashes, and strict recomputation",
        "artifacts": [
            "external_validation/rollout_evidence_packet.md",
            "external_validation/rollout_evidence_work_orders.csv",
            "results/external_rollout_evidence_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_rollout_evidence_packet.py",
            "python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
            "python scripts\\audit_external_pairing_integrity.py --strict",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "closes": [
            "Independent real-robot or accepted high-fidelity external validation evidence",
            "External rollout metrics recomputed from raw JSONL logs",
        ],
    },
    "platform_fidelity": {
        "title": "Fill platform fidelity acceptance with real provenance",
        "operator_input": "accepted simulator or robot evidence, contact/dynamics/camera/state provenance, and task coverage",
        "artifacts": ["external_validation/fidelity_acceptance.json"],
        "commands": ["python scripts\\audit_external_fidelity_acceptance.py --strict"],
        "closes": ["Independent real-robot or accepted high-fidelity external validation evidence"],
    },
    "pilot_smoke_packet": {
        "title": "Run a quarantined first-panel backend smoke test",
        "operator_input": "real backend, accepted fidelity gate, prepared configs, unsealed aliases, and a pilot-specific run id",
        "artifacts": [
            "external_validation/pilot_smoke_packet.md",
            "external_validation/pilot_smoke_work_orders.csv",
            "results/external_pilot_smoke_packet_audit.json",
            "results/external_pilot_smoke_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_pilot_smoke_packet.py",
            "python scripts\\audit_external_pilot_smoke.py --strict --expected-records 12 --check-video-paths",
        ],
        "closes": ["operator backend smoke test before official collection; not evidence"],
    },
    "fidelity_provenance_packet": {
        "title": "Use the fidelity provenance packet as the platform acceptance checklist",
        "operator_input": "complete platform physics/contact, paired-reset replay, operator independence, calibration basis, code commit, skill-library hash, and acceptance gates",
        "artifacts": [
            "external_validation/fidelity_provenance_packet.md",
            "external_validation/fidelity_provenance_work_orders.csv",
            "results/external_fidelity_provenance_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_fidelity_provenance_packet.py",
            "python scripts\\audit_external_fidelity_acceptance.py --strict",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
        ],
        "closes": ["Independent real-robot or accepted high-fidelity external validation evidence"],
    },
    "alias_unseal": {
        "title": "Unseal method aliases only after configs, implementations, and run plan are frozen",
        "operator_input": "--unsealed-alias-map",
        "artifacts": ["external_validation/method_alias_map.json"],
        "commands": ["python scripts\\audit_external_collection_readiness.py --strict --unsealed-alias-map"],
        "closes": ["paired-reset method-panel integrity before collection"],
    },
    "specific_run_id": {
        "title": "Use a specific immutable external run id",
        "operator_input": "--run-id <platform>_<date>_<protocol_version>",
        "artifacts": ["external_validation/logs/*.jsonl"],
        "commands": ["python scripts\\audit_external_collection_readiness.py --strict --run-id <specific_run_id>"],
        "closes": ["run identity provenance"],
    },
    "real_method_implementations": {
        "title": "Replace scaffold-only methods with real non-oracle implementations or wrappers",
        "operator_input": "implementation_path and checkpoint_or_config_path/hash for every non-oracle method",
        "artifacts": [
            "external_validation/adapters/<method>/implementation.py",
            "external_validation/baselines/<method>/implementation.py",
            "external_validation/checkpoints_or_configs/<method>.*",
        ],
        "commands": [
            "python scripts\\build_external_baseline_contract.py",
            "python scripts\\validate_external_adapters.py --strict",
        ],
        "closes": ["Manifest-declared independent non-oracle baseline evidence and fairness contract"],
    },
    "method_implementation_packet": {
        "title": "Use the method implementation packet as the non-oracle work-order checklist",
        "operator_input": "complete every non-oracle method work order with real implementation/config/checkpoint paths and hashes",
        "artifacts": [
            "external_validation/method_implementation_packet.md",
            "external_validation/method_implementation_work_orders.csv",
            "results/external_method_implementation_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_method_implementation_packet.py",
            "python scripts\\validate_external_adapters.py --strict",
        ],
        "closes": ["Manifest-declared independent non-oracle baseline evidence and fairness contract"],
    },
    "run_collection": {
        "title": "Collect paired-reset external rollouts",
        "operator_input": "1,440 JSONL records over 4 tasks x 12 methods x 120 paired resets",
        "artifacts": [
            "external_validation/logs/peg_place_regrasp.jsonl",
            "external_validation/logs/drawer_to_pick_transfer.jsonl",
            "external_validation/logs/door_open_navigation.jsonl",
            "external_validation/logs/cable_route_insert.jsonl",
            "external_validation/videos/<task_family>/*",
        ],
        "commands": [
            "python external_validation\\runner\\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id <specific_run_id> --unsealed-alias-map",
        ],
        "closes": [
            "Independent real-robot or accepted high-fidelity external validation evidence",
            "External rollout metrics recomputed from raw JSONL logs",
        ],
    },
    "manifest_and_release": {
        "title": "Build the real manifest and hash-lock release artifacts",
        "operator_input": "manifest paths, code commit, skill-library hash, config/log/video/checkpoint hashes",
        "artifacts": ["external_validation/manifest.json", "results/external_manifest_builder_report.json"],
        "commands": [
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\audit_external_release_package.py --strict",
        ],
        "closes": [
            "Independent real-robot or accepted high-fidelity external validation evidence",
            "Manifest-declared real task configs replace non-evidence templates",
        ],
    },
    "strict_rollout_recompute": {
        "title": "Recompute external metrics from raw JSONL logs",
        "operator_input": "strict rollout validator over manifest-declared logs and videos",
        "artifacts": ["results/external_rollout_metrics.json", "results/external_rollout_metrics.md"],
        "commands": ["python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict"],
        "closes": ["External rollout metrics recomputed from raw JSONL logs"],
    },
    "strict_adapter_evidence": {
        "title": "Audit independent method evidence after the manifest is real",
        "operator_input": "manifest-declared non-oracle implementation paths and hashes",
        "artifacts": [
            "results/external_baseline_contract_audit.json",
            "results/external_adapter_contract_evidence_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_baseline_contract.py",
            "python scripts\\validate_external_adapters.py --strict",
        ],
        "closes": ["Manifest-declared independent non-oracle baseline evidence and fairness contract"],
    },
    "final_strict_gate": {
        "title": "Run the final strict external-evidence gate",
        "operator_input": "completed manifest, logs, videos, configs, checkpoints/hashes, adapters, and fidelity acceptance",
        "artifacts": ["results/external_evidence_audit.json", "results/submission_readiness_gap_audit.json"],
        "commands": [
            "python scripts\\audit_external_pairing_integrity.py --strict",
            "python scripts\\audit_external_evidence.py --strict",
            "python scripts\\audit_submission_readiness_gap.py",
        ],
        "closes": ["objective completion audit after real evidence exists"],
    },
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def require_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def missing_requirements_from_gap(gap: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in gap.get("requirements", []) or []
        if row.get("status") == "missing" and row.get("submission_blocking") is True
    ]
    if rows:
        return rows
    return [{"requirement": name, "blocker": "derived from strict external-evidence gates"} for name in EXPECTED_MISSING_REQUIREMENTS]


def blocker_name(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("name", ""))
    text = str(item)
    return text.split(":", 1)[0].strip()


def blocker_detail(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("detail", ""))
    text = str(item)
    return text.split(":", 1)[1].strip() if ":" in text else text


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    checks: list[dict[str, Any]] = []

    gap_path = RESULTS / "submission_readiness_gap_audit.json"
    collection_path = RESULTS / "external_collection_readiness_audit.json"
    preflight_path = RESULTS / "external_evidence_preflight.json"
    route_path = RESULTS / "independent_validation_route_audit.json"
    platform_probe_path = RESULTS / "external_platform_probe.json"
    task_binding_probe_path = RESULTS / "maniskill_task_binding_probe.json"
    env_smoke_probe_path = RESULTS / "maniskill_env_smoke_probe.json"
    onboarding_path = RESULTS / "external_platform_onboarding_audit.json"
    fidelity_provenance_path = RESULTS / "external_fidelity_provenance_audit.json"
    config_materialization_path = RESULTS / "external_config_materialization_plan.json"
    backend_contract_path = RESULTS / "external_backend_contract_audit.json"
    backend_integration_path = RESULTS / "external_backend_integration_audit.json"
    maniskill_backend_path = RESULTS / "maniskill_backend_readiness_audit.json"
    maniskill_preflight_path = RESULTS / "maniskill_reference_collection_preflight_audit.json"
    config_manifest_path = RESULTS / "external_config_manifest_audit.json"
    rollout_evidence_path = RESULTS / "external_rollout_evidence_audit.json"
    method_packet_path = RESULTS / "external_method_implementation_audit.json"
    pilot_smoke_path = RESULTS / "external_pilot_smoke_packet_audit.json"

    gap = require_json(gap_path)
    collection = require_json(collection_path)
    preflight = require_json(preflight_path)
    route = require_json(route_path)
    platform_probe = require_json(platform_probe_path)
    task_binding_probe = require_json(task_binding_probe_path)
    env_smoke_probe = require_json(env_smoke_probe_path)
    onboarding = require_json(onboarding_path)
    fidelity_provenance = require_json(fidelity_provenance_path)
    config_materialization = require_json(config_materialization_path)
    backend_contract = require_json(backend_contract_path)
    backend_integration = require_json(backend_integration_path)
    maniskill_backend = require_json(maniskill_backend_path)
    maniskill_preflight = require_json(maniskill_preflight_path)
    config_manifest = require_json(config_manifest_path)
    rollout_evidence = require_json(rollout_evidence_path)
    method_packet = require_json(method_packet_path)
    pilot_smoke = require_json(pilot_smoke_path)

    missing_requirements = missing_requirements_from_gap(gap)
    missing_names = [row.get("requirement", "") for row in missing_requirements]

    actions = []
    for action_id, action in ACTION_CATALOG.items():
        row = {"id": action_id, **action}
        actions.append(row)

    mapped_requirement_names = set(MISSING_REQUIREMENT_ACTIONS)
    add_check(
        checks,
        "source_audits_exist",
        all(
            path.exists()
            for path in [
                collection_path,
                preflight_path,
                route_path,
                platform_probe_path,
                task_binding_probe_path,
                env_smoke_probe_path,
                onboarding_path,
                fidelity_provenance_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                maniskill_preflight_path,
                config_manifest_path,
                rollout_evidence_path,
                method_packet_path,
                pilot_smoke_path,
            ]
        ),
        ", ".join(
            rel(path)
            for path in [
                collection_path,
                preflight_path,
                route_path,
                platform_probe_path,
                task_binding_probe_path,
                env_smoke_probe_path,
                onboarding_path,
                fidelity_provenance_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                maniskill_preflight_path,
                config_manifest_path,
                rollout_evidence_path,
                method_packet_path,
                pilot_smoke_path,
            ]
        ),
    )
    add_check(
        checks,
        "gap_audit_has_four_external_blockers",
        len(missing_requirements) == 4
        and set(missing_names) == mapped_requirement_names
        and (not gap or int(gap.get("blocking_missing_requirements", 0) or 0) == 4),
        f"missing={missing_names}",
    )
    unmapped = sorted(set(missing_names) - mapped_requirement_names)
    add_check(checks, "all_missing_requirements_mapped", not unmapped, f"unmapped={unmapped}")

    missing_action_ids = sorted(
        action_id
        for requirement, action_ids in MISSING_REQUIREMENT_ACTIONS.items()
        if requirement in missing_names
        for action_id in action_ids
        if action_id not in ACTION_CATALOG
    )
    add_check(checks, "all_action_ids_exist", not missing_action_ids, f"missing_action_ids={missing_action_ids}")

    collection_blockers = collection.get("blocking_missing", []) or []
    collection_blocker_names = {blocker_name(item) for item in collection_blockers}
    collection_checks = {check.get("name"): check.get("passed") for check in collection.get("checks", []) or []}
    required_collection_blockers = {
        "backend_module_ready",
        "fidelity_acceptance_ready",
        "alias_unsealing_explicit",
        "run_id_specific",
    }
    configs_accounted_for = (
        "real_task_configs_ready" in collection_blocker_names
        or collection_checks.get("real_task_configs_ready") is True
    )
    add_check(
        checks,
        "collection_preflight_fail_closed",
        collection.get("collection_ready") is False
        and collection.get("not_external_evidence") is True
        and required_collection_blockers.issubset(collection_blocker_names)
        and configs_accounted_for,
        f"collection_ready={collection.get('collection_ready')!r}, blockers={sorted(collection_blocker_names)}",
    )
    add_check(
        checks,
        "config_intake_directory_tracked",
        collection_checks.get("task_config_dir_exists") is True,
        f"task_config_dir_exists={collection_checks.get('task_config_dir_exists')!r}",
    )
    add_check(
        checks,
        "config_materializer_ready",
        config_materialization.get("passed") is True
        and config_materialization.get("not_external_evidence") is True
        and config_materialization.get("write_enabled") is False
        and int(config_materialization.get("task_count", 0) or 0) >= 4,
        (
            f"passed={config_materialization.get('passed')!r}, "
            f"write_enabled={config_materialization.get('write_enabled')!r}, "
            f"task_count={config_materialization.get('task_count')!r}"
        ),
    )
    add_check(
        checks,
        "backend_contract_gate_ready",
        backend_contract.get("passed") is True
        and backend_contract.get("not_external_evidence") is True
        and backend_contract.get("backend_contract_harness_ready") is True
        and backend_contract.get("actual_backend_ready") is False
        and "audit_external_backend_contract.py --strict" in str(backend_contract.get("strict_command", "")),
        (
            f"harness_ready={backend_contract.get('backend_contract_harness_ready')!r}, "
            f"actual_backend_ready={backend_contract.get('actual_backend_ready')!r}"
        ),
    )
    backend_integration_checks = {check.get("name"): check.get("passed") for check in backend_integration.get("checks", []) or []}
    add_check(
        checks,
        "backend_integration_packet_ready",
        backend_integration.get("passed") is True
        and backend_integration.get("not_external_evidence") is True
        and backend_integration.get("backend_integration_packet_ready") is True
        and backend_integration.get("strict_backend_ready") is False
        and backend_integration.get("strict_evidence_ready") is False
        and backend_integration_checks.get("work_orders_cover_backend_to_manifest_path") is True
        and backend_integration_checks.get("collection_readiness_still_blocks_backend") is True
        and (EXTERNAL / "backend_integration_packet.md").exists()
        and (EXTERNAL / "backend_integration_work_orders.csv").exists(),
        (
            f"backend_integration_packet_ready={backend_integration.get('backend_integration_packet_ready')!r}, "
            f"strict_backend_ready={backend_integration.get('strict_backend_ready')!r}"
        ),
    )
    maniskill_backend_checks = {check.get("name"): check.get("passed") for check in maniskill_backend.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_backend_audit_ready",
        maniskill_backend.get("passed") is True
        and maniskill_backend.get("not_external_evidence") is True
        and maniskill_backend.get("backend_contract_ready") is True
        and maniskill_backend.get("reference_backend_available") is True
        and maniskill_backend.get("video_writer_ready") is True
        and maniskill_backend.get("official_collection_ready") is False
        and maniskill_backend.get("strict_external_evidence_ready") is False
        and maniskill_backend_checks.get("official_collection_fail_closed_without_enable_flag") is True
        and maniskill_backend_checks.get("video_export_fail_closed_before_reset") is True
        and maniskill_backend_checks.get("synthetic_mp4_writer_passes") is True,
        (
            f"backend_contract_ready={maniskill_backend.get('backend_contract_ready')!r}, "
            f"video_writer_ready={maniskill_backend.get('video_writer_ready')!r}, "
            f"official_collection_ready={maniskill_backend.get('official_collection_ready')!r}"
        ),
    )
    maniskill_preflight_checks = {check.get("name"): check.get("passed") for check in maniskill_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_reference_collection_preflight_ready",
        maniskill_preflight.get("passed") is True
        and maniskill_preflight.get("not_external_evidence") is True
        and maniskill_preflight.get("reference_backend_contract_ready") is True
        and maniskill_preflight.get("collection_ready") is False
        and maniskill_preflight.get("strict_external_evidence_ready") is False
        and int(maniskill_preflight.get("collection_blocking_missing_count", 0) or 0) == 1
        and any("fidelity_acceptance_ready" in str(item) for item in maniskill_preflight.get("collection_blocking_missing", []) or [])
        and maniskill_preflight_checks.get("reference_backend_collection_preflight_reaches_fidelity_gate") is True,
        (
            f"contract_ready={maniskill_preflight.get('reference_backend_contract_ready')!r}, "
            f"collection_ready={maniskill_preflight.get('collection_ready')!r}, "
            f"blocking={maniskill_preflight.get('collection_blocking_missing')!r}"
        ),
    )
    method_packet_checks = {check.get("name"): check.get("passed") for check in method_packet.get("checks", []) or []}
    config_manifest_checks = {check.get("name"): check.get("passed") for check in config_manifest.get("checks", []) or []}
    add_check(
        checks,
        "config_manifest_packet_ready",
        config_manifest.get("passed") is True
        and config_manifest.get("not_external_evidence") is True
        and config_manifest.get("config_manifest_packet_ready") is True
        and config_manifest.get("strict_config_evidence_ready") is False
        and config_manifest.get("manifest_declared_config_ready") is False
        and config_manifest_checks.get("work_orders_cover_config_to_manifest_path") is True
        and (EXTERNAL / "config_manifest_packet.md").exists()
        and (EXTERNAL / "config_manifest_work_orders.csv").exists(),
        (
            f"config_manifest_packet_ready={config_manifest.get('config_manifest_packet_ready')!r}, "
            f"strict_config_evidence_ready={config_manifest.get('strict_config_evidence_ready')!r}, "
            f"manifest_declared_config_ready={config_manifest.get('manifest_declared_config_ready')!r}"
        ),
    )
    rollout_evidence_checks = {check.get("name"): check.get("passed") for check in rollout_evidence.get("checks", []) or []}
    add_check(
        checks,
        "rollout_evidence_packet_ready",
        rollout_evidence.get("passed") is True
        and rollout_evidence.get("not_external_evidence") is True
        and rollout_evidence.get("rollout_evidence_packet_ready") is True
        and rollout_evidence.get("strict_rollout_evidence_ready") is False
        and rollout_evidence.get("strict_external_evidence_ready") is False
        and rollout_evidence_checks.get("task_work_orders_cover_all_planned_tasks") is True
        and rollout_evidence_checks.get("strict_rollout_metrics_still_fail_without_manifest") is True
        and (EXTERNAL / "rollout_evidence_packet.md").exists()
        and (EXTERNAL / "rollout_evidence_work_orders.csv").exists(),
        (
            f"rollout_evidence_packet_ready={rollout_evidence.get('rollout_evidence_packet_ready')!r}, "
            f"strict_rollout_evidence_ready={rollout_evidence.get('strict_rollout_evidence_ready')!r}, "
            f"strict_external_evidence_ready={rollout_evidence.get('strict_external_evidence_ready')!r}"
        ),
    )
    pilot_smoke_checks = {check.get("name"): check.get("passed") for check in pilot_smoke.get("checks", []) or []}
    add_check(
        checks,
        "pilot_smoke_packet_ready",
        pilot_smoke.get("passed") is True
        and pilot_smoke.get("not_external_evidence") is True
        and pilot_smoke.get("pilot_smoke_packet_ready") is True
        and pilot_smoke.get("strict_evidence_ready") is False
        and pilot_smoke_checks.get("quarantine_dirs_are_separate_from_official_evidence") is True
        and pilot_smoke_checks.get("pilot_commands_preserve_gate_order") is True
        and (EXTERNAL / "pilot_smoke_packet.md").exists()
        and (EXTERNAL / "pilot_smoke_work_orders.csv").exists(),
        (
            f"pilot_smoke_packet_ready={pilot_smoke.get('pilot_smoke_packet_ready')!r}, "
            f"strict_evidence_ready={pilot_smoke.get('strict_evidence_ready')!r}"
        ),
    )
    add_check(
        checks,
        "method_implementation_packet_ready",
        method_packet.get("passed") is True
        and method_packet.get("not_external_evidence") is True
        and method_packet.get("method_implementation_packet_ready") is True
        and method_packet.get("strict_adapter_evidence_ready") is False
        and method_packet_checks.get("work_orders_cover_all_missing_non_oracle_methods") is True
        and method_packet_checks.get("adapter_evidence_still_missing") is True
        and (EXTERNAL / "method_implementation_packet.md").exists()
        and (EXTERNAL / "method_implementation_work_orders.csv").exists(),
        (
            f"method_implementation_packet_ready={method_packet.get('method_implementation_packet_ready')!r}, "
            f"strict_adapter_evidence_ready={method_packet.get('strict_adapter_evidence_ready')!r}"
        ),
    )
    preflight_actions = preflight.get("operator_next_actions", []) or []
    add_check(
        checks,
        "preflight_operator_actions_present",
        len(preflight_actions) >= 5 and preflight.get("evidence_ready") is False,
        f"operator_next_actions={len(preflight_actions)}, evidence_ready={preflight.get('evidence_ready')!r}",
    )
    route_checks = {check.get("name"): check.get("passed") for check in route.get("checks", []) or []}
    add_check(
        checks,
        "route_independent_of_haonan",
        route_checks.get("primary_route_independent_of_haonan") is True
        and route_checks.get("primary_route_covers_collection_tasks") is True,
        f"primary_route={route.get('primary_route')!r}",
    )
    add_check(
        checks,
        "platform_probe_ready",
        platform_probe.get("version") == "external_platform_probe_v1"
        and platform_probe.get("passed") is True
        and platform_probe.get("not_external_evidence") is True
        and platform_probe.get("platform_probe_ready") is True
        and platform_probe.get("strict_external_evidence_ready") is False,
        (
            f"primary_route_install_ready={platform_probe.get('primary_route_install_ready')!r}, "
            f"missing={platform_probe.get('primary_route_missing_packages')!r}"
        ),
    )
    add_check(
        checks,
        "task_binding_probe_ready",
        task_binding_probe.get("version") == "maniskill_task_binding_probe_v1"
        and task_binding_probe.get("passed") is True
        and task_binding_probe.get("not_external_evidence") is True
        and task_binding_probe.get("task_binding_probe_ready") is True
        and task_binding_probe.get("accepted_task_binding_ready") is False
        and task_binding_probe.get("strict_external_evidence_ready") is False,
        (
            f"strict_task_binding_install_ready={task_binding_probe.get('strict_task_binding_install_ready')!r}, "
            f"missing={task_binding_probe.get('primary_missing_env_ids')!r}"
        ),
    )
    add_check(
        checks,
        "env_smoke_probe_ready",
        env_smoke_probe.get("version") == "maniskill_env_smoke_probe_v1"
        and env_smoke_probe.get("passed") is True
        and env_smoke_probe.get("not_external_evidence") is True
        and env_smoke_probe.get("env_smoke_probe_ready") is True
        and env_smoke_probe.get("accepted_fidelity_ready") is False
        and env_smoke_probe.get("strict_external_evidence_ready") is False,
        (
            f"strict_env_smoke_ready={env_smoke_probe.get('strict_env_smoke_ready')!r}, "
            f"primary_reset_missing={env_smoke_probe.get('primary_reset_missing')!r}"
        ),
    )
    onboarding_checks = {check.get("name"): check.get("passed") for check in onboarding.get("checks", []) or []}
    add_check(
        checks,
        "platform_onboarding_ready",
        onboarding.get("passed") is True
        and onboarding.get("not_external_evidence") is True
        and onboarding.get("platform_onboarding_ready") is True
        and onboarding.get("strict_evidence_ready") is False
        and onboarding_checks.get("primary_route_matches_independent_plan") is True
        and onboarding_checks.get("official_sources_are_primary_and_currently_checked") is True
        and onboarding_checks.get("platform_provenance_fields_cover_fidelity_hashes_and_observations") is True,
        (
            f"platform_onboarding_ready={onboarding.get('platform_onboarding_ready')!r}, "
            f"strict_evidence_ready={onboarding.get('strict_evidence_ready')!r}"
        ),
    )
    fidelity_provenance_checks = {check.get("name"): check.get("passed") for check in fidelity_provenance.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_provenance_packet_ready",
        fidelity_provenance.get("passed") is True
        and fidelity_provenance.get("not_external_evidence") is True
        and fidelity_provenance.get("fidelity_provenance_packet_ready") is True
        and fidelity_provenance.get("strict_fidelity_evidence_ready") is False
        and fidelity_provenance.get("strict_external_evidence_ready") is False
        and fidelity_provenance_checks.get("work_orders_cover_fidelity_blockers") is True
        and fidelity_provenance_checks.get("fidelity_acceptance_contract_ready_but_not_evidence") is True
        and (EXTERNAL / "fidelity_provenance_packet.md").exists()
        and (EXTERNAL / "fidelity_provenance_work_orders.csv").exists(),
        (
            f"fidelity_provenance_packet_ready={fidelity_provenance.get('fidelity_provenance_packet_ready')!r}, "
            f"strict_fidelity_evidence_ready={fidelity_provenance.get('strict_fidelity_evidence_ready')!r}, "
            f"strict_external_evidence_ready={fidelity_provenance.get('strict_external_evidence_ready')!r}"
        ),
    )

    post_collection_commands = collection.get("post_collection_strict_commands", []) or []
    required_command_fragments = [
        "build_external_manifest.py --write --check-video-paths",
        "audit_external_release_package.py --strict",
        "audit_external_fidelity_acceptance.py --strict",
        "validate_external_adapters.py --strict",
        "validate_external_configs.py --strict",
        "validate_external_rollouts.py --write-results --check-video-paths --strict",
        "audit_external_pairing_integrity.py --strict",
        "audit_external_evidence.py --strict",
        "audit_external_backend_contract.py --strict",
        "build_external_backend_integration_packet.py",
        "build_external_config_manifest_packet.py",
        "build_external_rollout_evidence_packet.py",
        "build_external_fidelity_provenance_packet.py",
        "build_external_platform_onboarding.py",
        "probe_external_platform.py",
        "probe_maniskill_task_bindings.py",
        "probe_maniskill_env_smoke.py",
        "build_external_method_implementation_packet.py",
        "build_external_pilot_smoke_packet.py",
        "audit_external_pilot_smoke.py",
    ]
    command_text = "\n".join(post_collection_commands + [cmd for action in actions for cmd in action["commands"]])
    missing_command_fragments = [fragment for fragment in required_command_fragments if fragment not in command_text]
    add_check(
        checks,
        "post_collection_strict_commands_cover_all_gates",
        not missing_command_fragments,
        f"missing_command_fragments={missing_command_fragments}",
    )

    manifest_path = EXTERNAL / "manifest.json"
    add_check(checks, "no_real_manifest_written", not manifest_path.exists(), "external_validation/manifest.json absent before real evidence")

    action_titles = " ".join(action["title"] for action in actions)
    add_check(
        checks,
        "operator_actions_cover_collection_blockers",
        all(
            term in action_titles.lower()
            for term in ["backend", "task configs", "fidelity", "aliases", "run id", "rollouts"]
        ),
        action_titles,
    )
    add_check(
        checks,
        "backend_action_runs_contract_before_readiness",
        "audit_external_backend_contract.py --strict" in "\n".join(ACTION_CATALOG["backend_module"]["commands"])
        and ACTION_CATALOG["backend_module"]["commands"][0].startswith("python scripts\\audit_external_backend_contract.py"),
        "; ".join(ACTION_CATALOG["backend_module"]["commands"]),
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_acquisition_packet_v1",
        "passed": passed,
        "not_external_evidence": True,
        "acquisition_packet_ready": passed,
        "strict_evidence_ready": False,
        "source_reports": [
            rel(path)
            for path in [
                gap_path,
                collection_path,
                preflight_path,
                route_path,
                platform_probe_path,
                task_binding_probe_path,
                env_smoke_probe_path,
                onboarding_path,
                fidelity_provenance_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                config_manifest_path,
                rollout_evidence_path,
                method_packet_path,
            ]
            if path.exists()
        ],
        "missing_requirements": [
            {
                "requirement": row.get("requirement"),
                "blocker": row.get("blocker"),
                "mapped_actions": MISSING_REQUIREMENT_ACTIONS.get(row.get("requirement"), []),
            }
            for row in missing_requirements
        ],
        "collection_blockers": collection_blockers,
        "operator_actions": actions,
        "strict_collection_command": collection.get("strict_collection_command", ""),
        "post_collection_strict_commands": post_collection_commands,
        "checks": checks,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# External Evidence Acquisition Packet",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not evidence: `true`.",
        "Strict evidence ready: `false`.",
        "",
        "This packet maps the remaining main-conference blockers to concrete operator inputs, artifacts, and strict validation commands. It is not robot evidence, not accepted high-fidelity simulator evidence, and not a substitute for the strict external audits.",
        "",
        "## Remaining Submission Blockers",
        "",
        "| Requirement | Operator actions |",
        "|---|---|",
    ]
    for row in payload["missing_requirements"]:
        lines.append(f"| `{row['requirement']}` | {', '.join(f'`{item}`' for item in row['mapped_actions'])} |")

    lines.extend(
        [
            "",
            "## Collection Preflight Blockers",
            "",
        ]
    )
    for item in collection_blockers:
        lines.append(f"- `{blocker_name(item)}`: {blocker_detail(item)}")

    lines.extend(
        [
            "",
            "## Operator Actions",
            "",
            "| ID | Action | Operator input | Key artifacts | Commands |",
            "|---|---|---|---|---|",
        ]
    )
    for action in actions:
        artifacts = "<br>".join(f"`{item}`" for item in action["artifacts"])
        commands = "<br>".join(f"`{item}`" for item in action["commands"])
        lines.append(
            f"| `{action['id']}` | {action['title']} | `{action['operator_input']}` | {artifacts} | {commands} |"
        )

    lines.extend(
        [
            "",
            "## Strict Collection Command",
            "",
            "```powershell",
            collection.get("strict_collection_command", ""),
            "```",
            "",
            "## Post-Collection Strict Gates",
            "",
        ]
    )
    for command in post_collection_commands:
        lines.append(f"- `{command}`")

    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"External acquisition packet: {'PASS' if passed else 'FAIL'}; actions={len(actions)}; blockers={len(missing_requirements)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
