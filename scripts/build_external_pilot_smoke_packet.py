from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"

PACKET_JSON = EXTERNAL / "pilot_smoke_packet.json"
PACKET_MD = EXTERNAL / "pilot_smoke_packet.md"
WORK_ORDERS = EXTERNAL / "pilot_smoke_work_orders.csv"
OUT_JSON = RESULTS / "external_pilot_smoke_packet_audit.json"
OUT_MD = RESULTS / "external_pilot_smoke_packet_audit.md"


PILOT_LOG_DIR = "external_validation\\pilot_smoke\\logs"
PILOT_VIDEO_DIR = "external_validation\\pilot_smoke\\videos"
PILOT_RUN_ID = "paper119_pilot_smoke_<platform>_<date>"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}


def pilot_commands() -> list[str]:
    return [
        (
            "python scripts\\audit_external_collection_readiness.py --strict "
            "--backend-module <module_or_path> --task-config-dir external_validation\\configs "
            f"--output-log-dir {PILOT_LOG_DIR} --video-dir {PILOT_VIDEO_DIR} "
            f"--run-id {PILOT_RUN_ID} --unsealed-alias-map --force"
        ),
        (
            "python external_validation\\runner\\real_collection_runner.py "
            "--backend-module <module_or_path> --task-config-dir external_validation\\configs "
            f"--output-log-dir {PILOT_LOG_DIR} --video-dir {PILOT_VIDEO_DIR} "
            f"--run-id {PILOT_RUN_ID} --unsealed-alias-map --max-rows 12 --force"
        ),
        (
            "python scripts\\audit_external_pilot_smoke.py --strict --expected-records 12 "
            "--check-video-paths"
        ),
        (
            "Remove or archive external_validation\\pilot_smoke before official collection; "
            "pilot logs/videos must never be listed in external_validation\\manifest.json"
        ),
    ]


def work_orders() -> list[dict[str, str]]:
    return [
        {
            "id": "pilot_backend_preflight",
            "title": "Run strict collection readiness against quarantine output dirs",
            "operator_input": "--backend-module, accepted fidelity file, unsealed aliases, specific pilot run id",
            "artifact": "results/external_collection_readiness_audit.json",
            "evidence_boundary": "not evidence; preflight only",
        },
        {
            "id": "pilot_first_panel",
            "title": "Collect the first 12-row method panel into pilot_smoke",
            "operator_input": "real backend plus prepared configs",
            "artifact": "external_validation/pilot_smoke/logs/*.jsonl and pilot_smoke/videos/*",
            "evidence_boundary": "quarantined smoke output; excluded from official manifest",
        },
        {
            "id": "pilot_schema_video_audit",
            "title": "Audit pilot records, videos, run ids, and quarantine paths",
            "operator_input": "pilot_smoke logs/videos",
            "artifact": "results/external_pilot_smoke_audit.json",
            "evidence_boundary": "does not satisfy rollout or external evidence gates",
        },
        {
            "id": "clear_pilot_before_full_collection",
            "title": "Remove or archive pilot output before official collection",
            "operator_input": "operator confirmation that manifest will not include pilot paths",
            "artifact": "clean external_validation/logs and external_validation/videos before official run",
            "evidence_boundary": "prevents pilot contamination of official evidence",
        },
    ]


def build_packet() -> dict[str, Any]:
    return {
        "version": "external_pilot_smoke_packet_v1",
        "not_external_evidence": True,
        "strict_evidence_ready": False,
        "purpose": "Quarantined first-panel smoke test for a real backend before full external collection.",
        "pilot_rows": 12,
        "quarantine_root": "external_validation/pilot_smoke",
        "pilot_log_dir": PILOT_LOG_DIR,
        "pilot_video_dir": PILOT_VIDEO_DIR,
        "forbidden_as_evidence": [
            "external_validation/pilot_smoke/logs/*.jsonl",
            "external_validation/pilot_smoke/videos/*",
            "external_validation/pilot_smoke/manifest.json",
        ],
        "official_evidence_dirs": [
            "external_validation/logs",
            "external_validation/videos",
            "external_validation/manifest.json",
        ],
        "commands": pilot_commands(),
        "work_orders": work_orders(),
    }


