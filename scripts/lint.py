#!/usr/bin/env python3
"""
Lint runner script for Jammin' Eats.

This script runs all configured linters on the project codebase.
"""

import subprocess
import sys
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.resolve()


def run_command(command, description):
    """Run a shell command and print its output."""
    print(f"\n\033[1;34m=== {description} ===\033[0m")
    result = subprocess.run(command, shell=True, cwd=ROOT_DIR)
    return result.returncode == 0


def main():
    """Run all linting tools."""
    success = True

    # Run Ruff for fast linting
    if not run_command("python -m ruff check src tests", "Running Ruff linter"):
        success = False

    # Run Pylint for more detailed linting
    if not run_command("python -m pylint src", "Running PyLint"):
        success = False

    # Run MyPy for type checking
    if not run_command("python -m mypy src", "Running Type Checking"):
        success = False

    if success:
        print("\n\033[1;32m✓ All linting checks passed! ✓\033[0m")
        return 0
    else:
        print("\n\033[1;31m✗ Linting found issues that need to be fixed! ✗\033[0m")
        return 1


if __name__ == "__main__":
    sys.exit(main())
