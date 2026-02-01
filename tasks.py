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
        [PYTHON, "-m", "pip_audit", "--skip-editable"],
    ],
    "audit": [[PYTHON, "-m", "pip_audit", "--skip-editable"]],
    "icons": [[PYTHON, "scripts/convert_icon.py"]],
    "build": [
        [
            PYTHON,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",
            "--name",
            "postlette",
            "--icon",
            "docs/images/logo-dark-navy.ico",
            "main.py",
        ]
    ],
    "docs-serve": [[PYTHON, "-m", "mkdocs", "serve"]],
    "docs-build": [[PYTHON, "-m", "mkdocs", "build", "--strict"]],
    "run": [[PYTHON, "main.py"]],
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        available = ", ".join(TASKS)
        print(f"Usage: python tasks.py <{available}>")
        sys.exit(1)

    task = sys.argv[1]
    if task == "icons":
        if len(sys.argv) < 4:
            print(
                "Usage: python tasks.py icons <svg_path> <background> "
                "[--output-dir DIR] [--base-name NAME]"
            )
            sys.exit(2)
        cmd = TASKS[task][0] + sys.argv[2:]
        result = subprocess.run(cmd, cwd=ROOT)
        sys.exit(result.returncode)
    for cmd in TASKS[task]:
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
