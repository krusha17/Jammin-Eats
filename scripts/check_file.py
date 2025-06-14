#!/usr/bin/env python3
"""
File-specific linting check for Jammin' Eats.

Checks a single file for linting issues and shows detailed output.
"""
import os
import sys
from pathlib import Path

# Import our basic linting functions
sys.path.append(str(Path(__file__).parent.resolve()))
from basic_lint import lint_file  # noqa: E402

# ANSI color codes for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def main():
    """Check a specific file for linting issues."""
    if len(sys.argv) < 2:
        print(f"{RED}Error: Please provide a file path to check.{RESET}")
        print(f"Usage: python {sys.argv[0]} <file_path>")
        return 1

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"{RED}Error: File not found: {filepath}{RESET}")
        return 1

    print(f"{BLUE}=== Checking {filepath} for linting issues ==={RESET}")

    errors = lint_file(filepath)

    if errors:
        print(f"\n{RED}Found {len(errors)} issues:{RESET}")

        # Group errors by type
        errors_by_type = {}
        for error in errors:
            if error.error_type not in errors_by_type:
                errors_by_type[error.error_type] = []
            errors_by_type[error.error_type].append(error)

        # Print errors by type
        for error_type, type_errors in errors_by_type.items():
            print(f"\n{YELLOW}{error_type.upper()} ISSUES:{RESET}")
            for error in sorted(type_errors, key=lambda e: e.line):
                print(f"  Line {error.line}: {error.message}")

        return 1
    else:
        print(f"\n{GREEN}✓ No issues found!{RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
