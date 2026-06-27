from __future__ import annotations

import tempfile
from pathlib import Path

from audit_external_evidence import is_scaffold_implementation


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = "external_validation/baselines/barrier_certified_energy_composer_v5"
SCAFFOLD_FILE = f"{SCAFFOLD_DIR}/adapter_template.py"


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> int:
    if not is_scaffold_implementation(SCAFFOLD_DIR):
        fail(f"scaffold directory was not detected as scaffold-only: {SCAFFOLD_DIR}")
    if not is_scaffold_implementation(SCAFFOLD_FILE):
        fail(f"scaffold adapter was not detected as scaffold-only: {SCAFFOLD_FILE}")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8", dir=ROOT) as handle:
        handle.write("def initialize(config):\n    return {}\n")
        temp_path = Path(handle.name)
    try:
        rel = temp_path.relative_to(ROOT).as_posix()
        if is_scaffold_implementation(rel):
            fail(f"ordinary adapter file was incorrectly detected as scaffold-only: {rel}")
    finally:
        temp_path.unlink(missing_ok=True)

    print("External adapter scaffold guard self-test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
