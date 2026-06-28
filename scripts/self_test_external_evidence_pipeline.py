from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import audit_external_evidence as evidence
import audit_external_fidelity_acceptance as fidelity_acceptance
import audit_external_pairing_integrity as pairing_integrity
import audit_external_release_package as release_package
import validate_external_adapters as adapter_validator
import validate_external_configs as config_validator
import validate_external_rollouts as rollout


REAL_ROOT = Path(__file__).resolve().parents[1]
REAL_MANIFEST = REAL_ROOT / "external_validation" / "manifest.json"
REAL_LOG_SCHEMA = REAL_ROOT / "external_validation" / "log_schema_v1.json"
REAL_CONFIG_SCHEMA = REAL_ROOT / "external_validation" / "config_schema_v1.json"

TASKS = [
    "peg_place_regrasp",
    "drawer_to_pick_transfer",
    "door_open_navigation",
    "cable_route_insert",
]

METHODS = [
    "greedy_module_sequence",
    "behavior_cloned_skill_chain",
    "option_graph_planner",
    "diffusion_skill_stitcher",
    "cem_trajectory_composer",
    "residual_rl_composer",
    "energy_compatibility_heuristic",
    "tamp_feasibility_screen",
    "stable_dmp_handoff",
    "proposed_energy_landscape_composer_v4_1",
    rollout.PRIMARY_METHOD,
    rollout.ORACLE_METHOD,
]

BASELINE_SUCCESS_CUTOFFS = {
    "proposed_energy_landscape_composer_v4_1": 24,
    "tamp_feasibility_screen": 21,
    "diffusion_skill_stitcher": 20,
    "cem_trajectory_composer": 19,
    "residual_rl_composer": 19,
    "energy_compatibility_heuristic": 18,
    "option_graph_planner": 17,
    "stable_dmp_handoff": 17,
    "behavior_cloned_skill_chain": 16,
    "greedy_module_sequence": 15,
}

FIXED_RISK_BUDGET = 0.15


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def make_config(task: str, *, version: str, template: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": version,
        "config_schema": "external_validation/config_schema_v1.json",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "TemporaryHighFidelitySim-v0",
        "skill_i": f"{task}_source_skill",
        "skill_j": f"{task}_target_skill",
        "seam_under_test": f"Candidate handoff from {task}_source_skill to {task}_target_skill under paired reset evidence.",
        "required_fidelity_checks": [
            "contact_dynamics_documented",
            "camera_state_logs_synchronized",
            "reset_hashes_reproducible",
        ],
        "reset_protocol": {
            "paired_resets": True,
            "reset_count": 30,
            "scene_id_template": f"{task}_scene_{{index:03d}}",
            "initial_state_hash_required": True,
        },
        "observation_interface": {
            "state_logging_required": True,
            "camera_logging_required": True,
            "contact_or_force_logging_required": True,
        },
        "compute_budget": {
            "same_for_all_non_oracle_methods": True,
            "wall_clock_seconds": 60,
            "simulator_query_budget": 128,
        },
        "paired_reset_count": 30,
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "must_log": json.loads(REAL_CONFIG_SCHEMA.read_text(encoding="utf-8"))["required_log_fields"],
    }
    if template:
        payload["not_external_evidence"] = True
        payload["template_only"] = True
    return payload


