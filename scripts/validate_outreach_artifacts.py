from pathlib import Path
import subprocess
import json


ROOT = Path(__file__).resolve().parents[1]
OUTREACH = ROOT / "outreach"
EXPECTED = {
    "paper119_one_page_memo.pdf": 1,
    "paper119_four_page_preview.pdf": 4,
}


def fail(message: str) -> None:
    raise SystemExit(message)


def pdf_pages(path: Path) -> int:
    try:
        proc = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    except Exception as exc:
        fail(f"pdfinfo failed for {path}: {exc}")
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    fail(f"pdfinfo did not report page count for {path}")


def main() -> None:
    for name, expected_pages in EXPECTED.items():
        path = OUTREACH / name
        if not path.exists():
            fail(f"missing outreach PDF: {path}")
        pages = pdf_pages(path)
        if pages != expected_pages:
            fail(f"{path.name} has {pages} pages; expected {expected_pages}")

    for name in ("paper119_one_page_memo.tex", "paper119_four_page_preview.tex"):
        text = (OUTREACH / name).read_text(encoding="utf-8")
        bad = sorted({char for char in text if ord(char) > 127})
        if bad:
            fail(f"{name} contains non-ASCII characters: {bad}")
        for forbidden in ("please do the real validation", "get to Yilun", "already main-conference ready"):
            if forbidden in text:
                fail(f"{name} contains forbidden outreach framing: {forbidden}")
        for required in ("diagnostic audit", "planner-edge updates", "failure-memory adaptation audit", "operator packet"):
            if required not in text:
                fail(f"{name} missing required mechanism-audit framing: {required}")

    package = ROOT / "docs" / "haonan_yilun_outreach_package.md"
    if not package.exists():
        fail(f"missing outreach package: {package}")
    package_text = package.read_text(encoding="utf-8")
    for required in (
        "diagnostic labels, seam decisions, and planner-edge updates",
        "failure-memory adaptation audit",
        "Do not pitch this as",
        "results/external_operator_packet.md",
        "do not frame Haonan as responsible for supplying the missing proof",
    ):
        if required not in package_text:
            fail(f"haonan/yilun outreach package missing required framing: {required}")

    send_ready = ROOT / "docs" / "haonan_yilun_send_ready_outreach.md"
    send_ready_audit = ROOT / "results" / "haonan_yilun_send_ready_outreach_audit.json"
    if not send_ready.exists():
        fail(f"missing send-ready outreach packet: {send_ready}")
    if not send_ready_audit.exists():
        fail(f"missing send-ready outreach audit: {send_ready_audit}")
    payload = json.loads(send_ready_audit.read_text(encoding="utf-8"))
    if payload.get("version") != "haonan_yilun_send_ready_outreach_v1":
        fail("send-ready outreach audit version mismatch")
    if payload.get("passed") is not True:
        fail("send-ready outreach audit did not pass")
    if payload.get("not_external_evidence") is not True:
        fail("send-ready outreach audit must remain non-evidence")
    if int(payload.get("first_email_word_count", 999) or 999) > 190:
        fail("send-ready first email is too long")
    if payload.get("primary_first_email_anchor") != "CoStream" or payload.get("secondary_first_email_anchor") != "none":
        fail("send-ready first email must use only CoStream as the paper anchor")
    checks = {check.get("name"): check.get("passed") for check in payload.get("checks", [])}
    for required in (
        "first_email_concise",
        "first_email_uses_one_primary_anchor",
        "first_contact_forbidden_phrases_absent",
        "haonan_not_proof_supplier",
        "yilun_access_motive_absent",
    ):
        if checks.get(required) is not True:
            fail(f"send-ready outreach audit missing passing check: {required}")

    print("Outreach artifact validation passed: one-page memo=1 page, four-page preview=4 pages.")


if __name__ == "__main__":
    main()
