from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import validate_external_rollouts as rollout


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "external_validation" / "log_schema_v1.json"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    digest_obj = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest_obj.update(chunk)
    return digest_obj.hexdigest()


def write_synthetic_mp4(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41"
    payload = b"\x00\x00\x02\x20mdat" + (b"synthetic self-test frame bytes; not external evidence\n" * 16)
    path.write_bytes(header + payload)


def make_record(task: str, scene_idx: int, method: str, *, success: bool, utility: float) -> dict:
    return {
        "run_id": "synthetic_self_test_only",
        "task_family": task,
        "platform_type": "high_fidelity_sim",
        "platform_name": "temporary_self_test_fixture",
        "scene_id": f"{task}_scene_{scene_idx:02d}",
        "episode_index": scene_idx,
        "seed": scene_idx,
        "method": method,
        "skill_i": f"{task}_skill_i",
        "skill_j": f"{task}_skill_j",
        "initial_state_hash": digest(f"{task}:{scene_idx}:initial"),
        "terminal_sample_set_hash": digest(f"{task}:{scene_idx}:terminal"),
        "basin_estimate": 0.82 if method == rollout.PRIMARY_METHOD else 0.55,
        "barrier_score": 0.12 if method == rollout.PRIMARY_METHOD else 0.31,
        "descent_continuity_score": 0.88 if method == rollout.PRIMARY_METHOD else 0.63,
        "predicted_seam_risk": 0.05 if method == rollout.PRIMARY_METHOD else 0.21,
        "fixed_risk_budget": 0.15,
        "decision": "accept" if method == rollout.PRIMARY_METHOD else "transition",
        "failure_diagnosis": "none" if success else "basin_miss",
        "repair_action": "none",
        "success": success,
        "seam_failure": not success,
        "barrier_violation": False,
        "damage_or_intervention": False,
        "composition_cost": 0.19 if method == rollout.PRIMARY_METHOD else 0.29,
        "realized_seam_breach": False,
        "utility": utility,
        "video_path": f"synthetic_self_test_only/{task}_{scene_idx}_{method}.mp4",
        "policy_or_config_hash": digest(f"{method}:config"),
    }


def method_hashes(methods: list[str]) -> dict[str, str]:
    return {method: digest(f"{method}:config") for method in methods}


def build_fixture(tmp: Path) -> tuple[dict, dict]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    tasks = [
        "peg_place_regrasp",
        "drawer_to_pick_transfer",
        "door_open_navigation",
        "cable_route_insert",
    ]
    log_dir = tmp / "logs"
    config_dir = tmp / "configs"
    log_dir.mkdir()
    config_dir.mkdir()
    methods = [
        rollout.PRIMARY_METHOD,
        "greedy_module_sequence",
    ]
    hashes = method_hashes(methods)
    manifest = {
        "tasks": [],
        "methods": [{"name": method, "checkpoint_or_config_hash": hashes[method]} for method in methods],
    }
    for task in tasks:
        config_path = config_dir / f"{task}.json"
        config_payload = {
            "task_family": task,
            "platform_type": "high_fidelity_sim",
            "platform_name": "temporary_self_test_fixture",
            "skill_i": f"{task}_skill_i",
            "skill_j": f"{task}_skill_j",
            "fixed_risk_budget": 0.15,
        }
        config_path.write_text(json.dumps(config_payload, sort_keys=True) + "\n", encoding="utf-8")
        log_path = log_dir / f"{task}.jsonl"
        with log_path.open("w", encoding="utf-8") as handle:
            for scene_idx in range(10):
                proposed_success = scene_idx < 8
                baseline_success = scene_idx < 6
                records = [
                    make_record(task, scene_idx, rollout.PRIMARY_METHOD, success=proposed_success, utility=1.0 if proposed_success else 0.42),
                    make_record(task, scene_idx, "greedy_module_sequence", success=baseline_success, utility=0.79 if baseline_success else 0.30),
                ]
                for record in records:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
        manifest["tasks"].append(
            {
                "task_family": task,
                "platform_type": "high_fidelity_sim",
                "platform_name": "temporary_self_test_fixture",
                "log_jsonl": str(log_path),
                "config_path": str(config_path),
                "config_hash": file_digest(config_path),
            }
        )
    return manifest, schema


def assert_close(name: str, actual: float, expected: float, tolerance: float = 1e-9) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{name}: {actual} != {expected}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="paper119_rollout_selftest_") as tmp_name:
        manifest, schema = build_fixture(Path(tmp_name))
        records, errors = rollout.load_records(manifest, schema, check_video_paths=False, max_errors=10)
        if errors:
            raise AssertionError(f"unexpected schema errors: {errors}")
        summary = rollout.summarize(records, schema)
        checks = rollout.threshold_checks(summary, schema)

        if len(records) != 80:
            raise AssertionError(f"expected 80 synthetic records, got {len(records)}")
        if summary["strongest_external_baseline"] != "greedy_module_sequence":
            raise AssertionError(f"wrong strongest baseline: {summary['strongest_external_baseline']}")
        assert_close("external_success_margin", summary["external_success_margin"], 0.2)
        assert_close("external_utility_margin", summary["external_utility_margin"], 0.29)
        assert_close("paired_win_rate", summary["paired_win_rate"], 1.0)
        assert_close("fixed_risk_coverage", summary["fixed_risk_coverage"], 1.0)
        assert_close("fixed_risk_breach", summary["fixed_risk_breach"], 0.0)
        if summary["positive_task_families"] != 4:
            raise AssertionError(f"positive_task_families: {summary['positive_task_families']} != 4")
        failed_checks = [check.message for check in checks if not check.passed]
        if failed_checks:
            raise AssertionError(f"unexpected failed threshold checks: {failed_checks}")

        bad_record = dict(records[0])
        del bad_record["utility"]
        bad_errors = rollout.validate_record(
            bad_record,
            line_id="synthetic_bad_record",
            schema=schema,
            manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
            manifest_tasks=set(summary["task_families"]),
            check_video_paths=False,
        )
        if not any("missing required fields" in error and "utility" in error for error in bad_errors):
            raise AssertionError(f"missing-field test did not fail as expected: {bad_errors}")

        stale_config_hash_manifest = json.loads(json.dumps(manifest))
        stale_config_hash_manifest["tasks"][0]["config_hash"] = digest("stale:task_config")
        _, stale_config_hash_errors = rollout.load_records(
            stale_config_hash_manifest,
            schema,
            check_video_paths=False,
            max_errors=10,
        )
        if not any("config_hash does not match config_path" in error for error in stale_config_hash_errors):
            raise AssertionError(f"stale task config hash test did not fail as expected: {stale_config_hash_errors}")

        config_task = str(records[0]["task_family"])
        task_config = json.loads(Path(manifest["tasks"][0]["config_path"]).read_text(encoding="utf-8"))
        stale_task_config_record = dict(records[0])
        stale_task_config_record["skill_i"] = "stale_skill_i_from_old_task_config"
        stale_task_config_errors = rollout.validate_record(
            stale_task_config_record,
            line_id="synthetic_stale_task_config_record",
            schema=schema,
            manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
            manifest_tasks=set(summary["task_families"]),
            check_video_paths=False,
            manifest_task_specs={config_task: manifest["tasks"][0]},
            manifest_task_configs={config_task: task_config},
            manifest_method_hashes=method_hashes([rollout.PRIMARY_METHOD, "greedy_module_sequence"]),
        )
        if not any("skill_i must match manifest task config" in error for error in stale_task_config_errors):
            raise AssertionError(f"stale task config row test did not fail as expected: {stale_task_config_errors}")

        spoofed_hash_record = dict(records[0])
        spoofed_hash_record["policy_or_config_hash"] = digest("spoofed:policy")
        spoofed_hash_errors = rollout.validate_record(
            spoofed_hash_record,
            line_id="synthetic_spoofed_policy_hash_record",
            schema=schema,
            manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
            manifest_tasks=set(summary["task_families"]),
            check_video_paths=False,
            manifest_method_hashes=method_hashes([rollout.PRIMARY_METHOD, "greedy_module_sequence"]),
        )
        if not any("policy_or_config_hash must match manifest checkpoint_or_config_hash" in error for error in spoofed_hash_errors):
            raise AssertionError(f"spoofed policy/config hash test did not fail as expected: {spoofed_hash_errors}")

        video_dir = Path(tmp_name) / "videos" / "peg_place_regrasp"
        good_video = video_dir / "good_render_backed_fixture.mp4"
        write_synthetic_mp4(good_video)
        good_video_record = dict(records[0])
        good_video_record["video_path"] = str(good_video)
        good_video_errors = rollout.validate_record(
            good_video_record,
            line_id="synthetic_good_video_record",
            schema=schema,
            manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
            manifest_tasks=set(summary["task_families"]),
            check_video_paths=True,
            manifest_video_dirs={"peg_place_regrasp": video_dir},
            strict_video_evidence=True,
        )
        if good_video_errors:
            raise AssertionError(f"strict video fixture unexpectedly failed: {good_video_errors}")

        fake_video = video_dir / "fake_text_payload.mp4"
        fake_video.write_bytes(b"plain text pretending to be an mp4\n" * 32)
        fake_video_record = dict(good_video_record)
        fake_video_record["video_path"] = str(fake_video)
        fake_video_errors = rollout.validate_record(
            fake_video_record,
            line_id="synthetic_fake_video_record",
            schema=schema,
            manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
            manifest_tasks=set(summary["task_families"]),
            check_video_paths=True,
            manifest_video_dirs={"peg_place_regrasp": video_dir},
            strict_video_evidence=True,
        )
        if not any("not MP4-like evidence" in error for error in fake_video_errors):
            raise AssertionError(f"strict video fixture did not reject fake MP4: {fake_video_errors}")

        forbidden_video_cases = {
            "staging": video_dir / "internal_runner_artifact.staging.mp4",
            "backup": video_dir / "internal_runner_artifact.backup.mp4",
        }
        for fragment, forbidden_video in forbidden_video_cases.items():
            write_synthetic_mp4(forbidden_video)
            forbidden_record = dict(good_video_record)
            forbidden_record["video_path"] = str(forbidden_video)
            forbidden_errors = rollout.validate_record(
                forbidden_record,
                line_id=f"synthetic_forbidden_{fragment}_video_record",
                schema=schema,
                manifest_methods={rollout.PRIMARY_METHOD, "greedy_module_sequence"},
                manifest_tasks=set(summary["task_families"]),
                check_video_paths=True,
                manifest_video_dirs={"peg_place_regrasp": video_dir},
                strict_video_evidence=True,
            )
            if not any("forbidden non-evidence fragment" in error and fragment in error for error in forbidden_errors):
                raise AssertionError(f"strict video fixture did not reject {fragment} MP4 path: {forbidden_errors}")

    print("External rollout validator self-test passed: synthetic metrics recomputed and schema failure path checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
