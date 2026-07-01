from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = ROOT / "results"
OUT_JSON = RESULTS / "reference_integrity_audit.json"
OUT_MD = RESULTS / "reference_integrity_audit.md"

CURRENT_YEAR = 2026

RECENT_PRIMARY_SOURCES = {
    "openx2023": {"arxiv": "2310.08864", "title": "Open X-Embodiment"},
    "du2019implicit": {"arxiv": "1903.08689", "title": "Implicit Generation and Generalization"},
    "wang2024poco": {"arxiv": "2402.02511", "title": "PoCo"},
    "liu2026simpact": {"arxiv": "2512.05955", "title": "SIMPACT", "venue": "Computer Vision and Pattern Recognition", "must_author": ["Haonan Chen", "Yilun Du"]},
    "liu2026oat": {"arxiv": "2602.04215", "title": "OAT", "must_author": ["Haonan Chen", "Yilun Du"]},
    "hou2026worldmodel": {"arxiv": "2605.00080", "title": "World Model for Robot Learning", "must_author": ["Yilun Du"]},
    "chen2026costream": {"arxiv": "2606.26423", "title": "CoStream", "must_author": ["Haonan Chen", "Yilun Du"]},
}

DOI_EXPECTATIONS = {
    "urain2021cep": "10.15607/RSS.2021.XVII.052",
    "pane2021runtime": "10.1109/LRA.2021.3094498",
    "rizwan2025ezskiros": "10.3389/frobt.2024.1363443",
    "chi2023diffusionpolicy": "10.15607/RSS.2023.XIX.026",
    "julian2020latent": "10.1177/0278364920944474",
    "vijayaraghavan2025compositionality": "10.1126/scirobotics.adp0751",
}

FORBIDDEN_BIB_TERMS = [
    "TODO",
    "PLACEHOLDER",
    "unknown",
    "citation needed",
    "personal communication",
]


def normalized_author_blob(author_field: str) -> str:
    variants = [author_field]
    for author in re.split(r"\s+and\s+", author_field):
        parts = [part.strip() for part in author.split(",", 1)]
        if len(parts) == 2:
            variants.append(f"{parts[1]} {parts[0]}")
    return " | ".join(variants)


def fail(message: str) -> None:
    raise SystemExit(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def cite_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]+)\}", tex):
        for raw in match.group(1).split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return keys


