#!/usr/bin/env python
"""
Jammin' Eats Checklist Validator

Parses pytest XML results and updates the Core System Validation Checklist
with appropriate status markers (✅/❌) based on test results.

Usage: python tools/checklist_validator.py CORE_SYSTEM_VALIDATION_CHECKLIST.md pytest-results.xml
"""

import sys
import re
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Status markers
PASS_MARKER = "✅"
FAIL_MARKER = "❌"
PENDING_MARKER = "⏳"

# Regular expression to find test IDs in the checklist markdown
ID_PATTERN = re.compile(r"\| (\w+-\d+) \| .* \|")

# Regular expression to find test case IDs in pytest names
# Example: test_db_init[ENV-01] or test_tutorial_goals[TG-03]
TEST_ID_PATTERN = re.compile(r"test_[\w_]+\[(\w+-\d+)\]")


def parse_pytest_results(xml_file):
    """
    Parse pytest results XML file and extract test IDs and their pass/fail status.

    Args:
        xml_file: Path to pytest XML results file

    Returns:
        dict: Mapping of test IDs to their status (True for pass, False for fail)
    """
    if not os.path.exists(xml_file):
        print(f"Warning: {xml_file} not found. No test results to process.")
        return {}

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        results = {}

        for testcase in root.findall(".//testcase"):
            name = testcase.get("name")

            # Extract test ID from test name if available
            match = TEST_ID_PATTERN.search(name)
            if match:
                test_id = match.group(1)
                # Check if test passed (no failure or error elements)
                passed = (
                    len(testcase.findall("./failure")) == 0
                    and len(testcase.findall("./error")) == 0
                )
                results[test_id] = passed

        return results
    except Exception as e:
        print(f"Error parsing pytest results: {e}")
        return {}


def update_checklist(checklist_file, test_results):
    """
    Update the checklist markdown file with test results.

    Args:
        checklist_file: Path to the checklist markdown file
        test_results: Dict of test IDs and their status

    Returns:
        bool: True if checklist was updated, False otherwise
    """
    if not os.path.exists(checklist_file):
        print(f"Error: {checklist_file} not found")
        return False

    try:
        with open(checklist_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        updated_lines = []

        for line in lines:
            # Check if line contains a test ID
            match = ID_PATTERN.search(line)
            if match:
                test_id = match.group(1)
                # Check if we have a test result for this ID
                if test_id in test_results:
                    # Update status based on test result
                    status = PASS_MARKER if test_results[test_id] else FAIL_MARKER
                    # Replace any existing status marker or add new one
                    if (
                        PASS_MARKER in line
                        or FAIL_MARKER in line
                        or PENDING_MARKER in line
                    ):
                        line = re.sub(
                            r"\| (\w+-\d+) \|", f"| {test_id} {status} |", line
                        )
                    else:
                        line = line.replace(f"| {test_id} |", f"| {test_id} {status} |")
                    updated = True

            updated_lines.append(line)

        # Add timestamp to show when checklist was last updated
        for i, line in enumerate(updated_lines):
            if "**Status:**" in line:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                if "Last updated:" in line:
                    updated_lines[i] = re.sub(
                        r"Last updated: .*\*\*", f"Last updated: {timestamp}**", line
                    )
                else:
                    updated_lines[i] = line.replace(
                        "**Status:**", f"**Status:** Last updated: {timestamp}**"
                    )
                updated = True
                break

        if updated:
            with open(checklist_file, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)
            print(f"Updated {checklist_file} with test results")
            return True
        else:
            print(f"No updates needed for {checklist_file}")
            return False

    except Exception as e:
        print(f"Error updating checklist: {e}")
        return False


def update_readme_badge(test_results):
    """
    Update the README.md with a status badge.

    Args:
        test_results: Dict of test IDs and their status
    """
    readme_file = "README.md"
    if not os.path.exists(readme_file):
        print(f"Warning: {readme_file} not found. Skipping badge update.")
        return

    try:
        # Calculate pass percentage
        if test_results:
            passed = sum(1 for status in test_results.values() if status)
            total = len(test_results)
            percentage = int((passed / total) * 100) if total > 0 else 0
            color = (
                "brightgreen"
                if percentage >= 90
                else "yellow"
                if percentage >= 70
                else "red"
            )

            # Badge markdown
            badge = f"![Checklist Status](https://img.shields.io/badge/checklist-{percentage}%25-{color})"

            with open(readme_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Update or add badge
            if "![Checklist Status](" in content:
                content = re.sub(r"!\[Checklist Status\]\(.*\)", badge, content)
            else:
                # Add after title
                content = re.sub(
                    r"^(# .*)$", f"\\1\n\n{badge}", content, count=1, flags=re.MULTILINE
                )

            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Updated {readme_file} with checklist badge ({percentage}%)")
    except Exception as e:
        print(f"Error updating README badge: {e}")


def main():
    """
    Main entry point for the script.
    """
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} CHECKLIST_FILE PYTEST_RESULTS_XML")
        sys.exit(1)

    checklist_file = sys.argv[1]
    pytest_results_xml = sys.argv[2]

    # Parse test results
    test_results = parse_pytest_results(pytest_results_xml)
    print(f"Found {len(test_results)} test results in {pytest_results_xml}")

    # Update checklist
    updated = update_checklist(checklist_file, test_results)

    # Update README badge
    if test_results:
        update_readme_badge(test_results)

    sys.exit(0 if updated or not test_results else 1)


if __name__ == "__main__":
    main()
