from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
MANIFEST_TEMPLATE = EXTERNAL / "manifest_template.json"

SPEC_DIR = EXTERNAL / "baseline_specs"
CONTRACT_MD = EXTERNAL / "baseline_implementation_contract.md"
MATRIX_CSV = EXTERNAL / "baseline_implementation_matrix.csv"
OUT_JSON = RESULTS / "external_baseline_contract_audit.json"
OUT_MD = RESULTS / "external_baseline_contract_audit.md"


NON_ORACLE_METHODS = {
    "greedy_module_sequence",
    "behavior_cloned_skill_chain",
    "option_graph_planner",
    "tamp_feasibility_screen",
    "stable_dmp_handoff",
    "diffusion_skill_stitcher",
    "cem_trajectory_composer",
    "residual_rl_composer",
    "energy_compatibility_heuristic",
    "proposed_energy_landscape_composer_v4_1",
    "barrier_certified_energy_composer_v5",
}


METHOD_DETAILS = {
    "greedy_module_sequence": {
        "role": "open-loop skill graph baseline",
        "required_entrypoint": "select_next_skill_and_handoff",
        "allowed_inputs": ["skill library", "current observation", "task graph", "shared reset metadata"],
        "forbidden_advantages": ["energy seam labels", "post hoc basin truth", "extra reset attempts"],
    },
    "behavior_cloned_skill_chain": {
        "role": "demonstration sequence baseline",
        "required_entrypoint": "predict_demonstrated_handoff",
        "allowed_inputs": ["demonstration policy or checkpoint", "current observation", "shared skill library"],
        "forbidden_advantages": ["v5 diagnostic labels", "post hoc oracle repair", "unpaired demonstration resets"],
    },
    "option_graph_planner": {
        "role": "temporal-abstraction planning baseline",
        "required_entrypoint": "plan_over_option_graph",
        "allowed_inputs": ["option graph", "current observation", "shared skill library", "same compute budget"],
        "forbidden_advantages": ["hidden basin classifier", "privileged barrier score"],
    },
    "tamp_feasibility_screen": {
        "role": "task-and-motion feasibility baseline",
        "required_entrypoint": "screen_symbolic_geometric_transition",
        "allowed_inputs": ["task symbols", "geometric scene state", "shared skill library"],
        "forbidden_advantages": ["energy descent continuity", "post hoc contact outcome"],
    },
    "stable_dmp_handoff": {
        "role": "stable dynamics handoff baseline",
        "required_entrypoint": "generate_stable_handoff",
        "allowed_inputs": ["DMP or stable dynamics parameters", "current observation", "shared skill library"],
        "forbidden_advantages": ["oracle basin membership", "future failure labels"],
    },
    "diffusion_skill_stitcher": {
        "role": "generative handoff sampler baseline",
        "required_entrypoint": "sample_handoff_state",
        "allowed_inputs": ["diffusion/generative model checkpoint", "current observation", "shared skill library"],
        "forbidden_advantages": ["v5 accept/reject labels unless explicitly trained on the same data as all baselines"],
    },
    "cem_trajectory_composer": {
        "role": "trajectory-search baseline",
        "required_entrypoint": "optimize_handoff_with_cem",
        "allowed_inputs": ["same rollout/simulation budget", "current observation", "shared skill library"],
        "forbidden_advantages": ["larger compute budget", "extra reset attempts", "oracle basin state"],
    },
    "residual_rl_composer": {
        "role": "learned residual repair baseline",
        "required_entrypoint": "apply_residual_repair_policy",
        "allowed_inputs": ["residual policy checkpoint", "current observation", "shared skill library"],
        "forbidden_advantages": ["training on evaluation resets", "post hoc barrier labels"],
    },
    "energy_compatibility_heuristic": {
        "role": "non-certified energy heuristic baseline",
        "required_entrypoint": "score_energy_compatibility",
        "allowed_inputs": ["same energy estimates available to all non-oracle methods", "current observation"],
        "forbidden_advantages": ["fixed-risk calibration gate", "repair memory from proposed v5"],
    },
    "proposed_energy_landscape_composer_v4_1": {
        "role": "previous proposed method baseline",
        "required_entrypoint": "compose_with_v4_1_rules",
        "allowed_inputs": ["same energy estimates", "current observation", "shared skill library"],
        "forbidden_advantages": ["v5-only repair memory", "v5 fixed-risk calibration updates"],
    },
    "barrier_certified_energy_composer_v5": {
        "role": "primary method",
        "required_entrypoint": "compose_with_barrier_certified_seam_model",
        "allowed_inputs": ["terminal samples", "basin posterior", "barrier score", "descent continuity", "calibrated risk"],
        "forbidden_advantages": ["post hoc oracle basin truth", "unpaired reset retries"],
    },
    "oracle_basin_composer": {
        "role": "post hoc upper bound only",
        "required_entrypoint": "evaluate_oracle_upper_bound",
        "allowed_inputs": ["true basin/barrier information after rollout or from simulator ground truth"],
        "forbidden_advantages": ["deployment decision use", "selection as strongest non-oracle baseline"],
    },
}


