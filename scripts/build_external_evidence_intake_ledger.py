from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

OUT_JSON = EXTERNAL / "evidence_intake_ledger.json"
OUT_MD = EXTERNAL / "evidence_intake_ledger.md"
OUT_CSV = EXTERNAL / "evidence_intake_ledger.csv"
AUDIT_JSON = RESULTS / "external_evidence_intake_ledger_audit.json"
AUDIT_MD = RESULTS / "external_evidence_intake_ledger_audit.md"

VERSION = "external_evidence_intake_ledger_v1"


STRICT_COMMANDS = [
    r"python scripts\audit_external_fidelity_acceptance.py --strict",
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\audit_external_collection_readiness.py --strict --backend-module <module_or_path> --task-config-dir external_validation\configs --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_precollection_freeze_receipt.py --backend-module <module_or_path> --run-id <specific_run_id> --operator-id <operator_or_lab> --collection-machine <machine_or_robot_platform> --date-locked <YYYY-MM-DD> --unsealed-alias-map",
    r"python external_validation\runner\real_collection_runner.py --backend-module <module_or_path> --task-config-dir external_validation\configs --output-log-dir external_validation\logs --video-dir external_validation\videos --run-id <specific_run_id> --unsealed-alias-map",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_pairing_integrity.py --strict",
    r"python scripts\audit_external_release_package.py --strict",
    r"python scripts\audit_external_evidence.py --strict",
]

