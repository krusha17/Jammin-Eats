# Jammin' Eats CI/CD Guide

## Overview

This document explains the Continuous Integration (CI) and quality assurance setup for Jammin' Eats. As a professional game development project, we use automated testing and quality checks to maintain code quality and prevent regressions.

## Pre-commit Hook System

Jammin' Eats uses **pre-commit hooks** for immediate code quality validation. This ensures that all code changes meet quality standards before they're even committed to the repository.

### Automated Quality Checks

Every time you commit code (both CLI and GUI), the following tools run automatically:

1. **Ruff**: Fast Python linter for code style and error detection
2. **Black**: Code formatter for consistent styling
3. **Pylint**: Static analysis for code quality metrics
4. **MyPy**: Type checking for better code reliability

### Configuration Files

- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `mypy.ini`: Type checking settings
- `.pylintrc`: Static analysis rules and disabled checks
- `pyproject.toml`: Project configuration and tool settings

## Development Workflow

### Setting Up Pre-commit Hooks

When setting up the development environment:

```bash
# Install pre-commit hooks after cloning
pre-commit install

# Run hooks on all files (optional, for initial setup)
pre-commit run --all-files
```

### Daily Development

1. **Make Code Changes**: Edit files as normal
2. **Stage Changes**: `git add .` or use GUI
3. **Commit**: `git commit -m "Your message"` or use GUI
4. **Automatic Validation**: Pre-commit hooks run automatically
5. **Fix Issues**: If hooks fail, fix issues and commit again

### What Happens on Commit

When you commit code, the system:

1. **Runs Ruff**: Checks for linting errors and code style issues
2. **Runs Black**: Automatically formats code if needed
3. **Runs Pylint**: Performs static analysis
4. **Runs MyPy**: Validates type annotations
5. **Blocks Commit**: If any check fails, commit is prevented
6. **Shows Errors**: Displays specific issues to fix

## Testing Framework

### Running Tests Locally

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_dal.py

# Debug mode for game testing
python debug_main.py
```

### Test Structure

```
tests/
├── unit/           # Unit tests for individual modules
├── integration/    # Integration tests for module interactions
└── fixtures/       # Test data and mock objects
```

### Key Test Areas

- **Database Layer**: DAL operations and schema validation
- **State Machine**: Game state transitions and logic
- **Tutorial System**: Completion tracking and persistence
- **Asset Loading**: Fallback systems and error handling
- **UI Components**: Menu interactions and state management

## Code Quality Standards

### Linting Rules (Ruff)

- **E402**: Module imports must be at top of file (suppressed in tests with `# noqa: E402`)
- **F401**: No unused imports
- **F841**: No unused variables
- **Line Length**: Maximum 88 characters (Black standard)

### Type Checking (MyPy)

- **Ignore Missing Imports**: External libraries without stubs are ignored
- **Explicit Package Bases**: Prevents "source file found twice" errors
- **Exclude Patterns**: Tests and debug modules are excluded from strict checking

### Static Analysis (Pylint)

Selected checks disabled for game development:
- **C0114**: Missing module docstring (where appropriate)
- **C0115**: Missing class docstring (where appropriate)
- **R0903**: Too few public methods (common in game entities)
- **W0613**: Unused argument (common in event handlers)

## Error Handling and Fallbacks

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. **Read the Error Messages**: They show exactly what needs fixing
2. **Fix Issues**: Address linting, formatting, or type errors
3. **Commit Again**: Hooks will re-run automatically
4. **Contact Team**: If stuck, check with other developers

### Common Issues and Solutions

#### Import Order (E402)
```python
# Wrong - imports after code
sys.path.append("../src")
import game  # E402 error

# Right - imports at top, or use noqa
sys.path.append("../src")
import game  # noqa: E402
```

#### Unused Imports (F401)
```python
# Wrong - imported but not used
import unused_module  # F401 error

# Right - remove unused imports
# import unused_module  # Removed
```

#### Type Annotations
```python
# Add type hints for better MyPy compliance
def process_customer(customer: Customer) -> bool:
    return customer.is_satisfied()
```

## Performance and Optimization

### Pre-commit Hook Performance

- **Fast Execution**: Hooks typically run in 2-5 seconds
- **Incremental Checking**: Only changed files are checked
- **Parallel Processing**: Multiple tools run simultaneously when possible

### Best Practices

1. **Commit Early and Often**: Smaller commits are easier to validate
2. **Fix Issues Immediately**: Don't let quality debt accumulate
3. **Use IDE Integration**: Many editors can run these tools continuously
4. **Review Hook Output**: Understanding errors helps prevent future issues

## Troubleshooting

### Common Setup Issues

**Git Hooks Not Running**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

**Python Environment Issues**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

**Permission Issues on Windows**
- Ensure Git for Windows includes Unix shell tools
- Add Git's `usr/bin` directory to PATH
- Use Git Bash or PowerShell with administrator privileges if needed

### Getting Help

1. **Check Console Output**: Error messages are usually very specific
2. **Review Documentation**: This guide and tool-specific docs
3. **Test Locally**: Run `pre-commit run --all-files` to test all files
4. **Ask Team**: Don't hesitate to ask for help with complex issues

---

> **Note**: This CI/CD setup ensures professional code quality standards while maintaining rapid development velocity. All team members benefit from consistent, high-quality code that's automatically validated before integration.
