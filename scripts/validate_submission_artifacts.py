import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOWNLOADS_PDF = Path("C:/Users/wangz/Downloads/119.pdf")
DESKTOP_PDF = Path("C:/Users/wangz/Desktop/119.pdf")
ROOT_PDF = ROOT.parent / "119.pdf"
CHILD_PDF = ROOT / "119.pdf"


def fail(message):
    raise SystemExit(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_pages(path):
    try:
        proc = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    except Exception as exc:
        fail(f"pdfinfo failed for {path}: {exc}")
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    fail("pdfinfo did not report page count")


def count_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def numeric_finiteness(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row_idx, row in enumerate(reader, start=2):
            for key, value in row.items():
                if value is None or value == "":
                    continue
                try:
                    number = float(value)
                except ValueError:
                    continue
                if not math.isfinite(number):
                    fail(f"non-finite numeric value in {path} row {row_idx} column {key}")


def main():
    summary_path = RESULTS / "summary.json"
    if not summary_path.exists():
        fail("missing results/summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("version") != "v5_expanded":
        fail("summary version is not v5_expanded")
    if summary.get("terminal_decision") != "STRONG_REVISE":
        fail("terminal decision must be STRONG_REVISE")
    if summary.get("iclr_main_ready") is not False:
        fail("ICLR main readiness must be false")
    if summary.get("scope_gate_pass") is not False:
        fail("scope gate must remain false")
    if summary.get("local_gates_pass") is not True:
        fail("local gates did not pass")
    failed = [name for name, ok in summary["gates"].items() if not ok]
    if failed:
        fail(f"failed gates: {failed}")

    expected_files = {
        "dataset_summary": RESULTS / "dataset_summary.csv",
        "main_cell": RESULTS / "cell_metrics.csv",
        "main_group": RESULTS / "main_group_metrics.csv",
        "seed_metric": RESULTS / "seed_metrics.csv",
        "metric": RESULTS / "metrics.csv",
        "hard_seed": RESULTS / "hard_seed_metrics.csv",
        "hard_metric": RESULTS / "hard_aggregate_metrics.csv",
        "hard_pairwise": RESULTS / "hard_pairwise_stats.csv",
        "ablation_cell": RESULTS / "ablation_cell_metrics.csv",
        "ablation_seed": RESULTS / "ablation_seed_metrics.csv",
        "ablation_metric": RESULTS / "ablation_metrics.csv",
        "stress_cell": RESULTS / "stress_sweep_cell_metrics.csv",
        "stress_seed": RESULTS / "stress_sweep_seed_metrics.csv",
        "stress_metric": RESULTS / "stress_sweep.csv",
        "fixed_risk_cell": RESULTS / "fixed_risk_cell_metrics.csv",
        "fixed_risk_seed": RESULTS / "fixed_risk_seed_metrics.csv",
        "fixed_risk_metric": RESULTS / "fixed_risk_metrics.csv",
        "fixed_risk_pairwise": RESULTS / "fixed_risk_pairwise_stats.csv",
        "failure_cases": RESULTS / "failure_cases.csv",
    }
    for key, path in expected_files.items():
        if not path.exists():
            fail(f"missing expected CSV: {path}")
        actual = count_rows(path)
        expected = int(summary["row_counts"][key])
        if actual != expected:
            fail(f"row-count mismatch for {key}: {actual} != {expected}")

    for path in expected_files.values():
        numeric_finiteness(path)

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    if "citebordercolor={0 1 0}" not in tex:
        fail("bright boxed citation configuration missing")
    if "STRONG\\_REVISE" not in tex:
        fail("manuscript does not state STRONG_REVISE")
    if "not ICLR-main ready" not in tex:
        fail("manuscript does not state ICLR-main readiness boundary")
    if "\\bibliography{references}" not in tex:
        fail("bibliography missing")

    if not DOWNLOADS_PDF.exists():
        fail(f"missing canonical PDF: {DOWNLOADS_PDF}")
    if DESKTOP_PDF.exists():
        fail(f"desktop PDF must not exist: {DESKTOP_PDF}")
    if ROOT_PDF.exists():
        fail(f"root numbered PDF must not exist: {ROOT_PDF}")
    if CHILD_PDF.exists():
        fail(f"child numbered PDF must not exist: {CHILD_PDF}")
    pages = pdf_pages(DOWNLOADS_PDF)
    if pages < 25:
        fail(f"PDF has only {pages} pages; expected at least 25")

    digest = sha256(DOWNLOADS_PDF)
    print(f"Paper 119 validation passed. SHA256={digest} pages={pages}")


if __name__ == "__main__":
    main()
