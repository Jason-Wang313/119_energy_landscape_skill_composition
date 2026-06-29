from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external_validation"
RESULTS = ROOT / "results"
DEFAULT_MANIFEST = EXTERNAL / "manifest.json"
OUT_JSON = RESULTS / "external_release_package_audit.json"
OUT_MD = RESULTS / "external_release_package_audit.md"
ARTIFACT_TYPES = ("code", "configs", "logs", "videos", "checkpoints")
FORBIDDEN_RELEASE_LOG_VIDEO_FRAGMENTS = {
    "backup",
    "diagnostic",
    "fallback",
    "not_external_evidence",
    "pilot_smoke",
    "placeholder",
    "render_video_preflight",
    "staging",
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc


def rel_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if path.is_dir():
        digest = hashlib.sha256()
        files = sorted(child for child in path.rglob("*") if child.is_file())
        for child in files:
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(sha256_file(child).encode("ascii"))
            digest.update(b"\0")
        return digest.hexdigest().upper()
    raise FileNotFoundError(path)


def is_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)


def inspect_config(path: Path) -> list[str]:
    if path.suffix.lower() != ".json":
        return []
    try:
        payload = read_json(path)
    except SystemExit as exc:
        return [str(exc)]
    blockers = []
    if payload.get("template_only") is True or payload.get("not_external_evidence") is True:
        blockers.append("config is marked template_only/not_external_evidence")
    if "template" in str(payload.get("version", "")).lower():
        blockers.append(f"config version appears to be a template: {payload.get('version')!r}")
    return blockers


def inspect_video_file(path: Path) -> list[str]:
    blockers: list[str] = []
    if path.suffix.lower() != ".mp4":
        blockers.append("video artifact must be an .mp4 file")
        return blockers
    if path.stat().st_size < 1024:
        blockers.append("video artifact is too small to be credible rollout media")
    with path.open("rb") as handle:
        header = handle.read(16)
    if len(header) < 12 or header[4:8] != b"ftyp":
        blockers.append("video artifact is not MP4-like evidence with an ftyp box")
    return blockers


def inspect_video_artifact(path: Path) -> list[str]:
    if path.is_file():
        return inspect_video_file(path)
    if not path.is_dir():
        return []
    mp4_files = sorted(child for child in path.rglob("*.mp4") if child.is_file())
    blockers: list[str] = []
    if not mp4_files:
        blockers.append("video directory contains no MP4 files")
    for child in mp4_files:
        child_blockers = inspect_video_file(child)
        blockers.extend(f"{rel(child)}: {item}" for item in child_blockers)
    return blockers


