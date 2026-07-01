from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "run_experiment.py"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"

OUT_JSON = RESULTS / "local_model_release_manifest.json"
OUT_AUDIT_JSON = RESULTS / "local_model_release_audit.json"
OUT_AUDIT_MD = RESULTS / "local_model_release_audit.md"
OUT_CARD = DOCS / "local_model_release.md"

PROPOSED = "barrier_certified_energy_composer_v5"
ORACLE = "oracle_basin_composer"

RESULT_ARTIFACTS = [
    RESULTS / "summary.json",
    RESULTS / "hard_aggregate_metrics.csv",
    RESULTS / "hard_pairwise_stats.csv",
    RESULTS / "ablation_metrics.csv",
    RESULTS / "fixed_risk_metrics.csv",
    RESULTS / "planner_edge_policy_audit.json",
    RESULTS / "failure_memory_adaptation_audit.json",
    RESULTS / "seam_prediction_calibration_audit.json",
    RESULTS / "diagnostic_mechanism_audit.json",
    RESULTS / "decision_quality_audit.json",
    RESULTS / "holdout_robustness_audit.json",
    RESULTS / "local_falsification_audit.json",
]

REFERENCE_ADAPTER_ARTIFACTS = [
    ROOT / "external_validation" / "baselines" / "common_reference_adapter.py",
    ROOT / "external_validation" / "baselines" / PROPOSED / "adapter.py",
    ROOT / "external_validation" / "baselines" / PROPOSED / "reference_adapter_metadata.json",
    ROOT / "external_validation" / "reference_adapter_report.md",
]


