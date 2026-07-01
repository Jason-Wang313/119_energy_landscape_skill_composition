from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = RESULTS / "external_evidence_closure_brief.json"
OUT_MD = RESULTS / "external_evidence_closure_brief.md"
OUT_DOC = DOCS / "external_evidence_closure_brief.md"

VERSION = "external_evidence_closure_brief_v1"

EXPECTED_MISSING_REQUIREMENTS = [
    "Independent real-robot or accepted high-fidelity external validation evidence",
    "External rollout metrics recomputed from raw JSONL logs",
    "Manifest-declared real task configs replace non-evidence templates",
    "Manifest-declared independent non-oracle baseline evidence and fairness contract",
]

CLOSURE_SPEC: dict[str, dict[str, Any]] = {
    "Independent real-robot or accepted high-fidelity external validation evidence": {
        "closure_id": "accepted_fidelity_and_manifest",
        "proof_artifacts": [
            "external_validation/fidelity_acceptance.json",
            "external_validation/manifest.json",
            "external_validation/platform_onboarding_packet.json",
            "external_validation/precollection_freeze_receipt.json",
            "external_validation/postcollection_evidence_seal.json",
        ],
        "operator_inputs": [
            "independent operator or lab identity",
            "accepted robot or high-fidelity simulator machine",
            "contact solver, friction model, timing, observation, controller, and asset provenance",
            "render-backed video readiness and paired-reset replay acceptance",
            "current clean code commit and skill-library hash",
        ],
        "strict_gates": [
            "python scripts\\materialize_fidelity_acceptance.py ... --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write",
            "python scripts\\audit_external_fidelity_acceptance.py --strict",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "completion_test": "accepted fidelity provenance exists, the official manifest exists, and the final strict external evidence audit no longer reports fidelity or manifest blockers",
    },
    "External rollout metrics recomputed from raw JSONL logs": {
        "closure_id": "raw_rollouts_videos_and_metrics",
        "proof_artifacts": [
            "external_validation/logs/*.jsonl",
            "external_validation/videos/<task_family>/*.mp4",
            "results/external_rollout_metrics.json",
            "results/external_rollout_metrics.md",
        ],
        "operator_inputs": [
            "paired resets for every task/method panel",
            "official JSONL rows written only by the checked runner path",
            "render-backed MP4 videos for success and failure evidence",
            "manifest-declared task, method, config, and policy/config hashes",
        ],
        "strict_gates": [
            "python external_validation\\runner\\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id <specific_run_id> --unsealed-alias-map",
            "python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
            "python scripts\\audit_external_pairing_integrity.py --strict",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "completion_test": "strict rollout validation recomputes metrics from raw JSONL logs and the final audit agrees with the manifest metrics",
    },
    "Manifest-declared real task configs replace non-evidence templates": {
        "closure_id": "manifest_bound_task_configs",
        "proof_artifacts": [
            "external_validation/configs/peg_place_regrasp.json",
            "external_validation/configs/drawer_to_pick_transfer.json",
            "external_validation/configs/door_open_navigation.json",
            "external_validation/configs/cable_route_insert.json",
            "external_validation/manifest.json",
        ],
        "operator_inputs": [
            "accepted backend task binding for each task family",
            "real platform timing and query-budget fields",
            "manifest config_path/config_hash fields matching the collected logs",
        ],
        "strict_gates": [
            "python scripts\\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
            "python scripts\\validate_external_configs.py --strict",
            "python scripts\\build_external_manifest.py --write --check-video-paths",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "completion_test": "strict config evidence passes against manifest-declared config files and hashes rather than template or local-dry-run configs",
    },
    "Manifest-declared independent non-oracle baseline evidence and fairness contract": {
        "closure_id": "independent_methods_and_fairness_contract",
        "proof_artifacts": [
            "external_validation/method_implementation_work_orders.csv",
            "external_validation/method_manifest_cutover_checklist.csv",
            "external_validation/method_config_candidates.csv",
            "external_validation/manifest.json",
            "external_validation/checkpoints_or_configs/<method>.*",
        ],
        "operator_inputs": [
            "real non-oracle implementation/config/checkpoint path for every required method",
            "checkpoint_or_config_hash values backed by real artifacts, not implementation source",
            "matching JSONL policy_or_config_hash values",
            "shared skill library, observation interface, compute budget, and paired-reset contract hashes",
        ],
        "strict_gates": [
            "python scripts\\build_external_baseline_contract.py",
            "python scripts\\validate_external_adapters.py --strict",
            "python scripts\\audit_external_release_package.py --strict",
            "python scripts\\audit_external_evidence.py --strict",
        ],
        "completion_test": "strict adapter evidence passes and the final audit accepts the independent non-oracle method evidence plus fairness contract",
    },
}

COMMAND_SPINE = [
    "python scripts\\probe_external_platform.py --strict",
    "python scripts\\probe_maniskill_task_bindings.py --strict",
    "python scripts\\probe_maniskill_env_smoke.py --strict",
    "python scripts\\probe_maniskill_fidelity_metadata.py --strict",
    "python scripts\\audit_maniskill_render_video_preflight.py --timeout-seconds 120 --max-envs 4 --width 128 --height 128 --render-backend <accepted_backend> --shader-pack <accepted_shader_pack> --profile-matrix --profile-matrix-max-envs 1 --timeout-diagnosis-seconds 180 --timeout-diagnosis-width 64 --timeout-diagnosis-height 64",
    "python scripts\\materialize_external_configs.py --platform-type <real_robot|high_fidelity_sim> --platform-name <accepted_platform_name> --wall-clock-seconds <seconds> --simulator-query-budget <queries> --confirm-real-platform --write",
    "python scripts\\audit_external_backend_contract.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --alias-map external_validation\\method_alias_map.json",
    "python scripts\\materialize_fidelity_acceptance.py --operator-name-or-lab <independent_operator_or_lab> --accepted-collection-machine <machine_or_robot_platform> --contact-solver-and-friction-model <solver_friction_contact_model> --timestep-and-substeps-per-control-step <sim_dt_control_dt_substeps> --paired-reset-replay-test <paired_reset_replay_result> --real-or-benchmark-calibration-basis <calibration_basis> --task-binding-decision <accepted_or_replaced_task_bindings> --acceptance-gate-signoff <gate_signoff_summary> --known-limitations <known_limitations> --date-locked <YYYY-MM-DD> --code-commit <current_clean_checkout_commit_sha> --skill-library-hash <current_baselines_sha256> --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --write",
    "python scripts\\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\\configs --run-id <specific_run_id> --unsealed-alias-map",
    "python scripts\\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
    "python external_validation\\runner\\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\\configs --output-log-dir external_validation\\logs --video-dir external_validation\\videos --run-id <specific_run_id> --unsealed-alias-map",
    "python scripts\\build_external_postcollection_evidence_seal.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-sealed <YYYY-MM-DD>",
    "python scripts\\audit_external_postcollection_seal_consistency.py",
    "python scripts\\build_external_manifest.py --write --check-video-paths",
    "python scripts\\validate_external_configs.py --strict",
    "python scripts\\validate_external_adapters.py --strict",
    "python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
    "python scripts\\audit_external_pairing_integrity.py --strict",
    "python scripts\\audit_external_release_package.py --strict",
    "python scripts\\audit_external_evidence.py --strict",
    "python scripts\\audit_submission_readiness_gap.py",
]

REQUIRED_COMMAND_FRAGMENTS = [
    "probe_external_platform.py --strict",
    "probe_maniskill_task_bindings.py --strict",
    "probe_maniskill_env_smoke.py --strict",
    "probe_maniskill_fidelity_metadata.py --strict",
    "audit_maniskill_render_video_preflight.py",
    "materialize_external_configs.py",
    "audit_external_backend_contract.py --strict",
    "materialize_fidelity_acceptance.py",
    "--confirm-independent-operator",
    "audit_external_collection_readiness.py --strict",
    "build_external_precollection_freeze_receipt.py",
    "real_collection_runner.py",
    "build_external_postcollection_evidence_seal.py",
    "audit_external_postcollection_seal_consistency.py",
    "build_external_manifest.py --write --check-video-paths",
    "validate_external_configs.py --strict",
    "validate_external_adapters.py --strict",
    "validate_external_rollouts.py",
    "audit_external_pairing_integrity.py --strict",
    "audit_external_release_package.py --strict",
    "audit_external_evidence.py --strict",
    "audit_submission_readiness_gap.py",
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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def named_checks(payload: dict[str, Any]) -> dict[str, bool]:
    return {str(check.get("name")): check.get("passed") is True for check in payload.get("checks", []) or []}


def missing_requirements(gap: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in gap.get("requirements", []) or []
        if isinstance(row, dict) and row.get("status") == "missing" and row.get("submission_blocking") is True
    ]


def build_closure_items(missing: list[dict[str, Any]], acquisition: dict[str, Any]) -> list[dict[str, Any]]:
    acquisition_missing = {
        str(row.get("requirement")): row
        for row in acquisition.get("missing_requirements", []) or []
        if isinstance(row, dict)
    }
    items: list[dict[str, Any]] = []
    for row in missing:
        requirement = str(row.get("requirement", ""))
        spec = CLOSURE_SPEC.get(requirement, {})
        acquisition_row = acquisition_missing.get(requirement, {})
        items.append(
            {
                "requirement": requirement,
                "closure_id": spec.get("closure_id", ""),
                "current_blocker": str(row.get("blocker", "")),
                "mapped_operator_actions": list(acquisition_row.get("mapped_actions", []) or []),
                "proof_artifacts": list(spec.get("proof_artifacts", []) or []),
                "operator_inputs": list(spec.get("operator_inputs", []) or []),
                "strict_gates": list(spec.get("strict_gates", []) or []),
                "completion_test": spec.get("completion_test", ""),
                "evidence_ready_now": False,
            }
        )
    return items


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Evidence Closure Brief",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Current decision: `{payload['current_decision']}`.",
        f"Current readiness: `{payload['satisfied_requirements']}/{payload['total_requirements']}` requirements satisfied.",
        f"Blocking missing requirements: `{payload['blocking_missing_requirements']}`.",
        f"Haonan dependency: `{str(payload['haonan_dependency']).lower()}`.",
        "",
        "This is the compact closure recipe for the remaining proof layer. It does not create robot evidence, simulator evidence, rollout logs, videos, checkpoints, or `external_validation/manifest.json`. Its job is to make the final validation layer unambiguous: an independent operator must close all four external-evidence blockers through the strict gates below.",
        "",
        "## Minimum Proof Package",
        "",
    ]
    for item in payload["closure_items"]:
        lines.extend(
            [
                f"### {item['closure_id']}",
                "",
                f"- Requirement: `{item['requirement']}`",
                f"- Current blocker: {item['current_blocker']}",
                f"- Evidence ready now: `{str(item['evidence_ready_now']).lower()}`",
                "- Proof artifacts:",
            ]
        )
        for artifact in item["proof_artifacts"]:
            lines.append(f"  - `{artifact}`")
        lines.append("- Operator inputs:")
        for operator_input in item["operator_inputs"]:
            lines.append(f"  - {operator_input}")
        lines.append("- Strict gates:")
        for command in item["strict_gates"]:
            lines.append(f"  - `{command}`")
        lines.append(f"- Completion test: {item['completion_test']}")
        lines.append("")

    lines.extend(
        [
            "## Chronological Command Spine",
            "",
            "These commands are placeholders until an independent operator supplies real platform identifiers, backend module, run id, signoff fields, and collection-machine details. They are listed to preserve order: probe, qualify, accept fidelity, freeze, collect, seal, manifest, recompute, then audit.",
            "",
            "```powershell",
        ]
    )
    lines.extend(payload["command_spine"])
    lines.extend(
        [
            "```",
            "",
            "## Outreach Boundary",
            "",
            "Use this brief as the private answer to what remains. Do not pitch Haonan as responsible for supplying the missing proof. The collaboration ask should be about whether the seam-certification layer is scientifically useful in a behavior-composition stack and what would falsify it cleanly.",
            "",
            "## Checks",
            "",
        ]
    )
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    text = "\n".join(lines) + "\n"
    OUT_MD.write_text(text, encoding="utf-8")
    OUT_DOC.write_text(text, encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)

    gap = read_json(RESULTS / "submission_readiness_gap_audit.json")
    acquisition = read_json(RESULTS / "external_acquisition_packet.json")
    execution = read_json(RESULTS / "external_execution_readiness_audit.json")
    intake = read_json(RESULTS / "external_evidence_intake_ledger_audit.json")
    release = read_json(RESULTS / "external_operator_release_bundle_plan.json")
    collection_job = read_json(RESULTS / "external_collection_job_packet_audit.json")
    machine_bootstrap = read_json(RESULTS / "external_collection_machine_bootstrap_audit.json")

    missing = missing_requirements(gap)
    missing_names = [str(row.get("requirement", "")) for row in missing]
    closure_items = build_closure_items(missing, acquisition)
    command_text = "\n".join(COMMAND_SPINE)
    acquisition_checks = named_checks(acquisition)

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "brief_is_non_evidence_and_currently_incomplete",
        gap.get("objective_complete") is False
        and gap.get("current_decision") == "STRONG_REVISE"
        and acquisition.get("strict_evidence_ready") is False,
        f"objective_complete={gap.get('objective_complete')!r}, decision={gap.get('current_decision')!r}, strict={acquisition.get('strict_evidence_ready')!r}",
    )
    add_check(
        checks,
        "exact_four_submission_blockers_mapped",
        missing_names == EXPECTED_MISSING_REQUIREMENTS
        and int(gap.get("blocking_missing_requirements", 0) or 0) == 4
        and len(closure_items) == 4,
        f"missing={missing_names}",
    )
    add_check(
        checks,
        "closure_items_are_concrete",
        all(
            item.get("closure_id")
            and len(item.get("mapped_operator_actions", []) or []) >= 4
            and len(item.get("proof_artifacts", []) or []) >= 4
            and len(item.get("operator_inputs", []) or []) >= 3
            and len(item.get("strict_gates", []) or []) >= 3
            and item.get("completion_test")
            and item.get("evidence_ready_now") is False
            for item in closure_items
        ),
        f"items={len(closure_items)}",
    )
    add_check(
        checks,
        "command_spine_covers_all_strict_gates",
        all(fragment in command_text for fragment in REQUIRED_COMMAND_FRAGMENTS),
        f"missing={[fragment for fragment in REQUIRED_COMMAND_FRAGMENTS if fragment not in command_text]}",
    )
    add_check(
        checks,
        "independent_route_not_haonan_dependent",
        acquisition_checks.get("route_independent_of_haonan") is True
        and "Haonan" not in " ".join(item["completion_test"] for item in closure_items),
        f"route_check={acquisition_checks.get('route_independent_of_haonan')!r}",
    )
    add_check(
        checks,
        "source_packets_ready_but_not_evidence",
        acquisition.get("passed") is True
        and execution.get("passed") is True
        and execution.get("execution_packet_ready") is True
        and execution.get("strict_evidence_ready") is False
        and intake.get("passed") is True
        and intake.get("blocking_failure_count") == intake.get("mapped_failure_count")
        and release.get("passed") is True
        and release.get("strict_external_evidence_ready") is False
        and release.get("bundle_state") == "READY_TO_SEND_OPERATOR_PACKAGE",
        (
            f"acquisition={acquisition.get('passed')!r}, execution={execution.get('execution_packet_ready')!r}, "
            f"intake={intake.get('mapped_failure_count')}/{intake.get('blocking_failure_count')}, release={release.get('bundle_state')!r}"
        ),
    )
    add_check(
        checks,
        "collection_spines_exist_for_windows_and_linux",
        collection_job.get("passed") is True
        and machine_bootstrap.get("passed") is True
        and (EXTERNAL / "collection_job_commands.ps1").exists()
        and (EXTERNAL / "collection_job_commands.sh").exists()
        and (EXTERNAL / "collection_machine_bootstrap.ps1").exists()
        and (EXTERNAL / "collection_machine_bootstrap.sh").exists(),
        f"job={collection_job.get('passed')!r}, bootstrap={machine_bootstrap.get('passed')!r}",
    )
    add_check(
        checks,
        "no_real_manifest_written_before_external_evidence",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "current_decision": gap.get("current_decision"),
        "objective_complete": gap.get("objective_complete"),
        "satisfied_requirements": gap.get("satisfied_requirements"),
        "total_requirements": len(gap.get("requirements", []) or []),
        "blocking_missing_requirements": gap.get("blocking_missing_requirements"),
        "missing_requirements": missing_names,
        "haonan_dependency": False,
        "primary_independent_route": "maniskill_sapien_primary",
        "source_packets": {
            "submission_readiness_gap": "results/submission_readiness_gap_audit.json",
            "external_acquisition_packet": "results/external_acquisition_packet.json",
            "external_execution_readiness": "results/external_execution_readiness_audit.json",
            "external_evidence_intake_ledger": "results/external_evidence_intake_ledger_audit.json",
            "operator_release_bundle": "results/external_operator_release_bundle_plan.json",
        },
        "closure_items": closure_items,
        "command_spine": COMMAND_SPINE,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)
    print(
        "External evidence closure brief: "
        f"{'PASS' if passed else 'FAIL'}; blockers={len(closure_items)}; route={payload['primary_independent_route']}"
    )
    if not passed:
        for check in payload["failed_checks"]:
            print(f"FAILED {check['name']}: {check['detail']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_DOC}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
