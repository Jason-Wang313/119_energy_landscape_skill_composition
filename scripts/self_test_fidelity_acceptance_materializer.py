from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

import materialize_fidelity_acceptance as materializer


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "fidelity_acceptance_materializer_self_test.json"
OUT_MD = RESULTS / "fidelity_acceptance_materializer_self_test.md"
REAL_ACCEPTANCE = ROOT / "external_validation" / "fidelity_acceptance.json"

GOOD_COMMIT = "a" * 40
STALE_COMMIT = "b" * 40
GOOD_HASH = "C" * 64
BAD_HASH = "D" * 64


def file_digest(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_draft() -> dict[str, Any]:
    return {
        "version": materializer.DRAFT_VERSION,
        "not_external_evidence": True,
        "draft_only": True,
        "acceptance_ready": False,
        "route": "high_fidelity_sim",
        "platform": {"platform_type": "high_fidelity_sim", "platform_name": "materializer-self-test"},
        "qualification": {},
        "task_fidelity": [],
        "provenance": {},
        "acceptance_gates": [
            {"name": "platform_provenance_complete", "status": "draft_unaccepted"},
            {"name": "paired_reset_replay_verified", "status": "draft_unaccepted"},
            {"name": "contact_failure_observable", "status": "draft_unaccepted"},
            {"name": "non_oracle_methods_fair", "status": "draft_unaccepted"},
            {"name": "raw_logs_drive_metrics", "status": "draft_unaccepted"},
        ],
    }


def make_args(draft: Path, *, code_commit: str = GOOD_COMMIT, skill_hash: str = GOOD_HASH, write: bool = True) -> argparse.Namespace:
    return argparse.Namespace(
        draft=draft,
        operator_name_or_lab="Synthetic Materializer Guard Lab",
        accepted_collection_machine="Synthetic high-fidelity simulator host",
        contact_solver_and_friction_model="Synthetic fixed contact solver and friction model",
        timestep_and_substeps_per_control_step="sim_dt=0.01, control_dt=0.05, substeps=5",
        paired_reset_replay_test="Synthetic paired reset replay passes for every method panel",
        real_or_benchmark_calibration_basis="Synthetic benchmark calibration fixture",
        task_binding_decision="Synthetic task bindings accepted for self-test only",
        acceptance_gate_signoff="Synthetic self-test gate signoff",
        known_limitations="Temporary materializer self-test fixture, not evidence",
        date_locked="2026-06-29T00:00:00Z self-test lock",
        code_commit=code_commit,
        skill_library_hash=skill_hash,
        confirm_real_platform=True,
        confirm_independent_operator=True,
        confirm_render_backed_videos=True,
        confirm_real_rollout_evidence=True,
        confirm_manifest_declaration=True,
        write=write,
        force=True,
    )


@contextmanager
def patched_materializer(
    *,
    draft: Path,
    output: Path,
    manifest: Path,
    commit: str = GOOD_COMMIT,
    skill_hash: str = GOOD_HASH,
    dirty_status: str = "",
) -> Iterator[None]:
    original_draft = materializer.DRAFT_JSON
    original_output = materializer.OUTPUT_JSON
    original_manifest = materializer.MANIFEST_JSON
    original_run_git: Callable[[list[str]], str] = materializer.run_git
    original_sha256_tree: Callable[[Path], str] = materializer.sha256_tree

    def fake_run_git(args: list[str]) -> str:
        if args == ["rev-parse", "HEAD"]:
            return commit
        if args == ["status", "--short"]:
            return dirty_status
        return ""

    def fake_sha256_tree(_: Path) -> str:
        return skill_hash

    materializer.DRAFT_JSON = draft
    materializer.OUTPUT_JSON = output
    materializer.MANIFEST_JSON = manifest
    materializer.run_git = fake_run_git
    materializer.sha256_tree = fake_sha256_tree
    try:
        yield
    finally:
        materializer.DRAFT_JSON = original_draft
        materializer.OUTPUT_JSON = original_output
        materializer.MANIFEST_JSON = original_manifest
        materializer.run_git = original_run_git
        materializer.sha256_tree = original_sha256_tree


def run_case(
    tmp: Path,
    name: str,
    *,
    supplied_commit: str = GOOD_COMMIT,
    supplied_hash: str = GOOD_HASH,
    current_commit: str = GOOD_COMMIT,
    current_hash: str = GOOD_HASH,
    dirty_status: str = "",
) -> dict[str, Any]:
    draft = tmp / f"{name}_draft.json"
    output = tmp / f"{name}_acceptance.json"
    manifest = tmp / f"{name}_manifest.json"
    write_json(draft, fixture_draft())

    args = make_args(draft, code_commit=supplied_commit, skill_hash=supplied_hash, write=True)
    with patched_materializer(
        draft=draft,
        output=output,
        manifest=manifest,
        commit=current_commit,
        skill_hash=current_hash,
        dirty_status=dirty_status,
    ):
        try:
            payload = materializer.build_plan(args)
            raised = False
            error = ""
        except SystemExit as exc:
            payload = {}
            raised = True
            error = str(exc)

    written_payload = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    return {
        "name": name,
        "raised": raised,
        "error": error,
        "output_exists": output.exists(),
        "payload_passed": payload.get("passed"),
        "acceptance_write_ready": payload.get("acceptance_write_ready"),
        "candidate_acceptance_ready": payload.get("candidate_acceptance_ready"),
        "written_version": written_payload.get("version"),
        "written_acceptance_ready": written_payload.get("acceptance_ready"),
    }


def cache_exclusion_check(tmp: Path) -> dict[str, Any]:
    tree = tmp / "baseline_tree"
    pycache = tree / "method" / "__pycache__"
    pycache.mkdir(parents=True)
    source = tree / "method" / "adapter.py"
    cache = pycache / "adapter.cpython-311.pyc"
    source.write_text("POLICY = 'stable'\n", encoding="utf-8")
    cache.write_bytes(b"first transient cache")
    digest_before = materializer.sha256_tree(tree)
    cache.write_bytes(b"changed transient cache")
    digest_after = materializer.sha256_tree(tree)
    return {
        "digest_before": digest_before,
        "digest_after": digest_after,
        "unchanged_after_pyc_mutation": digest_before == digest_after,
    }


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def write_report(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Fidelity Acceptance Materializer Self-Test",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        "Not evidence: `true`.",
        "",
        "This self-test exercises the guarded fidelity-acceptance materializer on temporary files only. It verifies that a clean matching checkout can write a temporary acceptance file, while stale commits, mismatched skill-library hashes, and dirty checkouts are rejected before any write.",
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
    real_before = file_digest(REAL_ACCEPTANCE)
    checks: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="paper119_materializer_selftest_", dir=RESULTS) as tmp_name:
        tmp = Path(tmp_name)
        good = run_case(tmp, "matching_clean_checkout")
        stale = run_case(tmp, "stale_commit", supplied_commit=STALE_COMMIT)
        bad_hash = run_case(tmp, "mismatched_skill_hash", supplied_hash=BAD_HASH)
        dirty = run_case(tmp, "dirty_checkout", dirty_status=" M scripts/materialize_fidelity_acceptance.py")
        cache = cache_exclusion_check(tmp)

    real_after = file_digest(REAL_ACCEPTANCE)
    add_check(
        checks,
        "matching_clean_checkout_writes_temp_acceptance",
        good["raised"] is False
        and good["output_exists"] is True
        and good["payload_passed"] is True
        and good["acceptance_write_ready"] is True
        and good["candidate_acceptance_ready"] is True
        and good["written_version"] == materializer.EVIDENCE_VERSION
        and good["written_acceptance_ready"] is True,
        str(good),
    )
    add_check(
        checks,
        "stale_commit_rejected_without_temp_write",
        stale["raised"] is True and stale["output_exists"] is False,
        str(stale),
    )
    add_check(
        checks,
        "mismatched_skill_hash_rejected_without_temp_write",
        bad_hash["raised"] is True and bad_hash["output_exists"] is False,
        str(bad_hash),
    )
    add_check(
        checks,
        "dirty_checkout_rejected_without_temp_write",
        dirty["raised"] is True and dirty["output_exists"] is False,
        str(dirty),
    )
    add_check(
        checks,
        "pycache_excluded_from_skill_library_hash",
        cache["unchanged_after_pyc_mutation"] is True,
        str(cache),
    )
    add_check(
        checks,
        "real_acceptance_file_not_touched",
        real_before == real_after,
        f"before={real_before}, after={real_after}",
    )

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "fidelity_acceptance_materializer_self_test_v1",
        "passed": passed,
        "not_external_evidence": True,
        "temporary_good_case": good,
        "temporary_stale_commit_case": stale,
        "temporary_mismatched_hash_case": bad_hash,
        "temporary_dirty_checkout_case": dirty,
        "cache_exclusion_case": cache,
        "real_acceptance_before": real_before,
        "real_acceptance_after": real_after,
        "checks": checks,
    }
    write_report(payload)
    print(f"Fidelity acceptance materializer self-test: {'PASS' if passed else 'FAIL'}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