def write_csv(rows: list[dict[str, str]]) -> None:
    with WORK_ORDERS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "title", "operator_input", "artifact", "evidence_boundary"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(packet: dict[str, Any]) -> None:
    lines = [
        "# External Pilot Smoke Packet",
        "",
        "Not evidence: `true`.",
        f"Strict evidence ready: `{str(packet['strict_evidence_ready']).lower()}`.",
        f"Pilot rows: `{packet['pilot_rows']}`.",
        "",
        "This packet lets an independent operator test a real backend on one 12-row method panel without contaminating official evidence. Pilot logs and videos are quarantined under `external_validation/pilot_smoke/` and must never be included in `external_validation/manifest.json`.",
        "",
        "## Commands",
        "",
    ]
    for command in packet["commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Work Orders", ""])
    for row in packet["work_orders"]:
        lines.append(f"- `{row['id']}`: {row['title']} ({row['evidence_boundary']})")
    lines.extend(["", "## Forbidden As Evidence", ""])
    for item in packet["forbidden_as_evidence"]:
        lines.append(f"- `{item}`")
    PACKET_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_audit(packet: dict[str, Any]) -> dict[str, Any]:
    runner_probe = optional_json(RESULTS / "external_runner_backend_self_test.json")
    collection = optional_json(RESULTS / "external_collection_readiness_audit.json")
    pilot_audit = optional_json(RESULTS / "external_pilot_smoke_audit.json")
    commands = packet["commands"]

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "packet_is_non_evidence_and_fail_closed",
        packet.get("not_external_evidence") is True and packet.get("strict_evidence_ready") is False,
        f"strict_evidence_ready={packet.get('strict_evidence_ready')!r}",
    )
    add_check(
        checks,
        "quarantine_dirs_are_separate_from_official_evidence",
        packet["quarantine_root"] == "external_validation/pilot_smoke"
        and all("external_validation/pilot_smoke" in item for item in packet["forbidden_as_evidence"])
        and "external_validation/logs" in packet["official_evidence_dirs"]
        and "external_validation/videos" in packet["official_evidence_dirs"],
        f"quarantine_root={packet['quarantine_root']}",
    )
    add_check(
        checks,
        "runner_backend_probe_already_exercises_actual_runner",
        runner_probe.get("passed") is True
        and runner_probe.get("not_external_evidence") is True
        and int(runner_probe.get("records_written", 0) or 0) >= 2,
        f"records={runner_probe.get('records_written')!r}",
    )
    add_check(
        checks,
        "pilot_commands_preserve_gate_order",
        "audit_external_collection_readiness.py --strict" in commands[0]
        and "real_collection_runner.py" in commands[1]
        and "audit_external_pilot_smoke.py --strict" in commands[2],
        f"commands={commands}",
    )
    add_check(
        checks,
        "pilot_audit_reports_non_evidence_state",
        pilot_audit.get("not_external_evidence") is True
        and pilot_audit.get("strict_evidence_ready") is False
        and pilot_audit.get("passed") is True,
        (
            f"passed={pilot_audit.get('passed')!r}, "
            f"records={pilot_audit.get('records_observed')!r}"
        ),
    )
    add_check(
        checks,
        "collection_readiness_remains_official_gate",
        collection.get("passed") is True
        and collection.get("not_external_evidence") is True
        and collection.get("collection_ready") is False,
        f"collection_ready={collection.get('collection_ready')!r}",
    )
    add_check(
        checks,
        "packet_files_written",
        PACKET_JSON.exists() and PACKET_MD.exists() and WORK_ORDERS.exists(),
        f"json={PACKET_JSON.exists()}, md={PACKET_MD.exists()}, csv={WORK_ORDERS.exists()}",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": "external_pilot_smoke_packet_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "pilot_smoke_packet_ready": passed,
        "strict_evidence_ready": False,
        "pilot_rows": packet["pilot_rows"],
        "quarantine_root": packet["quarantine_root"],
        "commands": commands,
        "checks": checks,
    }


def write_audit_md(payload: dict[str, Any]) -> None:
    lines = [
        "# External Pilot Smoke Packet Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Pilot smoke packet ready: `{str(payload['pilot_smoke_packet_ready']).lower()}`.",
        f"Strict evidence ready: `{str(payload['strict_evidence_ready']).lower()}`.",
        "",
        "This audit checks that the pilot-smoke route is available as a quarantined backend smoke test and remains outside official external evidence.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    EXTERNAL.mkdir(exist_ok=True)
    packet = build_packet()
    PACKET_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(packet)
    write_csv(packet["work_orders"])
    audit = build_audit(packet)
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit_md(audit)
    print(
        "External pilot smoke packet: "
        f"{'PASS' if audit['passed'] else 'FAIL'}; "
        f"pilot_rows={audit['pilot_rows']}; "
        f"not_evidence={audit['not_external_evidence']}"
    )
    print(f"Wrote {PACKET_JSON}")
    print(f"Wrote {PACKET_MD}")
    print(f"Wrote {WORK_ORDERS}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if audit["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
