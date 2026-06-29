from pathlib import Path
import subprocess


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

    print("Outreach artifact validation passed: one-page memo=1 page, four-page preview=4 pages.")


if __name__ == "__main__":
    main()