GROUPS: dict[str, dict[str, str]] = {
    "manifest_contract": {
        "operator_artifacts": "external_validation/manifest.json with version, route, schema, shared-skill/reset/observation/compute flags, task/method declarations, metrics, and release artifacts",
        "source_packet": "external_validation/manifest_assembly_checklist.csv",
        "strict_gate": "python scripts\\build_external_manifest.py --write --check-video-paths; python scripts\\audit_external_evidence.py --strict",
        "completion_test": "manifest exists, has external_validation_v1, declares log schema, route, tasks, methods, fairness flags, recomputed metrics, and release hashes",
    },
    "fidelity_acceptance": {
        "operator_artifacts": "external_validation/fidelity_acceptance.json promoted from the draft with independent operator signoff, accepted platform provenance, render-backed videos, real rollout evidence, manifest declaration, commit, and skill hash",
        "source_packet": "external_validation/fidelity_provenance_packet.md; external_validation/fidelity_acceptance_draft.md; results/fidelity_acceptance_materialization_plan.md",
        "strict_gate": "python scripts\\materialize_fidelity_acceptance.py ... --confirm-real-platform --confirm-independent-operator --confirm-render-backed-videos --confirm-real-rollout-evidence --confirm-manifest-declaration --write; python scripts\\audit_external_fidelity_acceptance.py --strict",
        "completion_test": "fidelity acceptance audit reports acceptance_ready=true and strict fidelity evidence true",
    },
    "task_configs": {
        "operator_artifacts": "external_validation/configs/<task_family>.json consumed by the accepted backend, with config_hash declared in external_validation/manifest.json",
        "source_packet": "external_validation/config_manifest_packet.md; external_validation/config_manifest_work_orders.csv",
        "strict_gate": "python scripts\\materialize_external_configs.py ... --confirm-real-platform --write; python scripts\\build_external_manifest.py --write --check-video-paths; python scripts\\validate_external_configs.py --strict",
        "completion_test": "strict config evidence audit passes with manifest-declared configs and matching hashes",
    },
    "rollout_logs_videos_metrics": {
        "operator_artifacts": "manifest-declared external_validation/logs/*.jsonl, external_validation/videos/<task_family>/ files, and metrics recomputed from raw JSONL logs",
        "source_packet": "external_validation/rollout_evidence_packet.md; external_validation/rollout_evidence_work_orders.csv",
        "strict_gate": "python external_validation\\runner\\real_collection_runner.py ...; python scripts\\build_external_manifest.py --write --check-video-paths; python scripts\\validate_external_rollouts.py --write-results --check-video-paths --strict",
        "completion_test": "external rollout metric validator passes and manifest metrics match recomputed rollout metrics",
    },
    "methods_baselines": {
        "operator_artifacts": "manifest-declared independent non-oracle implementations/configs/checkpoints with hashes and JSONL policy_or_config_hash values matching the manifest",
        "source_packet": "external_validation/method_implementation_packet.md; external_validation/method_implementation_work_orders.csv; external_validation/method_reference_provenance.csv",
        "strict_gate": "python scripts\\validate_external_adapters.py --strict; python scripts\\audit_external_evidence.py --strict",
        "completion_test": "strict adapter evidence audit passes; scaffolds/reference adapters are not counted as evidence, and checkpoint_or_config_hash values match real checkpoint_or_config_path artifacts rather than implementation source",
    },
    "ablations": {
        "operator_artifacts": "manifest-declared external ablation logs/videos for basin_overlap, barrier_height, descent_continuity, risk_calibration, and seam_repair on the same accepted configs, skill library, resets, observation interface, and compute budget",
        "source_packet": "external_validation/ablation_collection_packet.md; external_validation/ablation_collection_work_orders.csv",
        "strict_gate": "python scripts\\build_external_ablation_collection_packet.py; python scripts\\build_external_manifest.py --write --check-video-paths; python scripts\\audit_external_evidence.py --strict",
        "completion_test": "external evidence audit reports all five manifest.ablations.* flags true with manifest-declared external ablation evidence",
    },
    "pairing_release": {
        "operator_artifacts": "complete paired-reset method panels and release_artifacts entries for code, configs, logs, videos, and checkpoints with valid SHA256 hashes",
        "source_packet": "external_validation/manifest_assembly_checklist.csv; results/external_release_package_audit.md; results/external_pairing_integrity_audit.md",
        "strict_gate": "python scripts\\audit_external_pairing_integrity.py --strict; python scripts\\audit_external_release_package.py --strict",
        "completion_test": "pairing_ready=true and release_package_ready=true under strict audits",
    },
    "oracle_boundary": {
        "operator_artifacts": "manifest metrics explain oracle upper-bound status and saturation/boundary interpretation without using the oracle as an independent baseline",
        "source_packet": "external_validation/manifest_template.json; docs/claim_evidence_ledger.json",
        "strict_gate": "python scripts\\audit_external_evidence.py --strict",
        "completion_test": "oracle_reported=true and oracle_stronger_or_saturated_explained is explicitly set in manifest metrics",
    },
}

FAILURE_GROUPS = {
    "manifest_exists": "manifest_contract",
    "manifest_version": "manifest_contract",
    "manifest_declares_log_schema": "manifest_contract",
    "validation_route": "manifest_contract",
    "shared_skill_library": "manifest_contract",
    "same_initial_states": "manifest_contract",
    "same_observation_interface": "manifest_contract",
    "same_compute_budget": "manifest_contract",
    "paired_resets": "manifest_contract",
    "external_fidelity_acceptance_ready": "fidelity_acceptance",
    "external_config_evidence_passed": "task_configs",
    "valid_task_families": "task_configs",
    "episodes_per_method": "task_configs",
    "episode_log_schema": "rollout_logs_videos_metrics",
    "task_video_dirs": "rollout_logs_videos_metrics",
    "external_success_margin": "rollout_logs_videos_metrics",
    "external_utility_margin": "rollout_logs_videos_metrics",
    "paired_win_rate": "rollout_logs_videos_metrics",
    "fixed_risk_breach": "rollout_logs_videos_metrics",
    "fixed_risk_coverage": "rollout_logs_videos_metrics",
    "positive_task_family_coverage": "rollout_logs_videos_metrics",
    "external_rollout_metrics_passed": "rollout_logs_videos_metrics",
    "external_rollout_confidence_gates_passed": "rollout_logs_videos_metrics",
    "manifest_metrics_match_rollout": "rollout_logs_videos_metrics",
    "external_adapter_contract_evidence_passed": "methods_baselines",
    "required_methods": "methods_baselines",
    "independent_method_implementations": "methods_baselines",
    "release_checkpoints": "methods_baselines",
    "external_ablations": "ablations",
    "external_pairing_integrity_ready": "pairing_release",
    "external_release_package_ready": "pairing_release",
    "release_code": "pairing_release",
    "release_configs": "pairing_release",
    "release_logs": "pairing_release",
    "release_videos": "pairing_release",
    "oracle_reported": "oracle_boundary",
    "oracle_boundary": "oracle_boundary",
}


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


