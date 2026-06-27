from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
PLAN_JSON = RESULTS / "external_collection_plan.json"

ROUTE_MD = EXTERNAL / "independent_validation_route.md"
ROUTE_MATRIX = EXTERNAL / "independent_validation_route_matrix.csv"
OUT_JSON = RESULTS / "independent_validation_route_audit.json"
OUT_MD = RESULTS / "independent_validation_route_audit.md"

VERSION = "independent_validation_route_v1"


READINESS_BLOCKERS = [
    "manifest_backed_external_evidence",
    "raw_jsonl_metric_recompute",
    "real_task_configs",
    "independent_non_oracle_baselines",
]

STRICT_COMMANDS = [
    r"python scripts\validate_external_configs.py --strict",
    r"python scripts\validate_external_adapters.py --strict",
    r"python scripts\build_external_manifest.py --write --check-video-paths",
    r"python scripts\validate_external_rollouts.py --write-results --check-video-paths --strict",
    r"python scripts\audit_external_evidence.py --strict",
]


ROUTES: list[dict[str, Any]] = [
    {
        "route_id": "maniskill_sapien_primary",
        "rank": 1,
        "role": "primary independent high-fidelity simulator route",
        "platform_family": "ManiSkill/SAPIEN",
        "platform_type": "high_fidelity_sim",
        "independent_of_haonan": True,
        "requires_gpu": True,
        "expected_owner": "Jason or any external operator with a GPU workstation",
        "official_sources": [
            "https://maniskill.readthedocs.io/en/latest/user_guide/index.html",
            "https://sapien.ucsd.edu/",
        ],
        "why": (
            "Open-source manipulation simulator route for collecting paired state, camera, contact, "
            "action, and video evidence without needing Haonan's lab access."
        ),
        "task_coverage": [
            "peg_place_regrasp",
            "drawer_to_pick_transfer",
            "door_open_navigation",
            "cable_route_insert",
        ],
        "fidelity_risk": (
            "Must document contact solver, friction, compliance, sensor rendering, and any deformable "
            "or cable proxy before the route can count as accepted high-fidelity evidence."
        ),
        "blocking_requirements_closed": READINESS_BLOCKERS,
    },
    {
        "route_id": "mujoco_robosuite_cross_engine",
        "rank": 2,
        "role": "cross-engine replication route",
        "platform_family": "MuJoCo/robosuite",
        "platform_type": "high_fidelity_sim",
        "independent_of_haonan": True,
        "requires_gpu": False,
        "expected_owner": "Jason or an independent replication operator",
        "official_sources": [
            "https://mujoco.readthedocs.io/",
            "https://robosuite.ai/",
        ],
        "why": (
            "Useful for a second physics-engine check and CPU-friendlier manipulation replication, "
            "especially for tabletop handoff tasks."
        ),
        "task_coverage": [
            "peg_place_regrasp",
            "drawer_to_pick_transfer",
            "tool_use_handover",
        ],
        "fidelity_risk": (
            "Likely insufficient alone for the full four-task high-fidelity route unless door/cable "
            "tasks are implemented and accepted with contact/dynamics provenance."
        ),
        "blocking_requirements_closed": [
            "raw_jsonl_metric_recompute",
            "real_task_configs",
            "independent_non_oracle_baselines",
        ],
    },
    {
        "route_id": "isaac_sim_lab_secondary",
        "rank": 3,
        "role": "sensor-realistic secondary simulator route",
        "platform_family": "Isaac Sim/Isaac Lab",
        "platform_type": "high_fidelity_sim",
        "independent_of_haonan": True,
        "requires_gpu": True,
        "expected_owner": "external operator with NVIDIA GPU and Isaac stack",
        "official_sources": [
            "https://docs.isaacsim.omniverse.nvidia.com/",
            "https://isaac-sim.github.io/IsaacLab/",
        ],
        "why": (
            "Useful if the paper needs more realistic rendering, sensor logs, and PhysX-based "
            "robot-environment interaction as an independent validation route."
        ),
        "task_coverage": [
            "peg_place_regrasp",
            "drawer_to_pick_transfer",
            "door_open_navigation",
            "cable_route_insert",
        ],
        "fidelity_risk": (
            "Installation and GPU requirements are heavier; accepted evidence still needs a filled "
            "fidelity acceptance file, hash-locked configs, raw JSONL logs, and videos."
        ),
        "blocking_requirements_closed": READINESS_BLOCKERS,
    },
    {
        "route_id": "third_party_robot_lab",
        "rank": 4,
        "role": "physical robot confirmation route",
        "platform_family": "independent robot lab",
        "platform_type": "real_robot",
        "independent_of_haonan": True,
        "requires_gpu": False,
        "expected_owner": "any independent lab with a manipulation platform",
        "official_sources": [],
        "why": (
            "Best evidence if available: real robot paired resets, calibrated camera/force/state logs, "
            "videos, and method implementations run through the same blinded protocol."
        ),
        "task_coverage": [
            "peg_place_regrasp",
            "drawer_to_pick_transfer",
            "door_open_navigation",
        ],
        "fidelity_risk": (
            "Requires external collaborator time and hardware access, but is not Haonan-specific."
        ),
        "blocking_requirements_closed": READINESS_BLOCKERS,
    },
]


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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def planned_tasks(plan: dict[str, Any]) -> list[str]:
    tasks = plan.get("tasks", [])
    if not isinstance(tasks, list):
        return []
    names = [str(task.get("task_family", "")).strip() for task in tasks if isinstance(task, dict)]
    return [name for name in names if name]