class ConstantEvaluator:
    def __init__(self) -> None:
        self.env: dict[str, Any] = {}

    def eval(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self.eval(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self.eval(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return {self.eval(key): self.eval(value) for key, value in zip(node.keys, node.values)}
        if isinstance(node, ast.Name):
            if node.id in self.env:
                return self.env[node.id]
            raise ValueError(f"unknown constant name: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = self.eval(node.operand)
            if isinstance(value, (int, float)):
                return -value
        if isinstance(node, ast.Call):
            return self.eval_call(node)
        raise ValueError(f"unsupported constant expression: {ast.dump(node, include_attributes=False)}")

    def eval_call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("unsupported call target")
        name = node.func.id
        args = [self.eval(arg) for arg in node.args]
        if name == "range" and len(args) in {1, 2, 3}:
            return range(*args)
        if name == "list" and len(args) == 1 and isinstance(args[0], range):
            return list(args[0])
        raise ValueError(f"unsupported call: {name}")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def extract_constants() -> dict[str, Any]:
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    evaluator = ConstantEvaluator()
    wanted = {
        "VERSION",
        "BASE_SEED",
        "EPISODES_PER_CELL",
        "SEEDS",
        "PROPOSED",
        "OLD_V4",
        "ORACLE",
        "TASKS",
        "REGIMES",
        "SPLITS",
        "METHODS",
    }
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            if any(name in wanted for name in names):
                value = evaluator.eval(node.value)
                for name in names:
                    evaluator.env[name] = value
    missing = sorted(wanted - set(evaluator.env))
    if missing:
        raise SystemExit(f"could not extract constants from {rel(SRC)}: {missing}")
    return {name: evaluator.env[name] for name in sorted(wanted)}


def artifact_entry(path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": rel(path), "exists": path.exists()}
    if path.exists():
        entry["sha256"] = sha256_file(path)
        if path.suffix.lower() == ".csv":
            entry["rows"] = csv_row_count(path)
    return entry


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    constants = extract_constants()
    summary = read_json(RESULTS / "summary.json")
    methods = constants["METHODS"]
    tasks = constants["TASKS"]
    regimes = constants["REGIMES"]
    splits = constants["SPLITS"]
    proposed = next((method for method in methods if method.get("name") == PROPOSED), None)

    method_hashes = {
        str(method["name"]): sha256_json(method)
        for method in methods
        if isinstance(method, dict) and "name" in method
    }
    result_artifacts = [artifact_entry(path) for path in RESULT_ARTIFACTS]
    adapter_artifacts = [artifact_entry(path) for path in REFERENCE_ADAPTER_ARTIFACTS]

    manifest: dict[str, Any] = {
        "version": "paper119_local_model_release_v1",
        "not_external_evidence": True,
        "local_model_release_ready": True,
        "external_evidence_ready": False,
        "does_not_release_trained_robot_policy": True,
        "does_not_release_real_robot_checkpoint": True,
        "identity": "Local world/action model for robot skill seams: predict handoff failure, diagnose why, choose repair/probe/abstain/transition, and update planner edge beliefs.",
        "source": {
            "path": rel(SRC),
            "sha256": sha256_file(SRC),
            "version": constants["VERSION"],
            "base_seed": constants["BASE_SEED"],
            "episodes_per_cell": constants["EPISODES_PER_CELL"],
            "seeds": constants["SEEDS"],
        },
        "dimensions": {
            "task_count": len(tasks),
            "regime_count": len(regimes),
            "split_count": len(splits),
            "method_count": len(methods),
            "non_oracle_method_count": len([method for method in methods if method.get("name") != ORACLE]),
        },
        "proposed_method": {
            "name": PROPOSED,
            "parameter_hash": method_hashes.get(PROPOSED, ""),
            "parameters": proposed or {},
        },
        "method_parameter_hashes": method_hashes,
        "tasks": [task.get("name") for task in tasks],
        "regimes": [regime.get("name") for regime in regimes],
        "splits": [split.get("name") for split in splits],
        "result_artifacts": result_artifacts,
        "reference_adapter_artifacts": adapter_artifacts,
        "summary_state": {
            "terminal_decision": summary.get("terminal_decision"),
            "iclr_main_ready": summary.get("iclr_main_ready"),
            "scope_gate_pass": summary.get("scope_gate_pass"),
            "local_gates_pass": summary.get("local_gates_pass"),
            "strongest_non_oracle": summary.get("strongest_non_oracle"),
            "missing_scope_evidence": summary.get("missing_scope_evidence", []),
        },
        "boundary": [
            "This is a frozen local mechanism and reproducibility release.",
            "It is not a trained robot policy checkpoint.",
            "It is not real robot or accepted high-fidelity simulator validation.",
            "It does not satisfy external_validation/manifest.json or strict external evidence gates.",
        ],
    }
    manifest["release_hash"] = sha256_json({key: value for key, value in manifest.items() if key != "release_hash"})

    checks: list[dict[str, Any]] = []
    add_check(checks, "source_exists", SRC.exists(), rel(SRC))
    add_check(checks, "source_version_matches_summary", constants["VERSION"] == summary.get("version"), f"source={constants['VERSION']!r}, summary={summary.get('version')!r}")
    add_check(checks, "proposed_method_present", proposed is not None and method_hashes.get(PROPOSED, "") != "", f"hash={method_hashes.get(PROPOSED, '')}")
    add_check(checks, "method_family_complete", len(methods) >= 12 and len(method_hashes) >= 12, f"methods={len(methods)}, hashes={len(method_hashes)}")
    add_check(checks, "local_dimensions_complete", len(tasks) >= 6 and len(regimes) >= 8 and len(splits) >= 5, f"tasks={len(tasks)}, regimes={len(regimes)}, splits={len(splits)}")
    add_check(checks, "summary_remains_bounded", summary.get("terminal_decision") == "STRONG_REVISE" and summary.get("iclr_main_ready") is False and summary.get("scope_gate_pass") is False, str(manifest["summary_state"]))
    add_check(checks, "local_gates_pass", summary.get("local_gates_pass") is True, f"local_gates_pass={summary.get('local_gates_pass')!r}")
    missing_results = [item["path"] for item in result_artifacts if not item.get("exists")]
    add_check(checks, "result_artifacts_hash_locked", not missing_results and all(item.get("sha256") for item in result_artifacts), f"missing={missing_results}")
    missing_adapters = [item["path"] for item in adapter_artifacts if not item.get("exists")]
    add_check(checks, "reference_adapter_artifacts_hash_locked", not missing_adapters and all(item.get("sha256") for item in adapter_artifacts), f"missing={missing_adapters}")
    add_check(checks, "explicitly_not_external_evidence", manifest["not_external_evidence"] is True and manifest["external_evidence_ready"] is False, f"not_external_evidence={manifest['not_external_evidence']}, external_evidence_ready={manifest['external_evidence_ready']}")
    add_check(checks, "not_a_robot_policy_checkpoint", manifest["does_not_release_trained_robot_policy"] is True and manifest["does_not_release_real_robot_checkpoint"] is True, "local deterministic seam model only")
    add_check(checks, "release_hash_present", len(manifest["release_hash"]) == 64, manifest["release_hash"])
    return manifest, checks


def write_outputs(manifest: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    passed = all(check["passed"] for check in checks)
    audit = {
        "version": "paper119_local_model_release_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "local_model_release_ready": manifest.get("local_model_release_ready") is True,
        "external_evidence_ready": False,
        "manifest": rel(OUT_JSON),
        "model_card": rel(OUT_CARD),
        "release_hash": manifest.get("release_hash"),
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    proposed = manifest["proposed_method"]
    card_lines = [
        "# Local Model Release Card",
        "",
        f"Release hash: `{manifest['release_hash']}`.",
        "Not external evidence: `true`.",
        "External evidence ready: `false`.",
        "",
        "## Identity",
        "",
        manifest["identity"],
        "",
        "## What Is Released",
        "",
        f"- Source generator: `{manifest['source']['path']}`.",
        f"- Source SHA256: `{manifest['source']['sha256']}`.",
        f"- Generator version: `{manifest['source']['version']}`.",
        f"- Deterministic base seed: `{manifest['source']['base_seed']}`.",
        f"- Proposed method: `{proposed['name']}`.",
        f"- Proposed parameter hash: `{proposed['parameter_hash']}`.",
        f"- Methods/task-regime-split dimensions: `{manifest['dimensions']['method_count']}` methods, `{manifest['dimensions']['task_count']}` tasks, `{manifest['dimensions']['regime_count']}` regimes, `{manifest['dimensions']['split_count']}` splits.",
        "",
        "## Boundaries",
        "",
    ]
    for item in manifest["boundary"]:
        card_lines.append(f"- {item}")
    card_lines.extend(["", "## Result Artifact Hashes", ""])
    for item in manifest["result_artifacts"]:
        row_text = f", rows={item['rows']}" if "rows" in item else ""
        card_lines.append(f"- `{item['path']}` `{item.get('sha256', 'missing')}`{row_text}")
    card_lines.extend(["", "## Reference Adapter Hashes", ""])
    for item in manifest["reference_adapter_artifacts"]:
        card_lines.append(f"- `{item['path']}` `{item.get('sha256', 'missing')}`")
    card_lines.extend(
        [
            "",
            "## Strict Evidence Boundary",
            "",
            "This card helps reviewers reproduce the local skill-seam action-model study. It does not replace `external_validation/manifest.json`, raw external JSONL logs, render-backed videos, calibrated state/contact/camera logs, accepted platform fidelity provenance, or manifest-declared independent baseline evidence.",
        ]
    )
    OUT_CARD.write_text("\n".join(card_lines) + "\n", encoding="utf-8")

    audit_lines = [
        "# Local Model Release Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        "Not external evidence: `true`.",
        f"Local model release ready: `{str(audit['local_model_release_ready']).lower()}`.",
        "External evidence ready: `false`.",
        f"Manifest: `{rel(OUT_JSON)}`.",
        f"Model card: `{rel(OUT_CARD)}`.",
        f"Release hash: `{manifest['release_hash']}`.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        audit_lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_AUDIT_MD.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest, checks = build_manifest()
    write_outputs(manifest, checks)
    passed = all(check["passed"] for check in checks)
    print(
        "Local model release: "
        f"{'PASS' if passed else 'FAIL'}; "
        f"release_hash={manifest.get('release_hash')}; "
        "not_evidence=True"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_AUDIT_JSON}")
    print(f"Wrote {OUT_AUDIT_MD}")
    print(f"Wrote {OUT_CARD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
