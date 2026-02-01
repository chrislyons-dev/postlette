"""Task runner for Postlette. Usage: python tasks.py <command>"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")

TASKS: dict[str, list[str]] = {
    "test": [PYTHON, "-m", "pytest", "tests/", "-v"],
    "lint": [PYTHON, "-m", "ruff", "check", "."],
    "fix": [PYTHON, "-m", "ruff", "check", "--fix", "."],
    "run": [PYTHON, "main.py"],
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        available = ", ".join(TASKS)
        print(f"Usage: python tasks.py <{available}>")
        sys.exit(1)

    task = sys.argv[1]
    result = subprocess.run(TASKS[task], cwd=ROOT)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
