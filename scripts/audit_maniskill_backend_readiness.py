from __future__ import annotations

import json
import os
import sys
import tempfile
import importlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
RUNNER = EXTERNAL / "runner"
BACKEND_MODULE = "external_validation.runner.maniskill_reference_backend"
BACKEND_FILE = RUNNER / "maniskill_reference_backend.py"
OUT_JSON = RESULTS / "maniskill_backend_readiness_audit.json"
OUT_MD = RESULTS / "maniskill_backend_readiness_audit.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(RUNNER) not in sys.path:
    sys.path.insert(0, str(RUNNER))

from audit_external_backend_contract import backend_module_checks, create_backend  # noqa: E402


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {rel(path)}: {exc}") from exc


def alias_methods() -> list[str]:
    payload = read_json(EXTERNAL / "method_alias_map.json")
    aliases = payload.get("aliases", [])
    return sorted(
        str(item.get("method", "")).strip()
        for item in aliases
        if isinstance(item, dict) and str(item.get("method", "")).strip()
    )


def build_payload() -> dict[str, Any]:
    contract_checks, contract_ready = backend_module_checks(
        BACKEND_MODULE,
        EXTERNAL / "configs",
        EXTERNAL / "method_alias_map.json",
    )
    checks: list[dict[str, Any]] = list(contract_checks)
    backend_module = importlib.import_module(BACKEND_MODULE)
    backend = create_backend(BACKEND_MODULE)
    provenance = backend.platform_provenance()
    methods = alias_methods()
    adapter_paths = [EXTERNAL / "baselines" / method / "adapter.py" for method in methods]

    add_check(checks, "backend_file_exists", BACKEND_FILE.exists(), rel(BACKEND_FILE))
    add_check(
        checks,
        "backend_is_non_template",
        getattr(backend, "TEMPLATE_ONLY", True) is False
        and getattr(backend, "BACKEND_NAME", "") == "maniskill_sapien_reference_backend_v1",
        f"TEMPLATE_ONLY={getattr(backend, 'TEMPLATE_ONLY', None)!r}, BACKEND_NAME={getattr(backend, 'BACKEND_NAME', '')!r}",
    )
    add_check(
        checks,
        "backend_contract_strict_passes",
        contract_ready,
        "strict backend-module contract passed" if contract_ready else "strict backend-module contract failed",
    )
    add_check(
        checks,
        "platform_provenance_marks_non_evidence",
        provenance.get("not_external_evidence") is True
        and provenance.get("collection_enabled_by_default") is False,
        (
            f"not_external_evidence={provenance.get('not_external_evidence')!r}, "
            f"collection_enabled_by_default={provenance.get('collection_enabled_by_default')!r}"
        ),
    )
    add_check(
        checks,
        "delegates_to_reference_adapters",
        len(methods) >= 12 and all(path.exists() for path in adapter_paths),
        f"methods={len(methods)}, missing={[rel(path) for path in adapter_paths if not path.exists()]}",
    )
    old_flag = os.environ.pop("PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS", None)
    try:
        try:
            backend.execute_skill_pair({"proposal": {"decision": "accept", "predicted_seam_risk": 0.01}})
            fail_closed = False
            detail = "execute_skill_pair unexpectedly ran without enable flag"
        except RuntimeError as exc:
            fail_closed = "fail-closed" in str(exc) or "ENABLE_ROLLOUTS" in str(exc)
            detail = str(exc)
    finally:
        if old_flag is not None:
            os.environ["PAPER119_MANISKILL_REFERENCE_BACKEND_ENABLE_ROLLOUTS"] = old_flag
    add_check(
        checks,
        "official_collection_fail_closed_without_enable_flag",
        fail_closed,
        detail,
    )
    try:
        backend.record_video(Path("external_validation/videos/probe.mp4"))
        video_fail_closed = False
        video_detail = "record_video unexpectedly ran"
    except RuntimeError as exc:
        video_fail_closed = "requires a reset ManiSkill environment" in str(exc)
        video_detail = str(exc)
    add_check(
        checks,
        "video_export_fail_closed_before_reset",
        video_fail_closed,
        video_detail,
    )
    writer = getattr(backend_module, "write_mp4", None)
    video_writer_ok = False
    video_writer_detail = "write_mp4 missing"
    if callable(writer):
        import numpy as np

        with tempfile.TemporaryDirectory(prefix="paper119_maniskill_video_") as tmp_name:
            target = Path(tmp_name) / "probe.mp4"
            frames = [
                np.zeros((32, 32, 3), dtype=np.uint8),
                np.full((32, 32, 3), 255, dtype=np.uint8),
            ]
            try:
                writer(target, frames, fps=4)
                header = target.read_bytes()[:64]
                video_writer_ok = target.exists() and target.stat().st_size >= 512 and b"ftyp" in header
                video_writer_detail = f"bytes={target.stat().st_size}, mp4_header={b'ftyp' in header}"
            except Exception as exc:  # noqa: BLE001 - report the concrete writer failure.
                video_writer_detail = f"{type(exc).__name__}: {exc}"
    add_check(
        checks,
        "synthetic_mp4_writer_passes",
        video_writer_ok,
        video_writer_detail,
    )
    extractor = getattr(backend_module, "_as_uint8_rgb_frame", None)
    state_frame_rejected = False
    state_frame_detail = "_as_uint8_rgb_frame missing"
    if callable(extractor):
        import numpy as np

        try:
            extractor({"state": np.arange(27, dtype=np.float32).reshape(1, 9, 3)})
            state_frame_detail = "state-shaped array was accepted as an RGB frame"
        except RuntimeError as exc:
            state_frame_rejected = "state-like arrays" in str(exc) or "RGB-like frame" in str(exc)
            state_frame_detail = str(exc)
        except Exception as exc:  # noqa: BLE001 - report the concrete extractor failure.
            state_frame_detail = f"{type(exc).__name__}: {exc}"
    add_check(
        checks,
        "state_shaped_arrays_rejected_as_video_frames",
        state_frame_rejected,
        state_frame_detail,
    )
    add_check(
        checks,
        "strict_evidence_remains_false",
        provenance.get("not_external_evidence") is True,
        "backend contract and MP4-writer readiness are not rollout evidence, fidelity acceptance, logs, or manifest evidence",
    )

    passed = all(check["passed"] for check in checks)
    return {
        "version": "maniskill_reference_backend_audit_v1",
        "passed": passed,
        "not_external_evidence": True,
        "backend_module": BACKEND_MODULE,
        "backend_file": rel(BACKEND_FILE),
        "backend_contract_ready": contract_ready,
        "reference_backend_available": passed,
        "reference_backend_collection_enabled": False,
        "video_writer_ready": video_writer_ok,
        "official_collection_ready": False,
        "strict_external_evidence_ready": False,
        "method_adapter_count": len(methods),
        "platform_provenance": provenance,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ManiSkill Reference Backend Readiness Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        f"Backend module: `{payload['backend_module']}`.",
        f"Backend contract ready: `{str(payload['backend_contract_ready']).lower()}`.",
        f"Reference backend collection enabled: `{str(payload['reference_backend_collection_enabled']).lower()}`.",
        f"Video writer ready: `{str(payload['video_writer_ready']).lower()}`.",
        f"Official collection ready: `{str(payload['official_collection_ready']).lower()}`.",
        f"Strict external evidence ready: `{str(payload['strict_external_evidence_ready']).lower()}`.",
        "",
        "This audit qualifies the repository's ManiSkill/SAPIEN reference backend against the backend API, method-adapter wiring, and MP4 writer path. It does not provide rollout evidence: official collection still requires accepted fidelity provenance, installed assets, explicit alias unsealing, renderable per-episode videos, JSONL logs, manifests, and strict evidence audits.",
        "",
        "## Checks",
        "",
    ]
    for check in payload["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        "ManiSkill reference backend readiness audit: "
        f"{'PASS' if payload['passed'] else 'FAIL'}; "
        f"backend_contract_ready={payload['backend_contract_ready']}; "
        f"official_collection_ready={payload['official_collection_ready']}; "
        f"not_evidence={payload['not_external_evidence']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
