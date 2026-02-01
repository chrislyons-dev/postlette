"""Task runner for Postlette. Usage: python tasks.py <command>"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")

TASKS: dict[str, list[list[str]]] = {
    "test": [[PYTHON, "-m", "pytest", "tests/", "-v"]],
    "lint": [[PYTHON, "-m", "ruff", "check", "."]],
    "format": [[PYTHON, "-m", "ruff", "format", "."]],
    "format-check": [[PYTHON, "-m", "ruff", "format", "--check", "."]],
    "fix": [
        [PYTHON, "-m", "ruff", "check", "--fix", "."],
        [PYTHON, "-m", "ruff", "format", "."],
    ],
    "check": [
        [PYTHON, "-m", "ruff", "format", "."],
        [PYTHON, "-m", "ruff", "check", "--fix", "."],
        [PYTHON, "-m", "pytest", "tests/", "-v"],
        [PYTHON, "-m", "pip_audit"],
    ],
    "audit": [[PYTHON, "-m", "pip_audit"]],
    "run": [[PYTHON, "main.py"]],
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        available = ", ".join(TASKS)
        print(f"Usage: python tasks.py <{available}>")
        sys.exit(1)

    task = sys.argv[1]
    for cmd in TASKS[task]:
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