def inspect_entry(kind: str, entry: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    path_value = str(entry.get("path", ""))
    declared_hash = str(entry.get("sha256", ""))
    blockers: list[str] = []
    path = rel_path(path_value) if path_value else ROOT / "__missing__"
    path_rel = rel(path) if path_value else ""
    normalized = path_rel.replace("\\", "/").lower()

    if not path_value:
        blockers.append("path is empty")
    if not is_hash(declared_hash):
        blockers.append("sha256 is missing or malformed")
    if "external_validation/local_dry_run/" in normalized:
        blockers.append("local_dry_run artifact cannot be release evidence")
    if "external_validation/config_templates/" in normalized:
        blockers.append("config template artifact cannot be release evidence")
    if path.name == "adapter_template.py" or "scaffold" in path.name.lower():
        blockers.append("adapter scaffold/template cannot be release evidence")
    if kind in {"logs", "videos"}:
        forbidden_hits = sorted(
            fragment
            for fragment in FORBIDDEN_RELEASE_LOG_VIDEO_FRAGMENTS
            if fragment in normalized or fragment in path.name.lower()
        )
        if forbidden_hits:
            blockers.append(f"{kind} artifact contains forbidden non-evidence fragment(s): {forbidden_hits}")

    exists = path.exists()
    actual_hash = ""
    if not exists:
        blockers.append("path does not exist")
    else:
        actual_hash = sha256_path(path)
        if declared_hash and is_hash(declared_hash) and actual_hash.upper() != declared_hash.upper():
            blockers.append("sha256 does not match actual artifact")
        if kind == "configs":
            if path.is_file():
                blockers.extend(inspect_config(path))
            elif path.is_dir():
                for config_path in sorted(path.rglob("*.json")):
                    blockers.extend(f"{rel(config_path)}: {item}" for item in inspect_config(config_path))
        if kind == "videos":
            blockers.extend(inspect_video_artifact(path))

    return (
        {
            "kind": kind,
            "path": path_value,
            "exists": exists,
            "declared_sha256": declared_hash,
            "actual_sha256": actual_hash,
            "blocking_missing": blockers,
        },
        blockers,
    )


def build_payload(manifest_path: Path) -> dict[str, Any]:
    manifest_exists = manifest_path.exists()
    if not manifest_exists:
        return {
            "version": "external_release_package_audit_v1",
            "passed": True,
            "not_external_evidence": True,
            "release_package_ready": False,
            "manifest_path": rel(manifest_path),
            "artifact_counts": {kind: 0 for kind in ARTIFACT_TYPES},
            "entry_reports": [],
            "blocking_missing_count": 1,
            "blocking_missing": ["external_validation/manifest.json has not been written from real evidence"],
        }

    manifest = read_json(manifest_path)
    release = manifest.get("release_artifacts", {})
    release = release if isinstance(release, dict) else {}
    entry_reports: list[dict[str, Any]] = []
    blockers: list[str] = []
    artifact_counts: dict[str, int] = {}
    for kind in ARTIFACT_TYPES:
        entries = release.get(kind, [])
        entries = entries if isinstance(entries, list) else []
        artifact_counts[kind] = len(entries)
        if not entries:
            blockers.append(f"release_artifacts.{kind} is empty")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                blockers.append(f"release_artifacts.{kind}[{index}] is not an object")
                continue
            report, entry_blockers = inspect_entry(kind, entry)
            entry_reports.append(report)
            blockers.extend(f"{kind}:{entry.get('path', '<missing>')}: {item}" for item in entry_blockers)

    if not str(manifest.get("code_commit", "")).strip():
        blockers.append("code_commit is empty")
    if not str(manifest.get("skill_library_hash", "")).strip():
        blockers.append("skill_library_hash is empty")
    if manifest.get("local_dry_run_only") is True or manifest.get("not_external_evidence") is True:
        blockers.append("manifest is marked local_dry_run_only/not_external_evidence")

    ready = not blockers
    return {
        "version": "external_release_package_audit_v1",
        "passed": True,
        "not_external_evidence": not ready,
        "release_package_ready": ready,
        "manifest_path": rel(manifest_path),
        "artifact_counts": artifact_counts,
        "entry_reports": entry_reports,
        "blocking_missing_count": len(blockers),
        "blocking_missing": blockers,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    RESULTS.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# External Release Package Audit",
        "",
        f"Passed: `{str(payload['passed']).lower()}`.",
        f"Not evidence: `{str(payload['not_external_evidence']).lower()}`.",
        f"Release package ready: `{str(payload['release_package_ready']).lower()}`.",
        f"Blocking missing items: `{payload['blocking_missing_count']}`.",
        "",
        "This audit verifies manifest-declared release artifacts by path and SHA256 hash, and rejects local dry-run, template, scaffold, placeholder, staged, backup, diagnostic, fallback, empty-video-directory, or non-MP4-like log/video artifacts as evidence.",
        "",
        "## Artifact Counts",
        "",
    ]
    for kind, count in payload["artifact_counts"].items():
        lines.append(f"- `{kind}`: `{count}`")
    lines.extend(["", "## Blocking Missing", ""])
    if payload["blocking_missing"]:
        for blocker in payload["blocking_missing"][:100]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit manifest-declared external release artifacts and hashes.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="External validation manifest path.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless the release package is ready.")
    args = parser.parse_args()

    payload = build_payload(args.manifest)
    write_outputs(payload)
    print(
        "External release package audit: "
        f"release_package_ready={payload['release_package_ready']}; "
        f"blocking_missing={payload['blocking_missing_count']}"
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if payload["release_package_ready"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
