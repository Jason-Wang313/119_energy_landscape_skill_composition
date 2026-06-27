from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import audit_external_fidelity_acceptance as fidelity


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "external_fidelity_acceptance_self_test.json"
OUT_MD = RESULTS / "external_fidelity_acceptance_self_test.md"
REAL_REPORT = RESULTS / "external_fidelity_acceptance_audit.json"


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def required_task_entries() -> list[dict[str, Any]]:
    entries = []
    for task in sorted(fidelity.REQUIRED_TASKS):
        entries.append(
            {
                "task_family": task,
                "seam_observable": True,
                "failure_modes_visible_on_video": True,
                "contact_or_dynamics_property": f"{task} exposes basin mismatch, barrier, contact, or dynamics discontinuity in the temporary fixture.",
                "minimum_required_signal": "state, camera, and contact-or-force proxy channels are present for every synthetic run.",
            }
        )
    return entries


def synthetic_acceptance_payload() -> dict[str, Any]:
    return {
        "version": fidelity.EVIDENCE_VERSION,
        "not_external_evidence": True,
        "template_only": False,
        "route": "high_fidelity_sim",
        "purpose": "Temporary synthetic self-test fixture for the Paper 119 external fidelity acceptance gate.",
        "platform": {
            "platform_type": "high_fidelity_sim",
            "platform_name": "FidelityAcceptanceSelfTestSim-v1",
            "platform_version": "1.0.synthetic",
            "physics_engine": "deterministic synthetic contact dynamics engine",
            "contact_solver": "fixed-parameter projected contact solver",
            "timestep_seconds": 0.005,
            "substeps_per_control_step": 4,
            "robot_model_source": "temporary self-test robot model",
            "asset_sources": ["temporary synthetic task assets"],
            "sensor_modalities": ["state", "camera", "contact_or_force"],
            "state_observation_channels": ["joint_positions", "object_pose", "terminal_state"],
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
            "operator_independence_statement": "Temporary self-test operator fixture is independent of target collaborators.",
            "contact_dynamics_justification": "Synthetic contact and dynamics parameters are fixed, documented, and shared across all methods.",
            "paired_reset_replay_test": "Every method is replayed on the same task family, seed, skill pair, and initial-state hash.",
            "real_or_benchmark_calibration_basis": "This is a benchmark-style synthetic fixture used only to prove validator behavior.",
            "known_limitations": "Temporary self-test records are deleted after the run and must not be cited as validation evidence.",
        },
        "task_fidelity": required_task_entries(),
        "provenance": {
            "operator_name_or_lab": "Synthetic Fidelity Acceptance Self-Test Lab",
            "operator_not_target_collaborator": True,
            "date_locked": "2026-06-27",
            "code_commit": "synthetic-fidelity-self-test",
            "skill_library_hash": digest_text("paper119 synthetic fidelity skill library"),
            "artifact_hash_policy": "sha256",
        },
        "acceptance_gates": [
            {"name": "platform_provenance_complete", "status": "passed"},
            {"name": "paired_reset_replay_verified", "status": "passed"},
            {"name": "contact_failure_observable", "status": "passed"},
            {"name": "non_oracle_methods_fair", "status": "passed"},
            {"name": "raw_logs_drive_metrics", "status": "passed"},
        ],
    }


def synthetic_manifest_payload(acceptance_path: Path) -> dict[str, Any]:
    return {
        "version": "paper119_external_manifest_v1",
        "route": "high_fidelity_sim",
        "fidelity_acceptance_path": str(acceptance_path),
        "tasks": [
            {
                "task_family": task,
                "platform_type": "high_fidelity_sim",
                "config_path": f"external_validation/configs/{task}.json",
            }
            for task in sorted(fidelity.REQUIRED_TASKS)
        ],
    }


def checks_by_name(checks: list[dict[str, Any]]) -> dict[str, bool]:
    return {str(check.get("name")): bool(check.get("passed")) for check in checks}


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Fidelity Acceptance Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Synthetic acceptance ready: `{str(payload['synthetic_acceptance_ready']).lower()}`.",
        "",
        "This self-test builds a temporary high-fidelity acceptance fixture and exercises the platform/provenance acceptance gate directly. It proves the strict-ready path can pass for a complete synthetic fixture, that the template/default path remains fail-closed, and that the real fidelity audit report is not overwritten.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks: list[dict[str, Any]] = []
    report_before = file_digest(REAL_REPORT)

    with tempfile.TemporaryDirectory(prefix="paper119_fidelity_acceptance_selftest_") as tmp_name:
        tmp = Path(tmp_name)
        acceptance_path = tmp / "fidelity_acceptance.json"
        acceptance_payload = synthetic_acceptance_payload()
        manifest_payload = synthetic_manifest_payload(acceptance_path)
        write_json(acceptance_path, acceptance_payload)

        contract_checks = fidelity.audit_contract(acceptance_payload, acceptance_path)
        evidence_checks = fidelity.audit_evidence(
            acceptance_payload,
            acceptance_path,
            manifest_payload,
            True,
            "manifest",
        )

        template_payload = fidelity.read_json(fidelity.TEMPLATE)
        template_contract_checks = fidelity.audit_contract(template_payload, fidelity.TEMPLATE)
        template_evidence_checks = fidelity.audit_evidence(
            template_payload,
            fidelity.TEMPLATE,
            {},
            False,
            "template",
        )

    report_after = file_digest(REAL_REPORT)

    contract = checks_by_name(contract_checks)
    evidence = checks_by_name(evidence_checks)
    template_evidence = checks_by_name(template_evidence_checks)
    synthetic_ready = all(contract.values()) and all(evidence.values())
    template_ready = all(check.get("passed") for check in template_contract_checks) and all(
        check.get("passed") for check in template_evidence_checks
    )

    add_check(
        checks,
        "synthetic_strict_acceptance_ready",
        synthetic_ready,
        f"contract_failures={[c['name'] for c in contract_checks if not c['passed']]}, evidence_failures={[c['name'] for c in evidence_checks if not c['passed']]}",
    )
    add_check(
        checks,
        "synthetic_route_task_count",
        evidence.get("route_has_enough_task_families") is True,
        f"route_has_enough_task_families={evidence.get('route_has_enough_task_families')!r}",
    )
    add_check(
        checks,
        "synthetic_platform_modalities",
        evidence.get("modalities_cover_state_camera_contact") is True
        and evidence.get("contact_channels_declared") is True,
        f"modalities={evidence.get('modalities_cover_state_camera_contact')!r}, contact_channels={evidence.get('contact_channels_declared')!r}",
    )
    add_check(
        checks,
        "template_acceptance_fails_strict_evidence",
        template_ready is False
        and template_evidence.get("manifest_exists") is False
        and template_evidence.get("real_acceptance_file_exists") is False
        and template_evidence.get("not_template_only") is False,
        f"template_ready={template_ready!r}",
    )
    add_check(
        checks,
        "real_fidelity_report_not_overwritten",
        report_before == report_after,
        f"before={report_before}, after={report_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "external_fidelity_acceptance_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "synthetic_acceptance_ready": synthetic_ready,
        "template_acceptance_ready": template_ready,
        "real_fidelity_report_before": report_before,
        "real_fidelity_report_after": report_after,
        "checks": checks,
    }
    write_report(payload)
    print(f"External fidelity acceptance self-test: {'PASS' if passed else 'FAIL'}; synthetic_acceptance_ready={synthetic_ready}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
