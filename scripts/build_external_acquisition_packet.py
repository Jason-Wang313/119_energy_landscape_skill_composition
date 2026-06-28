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
        "fidelity_metadata_probe",
        "platform_onboarding",
        "fidelity_provenance_packet",
        "backend_integration_packet",
        "maniskill_reference_backend_audit",
        "maniskill_reference_collection_preflight",
        "fidelity_acceptance_draft",
        "fidelity_acceptance_materializer",
        "rollout_evidence_packet",
        "backend_module",
        "platform_fidelity",
        "pilot_smoke_packet",
        "maniskill_render_video_preflight",
        "maniskill_pilot_runtime_liveness",
        "maniskill_render_machine_qualification",
        "ablation_collection_packet",
        "evidence_intake_ledger",
        "run_collection",
        "manifest_and_release",
    ],
    "External rollout metrics recomputed from raw JSONL logs": [
        "rollout_evidence_packet",
        "ablation_collection_packet",
        "evidence_intake_ledger",
        "run_collection",
        "strict_rollout_recompute",
    ],
    "Manifest-declared real task configs replace non-evidence templates": [
        "config_manifest_packet",
        "evidence_intake_ledger",
        "real_task_configs",
        "manifest_and_release",
    ],
    "Manifest-declared independent non-oracle baseline evidence and fairness contract": [
        "method_implementation_packet",
        "evidence_intake_ledger",
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
    "fidelity_metadata_probe": {
        "title": "Probe ManiSkill/SAPIEN fidelity metadata",
        "operator_input": "record non-evidence timing, scene/backend, controller, observation, and asset metadata for every bound environment candidate",
        "artifacts": [
            "results/maniskill_fidelity_metadata_probe.json",
            "results/maniskill_fidelity_metadata_probe.md",
        ],
        "commands": [
            "python scripts\\probe_maniskill_fidelity_metadata.py",
            "python scripts\\probe_maniskill_fidelity_metadata.py --strict",
        ],
        "closes": ["platform timing/backend/controller metadata intake before operator fidelity acceptance"],
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
            "results/maniskill_fidelity_metadata_probe.json",
            "results/external_platform_onboarding_audit.json",
        ],
        "commands": [
            "python scripts\\probe_external_platform.py",
            "python scripts\\probe_maniskill_task_bindings.py",
            "python scripts\\probe_maniskill_env_smoke.py",
            "python scripts\\probe_maniskill_fidelity_metadata.py",
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
    "ablation_collection_packet": {
        "title": "Collect manifest-declared external ablations",
        "operator_input": "five required ablated variants on the same accepted task configs, skill library, paired resets, observation interface, and compute budget",
        "artifacts": [
            "external_validation/ablation_collection_packet.md",
            "external_validation/ablation_collection_work_orders.csv",
            "results/external_ablation_collection_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_ablation_collection_packet.py",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "closes": [
            "Independent real-robot or accepted high-fidelity external validation evidence",
            "External rollout metrics recomputed from raw JSONL logs",
        ],
    },
    "evidence_intake_ledger": {
        "title": "Use the evidence intake ledger to close every strict external-evidence failure",
        "operator_input": "complete the ledger rows for manifest, fidelity, configs, logs/videos, methods, metrics, ablations, pairing, release hashes, and oracle-boundary explanation",
        "artifacts": [
            "external_validation/evidence_intake_ledger.md",
            "external_validation/evidence_intake_ledger.csv",
            "results/external_evidence_intake_ledger_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_evidence_intake_ledger.py",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "closes": [
            "Independent real-robot or accepted high-fidelity external validation evidence",
            "External rollout metrics recomputed from raw JSONL logs",
            "Manifest-declared real task configs replace non-evidence templates",
            "Manifest-declared independent non-oracle baseline evidence and fairness contract",
        ],
    },
    "platform_fidelity": {
        "title": "Fill platform fidelity acceptance with real provenance",
        "operator_input": "accepted simulator or robot evidence, contact/dynamics/camera/state provenance, and task coverage",
        "artifacts": ["external_validation/fidelity_acceptance.json"],
        "commands": ["python scripts\\audit_external_fidelity_acceptance.py --strict"],
        "closes": ["Independent real-robot or accepted high-fidelity external validation evidence"],
    },
    "fidelity_acceptance_draft": {
        "title": "Generate the tracked ManiSkill fidelity acceptance draft",
        "operator_input": "review the prefilled draft, replace draft-only fields with accepted independent provenance, then promote it only after real platform evidence exists",
        "artifacts": [
            "external_validation/fidelity_acceptance_draft.json",
            "external_validation/fidelity_acceptance_draft.md",
            "results/external_fidelity_acceptance_draft_audit.json",
        ],
        "commands": [
            "python scripts\\build_external_fidelity_acceptance_draft.py",
            "python scripts\\audit_external_fidelity_acceptance.py --strict",
        ],
        "closes": ["platform fidelity acceptance intake; still not evidence until promoted, manifest-declared, and strict-audited"],
    },
    "fidelity_acceptance_materializer": {
        "title": "Materialize fidelity acceptance only through the guarded promotion path",
        "operator_input": "real platform provenance, independent operator signoff, render-backed evidence-video readiness, real rollout evidence, manifest declaration, code commit, and skill-library hash",
        "artifacts": [
            "scripts/materialize_fidelity_acceptance.py",
            "results/fidelity_acceptance_materialization_plan.json",
            "results/fidelity_acceptance_materialization_plan.md",
            "external_validation/fidelity_acceptance.json",
        ],
        "commands": [
            "python scripts\\materialize_fidelity_acceptance.py",
            "python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <commit_sha> --skill-library-hash <sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write",
            "python scripts\\audit_external_fidelity_acceptance.py --strict",
        ],
        "closes": ["guarded promotion from draft fidelity intake to manifest-declared acceptance; still not rollout evidence until strict audits pass"],
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
    "maniskill_pilot_runtime_liveness": {
        "title": "Audit bounded ManiSkill pilot runtime liveness",
        "operator_input": "tracked reference backend, prepared configs, unsealed aliases, pilot-specific run id, and a bounded timeout on the selected runtime machine",
        "artifacts": [
            "scripts/audit_maniskill_pilot_runtime_liveness.py",
            "results/maniskill_pilot_runtime_liveness_audit.json",
            "results/maniskill_pilot_runtime_liveness_audit.md",
        ],
        "commands": [
            "python scripts\\audit_maniskill_pilot_runtime_liveness.py --timeout-seconds 60 --max-rows 1",
        ],
        "closes": ["pre-collection runtime liveness check for the tracked ManiSkill route; not evidence"],
    },
    "maniskill_render_video_preflight": {
        "title": "Audit ManiSkill render-backed evidence-video export",
        "operator_input": "selected ManiSkill/SAPIEN runtime machine with renderer access before full external collection",
        "artifacts": [
            "scripts/audit_maniskill_render_video_preflight.py",
            "results/maniskill_render_video_preflight_audit.json",
            "results/maniskill_render_video_preflight_audit.md",
        ],
        "commands": [
            "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4",
        ],
        "closes": ["pre-collection render-backed MP4 readiness for the tracked ManiSkill route; not evidence"],
    },
    "maniskill_render_machine_qualification": {
        "title": "Qualify the exact render machine before official collection",
        "operator_input": "accepted collection machine with platform probe, render-backed MP4 preflight, pilot liveness, and no diagnostic fallback videos",
        "artifacts": [
            "external_validation/render_machine_qualification_packet.md",
            "scripts/build_maniskill_render_machine_qualification.py",
            "results/maniskill_render_machine_qualification.json",
            "results/maniskill_render_machine_qualification.md",
        ],
        "commands": [
            "python scripts\\build_maniskill_render_machine_qualification.py",
        ],
        "closes": ["accepted-machine render-backed MP4 qualification before collection; not evidence"],
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
            "external_validation/method_reference_provenance.csv",
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
        "artifacts": [
            "external_validation/manifest.json",
            "external_validation/manifest_assembly_checklist.csv",
            "results/external_manifest_builder_report.json",
        ],
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
    fidelity_metadata_probe_path = RESULTS / "maniskill_fidelity_metadata_probe.json"
    onboarding_path = RESULTS / "external_platform_onboarding_audit.json"
    fidelity_provenance_path = RESULTS / "external_fidelity_provenance_audit.json"
    fidelity_draft_path = RESULTS / "external_fidelity_acceptance_draft_audit.json"
    fidelity_materialization_path = RESULTS / "fidelity_acceptance_materialization_plan.json"
    config_materialization_path = RESULTS / "external_config_materialization_plan.json"
    backend_contract_path = RESULTS / "external_backend_contract_audit.json"
    backend_integration_path = RESULTS / "external_backend_integration_audit.json"
    maniskill_backend_path = RESULTS / "maniskill_backend_readiness_audit.json"
    maniskill_preflight_path = RESULTS / "maniskill_reference_collection_preflight_audit.json"
    config_manifest_path = RESULTS / "external_config_manifest_audit.json"
    rollout_evidence_path = RESULTS / "external_rollout_evidence_audit.json"
    ablation_packet_path = RESULTS / "external_ablation_collection_audit.json"
    evidence_intake_path = RESULTS / "external_evidence_intake_ledger_audit.json"
    method_packet_path = RESULTS / "external_method_implementation_audit.json"
    pilot_smoke_path = RESULTS / "external_pilot_smoke_packet_audit.json"
    render_preflight_path = RESULTS / "maniskill_render_video_preflight_audit.json"
    pilot_runtime_path = RESULTS / "maniskill_pilot_runtime_liveness_audit.json"
    render_machine_path = RESULTS / "maniskill_render_machine_qualification.json"

    gap = require_json(gap_path)
    collection = require_json(collection_path)
    preflight = require_json(preflight_path)
    route = require_json(route_path)
    platform_probe = require_json(platform_probe_path)
    task_binding_probe = require_json(task_binding_probe_path)
    env_smoke_probe = require_json(env_smoke_probe_path)
    fidelity_metadata_probe = require_json(fidelity_metadata_probe_path)
    onboarding = require_json(onboarding_path)
    fidelity_provenance = require_json(fidelity_provenance_path)
    fidelity_draft = require_json(fidelity_draft_path)
    fidelity_materialization = require_json(fidelity_materialization_path)
    config_materialization = require_json(config_materialization_path)
    backend_contract = require_json(backend_contract_path)
    backend_integration = require_json(backend_integration_path)
    maniskill_backend = require_json(maniskill_backend_path)
    maniskill_preflight = require_json(maniskill_preflight_path)
    config_manifest = require_json(config_manifest_path)
    rollout_evidence = require_json(rollout_evidence_path)
    ablation_packet = require_json(ablation_packet_path)
    evidence_intake = require_json(evidence_intake_path)
    method_packet = require_json(method_packet_path)
    pilot_smoke = require_json(pilot_smoke_path)
    render_preflight = require_json(render_preflight_path)
    pilot_runtime = require_json(pilot_runtime_path)
    render_machine = require_json(render_machine_path)

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
                fidelity_draft_path,
                fidelity_materialization_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                maniskill_preflight_path,
                config_manifest_path,
                rollout_evidence_path,
                ablation_packet_path,
                evidence_intake_path,
                method_packet_path,
                pilot_smoke_path,
                render_preflight_path,
                pilot_runtime_path,
                render_machine_path,
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
                fidelity_draft_path,
                fidelity_materialization_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                maniskill_preflight_path,
                config_manifest_path,
                rollout_evidence_path,
                ablation_packet_path,
                evidence_intake_path,
                method_packet_path,
                pilot_smoke_path,
                render_preflight_path,
                pilot_runtime_path,
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
        and config_manifest_checks.get("prepared_configs_pass_strict_schema_if_manifest_declared") is True
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
    ablation_checks = {check.get("name"): check.get("passed") for check in ablation_packet.get("checks", []) or []}
    add_check(
        checks,
        "ablation_collection_packet_ready",
        ablation_packet.get("passed") is True
        and ablation_packet.get("not_external_evidence") is True
        and ablation_packet.get("strict_external_evidence_ready") is False
        and ablation_packet.get("manifest_ablation_evidence_ready") is False
        and int(ablation_packet.get("work_order_count", 0) or 0) == 5
        and int(ablation_packet.get("expected_ablation_records", 0) or 0) >= 600
        and ablation_checks.get("every_required_ablation_has_work_order") is True
        and ablation_checks.get("task_and_reset_budget_preserved") is True
        and ablation_checks.get("operator_commands_cover_collection_manifest_rollout_and_strict_evidence") is True
        and (EXTERNAL / "ablation_collection_packet.md").exists()
        and (EXTERNAL / "ablation_collection_work_orders.csv").exists(),
        (
            f"work_order_count={ablation_packet.get('work_order_count')!r}, "
            f"expected_ablation_records={ablation_packet.get('expected_ablation_records')!r}, "
            f"manifest_ablation_evidence_ready={ablation_packet.get('manifest_ablation_evidence_ready')!r}"
        ),
    )
    intake_checks = {check.get("name"): check.get("passed") for check in evidence_intake.get("checks", []) or []}
    add_check(
        checks,
        "evidence_intake_ledger_ready",
        evidence_intake.get("passed") is True
        and evidence_intake.get("not_external_evidence") is True
        and evidence_intake.get("strict_external_evidence_ready") is False
        and int(evidence_intake.get("blocking_failure_count", 0) or 0) >= 30
        and evidence_intake.get("blocking_failure_count") == evidence_intake.get("mapped_failure_count")
        and not evidence_intake.get("unmapped_failures")
        and intake_checks.get("every_blocking_failure_is_mapped") is True
        and intake_checks.get("strict_command_spine_covers_final_evidence_path") is True
        and (EXTERNAL / "evidence_intake_ledger.md").exists()
        and (EXTERNAL / "evidence_intake_ledger.csv").exists(),
        (
            f"mapped={evidence_intake.get('mapped_failure_count')!r}/"
            f"{evidence_intake.get('blocking_failure_count')!r}, "
            f"groups={len(evidence_intake.get('closure_groups', []) or [])}"
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
    render_preflight_checks = {check.get("name"): check.get("passed") for check in render_preflight.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_video_preflight_recorded",
        render_preflight.get("version") == "maniskill_render_video_preflight_audit_v1"
        and render_preflight.get("passed") is True
        and render_preflight.get("not_external_evidence") is True
        and render_preflight.get("strict_external_evidence_ready") is False
        and int(render_preflight.get("env_count", 0) or 0) >= 1
        and isinstance(render_preflight.get("render_video_ready"), bool)
        and render_preflight_checks.get("render_preflight_is_non_evidence") is True
        and render_preflight_checks.get("quarantine_paths_are_not_official_evidence") is True
        and (render_preflight.get("render_video_ready") is True or bool(render_preflight.get("renderer_failure_classes")))
        and (render_preflight.get("render_video_ready") is True or bool(render_preflight.get("operator_remediation")))
        and (ROOT / "scripts" / "audit_maniskill_render_video_preflight.py").exists()
        and (RESULTS / "maniskill_render_video_preflight_audit.md").exists(),
        (
            f"render_video_ready={render_preflight.get('render_video_ready')!r}, "
            f"envs={render_preflight.get('env_count')!r}, "
            f"failure_classes={render_preflight.get('renderer_failure_classes')!r}"
        ),
    )
    pilot_runtime_checks = {check.get("name"): check.get("passed") for check in pilot_runtime.get("checks", []) or []}
    pilot_runtime_records = int(pilot_runtime.get("records_observed", 0) or 0)
    pilot_runtime_videos = int(pilot_runtime.get("videos_written", 0) or 0)
    pilot_runtime_fallbacks = len(pilot_runtime.get("diagnostic_video_fallbacks", []) or [])
    pilot_runtime_basic = (
        pilot_runtime.get("version") == "maniskill_pilot_runtime_liveness_audit_v1"
        and pilot_runtime.get("passed") is True
        and pilot_runtime.get("not_external_evidence") is True
        and pilot_runtime.get("strict_external_evidence_ready") is False
        and pilot_runtime.get("pilot_runtime_ready") is False
        and pilot_runtime.get("render_video_ready") is False
        and pilot_runtime_checks.get("bounded_runner_subprocess_exercised") is True
        and pilot_runtime_checks.get("timeout_or_result_recorded_as_readiness_state") is True
    )
    pilot_runtime_diagnostic_io = (
        pilot_runtime.get("runner_io_ready") is True
        and pilot_runtime_records >= 1
        and pilot_runtime_videos >= 1
        and pilot_runtime_fallbacks >= 1
    )
    pilot_runtime_unavailable = (
        pilot_runtime.get("runner_io_ready") is False
        and pilot_runtime_records == 0
        and pilot_runtime_videos == 0
        and pilot_runtime_fallbacks == 0
    )
    add_check(
        checks,
        "maniskill_pilot_runtime_liveness_ready",
        pilot_runtime_basic
        and (pilot_runtime_diagnostic_io or pilot_runtime_unavailable)
        and (ROOT / "scripts" / "audit_maniskill_pilot_runtime_liveness.py").exists()
        and (RESULTS / "maniskill_pilot_runtime_liveness_audit.md").exists(),
        (
            f"pilot_runtime_ready={pilot_runtime.get('pilot_runtime_ready')!r}, "
            f"runner_io_ready={pilot_runtime.get('runner_io_ready')!r}, "
            f"render_video_ready={pilot_runtime.get('render_video_ready')!r}, "
            f"timed_out={pilot_runtime.get('timed_out')!r}, "
            f"records={pilot_runtime_records!r}, "
            f"videos={pilot_runtime_videos!r}, "
            f"diagnostic_fallbacks={pilot_runtime_fallbacks}, "
            f"failure_summary={pilot_runtime.get('failure_summary')!r}"
        ),
    )
    render_machine_checks = {check.get("name"): check.get("passed") for check in render_machine.get("checks", []) or []}
    add_check(
        checks,
        "maniskill_render_machine_qualification_ready",
        render_machine.get("version") == "maniskill_render_machine_qualification_v1"
        and render_machine.get("passed") is True
        and render_machine.get("not_external_evidence") is True
        and render_machine.get("strict_external_evidence_ready") is False
        and render_machine.get("qualification_state") == "DO_NOT_COLLECT_RENDER_MACHINE"
        and render_machine.get("render_machine_qualified") is False
        and render_machine_checks.get("qualification_packet_is_non_evidence") is True
        and render_machine_checks.get("current_machine_fail_closed_when_render_not_ready") is True
        and (ROOT / "scripts" / "build_maniskill_render_machine_qualification.py").exists()
        and (EXTERNAL / "render_machine_qualification_packet.md").exists()
        and (RESULTS / "maniskill_render_machine_qualification.md").exists(),
        (
            f"qualification_state={render_machine.get('qualification_state')!r}, "
            f"render_machine_qualified={render_machine.get('render_machine_qualified')!r}, "
            f"blocking={len(render_machine.get('blocking_missing', []) or [])}"
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
        and method_packet_checks.get("manifest_entry_templates_cover_required_hash_fields") is True
        and method_packet_checks.get("work_orders_forbid_scaffolds_and_reference_adapters") is True
        and method_packet_checks.get("policy_or_config_hash_in_logs_required") is True
        and method_packet_checks.get("reference_adapter_provenance_covers_non_oracle_methods") is True
        and method_packet_checks.get("reference_adapter_hashes_recorded") is True
        and method_packet_checks.get("reference_adapters_marked_non_evidence") is True
        and method_packet_checks.get("reference_manifest_stubs_not_strict_ready") is True
        and method_packet_checks.get("adapter_evidence_still_missing") is True
        and (EXTERNAL / "method_implementation_packet.md").exists()
        and (EXTERNAL / "method_implementation_work_orders.csv").exists()
        and (EXTERNAL / "method_reference_provenance.csv").exists(),
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
    add_check(
        checks,
        "fidelity_metadata_probe_ready",
        fidelity_metadata_probe.get("version") == "maniskill_fidelity_metadata_probe_v1"
        and fidelity_metadata_probe.get("passed") is True
        and fidelity_metadata_probe.get("not_external_evidence") is True
        and fidelity_metadata_probe.get("metadata_probe_ready") is True
        and fidelity_metadata_probe.get("accepted_fidelity_ready") is False
        and fidelity_metadata_probe.get("strict_external_evidence_ready") is False,
        (
            f"strict_metadata_ready={fidelity_metadata_probe.get('strict_metadata_ready')!r}, "
            f"primary_metadata_missing={fidelity_metadata_probe.get('primary_metadata_missing')!r}"
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
    fidelity_draft_checks = {check.get("name"): check.get("passed") for check in fidelity_draft.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_draft_ready",
        fidelity_draft.get("passed") is True
        and fidelity_draft.get("not_external_evidence") is True
        and fidelity_draft.get("draft_ready") is True
        and fidelity_draft.get("acceptance_ready") is False
        and fidelity_draft.get("strict_fidelity_evidence_ready") is False
        and fidelity_draft.get("strict_external_evidence_ready") is False
        and fidelity_draft_checks.get("draft_is_non_evidence_and_fail_closed") is True
        and fidelity_draft_checks.get("candidate_platform_prefilled_from_reference_route") is True
        and fidelity_draft_checks.get("acceptance_gates_remain_unaccepted") is True
        and (EXTERNAL / "fidelity_acceptance_draft.json").exists()
        and (EXTERNAL / "fidelity_acceptance_draft.md").exists(),
        (
            f"draft_ready={fidelity_draft.get('draft_ready')!r}, "
            f"remaining_operator_inputs={fidelity_draft.get('remaining_operator_input_count')!r}, "
            f"acceptance_ready={fidelity_draft.get('acceptance_ready')!r}"
        ),
    )
    materializer_checks = {check.get("name"): check.get("passed") for check in fidelity_materialization.get("checks", []) or []}
    add_check(
        checks,
        "fidelity_acceptance_materializer_ready",
        fidelity_materialization.get("version") == "fidelity_acceptance_materialization_plan_v1"
        and fidelity_materialization.get("passed") is True
        and fidelity_materialization.get("not_external_evidence") is True
        and fidelity_materialization.get("write_enabled") is False
        and fidelity_materialization.get("acceptance_write_ready") is False
        and fidelity_materialization.get("strict_fidelity_evidence_ready") is False
        and materializer_checks.get("draft_exists_and_is_draft_version") is True
        and materializer_checks.get("operator_write_command_is_guarded") is True
        and (ROOT / "scripts" / "materialize_fidelity_acceptance.py").exists()
        and (RESULTS / "fidelity_acceptance_materialization_plan.md").exists(),
        (
            f"write_enabled={fidelity_materialization.get('write_enabled')!r}, "
            f"acceptance_write_ready={fidelity_materialization.get('acceptance_write_ready')!r}"
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
        "build_external_evidence_intake_ledger.py",
        "build_external_fidelity_provenance_packet.py",
        "build_external_fidelity_acceptance_draft.py",
        "materialize_fidelity_acceptance.py",
        "build_external_platform_onboarding.py",
        "probe_external_platform.py",
        "probe_maniskill_task_bindings.py",
        "probe_maniskill_env_smoke.py",
        "probe_maniskill_fidelity_metadata.py",
        "build_external_method_implementation_packet.py",
        "build_external_pilot_smoke_packet.py",
        "audit_external_pilot_smoke.py",
        "audit_maniskill_render_video_preflight.py",
        "audit_maniskill_pilot_runtime_liveness.py",
        "build_maniskill_render_machine_qualification.py",
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
                fidelity_metadata_probe_path,
                onboarding_path,
                fidelity_provenance_path,
                fidelity_draft_path,
                fidelity_materialization_path,
                config_materialization_path,
                backend_contract_path,
                backend_integration_path,
                maniskill_backend_path,
                config_manifest_path,
                rollout_evidence_path,
                ablation_packet_path,
                evidence_intake_path,
                method_packet_path,
                pilot_smoke_path,
                render_preflight_path,
                pilot_runtime_path,
                render_machine_path,
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
        "render_video_preflight": {
            "not_external_evidence": True,
            "render_video_ready": render_preflight.get("render_video_ready") is True,
            "strict_external_evidence_ready": render_preflight.get("strict_external_evidence_ready") is True,
            "env_count": int(render_preflight.get("env_count", 0) or 0),
            "render_ready_env_count": int(render_preflight.get("render_ready_env_count", 0) or 0),
            "blocking_missing": list(render_preflight.get("blocking_missing", []) or []),
            "renderer_failure_classes": list(render_preflight.get("renderer_failure_classes", []) or []),
            "operator_remediation": list(render_preflight.get("operator_remediation", []) or []),
            "renderer_profile_retest_commands": list(render_preflight.get("renderer_profile_retest_commands", []) or []),
            "audit_command": "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 45 --max-envs 4",
            "audit_path": "results/maniskill_render_video_preflight_audit.json",
            "audit_md_path": "results/maniskill_render_video_preflight_audit.md",
        },
        "render_machine_qualification": {
            "not_external_evidence": True,
            "qualification_state": render_machine.get("qualification_state"),
            "render_machine_qualified": render_machine.get("render_machine_qualified") is True,
            "strict_external_evidence_ready": render_machine.get("strict_external_evidence_ready") is True,
            "blocking_missing": list(render_machine.get("blocking_missing", []) or []),
            "audit_command": "python scripts\\build_maniskill_render_machine_qualification.py",
            "audit_path": "results/maniskill_render_machine_qualification.json",
            "audit_md_path": "results/maniskill_render_machine_qualification.md",
            "operator_packet_path": "external_validation/render_machine_qualification_packet.md",
        },
        "ablation_collection": {
            "not_external_evidence": True,
            "manifest_ablation_evidence_ready": ablation_packet.get("manifest_ablation_evidence_ready") is True,
            "strict_external_evidence_ready": ablation_packet.get("strict_external_evidence_ready") is True,
            "required_ablations": list(ablation_packet.get("required_ablations", []) or []),
            "expected_ablation_records": int(ablation_packet.get("expected_ablation_records", 0) or 0),
            "work_order_count": int(ablation_packet.get("work_order_count", 0) or 0),
            "blocking_missing": list(ablation_packet.get("blocking_missing", []) or []),
            "audit_command": "python scripts\\build_external_ablation_collection_packet.py",
            "audit_path": "results/external_ablation_collection_audit.json",
            "audit_md_path": "results/external_ablation_collection_audit.md",
            "operator_packet_path": "external_validation/ablation_collection_packet.md",
        },
        "evidence_intake_ledger": {
            "not_external_evidence": True,
            "strict_external_evidence_ready": evidence_intake.get("strict_external_evidence_ready") is True,
            "blocking_failure_count": int(evidence_intake.get("blocking_failure_count", 0) or 0),
            "mapped_failure_count": int(evidence_intake.get("mapped_failure_count", 0) or 0),
            "closure_group_count": len(evidence_intake.get("closure_groups", []) or []),
            "unmapped_failures": list(evidence_intake.get("unmapped_failures", []) or []),
            "audit_command": "python scripts\\build_external_evidence_intake_ledger.py",
            "audit_path": "results/external_evidence_intake_ledger_audit.json",
            "audit_md_path": "results/external_evidence_intake_ledger_audit.md",
            "operator_packet_path": "external_validation/evidence_intake_ledger.md",
            "operator_csv_path": "external_validation/evidence_intake_ledger.csv",
        },
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

    render_summary = payload["render_video_preflight"]
    lines.extend(
        [
            "",
            "## ManiSkill Render-Video Preflight",
            "",
            f"- Render video ready: `{str(render_summary['render_video_ready']).lower()}`",
            f"- Renderer failure classes: `{render_summary['renderer_failure_classes']}`",
            f"- Operator remediation items: `{len(render_summary['operator_remediation'])}`",
            f"- Blocking missing: `{render_summary['blocking_missing']}`",
            "",
            "Renderer profile retest commands:",
            "",
        ]
    )
    for command in render_summary["renderer_profile_retest_commands"] or ["none"]:
        lines.extend(["```powershell", command, "```"])

    ablation_summary = payload["ablation_collection"]
    lines.extend(
        [
            "",
            "## External Ablation Collection",
            "",
            f"- Manifest ablation evidence ready: `{str(ablation_summary['manifest_ablation_evidence_ready']).lower()}`",
            f"- Expected ablation records: `{ablation_summary['expected_ablation_records']}`",
            f"- Work orders: `{ablation_summary['work_order_count']}`",
            f"- Blocking missing: `{ablation_summary['blocking_missing']}`",
        ]
    )

    intake_summary = payload["evidence_intake_ledger"]
    lines.extend(
        [
            "",
            "## External Evidence Intake Ledger",
            "",
            f"- Blocking failures mapped: `{intake_summary['mapped_failure_count']}/{intake_summary['blocking_failure_count']}`",
            f"- Closure groups: `{intake_summary['closure_group_count']}`",
            f"- Strict external evidence ready: `{str(intake_summary['strict_external_evidence_ready']).lower()}`",
            f"- Unmapped failures: `{intake_summary['unmapped_failures']}`",
            f"- Ledger: `{intake_summary['operator_packet_path']}`",
            f"- CSV: `{intake_summary['operator_csv_path']}`",
        ]
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
