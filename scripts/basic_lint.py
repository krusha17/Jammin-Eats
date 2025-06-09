#!/usr/bin/env python3
"""
Basic linting script for Jammin' Eats that uses Python's built-in tools.

This script provides basic linting capabilities without requiring external packages.
"""
import ast
import os
import re
import sys
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.resolve()
SRC_DIR = ROOT_DIR / "src"

# ANSI color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Naming conventions based on your style guide
FILE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*\.py$')
CLASS_NAME_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
FUNCTION_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
VARIABLE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')
CONSTANT_NAME_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')

class LintingError:
    """Represents a linting error."""
    
    def __init__(self, filename, line, col, message, error_type="style"):
        self.filename = filename
        self.line = line
        self.col = col
        self.message = message
        self.error_type = error_type
    
    def __str__(self):
        return f"{self.filename}:{self.line}:{self.col}: {self.error_type}: {self.message}"

class BasicLinter(ast.NodeVisitor):
    """Basic linter using Python's AST module."""
    
    def __init__(self, filename):
        self.filename = filename
        self.errors = []
    
    def visit_ClassDef(self, node):
        # Check class naming convention
        if not CLASS_NAME_PATTERN.match(node.name):
            self.errors.append(LintingError(
                self.filename, node.lineno, node.col_offset,
                f"Class name '{node.name}' doesn't follow PascalCase convention",
                "naming"
            ))
        # Visit children
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # Check function naming convention
        if not FUNCTION_NAME_PATTERN.match(node.name) and not node.name.startswith('__'):
            self.errors.append(LintingError(
                self.filename, node.lineno, node.col_offset,
                f"Function name '{node.name}' doesn't follow snake_case convention",
                "naming"
            ))
        
        # Check function docstring
        if (not ast.get_docstring(node) and 
            not node.name.startswith('__') and 
            not (len(node.body) == 1 and isinstance(node.body[0], ast.Pass))):
            self.errors.append(LintingError(
                self.filename, node.lineno, node.col_offset,
                f"Missing docstring for function '{node.name}'",
                "docstring"
            ))
        
        # Check function length
        if len(node.body) > 50:  # Approximate size measure
            self.errors.append(LintingError(
                self.filename, node.lineno, node.col_offset,
                f"Function '{node.name}' is too long ({len(node.body)} statements)",
                "complexity"
            ))
        
        # Visit children
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        # Check variable naming convention for module-level constants
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper() and not CONSTANT_NAME_PATTERN.match(target.id):
                self.errors.append(LintingError(
                    self.filename, target.lineno, target.col_offset,
                    f"Constant name '{target.id}' doesn't follow ALL_CAPS convention",
                    "naming"
                ))
        self.generic_visit(node)
    
    def visit_Name(self, node):
        # Check variable naming convention for local variables (very basic)
        if isinstance(node.ctx, ast.Store) and not node.id.startswith('_'):
            if node.id.isupper() and not CONSTANT_NAME_PATTERN.match(node.id):
                self.errors.append(LintingError(
                    self.filename, node.lineno, node.col_offset,
                    f"ALL_CAPS name '{node.id}' should be used only for constants",
                    "naming"
                ))
        self.generic_visit(node)

def lint_file(filepath):
    """Lint a single Python file."""
    errors = []
    
    # Check file naming convention
    filename = os.path.basename(filepath)
    if not FILE_NAME_PATTERN.match(filename):
        errors.append(LintingError(
            filepath, 0, 0,
            f"File name '{filename}' doesn't follow snake_case convention",
            "naming"
        ))
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except UnicodeDecodeError:
        errors.append(LintingError(
            filepath, 0, 0,
            "File has encoding issues - ensure it's UTF-8 encoded",
            "encoding"
        ))
        return errors
    
    # Check for large files
    if len(lines) > 500:
        errors.append(LintingError(
            filepath, 0, 0,
            f"File is too large ({len(lines)} lines) - consider splitting it",
            "complexity"
        ))
    
    # Check line length
    for i, line in enumerate(lines):
        if len(line) > 100:
            errors.append(LintingError(
                filepath, i+1, len(line),
                f"Line too long ({len(line)} > 100 characters)",
                "style"
            ))
    
    # Check module docstring
    if not content.lstrip().startswith('"""') and not content.lstrip().startswith("'''"):
        errors.append(LintingError(
            filepath, 1, 0,
            "Missing module docstring",
            "docstring"
        ))
    
    # Parse and check AST
    try:
        tree = ast.parse(content)
        linter = BasicLinter(filepath)
        linter.visit(tree)
        errors.extend(linter.errors)
    except SyntaxError as e:
        errors.append(LintingError(
            filepath, e.lineno, e.offset,
            f"Syntax error: {e}",
            "syntax"
        ))
    
    return errors

def find_python_files(directory):
    """Recursively find all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}=== {text} ==={RESET}")

def main():
    """Run the linter on all Python files in src directory."""
    print_header("Running Basic Linter")
    
    python_files = find_python_files(SRC_DIR)
    if not python_files:
        print(f"{YELLOW}No Python files found in {SRC_DIR}{RESET}")
        return 0
    
    all_errors = []
    file_count = 0
    
    for filepath in python_files:
        file_count += 1
        rel_path = os.path.relpath(filepath, ROOT_DIR)
        errors = lint_file(filepath)
        if errors:
            all_errors.extend(errors)
            print(f"{YELLOW}Found {len(errors)} issues in {rel_path}{RESET}")
    
    # Print summary
    if all_errors:
        print(f"\n{RED}✗ Found {len(all_errors)} issues in {file_count} files{RESET}")
        # Group by file
        errors_by_file = {}
        for error in all_errors:
            if error.filename not in errors_by_file:
                errors_by_file[error.filename] = []
            errors_by_file[error.filename].append(error)
        
        # Print top issues (limit to avoid overwhelming output)
        issue_limit = 20
        issues_shown = 0
        print(f"\n{YELLOW}Top issues:{RESET}")
        for filename, errors in errors_by_file.items():
            rel_path = os.path.relpath(filename, ROOT_DIR)
            print(f"\n{BLUE}{rel_path}:{RESET}")
            for error in errors[:5]:  # Show at most 5 issues per file
                print(f"  Line {error.line}: {error.message}")
                issues_shown += 1
                if issues_shown >= issue_limit:
                    break
            if issues_shown >= issue_limit:
                remaining = len(all_errors) - issue_limit
                if remaining > 0:
                    print(f"\n{YELLOW}...and {remaining} more issues not shown{RESET}")
                break
        
        return 1
    else:
        print(f"\n{GREEN}✓ No issues found in {file_count} files{RESET}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
