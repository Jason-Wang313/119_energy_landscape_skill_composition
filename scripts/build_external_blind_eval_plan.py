from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
PLAN_JSON = RESULTS / "external_collection_plan.json"

PROTOCOL_MD = EXTERNAL / "blind_evaluation_protocol.md"
BLINDED_SHEET = EXTERNAL / "blinded_operator_sheet.csv"
ALIAS_MAP = EXTERNAL / "method_alias_map.json"
OUT_JSON = RESULTS / "external_blind_eval_audit.json"
OUT_MD = RESULTS / "external_blind_eval_audit.md"

VERSION = "external_blind_eval_plan_v1"
SEED = "paper119_external_blind_eval_v1_seed"


def fail(message: str) -> None:
    raise SystemExit(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"missing required input: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def stable_order_key(*parts: object) -> str:
    return digest_text("|".join(str(part) for part in parts))


def methods(plan: dict[str, Any]) -> list[str]:
    names = plan.get("methods", [])
    if not isinstance(names, list):
        return []
    return [str(name) for name in names if str(name)]


def tasks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    entries = plan.get("tasks", [])
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def build_aliases(method_names: list[str]) -> list[dict[str, str]]:
    shuffled = sorted(method_names, key=lambda name: stable_order_key(SEED, "alias", name))
    aliases = []
    for index, method in enumerate(shuffled):
        aliases.append(
            {
                "alias": f"method_{index:02d}",
                "method": method,
                "alias_hash": digest_text(f"{SEED}|{index}|{method}"),
            }
        )
    return aliases


def build_rows(plan: dict[str, Any], aliases: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task in tasks(plan):
        family = str(task.get("task_family", ""))
        log_jsonl = str(task.get("log_jsonl", ""))
        for reset in task.get("reset_plan", []):
            if not isinstance(reset, dict):
                continue
            reset_index = int(reset.get("reset_index", 0))
            scene_id = str(reset.get("scene_id", ""))
            seed = str(reset.get("seed", ""))
            ordered = sorted(
                aliases,
                key=lambda item: stable_order_key(SEED, family, scene_id, reset_index, item["alias"]),
            )
            for run_order, item in enumerate(ordered):
                alias = item["alias"]
                blind_run_id = f"paper119_blind_{family}_r{reset_index:03d}_{alias}"
                rows.append(
                    {
                        "not_external_evidence": "true",
                        "blind_run_id": blind_run_id,
                        "task_family": family,
                        "platform_type": str(task.get("platform_type", "")),
                        "platform_name": "FILL_AFTER_PLATFORM_SELECTION",
                        "reset_index": str(reset_index),
                        "scene_id": scene_id,
                        "episode_index": str(reset_index),
                        "seed": seed,
                        "run_order_within_reset": str(run_order),
                        "method_alias": alias,
                        "expected_log_jsonl": log_jsonl,
                        "expected_video_path": f"external_validation/videos/{family}/{blind_run_id}.mp4",
                        "status": "uncollected",
                        "operator_notes": "",
                    }
                )
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    BLINDED_SHEET.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "not_external_evidence",
        "blind_run_id",
        "task_family",
        "platform_type",
        "platform_name",
        "reset_index",
        "scene_id",
        "episode_index",
        "seed",
        "run_order_within_reset",
        "method_alias",
        "expected_log_jsonl",
        "expected_video_path",
        "status",
        "operator_notes",
    ]
    with BLINDED_SHEET.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_alias_map(aliases: list[dict[str, str]], plan: dict[str, Any]) -> None:
    payload = {
        "version": VERSION,
        "not_external_evidence": True,
        "seed_hash": digest_text(SEED),
        "purpose": "Method alias map for blinded external collection; seal until logs/videos/configs/checkpoints are frozen.",
        "source_collection_plan": rel(PLAN_JSON),
        "method_count": len(aliases),
        "aliases": aliases,
        "seal_conditions": [
            "Do not reveal aliases to the operator until all JSONL logs and videos are written.",
            "Do not tune any method after alias assignment.",
            "Do not edit aggregate metrics by hand; recompute them from JSONL logs.",
            "Freeze config, checkpoint, implementation, and skill-library hashes before unblinding.",
        ],
        "analysis_lock": {
            "primary_method": "barrier_certified_energy_composer_v5",
            "strongest_non_oracle_selected_after_all_methods": True,
            "fixed_risk_budget": 0.15,
            "success_margin_gate": 0.05,
            "utility_margin_gate": 0.08,
            "paired_win_rate_gate": 0.70,
            "coverage_gate": 0.55,
            "breach_gate": 0.02,
        },
        "expected_records": int(plan.get("total_required_records", 0) or 0),
    }
    ALIAS_MAP.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_protocol(plan: dict[str, Any]) -> None:
    lines = [
        "# External Blind Evaluation Protocol",
        "",
        "Not external evidence: `true`.",
        "",
        "Purpose: reduce method-order, operator-expectation, and post-hoc tuning leakage before collecting real robot or accepted high-fidelity simulator evidence for Paper 119.",
        "",
        "## Artifacts",
        "",
        f"- Blinded operator sheet: `{rel(BLINDED_SHEET)}`.",
        f"- Sealed method alias map: `{rel(ALIAS_MAP)}`.",
        f"- Source collection plan: `{rel(PLAN_JSON)}`.",
        "",
        "## Rules",
        "",
        "- Execute rows from the blinded operator sheet in `run_order_within_reset` order.",
        "- The operator sees `method_alias`, not method names.",
        "- The alias map remains sealed until JSONL logs, videos, configs, checkpoints, and implementation hashes are frozen.",
        "- Do not tune fixed-risk budget, thresholds, skill library, observation interface, or method hyperparameters after alias assignment.",
        "- Include failed, abstained, repaired, damaged, and oracle-gap episodes in the raw JSONL logs.",
        "- Recompute metrics from JSONL records before unblinding aggregate conclusions.",
        "",
        "## Locked Analysis Gates",
        "",
        "- External success margin over strongest non-oracle baseline >= `0.05`.",
        "- External utility margin over strongest non-oracle baseline >= `0.08`.",
        "- Paired win rate >= `0.70`.",
        "- Fixed-risk coverage >= `0.55` and breach <= `0.02` at budget `0.15`.",
        "- At least 3 of 4 task families must show positive margins.",
        "",
        "## Scale",
        "",
        f"- Required JSONL records: `{plan.get('total_required_records')}`.",
        f"- Methods: `{plan.get('method_count')}`.",
        f"- Task families: `{plan.get('task_family_count')}`.",
    ]
    PROTOCOL_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_audit(plan: dict[str, Any], aliases: list[dict[str, str]], rows: list[dict[str, str]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    method_names = methods(plan)
    expected_records = int(plan.get("total_required_records", 0) or 0)
    add_check(checks, "collection_plan_passed", plan.get("passed") is True, f"passed={plan.get('passed')!r}")
    add_check(checks, "alias_count_matches_methods", len(aliases) == len(method_names) >= 12, f"aliases={len(aliases)}, methods={len(method_names)}")
    add_check(checks, "row_count_matches_plan", len(rows) == expected_records >= 1440, f"rows={len(rows)}, expected={expected_records}")
    add_check(checks, "blind_artifacts_written", BLINDED_SHEET.exists() and ALIAS_MAP.exists() and PROTOCOL_MD.exists(), "blinded sheet, alias map, and protocol exist")

    alias_names = [item["alias"] for item in aliases]
    duplicate_aliases = sorted({alias for alias in alias_names if alias_names.count(alias) > 1})
    add_check(checks, "aliases_unique", not duplicate_aliases, f"duplicates={duplicate_aliases}")
    add_check(checks, "aliases_hide_method_names", not any(item["method"] in item["alias"] for item in aliases), "aliases do not contain method names")

    rows_by_reset: dict[tuple[str, str], list[str]] = {}
    for row in rows:
        key = (row["task_family"], row["scene_id"])
        rows_by_reset.setdefault(key, []).append(row["method_alias"])
    bad_resets = [
        f"{task}/{scene}"
        for (task, scene), reset_aliases in rows_by_reset.items()
        if sorted(reset_aliases) != sorted(alias_names)
    ]
    add_check(checks, "every_reset_has_all_aliases", not bad_resets and bool(rows_by_reset), f"bad_resets={bad_resets[:5]}, reset_count={len(rows_by_reset)}")

    reset_sequences = [tuple(reset_aliases) for reset_aliases in rows_by_reset.values()]
    order_sequences = set(reset_sequences)
    add_check(checks, "run_order_varies_by_reset", len(order_sequences) >= 4, f"distinct_orders={len(order_sequences)}")
    first_sequence = reset_sequences[0] if reset_sequences else ()
    add_check(checks, "first_order_not_alias_sorted", bool(first_sequence) and first_sequence != tuple(sorted(alias_names)), "first observed order differs from sorted aliases")

    sheet_text = BLINDED_SHEET.read_text(encoding="utf-8") if BLINDED_SHEET.exists() else ""
    leaked_methods = [name for name in method_names if name in sheet_text]
    add_check(checks, "blinded_sheet_has_no_method_names", not leaked_methods, f"leaked_methods={leaked_methods}")

    protocol_text = PROTOCOL_MD.read_text(encoding="utf-8") if PROTOCOL_MD.exists() else ""
    required_terms = ["sealed", "Do not tune", "JSONL", "unblinding", "fixed-risk budget"]
    missing_terms = [term for term in required_terms if term not in protocol_text]
    add_check(checks, "protocol_contains_anti_leakage_terms", not missing_terms, f"missing_terms={missing_terms}")

    return {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "seed_hash": digest_text(SEED),
        "blinded_operator_sheet": rel(BLINDED_SHEET),
        "method_alias_map": rel(ALIAS_MAP),
        "protocol": rel(PROTOCOL_MD),
        "method_count": len(method_names),
        "alias_count": len(aliases),
        "row_count": len(rows),
        "reset_count": len(rows_by_reset),
        "expected_records": expected_records,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# External Blind Evaluation Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Rows: `{audit['row_count']}`.",
        f"Aliases: `{audit['alias_count']}`.",
        f"Resets: `{audit['reset_count']}`.",
        f"Blinded sheet: `{audit['blinded_operator_sheet']}`.",
        f"Alias map: `{audit['method_alias_map']}`.",
        f"Protocol: `{audit['protocol']}`.",
        "",
        "This audit checks collection blinding and deterministic randomization only. It is not robot or high-fidelity simulator evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    plan = read_json(PLAN_JSON)
    EXTERNAL.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    aliases = build_aliases(methods(plan))
    rows = build_rows(plan, aliases)
    write_csv(rows)
    write_alias_map(aliases, plan)
    write_protocol(plan)
    audit = build_audit(plan, aliases, rows)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)

    status = "PASS" if audit["passed"] else "FAIL"
    print(
        f"External blind evaluation audit: {status}; "
        f"rows={audit['row_count']}; aliases={audit['alias_count']}; not_evidence={audit['not_external_evidence']}"
    )
    print(f"Wrote {BLINDED_SHEET}")
    print(f"Wrote {ALIAS_MAP}")
    print(f"Wrote {PROTOCOL_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