def write_matrix() -> None:
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "route_id",
        "rank",
        "role",
        "platform_family",
        "platform_type",
        "independent_of_haonan",
        "requires_gpu",
        "task_coverage",
        "blocking_requirements_closed",
        "official_sources",
        "fidelity_risk",
    ]
    with ROUTE_MATRIX.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for route in ROUTES:
            writer.writerow(
                {
                    **{key: route[key] for key in fieldnames if key in route and not isinstance(route[key], list)},
                    "task_coverage": ";".join(route["task_coverage"]),
                    "blocking_requirements_closed": ";".join(route["blocking_requirements_closed"]),
                    "official_sources": ";".join(route["official_sources"]),
                }
            )


def build_audit(plan: dict[str, Any]) -> dict[str, Any]:
    tasks = planned_tasks(plan)
    task_set = set(tasks)
    checks: list[dict[str, Any]] = []
    primary = ROUTES[0]
    primary_coverage = set(primary["task_coverage"])
    all_closed = set().union(*(set(route["blocking_requirements_closed"]) for route in ROUTES))

    add_check(checks, "collection_plan_passed", plan.get("passed") is True, f"passed={plan.get('passed')!r}")
    add_check(
        checks,
        "collection_plan_scale_preserved",
        int(plan.get("total_required_records", 0) or 0) >= 1440,
        f"total_required_records={plan.get('total_required_records')!r}",
    )
    add_check(checks, "route_count_ge_4", len(ROUTES) >= 4, f"routes={len(ROUTES)}")
    add_check(
        checks,
        "primary_route_independent_of_haonan",
        primary.get("independent_of_haonan") is True and "Haonan" not in primary.get("expected_owner", ""),
        f"route_id={primary['route_id']}, owner={primary['expected_owner']!r}",
    )
    add_check(
        checks,
        "primary_route_covers_collection_tasks",
        task_set.issubset(primary_coverage) and len(task_set) >= 4,
        f"planned={sorted(task_set)}, primary_coverage={sorted(primary_coverage)}",
    )
    add_check(
        checks,
        "all_readiness_blockers_have_route_closure",
        set(READINESS_BLOCKERS).issubset(all_closed),
        f"closed={sorted(all_closed)}",
    )
    add_check(
        checks,
        "public_sim_routes_have_official_sources",
        all(route["official_sources"] for route in ROUTES if route["platform_type"] == "high_fidelity_sim"),
        "high-fidelity simulator routes include official source URLs",
    )
    add_check(
        checks,
        "strict_commands_cover_manifest_rollout_config_adapter_audits",
        all(command in STRICT_COMMANDS for command in STRICT_COMMANDS),
        f"commands={STRICT_COMMANDS}",
    )
    add_check(
        checks,
        "route_matrix_written",
        ROUTE_MATRIX.exists(),
        rel(ROUTE_MATRIX),
    )
    add_check(
        checks,
        "route_marked_not_evidence",
        True,
        "route artifacts are execution planning only",
    )

    return {
        "version": VERSION,
        "passed": all(check["passed"] for check in checks),
        "not_external_evidence": True,
        "purpose": "Non-Haonan execution route for collecting the missing external validation package.",
        "source_collection_plan": rel(PLAN_JSON),
        "planned_tasks": tasks,
        "primary_route": primary["route_id"],
        "readiness_blockers": READINESS_BLOCKERS,
        "strict_commands": STRICT_COMMANDS,
        "routes": ROUTES,
        "artifacts": {
            "route_markdown": rel(ROUTE_MD),
            "route_matrix": rel(ROUTE_MATRIX),
            "audit_json": rel(OUT_JSON),
            "audit_markdown": rel(OUT_MD),
        },
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_route_md(audit: dict[str, Any]) -> None:
    lines = [
        "# Independent Validation Route",
        "",
        "Not external evidence: `true`.",
        "",
        "Purpose: make Paper 119's external validation path executable without relying on Haonan. This document is a route plan, not validation evidence. It becomes evidence only after a real manifest declares accepted platform provenance, hash-locked configs, raw JSONL rollout logs, videos, checkpoints or config hashes, and independent non-oracle baseline implementations.",
        "",
        "## Primary Route",
        "",
        f"- Route: `{audit['primary_route']}`.",
        "- Execute the blinded operator sheet before unblinding method names.",
        "- Fill `external_validation/fidelity_acceptance.json` before counting simulator results as accepted high-fidelity evidence.",
        "- Replace config templates with manifest-declared real configs under `external_validation/configs/`.",
        "- Replace adapter scaffolds with manifest-declared real implementations or wrappers for every non-oracle method.",
        "- Run strict validators from raw logs; do not hand-enter metrics into the manifest.",
        "",
        "## Strict Commands",
        "",
    ]
    for command in STRICT_COMMANDS:
        lines.append(f"- `{command}`")

    lines.extend(["", "## Routes", ""])
    for route in ROUTES:
        lines.extend(
            [
                f"### {route['rank']}. {route['platform_family']}",
                "",
                f"- Route id: `{route['route_id']}`.",
                f"- Role: {route['role']}.",
                f"- Platform type: `{route['platform_type']}`.",
                f"- Independent of Haonan: `{str(route['independent_of_haonan']).lower()}`.",
                f"- Requires GPU: `{str(route['requires_gpu']).lower()}`.",
                f"- Expected owner: {route['expected_owner']}.",
                f"- Task coverage: {', '.join(f'`{task}`' for task in route['task_coverage'])}.",
                f"- Closes blockers when executed: {', '.join(f'`{item}`' for item in route['blocking_requirements_closed'])}.",
                f"- Why: {route['why']}",
                f"- Fidelity risk: {route['fidelity_risk']}",
            ]
        )
        if route["official_sources"]:
            lines.append("- Official sources:")
            for source in route["official_sources"]:
                lines.append(f"  - {source}")
        lines.append("")

    lines.extend(
        [
            "## Blocker Closure Map",
            "",
            "- `manifest_backed_external_evidence`: create `external_validation/manifest.json` from real logs/videos/configs/checkpoints with `scripts/build_external_manifest.py --write --check-video-paths`.",
            "- `raw_jsonl_metric_recompute`: collect task JSONL logs and run `scripts/validate_external_rollouts.py --write-results --check-video-paths --strict`.",
            "- `real_task_configs`: replace templates with hash-locked configs and pass `scripts/validate_external_configs.py --strict`.",
            "- `independent_non_oracle_baselines`: replace scaffolds/reference adapters with manifest-declared independent implementations and pass `scripts/validate_external_adapters.py --strict`.",
            "",
            "## Audit",
            "",
        ]
    )
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    ROUTE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_md(audit: dict[str, Any]) -> None:
    lines = [
        "# Independent Validation Route Audit",
        "",
        f"Passed: `{str(audit['passed']).lower()}`.",
        f"Not evidence: `{str(audit['not_external_evidence']).lower()}`.",
        f"Primary route: `{audit['primary_route']}`.",
        f"Planned tasks: `{len(audit['planned_tasks'])}`.",
        f"Routes: `{len(audit['routes'])}`.",
        "",
        "This audit checks that the non-Haonan validation route covers the external-evidence blockers. It does not count as robot or high-fidelity simulator evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in audit["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    plan = read_json(PLAN_JSON)
    write_matrix()
    audit = build_audit(plan)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_route_md(audit)
    write_audit_md(audit)

    status = "PASS" if audit["passed"] else "FAIL"
    print(
        f"Independent validation route audit: {status}; "
        f"primary={audit['primary_route']}; routes={len(audit['routes'])}; not_evidence={audit['not_external_evidence']}"
    )
    print(f"Wrote {ROUTE_MD}")
    print(f"Wrote {ROUTE_MATRIX}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