def blocking_failures(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    failures = evidence.get("blocking_failures", [])
    return [row for row in failures if isinstance(row, dict)]


def build_rows(evidence: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    unmapped: list[str] = []
    for failure in blocking_failures(evidence):
        name = str(failure.get("name", ""))
        group = FAILURE_GROUPS.get(name)
        if not group:
            unmapped.append(name)
            continue
        spec = GROUPS[group]
        rows.append(
            {
                "failure_name": name,
                "current_detail": str(failure.get("detail", "")),
                "closure_group": group,
                "operator_artifacts": spec["operator_artifacts"],
                "source_packet": spec["source_packet"],
                "strict_gate": spec["strict_gate"],
                "completion_test": spec["completion_test"],
                "evidence_ready_now": "false",
            }
        )
    return rows, sorted(unmapped)


def write_csv(rows: list[dict[str, str]]) -> None:
    OUT_CSV.parent.mkdir(exist_ok=True)
    fieldnames = [
        "failure_name",
        "current_detail",
        "closure_group",
        "operator_artifacts",
        "source_packet",
        "strict_gate",
        "completion_test",
        "evidence_ready_now",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Evidence Intake Ledger",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        f"Blocking failures mapped: `{payload['mapped_failure_count']}/{payload['blocking_failure_count']}`.",
        "",
        "This ledger maps every current strict external-evidence failure to the operator artifact, source packet, strict gate, and completion test that would close it. It does not create a manifest, logs, videos, checkpoints, or external validation evidence.",
        "",
        "## Closure Groups",
        "",
    ]
    for group in payload["closure_groups"]:
        lines.append(
            f"- `{group['name']}`: failures `{group['failure_count']}`, source `{group['source_packet']}`."
        )
    lines.extend(["", "## Strict Command Spine", ""])
    for command in payload["operator_commands"]:
        lines.extend(["```powershell", command, "```"])
    lines.extend(["", "## Failure Ledger", ""])
    for row in payload["rows"]:
        lines.append(
            f"- `{row['failure_name']}` -> `{row['closure_group']}`: {row['completion_test']}"
        )
    lines.extend(["", "## Checks", ""])
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)

    evidence = read_json(RESULTS / "external_evidence_audit.json")
    collection = read_json(RESULTS / "external_collection_plan.json")
    manifest_template = read_json(EXTERNAL / "manifest_template.json")
    rollout_packet = read_json(RESULTS / "external_rollout_evidence_audit.json")
    config_packet = read_json(RESULTS / "external_config_manifest_audit.json")
    method_packet = read_json(RESULTS / "external_method_implementation_audit.json")
    ablation_packet = read_json(RESULTS / "external_ablation_collection_audit.json")
    fidelity_packet = read_json(RESULTS / "external_fidelity_provenance_audit.json")

    rows, unmapped = build_rows(evidence)
    groups_present = sorted({row["closure_group"] for row in rows})
    required_groups = set(GROUPS)
    group_counts = {
        group: sum(1 for row in rows if row["closure_group"] == group)
        for group in sorted(required_groups)
    }

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "ledger_is_non_evidence_and_fail_closed",
        True,
        "writes only ledger/audit files and keeps strict_external_evidence_ready=false",
    )
    add_check(
        checks,
        "strict_external_evidence_is_currently_missing",
        evidence.get("submission_ready") is False
        and len(blocking_failures(evidence)) >= 30,
        f"submission_ready={evidence.get('submission_ready')!r}, failures={len(blocking_failures(evidence))}",
    )
    add_check(
        checks,
        "every_blocking_failure_is_mapped",
        not unmapped and len(rows) == len(blocking_failures(evidence)),
        f"unmapped={unmapped}, mapped={len(rows)}, failures={len(blocking_failures(evidence))}",
    )
    add_check(
        checks,
        "all_required_closure_groups_present",
        required_groups.issubset(set(groups_present)),
        f"missing={sorted(required_groups - set(groups_present))}",
    )
    add_check(
        checks,
        "source_packets_loaded",
        collection.get("passed") is True
        and rollout_packet.get("passed") is True
        and config_packet.get("passed") is True
        and method_packet.get("passed") is True
        and ablation_packet.get("passed") is True
        and fidelity_packet.get("passed") is True,
        "collection, rollout, config, method, ablation, and fidelity packets loaded",
    )
    add_check(
        checks,
        "manifest_template_declares_expected_evidence_fields",
        manifest_template.get("version") == "external_validation_v1"
        and isinstance(manifest_template.get("tasks"), list)
        and isinstance(manifest_template.get("methods"), list)
        and isinstance(manifest_template.get("release_artifacts"), dict)
        and isinstance(manifest_template.get("ablations"), dict),
        "manifest template has version, tasks, methods, release_artifacts, and ablations",
    )
    command_text = "\n".join(STRICT_COMMANDS)
    add_check(
        checks,
        "strict_command_spine_covers_final_evidence_path",
        all(
            fragment in command_text
            for fragment in (
                "audit_external_fidelity_acceptance.py --strict",
                "validate_external_configs.py --strict",
                "validate_external_adapters.py --strict",
                "audit_external_collection_readiness.py --strict",
                "build_external_precollection_freeze_receipt.py",
                "real_collection_runner.py",
                "build_external_manifest.py --write --check-video-paths",
                "validate_external_rollouts.py --write-results --check-video-paths --strict",
                "audit_external_pairing_integrity.py --strict",
                "audit_external_release_package.py --strict",
                "audit_external_evidence.py --strict",
            )
        ),
        "strict command spine covers fidelity, configs, adapters, collection, manifest, rollouts, pairing, release, and final evidence",
    )
    add_check(
        checks,
        "no_real_manifest_written",
        not (EXTERNAL / "manifest.json").exists(),
        "external_validation/manifest.json remains absent before real evidence",
    )

    passed = all(check["passed"] for check in checks)
    closure_groups = [
        {
            "name": group,
            "failure_count": group_counts[group],
            "source_packet": GROUPS[group]["source_packet"],
            "strict_gate": GROUPS[group]["strict_gate"],
        }
        for group in sorted(group_counts)
    ]
    payload = {
        "version": VERSION,
        "passed": passed,
        "not_external_evidence": True,
        "strict_external_evidence_ready": False,
        "blocking_failure_count": len(blocking_failures(evidence)),
        "mapped_failure_count": len(rows),
        "unmapped_failures": unmapped,
        "closure_groups": closure_groups,
        "rows": rows,
        "operator_commands": STRICT_COMMANDS,
        "source_external_evidence_audit": rel(RESULTS / "external_evidence_audit.json"),
        "source_manifest_template": rel(EXTERNAL / "manifest_template.json"),
        "ledger_path": rel(OUT_MD),
        "ledger_csv_path": rel(OUT_CSV),
        "checks": checks,
    }

    write_csv(rows)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(payload)

    print(
        "External evidence intake ledger: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"mapped={len(rows)}/{len(blocking_failures(evidence))}; "
        f"groups={len(groups_present)}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {AUDIT_JSON}")
    print(f"Wrote {AUDIT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