def split_entries(bib: str) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for match in re.finditer(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,(?P<body>.*?)(?=^}\s*$)", bib, flags=re.DOTALL | re.MULTILINE):
        key = match.group("key").strip()
        body = match.group("body")
        fields: dict[str, str] = {}
        for field_match in re.finditer(r"^\s*([A-Za-z]+)\s*=\s*\{(.*?)\},?\s*$", body, flags=re.MULTILINE):
            fields[field_match.group(1).lower()] = re.sub(r"\s+", " ", field_match.group(2).strip())
        entries[key] = {"type": match.group("type").lower(), "fields": fields}
    return entries


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def contains_identifier(fields: dict[str, str], identifier: str) -> bool:
    blob = " ".join(fields.values())
    return identifier in blob


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    tex = read(PAPER / "main.tex")
    bib = read(PAPER / "references.bib")
    cited = cite_keys(tex)
    entries = split_entries(bib)
    checks: list[dict[str, Any]] = []

    add_check(checks, "bib_entries_parse", len(entries) >= 20, f"entries={len(entries)}")
    add_check(checks, "all_cited_keys_have_entries", not sorted(cited - set(entries)), f"missing={sorted(cited - set(entries))}")
    add_check(checks, "all_bib_entries_are_cited", not sorted(set(entries) - cited), f"uncited={sorted(set(entries) - cited)}")

    duplicate_keys = sorted({key for key in entries if list(entries).count(key) > 1})
    add_check(checks, "no_duplicate_keys", not duplicate_keys, f"duplicates={duplicate_keys}")

    forbidden_hits = [term for term in FORBIDDEN_BIB_TERMS if re.search(re.escape(term), bib, flags=re.IGNORECASE)]
    add_check(checks, "no_placeholder_bib_terms", not forbidden_hits, f"hits={forbidden_hits}")

    missing_required_fields = []
    bad_years = []
    recent_without_identifier = []
    for key, entry in sorted(entries.items()):
        fields = entry["fields"]
        for required in ("title", "author", "year"):
            if required not in fields or not fields[required].strip():
                missing_required_fields.append(f"{key}.{required}")
        try:
            year = int(fields.get("year", "0"))
        except ValueError:
            year = 0
        if year < 1980 or year > CURRENT_YEAR:
            bad_years.append(f"{key}={fields.get('year')!r}")
        if year >= 2023:
            has_identifier = bool(fields.get("doi") or fields.get("eprint") or "arXiv:" in fields.get("journal", "") or "arxiv.org/abs/" in fields.get("url", ""))
            if not has_identifier:
                recent_without_identifier.append(key)
    add_check(checks, "required_fields_present", not missing_required_fields, f"missing={missing_required_fields}")
    add_check(checks, "years_in_range", not bad_years, f"bad_years={bad_years}")
    add_check(checks, "recent_entries_have_primary_identifier", not recent_without_identifier, f"missing={recent_without_identifier}")

    for key, expected in RECENT_PRIMARY_SOURCES.items():
        entry = entries.get(key, {})
        fields = entry.get("fields", {})
        add_check(checks, f"recent_source_exists_{key}", bool(fields), key)
        if not fields:
            continue
        title = fields.get("title", "")
        author = fields.get("author", "")
        add_check(checks, f"recent_source_title_{key}", expected["title"].lower() in title.lower(), title)
        add_check(checks, f"recent_source_arxiv_{key}", contains_identifier(fields, str(expected["arxiv"])), str(expected["arxiv"]))
        add_check(checks, f"recent_source_url_{key}", fields.get("url", "").endswith(str(expected["arxiv"])), fields.get("url", ""))
        if "venue" in expected:
            venue_blob = " ".join(fields.get(name, "") for name in ("journal", "booktitle"))
            add_check(checks, f"recent_source_venue_{key}", str(expected["venue"]).lower() in venue_blob.lower(), venue_blob)
        for required_author in expected.get("must_author", []):
            author_blob = normalized_author_blob(author)
            add_check(checks, f"recent_source_author_{key}_{required_author.replace(' ', '_')}", required_author in author_blob, author)

    for key, expected_doi in DOI_EXPECTATIONS.items():
        entry = entries.get(key, {})
        fields = entry.get("fields", {})
        add_check(checks, f"doi_source_exists_{key}", bool(fields), key)
        if fields:
            add_check(checks, f"doi_matches_{key}", fields.get("doi", "").lower() == expected_doi.lower(), fields.get("doi", ""))

    recent_outreach = {"chen2026costream", "liu2026simpact", "liu2026oat", "wang2024poco", "hou2026worldmodel"}
    missing_recent_outreach = sorted(recent_outreach - cited)
    add_check(checks, "recent_outreach_sources_cited", not missing_recent_outreach, f"missing={missing_recent_outreach}")

    passed = all(check["passed"] for check in checks)
    payload = {
        "version": "reference_integrity_audit_v1",
        "passed": passed,
        "checked_entries": len(entries),
        "cited_keys": sorted(cited),
        "primary_source_expectations": {
            key: {"arxiv": value.get("arxiv"), "title": value.get("title")}
            for key, value in RECENT_PRIMARY_SOURCES.items()
        },
        "doi_expectations": DOI_EXPECTATIONS,
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Reference Integrity Audit",
        "",
        f"Passed: `{str(passed).lower()}`.",
        f"Checked BibTeX entries: `{len(entries)}`.",
        "",
        "This audit checks local bibliography integrity and required primary identifiers. It does not replace human related-work judgment.",
        "",
        "## Recent Primary Sources",
        "",
    ]
    for key, value in RECENT_PRIMARY_SOURCES.items():
        lines.append(f"- `{key}`: arXiv `{value['arxiv']}`, title contains `{value['title']}`")
    lines.extend(["", "## Checks", ""])
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"- `{status}` `{check['name']}`: {check['detail']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Reference integrity audit: {'PASS' if passed else 'FAIL'}; checks={len(checks)}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