def make_fidelity_acceptance() -> dict[str, Any]:
    return {
        "version": "paper119_fidelity_acceptance_v1",
        "not_external_evidence": True,
        "route": "high_fidelity_sim",
        "purpose": "Temporary synthetic self-test fixture for the Paper 119 external fidelity acceptance gate.",
        "platform": {
            "platform_type": "high_fidelity_sim",
            "platform_name": "TemporaryHighFidelitySim-v0",
            "platform_version": "0.0.synthetic",
            "physics_engine": "temporary deterministic contact dynamics engine",
            "contact_solver": "projected contact solver with fixed synthetic parameters",
            "timestep_seconds": 0.01,
            "substeps_per_control_step": 8,
            "robot_model_source": "temporary self-test robot model",
            "asset_sources": ["temporary synthetic task assets"],
            "sensor_modalities": ["state", "camera", "contact_or_force"],
            "state_observation_channels": ["terminal_state", "object_pose", "robot_pose"],
            "contact_or_force_channels": ["contact_events", "normal_force_proxy"],
        },
        "qualification": {
            "pre_registered_before_rollouts": True,
            "deterministic_paired_resets": True,
            "shared_skill_library": True,
            "same_observation_interface": True,
            "same_compute_budget": True,
            "no_privileged_state_for_non_oracle": True,
            "raw_jsonl_is_source_of_truth": True,
            "videos_tied_to_run_ids": True,
            "failed_and_abstained_runs_logged": True,
            "operator_independence_statement": "Temporary self-test operator is independent of target collaborators.",
            "contact_dynamics_justification": "Synthetic contact and dynamics parameters are fixed, logged, and shared across every method.",
            "paired_reset_replay_test": "Every method is replayed on the same scene, seed, skill pair, and initial-state hash.",
            "real_or_benchmark_calibration_basis": "This is a temporary self-test benchmark fixture used only to prove validator behavior.",
            "known_limitations": "Synthetic self-test records are deleted after the run and must not be cited as validation.",
        },
        "task_fidelity": [
            {
                "task_family": task,
                "seam_observable": True,
                "contact_or_dynamics_property": f"{task} seam contact and dynamics are fixed and logged in the synthetic fixture.",
                "minimum_required_signal": "state, camera, and contact-or-force proxy are present in every record",
                "failure_modes_visible_on_video": True,
            }
            for task in TASKS
        ],
        "provenance": {
            "operator_name_or_lab": "synthetic-self-test",
            "operator_not_target_collaborator": True,
            "date_locked": "2026-06-27",
            "code_commit": "synthetic-fixture",
            "skill_library_hash": digest_text("synthetic skill library"),
            "manifest_path": "external_validation/manifest.json",
            "artifact_hash_policy": "sha256",
        },
        "acceptance_gates": [
            {
                "name": "platform_provenance_complete",
                "status": "passed",
                "evidence": "synthetic platform provenance is fully populated",
            },
            {
                "name": "paired_reset_replay_verified",
                "status": "passed",
                "evidence": "synthetic records use paired scene, seed, skill, and initial-state hashes",
            },
            {
                "name": "contact_failure_observable",
                "status": "passed",
                "evidence": "synthetic state, camera, contact proxy, and video paths are present",
            },
            {
                "name": "non_oracle_methods_fair",
                "status": "passed",
                "evidence": "all non-oracle methods share skill, observation, reset, and compute assumptions",
            },
            {
                "name": "raw_logs_drive_metrics",
                "status": "passed",
                "evidence": "rollout metrics are recomputed from JSONL records",
            },
        ],
    }


def method_outcome(method: str, scene_index: int) -> tuple[bool, float]:
    if method == rollout.PRIMARY_METHOD:
        return True, 1.00
    if method == rollout.ORACLE_METHOD:
        return True, 1.08
    cutoff = BASELINE_SUCCESS_CUTOFFS[method]
    success = scene_index < cutoff
    if method == "proposed_energy_landscape_composer_v4_1":
        return success, 0.80 if success else 0.25
    return success, 0.65 if success else 0.20


