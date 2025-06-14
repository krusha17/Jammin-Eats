#!/usr/bin/env python3
"""
Linting Report Generator for Jammin' Eats

This script generates a linting report showing progress over time.
It uses the basic_lint.py script to gather linting data, then stores
and displays results in a user-friendly format.
"""
import datetime
import json
import os
import sys
from pathlib import Path
import importlib.util

# Load the basic linter module
ROOT_DIR = Path(__file__).parent.parent.resolve()
basic_lint_path = ROOT_DIR / "scripts" / "basic_lint.py"
spec = importlib.util.spec_from_file_location("basic_lint", basic_lint_path)
basic_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(basic_lint)

# Define paths
DATA_DIR = ROOT_DIR / "reports"
LINT_DATA_FILE = DATA_DIR / "lint_history.json"
REPORT_FILE = DATA_DIR / "lint_report.md"

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def ensure_directories():
    """Ensure necessary directories exist."""
    DATA_DIR.mkdir(exist_ok=True)


def run_lint():
    """Run the linter and get issue counts by file and type."""
    print(f"{BLUE}Running linter to gather data...{RESET}")

    # Get all Python files
    python_files = basic_lint.find_python_files(ROOT_DIR / "src")

    # Get issues by file and issue type
    issues_by_file = {}
    issues_by_type = {
        "naming": 0,
        "docstring": 0,
        "style": 0,
        "complexity": 0,
        "syntax": 0,
        "encoding": 0,
        "other": 0,
    }

    total_files = len(python_files)
    files_with_issues = 0
    total_issues = 0

    for filepath in python_files:
        rel_path = os.path.relpath(filepath, ROOT_DIR)
        errors = basic_lint.lint_file(filepath)

        if errors:
            files_with_issues += 1
            issues_by_file[rel_path] = len(errors)
            total_issues += len(errors)

            # Count by error type
            for error in errors:
                error_type = error.error_type
                if error_type in issues_by_type:
                    issues_by_type[error_type] += 1
                else:
                    issues_by_type["other"] += 1

    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_files": total_files,
        "files_with_issues": files_with_issues,
        "total_issues": total_issues,
        "issues_by_file": issues_by_file,
        "issues_by_type": issues_by_type,
    }


def load_history():
    """Load linting history from JSON file."""
    if not LINT_DATA_FILE.exists():
        return []

    try:
        with open(LINT_DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_history(history):
    """Save linting history to JSON file."""
    with open(LINT_DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)


def generate_report(history):
    """Generate a markdown report from linting history."""
    if not history:
        print(f"{YELLOW}No history data available to generate report.{RESET}")
        return

    current = history[-1]
    previous = history[-2] if len(history) > 1 else None

    with open(REPORT_FILE, "w") as f:
        # Report header
        f.write("# Jammin' Eats Linting Report\n\n")
        f.write(
            f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        # Current status
        f.write("## Current Status\n\n")
        f.write(f"- Total Files: {current['total_files']}\n")
        f.write(
            f"- Files With Issues: {current['files_with_issues']} ({current['files_with_issues']/current['total_files']*100:.1f}%)\n"
        )
        f.write(f"- Total Issues: {current['total_issues']}\n")
        f.write(
            f"- Average Issues Per File: {current['total_issues']/current['total_files']:.2f}\n\n"
        )

        # Progress tracker
        if previous:
            issue_diff = previous["total_issues"] - current["total_issues"]
            file_diff = previous["files_with_issues"] - current["files_with_issues"]

            f.write("## Progress Since Last Report\n\n")
            f.write(
                f"- Issues Fixed: {issue_diff if issue_diff >= 0 else '⚠️ ' + str(abs(issue_diff)) + ' new issues'}\n"
            )
            f.write(
                f"- Files Improved: {file_diff if file_diff >= 0 else '⚠️ ' + str(abs(file_diff)) + ' more files have issues'}\n\n"
            )

        # Issues by type
        f.write("## Issues by Type\n\n")
        f.write("| Type | Count | Percentage |\n")
        f.write("|------|------:|-----------:|\n")

        for issue_type, count in current["issues_by_type"].items():
            if count > 0:
                percentage = (
                    count / current["total_issues"] * 100
                    if current["total_issues"] > 0
                    else 0
                )
                f.write(
                    f"| {issue_type.capitalize()} | {count} | {percentage:.1f}% |\n"
                )
        f.write("\n")

        # Top 10 files with issues
        f.write("## Top 10 Files With Most Issues\n\n")
        f.write("| File | Issues |\n")
        f.write("|------|-------:|\n")

        sorted_files = sorted(
            current["issues_by_file"].items(), key=lambda x: x[1], reverse=True
        )
        for filepath, issue_count in sorted_files[:10]:
            f.write(f"| {filepath} | {issue_count} |\n")
        f.write("\n")

        # History chart (simplified)
        if len(history) > 1:
            f.write("## Historical Trend\n\n")
            f.write("| Date | Total Issues | Files With Issues |\n")
            f.write("|------|-------------:|------------------:|\n")

            # Show up to the last 5 records
            for record in history[-5:]:
                date = datetime.datetime.fromisoformat(record["timestamp"]).strftime(
                    "%Y-%m-%d"
                )
                f.write(
                    f"| {date} | {record['total_issues']} | {record['files_with_issues']} |\n"
                )

        f.write("\n## What to Focus On Next\n\n")

        # Give recommendations based on current stats
        issue_types = current["issues_by_type"]
        if issue_types["docstring"] > 0:
            f.write(
                "- **Add missing docstrings**: Documentation is key to maintainable code\n"
            )
        if issue_types["naming"] > 0:
            f.write(
                "- **Fix naming convention issues**: Follow the naming conventions guide\n"
            )
        if issue_types["style"] > 0:
            f.write("- **Address style issues**: Focus on line length and formatting\n")
        if issue_types["complexity"] > 0:
            f.write("- **Reduce complexity**: Break down large files and functions\n")

    print(f"{GREEN}Report generated at {REPORT_FILE}{RESET}")


def main():
    """Run the report generator."""
    ensure_directories()

    # Load existing data
    history = load_history()

    # Run linter and get new data
    print("Gathering linting data...")
    current_data = run_lint()

    # Add to history and save
    history.append(current_data)
    save_history(history)

    # Generate the report
    generate_report(history)

    # Show summary
    print(f"{BLUE}Summary:{RESET}")
    print(f"- Total files analyzed: {current_data['total_files']}")
    print(f"- Files with issues: {current_data['files_with_issues']}")
    print(f"- Total issues: {current_data['total_issues']}")

    if len(history) > 1:
        previous = history[-2]
        issue_diff = previous["total_issues"] - current_data["total_issues"]
        if issue_diff > 0:
            print(
                f"{GREEN}You've fixed {issue_diff} issues since the last report!{RESET}"
            )
        elif issue_diff < 0:
            print(
                f"{YELLOW}There are {abs(issue_diff)} new issues since the last report.{RESET}"
            )
        else:
            print(f"{YELLOW}No change in issue count since last report.{RESET}")

    print(f"\nFull report available at: {REPORT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
