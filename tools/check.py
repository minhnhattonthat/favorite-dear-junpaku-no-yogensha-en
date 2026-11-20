"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

    python -X utf8 tools/check.py

Runs pytest, then tools/lint.py over the merged script/ (codes, widths, page lines, stubs, leftover Japanese,
the keep list, label padding, box budgets). Exit 0 only if both pass. ROM-dependent tests skip when rom/ is
absent; slow emulator tests are marked `slow` and left out here (run them with `pytest -m slow`)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-m", "not slow", str(ROOT / "tests")],
                       cwd=ROOT)
    lint = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "lint.py")], cwd=ROOT)
    sys.exit(r.returncode or lint.returncode)