def make_record(root: Path, task: str, scene_index: int, method: str, video_path: Path, policy_hashes: dict[str, str]) -> dict[str, Any]:
    success, utility = method_outcome(method, scene_index)
    primary = method == rollout.PRIMARY_METHOD
    oracle = method == rollout.ORACLE_METHOD
    scene_id = f"{task}_scene_{scene_index:03d}"
    diagnosis = "none" if success else "basin_miss"
    return {
        "run_id": "synthetic_full_pipeline_self_test_only",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "TemporaryHighFidelitySim-v0",
        "scene_id": scene_id,
        "episode_index": scene_index,
        "seed": scene_index,
        "method": method,
        "skill_i": f"{task}_source_skill",
        "skill_j": f"{task}_target_skill",
        "initial_state_hash": digest_text(f"{task}:{scene_index}:initial"),
        "terminal_sample_set_hash": digest_text(f"{task}:{scene_index}:terminal"),
        "basin_estimate": 0.92 if primary or oracle else 0.62,
        "barrier_score": 0.05 if primary or oracle else 0.35,
        "descent_continuity_score": 0.94 if primary or oracle else 0.58,
        "predicted_seam_risk": 0.04 if primary or oracle else 0.24,
        "fixed_risk_budget": FIXED_RISK_BUDGET,
        "decision": "accept" if success else "transition",
        "failure_diagnosis": diagnosis,
        "repair_action": "none" if success else "bridge_reseed",
        "success": success,
        "seam_failure": not success,
        "barrier_violation": False if primary or oracle else not success,
        "damage_or_intervention": False,
        "composition_cost": 0.12 if primary or oracle else 0.32,
        "realized_seam_breach": False if primary or oracle else not success,
        "utility": utility,
        "video_path": rel(root, video_path),
        "policy_or_config_hash": policy_hashes[method],
    }