ADAPTER_API = {
    "initialize": "load method config/checkpoint and declare method_name, version, and hashes",
    "propose": "given shared observation, terminal samples, skill_i, skill_j, and compute budget, return seam decision and optional repair",
    "log": "emit predicted risk, diagnosis, decision, repair action, policy/config hash, and timing for the episode JSONL record",
    "reset": "clear method-local state between paired resets unless the method explicitly models online memory and logs it",
}


FAIRNESS_INVARIANTS = [
    "same skill library for every non-oracle method",
    "same initial state, scene_id, seed, and skill pair for paired comparisons",
    "same observation interface and no hidden state except where the platform exposes it to all methods",
    "same compute budget or a predeclared budget measured in wall-clock time and simulator queries",
    "same logging schema, video requirement, and policy/config hash requirement",
    "oracle_basin_composer is reported only as a post hoc upper bound and is excluded from strongest non-oracle selection",
]

REQUIRED_ADAPTER_API_KEYS = {"initialize", "propose", "log", "reset"}
REQUIRED_RELEASE_EVIDENCE_FIELDS = {
    "implementation_path_or_repository",
    "checkpoint_or_config_path",
    "sha256_or_commit",
    "episode_log_fields",
}
REQUIRED_EPISODE_LOG_FIELDS = {
    "method",
    "policy_or_config_hash",
    "predicted_seam_risk",
    "decision",
    "failure_diagnosis",
    "success",
    "realized_seam_breach",
    "utility",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def method_names(manifest: dict[str, Any]) -> list[str]:
    methods = manifest.get("methods", [])
    if not isinstance(methods, list):
        return []
    names = [str(method.get("name", "")).strip() for method in methods if isinstance(method, dict)]
    return [name for name in names if name]


def method_rows(names: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for name in names:
        detail = METHOD_DETAILS.get(
            name,
            {
                "role": "unknown baseline",
                "required_entrypoint": "declare_method_adapter",
                "allowed_inputs": ["shared observation", "shared skill library"],
                "forbidden_advantages": ["undeclared privileged information"],
            },
        )
        is_oracle = name == "oracle_basin_composer"
        rows.append(
            {
                "not_external_evidence": "true",
                "method": name,
                "role": str(detail["role"]),
                "requires_independent_source": "false" if is_oracle else "true",
                "expected_adapter_dir": "post_hoc_upper_bound" if is_oracle else f"external_validation/baselines/{name}",
                "required_entrypoint": str(detail["required_entrypoint"]),
                "same_skill_library": "true",
                "same_observation_interface": "true",
                "same_compute_budget": "true" if not is_oracle else "not_applicable",
                "logging_required": "true",
                "oracle_boundary": "post_hoc_only" if is_oracle else "non_oracle",
                "implementation_status": "post_hoc_upper_bound_only" if is_oracle else "missing_external_source",
            }
        )
    return rows


def write_matrix(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "not_external_evidence",
        "method",
        "role",
        "requires_independent_source",
        "expected_adapter_dir",
        "required_entrypoint",
        "same_skill_library",
        "same_observation_interface",
        "same_compute_budget",
        "logging_required",
        "oracle_boundary",
        "implementation_status",
    ]
    with MATRIX_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_specs(names: list[str]) -> list[str]:
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name in names:
        detail = METHOD_DETAILS.get(name, METHOD_DETAILS["greedy_module_sequence"])
        payload = {
            "version": "paper119_external_baseline_spec_v1",
            "not_external_evidence": True,
            "method": name,
            "role": detail["role"],
            "required_entrypoint": detail["required_entrypoint"],
            "adapter_api": ADAPTER_API,
            "allowed_inputs": detail["allowed_inputs"],
            "forbidden_advantages": detail["forbidden_advantages"],
            "fairness_invariants": FAIRNESS_INVARIANTS,
            "required_release_evidence": {
                "implementation_path_or_repository": "required for every non-oracle method",
                "checkpoint_or_config_path": "required when the method uses learned weights or tuned parameters",
                "sha256_or_commit": "required for implementation, config, and checkpoint artifacts",
                "episode_log_fields": [
                    "method",
                    "policy_or_config_hash",
                    "predicted_seam_risk",
                    "decision",
                    "failure_diagnosis",
                    "success",
                    "realized_seam_breach",
                    "utility",
                ],
            },
        }
        path = SPEC_DIR / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path.relative_to(ROOT).as_posix())
    return written


def write_contract(names: list[str], rows: list[dict[str, str]], spec_files: list[str]) -> None:
    missing = [row["method"] for row in rows if row["implementation_status"] == "missing_external_source"]
    lines = [
        "# External Baseline Implementation Contract",
        "",
        "Not external evidence: `true`.",
        "",
        "Purpose: make the missing independent baseline layer explicit before any real robot or high-fidelity simulator run is counted as evidence.",
        "",
        "A future submission-ready evidence package must provide independent source, config/checkpoint hashes, and episode logs for every non-oracle method below. This contract is a checklist and interface specification only; it does not satisfy the external evidence gate.",
        "",
        "## Adapter API",
        "",
    ]
    for name, detail in ADAPTER_API.items():
        lines.append(f"- `{name}`: {detail}.")
    lines.extend(["", "## Fairness Invariants", ""])
    for invariant in FAIRNESS_INVARIANTS:
        lines.append(f"- {invariant}.")
    lines.extend(["", "## Method Matrix", ""])
    for row in rows:
        lines.append(
            f"- `{row['method']}`: {row['role']}; entrypoint `{row['required_entrypoint']}`; "
            f"adapter `{row['expected_adapter_dir']}`; status `{row['implementation_status']}`."
        )
    lines.extend(["", "## Missing Independent Implementations", ""])
    for method in missing:
        lines.append(f"- `{method}`")
    lines.extend(["", "## Generated Spec Files", ""])
    for spec in spec_files:
        lines.append(f"- `{spec}`")
    CONTRACT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def read_spec_file(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {"_error": f"missing spec file: {rel_path}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"_error": f"invalid JSON in {rel_path}: {exc}"}
    if not isinstance(payload, dict):
        return {"_error": f"spec is not an object: {rel_path}"}
    return payload


def build_audit(names: list[str], rows: list[dict[str, str]], spec_files: list[str]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    method_set = set(names)
    missing_required = sorted((NON_ORACLE_METHODS | {"oracle_basin_composer"}) - method_set)
    missing_implementations = [row["method"] for row in rows if row["implementation_status"] == "missing_external_source"]
    oracle_rows = [row for row in rows if row["method"] == "oracle_basin_composer"]
    non_oracle_rows = [row for row in rows if row["method"] != "oracle_basin_composer"]
    spec_payloads = [read_spec_file(path) for path in spec_files]
    spec_methods = {payload.get("method") for payload in spec_payloads if "_error" not in payload}
    spec_errors = [str(payload["_error"]) for payload in spec_payloads if "_error" in payload]
    release_evidence_errors = []
    log_field_errors = []
    for payload in spec_payloads:
        if "_error" in payload:
            continue
        method = str(payload.get("method", ""))
        release_evidence = payload.get("required_release_evidence")
        if not isinstance(release_evidence, dict):
            release_evidence_errors.append(f"{method}: missing required_release_evidence")
            continue
        missing_fields = sorted(REQUIRED_RELEASE_EVIDENCE_FIELDS - set(release_evidence))
        if missing_fields:
            release_evidence_errors.append(f"{method}: missing {missing_fields}")
        log_fields = release_evidence.get("episode_log_fields", [])
        if not isinstance(log_fields, list):
            log_field_errors.append(f"{method}: episode_log_fields is not a list")
            continue
        missing_log_fields = sorted(REQUIRED_EPISODE_LOG_FIELDS - {str(field) for field in log_fields})
        if missing_log_fields:
            log_field_errors.append(f"{method}: missing {missing_log_fields}")

    add_check(checks, "not_external_evidence_declared", True, "contract, matrix, specs, and audit are scaffolding only")
    add_check(checks, "method_count_ge_12", len(names) >= 12, f"method_count={len(names)}")
    add_check(checks, "all_required_methods_present", not missing_required, f"missing={missing_required}")
    add_check(checks, "matrix_rows_match_methods", len(rows) == len(names), f"rows={len(rows)}, methods={len(names)}")
    add_check(checks, "spec_files_match_methods", len(spec_files) == len(names), f"specs={len(spec_files)}, methods={len(names)}")
    add_check(
        checks,
        "spec_files_are_method_bound",
        not spec_errors and spec_methods == method_set,
        f"spec_errors={spec_errors}, missing={sorted(method_set - spec_methods)}",
    )
    add_check(
        checks,
        "adapter_api_covers_required_methods",
        REQUIRED_ADAPTER_API_KEYS.issubset(set(ADAPTER_API)),
        f"missing={sorted(REQUIRED_ADAPTER_API_KEYS - set(ADAPTER_API))}",
    )
    add_check(checks, "fairness_invariants_declared", len(FAIRNESS_INVARIANTS) >= 6, f"invariants={len(FAIRNESS_INVARIANTS)}")
    add_check(
        checks,
        "specs_require_release_evidence",
        not release_evidence_errors,
        f"errors={release_evidence_errors}",
    )
    add_check(
        checks,
        "specs_require_policy_config_hash_logs",
        not log_field_errors,
        f"errors={log_field_errors}",
    )
    add_check(
        checks,
        "non_oracle_requires_independent_source",
        all(row["requires_independent_source"] == "true" for row in non_oracle_rows),
        "all non-oracle rows require independent source",
    )
    add_check(
        checks,
        "oracle_post_hoc_only",
        len(oracle_rows) == 1 and oracle_rows[0]["oracle_boundary"] == "post_hoc_only",
        f"oracle_rows={oracle_rows}",
    )
    add_check(
        checks,
        "implementations_not_marked_ready",
        set(missing_implementations) == NON_ORACLE_METHODS,
        f"missing_implementations={missing_implementations}",
    )
    add_check(checks, "contract_file_exists", CONTRACT_MD.exists(), str(CONTRACT_MD))
    add_check(checks, "matrix_file_exists", MATRIX_CSV.exists(), str(MATRIX_CSV))

    return {
        "version": "external_baseline_contract_audit_v1",
        "not_external_evidence": True,
        "passed": all(check["passed"] for check in checks),
        "implementations_ready": False,
        "method_count": len(names),
        "non_oracle_method_count": len(non_oracle_rows),
        "missing_implementations": missing_implementations,
        "contract": CONTRACT_MD.relative_to(ROOT).as_posix(),
        "matrix": MATRIX_CSV.relative_to(ROOT).as_posix(),
        "spec_files": spec_files,
        "adapter_api": ADAPTER_API,
        "fairness_invariants": FAIRNESS_INVARIANTS,
        "checks": checks,
    }


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Baseline Contract Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Implementations ready: `{str(audit['implementations_ready']).lower()}`.",
        f"Methods: `{audit['method_count']}`.",
        "",
        "This audit verifies that the baseline implementation contract is complete. It deliberately does not claim that manifest-declared independent baseline evidence exists.",
        "",
        "## Missing Independent Implementations",
        "",
    ]
    for method in audit["missing_implementations"]:
        lines.append(f"- `{method}`")
    lines.extend(["", "## Checks", ""])
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    manifest = read_json(MANIFEST_TEMPLATE)
    names = method_names(manifest)
    rows = method_rows(names)
    write_matrix(rows)
    spec_files = write_specs(names)
    write_contract(names, rows, spec_files)
    audit = build_audit(names, rows, spec_files)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)
    status = "PASS" if audit["passed"] else "FAIL"
    print(
        f"External baseline contract audit: {status}; methods={audit['method_count']}; "
        f"implementations_ready={audit['implementations_ready']}"
    )
    print(f"Wrote {CONTRACT_MD}")
    print(f"Wrote {MATRIX_CSV}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