def write_baseline_artifacts(root: Path, external: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    methods: list[dict[str, Any]] = []
    code_release: list[dict[str, str]] = []
    checkpoint_release: list[dict[str, str]] = []
    policy_hashes: dict[str, str] = {}
    for method in METHODS:
        method_entry: dict[str, Any] = {"name": method}
        checkpoint = external / "checkpoints" / f"{method}.sha256"
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        checkpoint.write_text(json.dumps({"method": method, "synthetic_self_test_only": True}, sort_keys=True) + "\n", encoding="utf-8")
        checkpoint_hash = file_sha(checkpoint)
        policy_hashes[method] = checkpoint_hash
        method_entry["checkpoint"] = rel(root, checkpoint)
        method_entry["checkpoint_or_config_path"] = rel(root, checkpoint)
        method_entry["checkpoint_or_config_hash"] = checkpoint_hash
        checkpoint_release.append({"path": rel(root, checkpoint), "sha256": checkpoint_hash})

        if method != rollout.ORACLE_METHOD:
            adapter = external / "implementations" / method / "adapter.py"
            adapter.parent.mkdir(parents=True, exist_ok=True)
            adapter.write_text(
                f"""
POLICY_HASH = "{checkpoint_hash}"

def initialize(config):
    return {{"method_name": config.get("method_name"), "policy_or_config_hash": POLICY_HASH}}

def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    return {{
        "decision": "accept",
        "predicted_seam_risk": 0.04,
        "failure_diagnosis": "none",
        "repair_action": "none",
    }}

def log(episode_context, proposal, outcome):
    return {{
        "predicted_seam_risk": proposal["predicted_seam_risk"],
        "decision": proposal["decision"],
        "failure_diagnosis": proposal["failure_diagnosis"],
        "repair_action": proposal["repair_action"],
        "policy_or_config_hash": POLICY_HASH,
    }}

def reset(reset_context):
    return None
""".lstrip(),
                encoding="utf-8",
            )
            method_entry["implementation"] = rel(root, adapter)
            code_release.append({"path": rel(root, adapter), "sha256": file_sha(adapter)})
        methods.append(method_entry)
    return methods, code_release, checkpoint_release, policy_hashes


def write_task_artifacts(root: Path, external: Path, policy_hashes: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    config_release: list[dict[str, str]] = []
    log_release: list[dict[str, str]] = []
    video_release: list[dict[str, str]] = []
    tasks: list[dict[str, Any]] = []
    schema = json.loads(REAL_CONFIG_SCHEMA.read_text(encoding="utf-8"))
    for task in TASKS:
        config_path = external / "configs" / f"{task}.json"
        write_json(config_path, make_config(task, version=schema["evidence_version"], template=False))
        config_release.append({"path": rel(root, config_path), "sha256": file_sha(config_path)})

        template_path = external / "config_templates" / f"{task}.json"
        write_json(template_path, make_config(task, version=schema["template_version"], template=True))

        video_dir = external / "videos" / task
        log_path = external / "logs" / f"{task}.jsonl"
        video_dir.mkdir(parents=True, exist_ok=True)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as handle:
            for scene_index in range(30):
                for method in METHODS:
                    video_path = video_dir / f"{scene_index:03d}_{method}.mp4"
                    video_path.write_bytes((f"synthetic self-test video bytes for {task} {scene_index} {method}\n".encode("utf-8")) * 32)
                    record = make_record(root, task, scene_index, method, video_path, policy_hashes)
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
                    if scene_index == 0 and method in {rollout.PRIMARY_METHOD, "proposed_energy_landscape_composer_v4_1", rollout.ORACLE_METHOD}:
                        video_release.append({"path": rel(root, video_path), "sha256": file_sha(video_path)})
        log_release.append({"path": rel(root, log_path), "sha256": file_sha(log_path)})
        tasks.append(
            {
                "task_family": task,
                "platform_type": "high_fidelity_sim",
                "platform_name": "TemporaryHighFidelitySim-v0",
                "episodes_per_method": 30,
                "skill_i": f"{task}_source_skill",
                "skill_j": f"{task}_target_skill",
                "config_path": rel(root, config_path),
                "log_jsonl": rel(root, log_path),
                "video_dir": rel(root, video_dir),
            }
        )
    return tasks, config_release, log_release, video_release


def patch_module_paths(root: Path, external: Path, results: Path) -> None:
    rollout.ROOT = root
    rollout.EXTERNAL = external
    rollout.RESULTS = results
    rollout.DEFAULT_MANIFEST = external / "manifest.json"
    rollout.DEFAULT_SCHEMA = external / "log_schema_v1.json"
    rollout.OUT_JSON = results / "external_rollout_metrics.json"
    rollout.OUT_MD = results / "external_rollout_metrics.md"

    config_validator.ROOT = root
    config_validator.EXTERNAL = external
    config_validator.RESULTS = results
    config_validator.SCHEMA = external / "config_schema_v1.json"
    config_validator.TEMPLATE_DIR = external / "config_templates"
    config_validator.MANIFEST = external / "manifest.json"
    config_validator.TEMPLATE_OUT_JSON = results / "external_config_template_audit.json"
    config_validator.TEMPLATE_OUT_MD = results / "external_config_template_audit.md"
    config_validator.EVIDENCE_OUT_JSON = results / "external_config_evidence_audit.json"
    config_validator.EVIDENCE_OUT_MD = results / "external_config_evidence_audit.md"

    adapter_validator.ROOT = root
    adapter_validator.EXTERNAL = external
    adapter_validator.RESULTS = results
    adapter_validator.SPEC_DIR = external / "baseline_specs"
    adapter_validator.BASELINES_DIR = external / "baselines"
    adapter_validator.MANIFEST = external / "manifest.json"
    adapter_validator.LOG_SCHEMA = external / "log_schema_v1.json"
    adapter_validator.OUT_JSON = results / "external_adapter_contract_audit.json"
    adapter_validator.OUT_MD = results / "external_adapter_contract_audit.md"
    adapter_validator.EVIDENCE_OUT_JSON = results / "external_adapter_contract_evidence_audit.json"
    adapter_validator.EVIDENCE_OUT_MD = results / "external_adapter_contract_evidence_audit.md"

    fidelity_acceptance.ROOT = root
    fidelity_acceptance.EXTERNAL = external
    fidelity_acceptance.RESULTS = results
    fidelity_acceptance.MANIFEST = external / "manifest.json"
    fidelity_acceptance.MANIFEST_TEMPLATE = external / "manifest_template.json"
    fidelity_acceptance.TEMPLATE = external / "fidelity_acceptance_template.json"
    fidelity_acceptance.DEFAULT_ACCEPTANCE = external / "fidelity_acceptance.json"
    fidelity_acceptance.OUT_JSON = results / "external_fidelity_acceptance_audit.json"
    fidelity_acceptance.OUT_MD = results / "external_fidelity_acceptance_audit.md"

    pairing_integrity.ROOT = root
    pairing_integrity.EXTERNAL = external
    pairing_integrity.RESULTS = results
    pairing_integrity.DEFAULT_MANIFEST = external / "manifest.json"
    pairing_integrity.DEFAULT_SCHEMA = external / "log_schema_v1.json"
    pairing_integrity.OUT_JSON = results / "external_pairing_integrity_audit.json"
    pairing_integrity.OUT_MD = results / "external_pairing_integrity_audit.md"

    release_package.ROOT = root
    release_package.EXTERNAL = external
    release_package.RESULTS = results
    release_package.DEFAULT_MANIFEST = external / "manifest.json"
    release_package.OUT_JSON = results / "external_release_package_audit.json"
    release_package.OUT_MD = results / "external_release_package_audit.md"

    evidence.ROOT = root
    evidence.RESULTS = results
    evidence.CONTRACT_DIR = external
    evidence.MANIFEST = external / "manifest.json"
    evidence.TEMPLATE = external / "manifest_template.json"
    evidence.AUDIT_JSON = results / "external_evidence_audit.json"
    evidence.AUDIT_MD = results / "external_evidence_audit.md"
    evidence.LOG_SCHEMA = external / "log_schema_v1.json"
    evidence.ROLLOUT_VALIDATOR = root / "scripts" / "validate_external_rollouts.py"
    evidence.ROLLOUT_METRICS_JSON = results / "external_rollout_metrics.json"
    evidence.PAIRING_INTEGRITY_JSON = results / "external_pairing_integrity_audit.json"
    evidence.RELEASE_PACKAGE_JSON = results / "external_release_package_audit.json"
    evidence.BASELINE_CONTRACT_JSON = results / "external_baseline_contract_audit.json"
    evidence.ADAPTER_SCAFFOLD_JSON = results / "external_adapter_scaffold_audit.json"
    evidence.ADAPTER_CONTRACT_JSON = results / "external_adapter_contract_audit.json"
    evidence.ADAPTER_CONTRACT_EVIDENCE_JSON = results / "external_adapter_contract_evidence_audit.json"
    evidence.CONFIG_SCHEMA = external / "config_schema_v1.json"
    evidence.CONFIG_TEMPLATE_AUDIT_JSON = results / "external_config_template_audit.json"
    evidence.CONFIG_EVIDENCE_AUDIT_JSON = results / "external_config_evidence_audit.json"
    evidence.FIDELITY_ACCEPTANCE_AUDIT_JSON = results / "external_fidelity_acceptance_audit.json"
    evidence.BLIND_EVAL_AUDIT_JSON = results / "external_blind_eval_audit.json"


def assert_real_manifest_untouched(before: bytes | None) -> None:
    if before is None:
        if REAL_MANIFEST.exists():
            raise AssertionError(f"self-test created real manifest: {REAL_MANIFEST}")
        return
    if not REAL_MANIFEST.exists() or REAL_MANIFEST.read_bytes() != before:
        raise AssertionError(f"self-test modified real manifest: {REAL_MANIFEST}")


def main() -> int:
    real_manifest_before = REAL_MANIFEST.read_bytes() if REAL_MANIFEST.exists() else None
    with tempfile.TemporaryDirectory(prefix="paper119_external_pipeline_selftest_") as tmp_name:
        root = Path(tmp_name)
        external = root / "external_validation"
        results = root / "results"
        scripts = root / "scripts"
        external.mkdir()
        results.mkdir()
        scripts.mkdir()
        patch_module_paths(root, external, results)

        (external / "log_schema_v1.json").write_text(REAL_LOG_SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
        (external / "config_schema_v1.json").write_text(REAL_CONFIG_SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
        (external / "manifest_template.json").write_text('{"not_external_evidence": true}\n', encoding="utf-8")
        write_json(external / "fidelity_acceptance_template.json", make_fidelity_acceptance() | {"version": "paper119_fidelity_acceptance_template_v1", "template_only": True})
        write_json(external / "fidelity_acceptance.json", make_fidelity_acceptance())
        (scripts / "validate_external_rollouts.py").write_text("# temporary self-test sentinel\n", encoding="utf-8")

        methods, code_release, checkpoint_release, policy_hashes = write_baseline_artifacts(root, external)
        tasks, config_release, log_release, video_release = write_task_artifacts(root, external, policy_hashes)

        manifest: dict[str, Any] = {
            "version": "external_validation_v1",
            "synthetic_self_test_only": True,
            "log_schema": "external_validation/log_schema_v1.json",
            "route": "high_fidelity_sim",
            "code_commit": "synthetic-fixture",
            "skill_library_hash": digest_text("synthetic skill library"),
            "fidelity_acceptance_path": "external_validation/fidelity_acceptance.json",
            "shared_skill_library": True,
            "same_initial_states": True,
            "same_observation_interface": True,
            "same_compute_budget": True,
            "paired_resets": True,
            "tasks": tasks,
            "methods": methods,
            "ablations": {
                "basin_overlap": True,
                "barrier_height": True,
                "descent_continuity": True,
                "risk_calibration": True,
                "seam_repair": True,
            },
            "release_artifacts": {
                "code": code_release,
                "configs": config_release,
                "logs": log_release,
                "videos": video_release,
                "checkpoints": checkpoint_release,
            },
        }
        write_json(external / "manifest.json", manifest)

        schema = json.loads((external / "log_schema_v1.json").read_text(encoding="utf-8"))
        records, errors = rollout.load_records(manifest, schema, check_video_paths=True, max_errors=1)
        if errors:
            raise AssertionError(f"synthetic external records failed validation: {errors[:3]}")
        rollout_summary = rollout.summarize(records, schema)
        threshold_checks = rollout.threshold_checks(rollout_summary, schema)
        failed_thresholds = [check.message for check in threshold_checks if not check.passed]
        if failed_thresholds:
            raise AssertionError(f"synthetic external rollout thresholds failed: {failed_thresholds}")
        rollout.write_outputs(rollout_summary, threshold_checks, [])

        manifest["metrics"] = {
            "external_success_margin": rollout_summary["external_success_margin"],
            "external_utility_margin": rollout_summary["external_utility_margin"],
            "paired_win_rate": rollout_summary["paired_win_rate"],
            "fixed_risk_breach": rollout_summary["fixed_risk_breach"],
            "fixed_risk_coverage": rollout_summary["fixed_risk_coverage"],
            "positive_task_families": rollout_summary["positive_task_families"],
            "external_task_families": rollout_summary["external_task_families"],
            "oracle_reported": True,
            "oracle_stronger_or_saturated_explained": True,
        }
        write_json(external / "manifest.json", manifest)

        template_audit = config_validator.build_audit(strict=False)
        if template_audit["passed"] is not True:
            raise AssertionError(f"synthetic config templates failed: {template_audit['failed_configs']}")
        write_json(results / "external_config_template_audit.json", template_audit)
        config_validator.write_md(template_audit, results / "external_config_template_audit.md")

        evidence_config_audit = config_validator.build_audit(strict=True)
        if evidence_config_audit["passed"] is not True:
            raise AssertionError(f"synthetic evidence configs failed: {evidence_config_audit['failed_configs']}")
        write_json(results / "external_config_evidence_audit.json", evidence_config_audit)
        config_validator.write_md(evidence_config_audit, results / "external_config_evidence_audit.md")

        write_json(
            results / "external_baseline_contract_audit.json",
            {
                "version": "external_baseline_contract_audit_v1",
                "not_external_evidence": True,
                "passed": True,
                "methods": METHODS,
            },
        )
        write_json(
            results / "external_adapter_scaffold_audit.json",
            {
                "version": "external_adapter_scaffold_audit_v1",
                "not_external_evidence": True,
                "passed": True,
                "methods": METHODS,
            },
        )

        baseline_spec_dir = external / "baseline_specs"
        baseline_spec_dir.mkdir(parents=True, exist_ok=True)
        for method in METHODS:
            write_json(
                baseline_spec_dir / f"{method}.json",
                {
                    "version": "paper119_external_baseline_spec_v1",
                    "not_external_evidence": True,
                    "method": method,
                    "required_entrypoint": f"{method}_entrypoint",
                },
            )
        scaffold_dir = external / "baselines"
        scaffold_dir.mkdir(parents=True, exist_ok=True)
        for method in METHODS:
            if method == rollout.ORACLE_METHOD:
                continue
            method_dir = scaffold_dir / method
            method_dir.mkdir(parents=True, exist_ok=True)
            (method_dir / "adapter_template.py").write_text(
                """
NOT_EXTERNAL_EVIDENCE = True
SCAFFOLD_ONLY = True

def initialize(config):
    raise NotImplementedError()

def propose(observation, terminal_samples, skill_i, skill_j, compute_budget):
    raise NotImplementedError()

def log(episode_context, proposal, outcome):
    raise NotImplementedError()

def reset(reset_context):
    raise NotImplementedError()
""".lstrip(),
                encoding="utf-8",
            )

        adapter_contract_audit = adapter_validator.build_audit(strict=False)
        if adapter_contract_audit["passed"] is not True:
            raise AssertionError(f"synthetic adapter contract audit failed: {adapter_contract_audit['failed_adapters']}")
        adapter_validator.write_outputs(adapter_contract_audit)

        adapter_contract_evidence = adapter_validator.build_audit(strict=True)
        if adapter_contract_evidence["passed"] is not True:
            raise AssertionError(f"synthetic adapter contract evidence audit failed: {adapter_contract_evidence['failed_adapters']}")
        adapter_validator.write_outputs(adapter_contract_evidence)

        source, source_kind = fidelity_acceptance.choose_source(manifest, manifest_exists=True)
        acceptance_payload = fidelity_acceptance.read_json(source)
        contract_checks = fidelity_acceptance.audit_contract(acceptance_payload, source)
        evidence_checks = fidelity_acceptance.audit_evidence(acceptance_payload, source, manifest, True, source_kind)
        acceptance_ready = all(check["passed"] for check in contract_checks + evidence_checks)
        if not acceptance_ready:
            failures = [f"{check['name']}: {check['detail']}" for check in contract_checks + evidence_checks if not check["passed"]]
            raise AssertionError(f"synthetic fidelity acceptance failed: {failures}")
        fidelity_result = {
            "version": "external_fidelity_acceptance_audit_v1",
            "passed": True,
            "not_external_evidence": True,
            "acceptance_ready": True,
            "readiness_state": "READY",
            "source": rel(root, source),
            "source_kind": source_kind,
            "manifest_exists": True,
            "expected_real_acceptance_path": rel(root, external / "fidelity_acceptance.json"),
            "blocking_missing_count": 0,
            "blocking_missing": [],
            "contract_checks": contract_checks,
            "evidence_checks": evidence_checks,
            "operator_next_actions": [],
        }
        write_json(results / "external_fidelity_acceptance_audit.json", fidelity_result)
        fidelity_acceptance.write_markdown(fidelity_result)

        pairing_result = pairing_integrity.build_payload(external / "manifest.json", external / "log_schema_v1.json")
        if pairing_result["pairing_ready"] is not True:
            raise AssertionError(f"synthetic pairing integrity failed: {pairing_result['blocking_missing']}")
        pairing_integrity.write_outputs(pairing_result)

        release_result = release_package.build_payload(external / "manifest.json")
        if release_result["release_package_ready"] is not True:
            raise AssertionError(f"synthetic release package failed: {release_result['blocking_missing']}")
        release_package.write_outputs(release_result)

        write_json(
            results / "external_blind_eval_audit.json",
            {
                "version": "external_blind_eval_plan_v1",
                "passed": True,
                "not_external_evidence": True,
                "row_count": 1440,
                "alias_count": 12,
                "checks": [
                    {"name": "blinded_sheet_has_no_method_names", "passed": True, "detail": "synthetic self-test"}
                ],
            },
        )

        audit = evidence.audit_manifest(manifest, manifest_exists=True)
        evidence.AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        evidence.write_markdown(audit)
        if audit["submission_ready"] is not True:
            failures = [f"{item['name']}: {item['detail']}" for item in audit["blocking_failures"]]
            raise AssertionError(f"synthetic full-pipeline audit did not pass: {failures}")

    assert_real_manifest_untouched(real_manifest_before)
    print("External evidence pipeline self-test passed: temporary synthetic package reaches READY and real repo evidence remains untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
