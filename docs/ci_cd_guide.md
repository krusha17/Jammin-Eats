# Jammin' Eats CI/CD Guide

## Overview

This document explains the Continuous Integration (CI) and Continuous Deployment (CD) setup for Jammin' Eats. As a professional game development project, we use automated testing and quality checks to maintain code quality and prevent regressions.

## Workflow Structure

Jammin' Eats uses GitHub Actions for CI/CD. There are two main workflow files:

1. **`docs.yml`**: Handles documentation updates and checklist validation
2. **`tests.yml`**: Runs comprehensive testing, linting, type checking, and security audits

## What Gets Tested and When

### On Every Push and Pull Request

Whenever code is pushed to `main`, `dev`, or any `feature/*` branch, or when a pull request is created targeting `main` or `dev`, the following checks run automatically:

- **Unit Tests**: Tests for individual modules (DAL, state machine, etc.)
- **Integration Tests**: Tests for interactions between modules
- **Linting**: Code style and formatting checks using `ruff`
- **Type Checking**: Static type analysis using `mypy`
- **Security Audit**: Vulnerability scans using `pip-audit`
- **Code Coverage**: Measure of how much code is covered by tests
- **Checklist Validation**: Ensures the `CORE_SYSTEM_VALIDATION_CHECKLIST.md` is up-to-date

## Understanding Test Results

### Dashboard View

On GitHub, navigate to the "Actions" tab to see all workflow runs. Each run will be marked with:
- ✅ Green check: All tests passed
- ❌ Red X: One or more tests failed

### Detailed Test Results

Click on any workflow run to see detailed results:

1. **Test Output**: Shows exactly which tests passed or failed
2. **Coverage Report**: Available as a downloadable artifact
3. **Lint and Type Errors**: Listed in their respective steps

## Running Tests Locally

Before pushing code, you should run tests locally:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/unit/test_dal.py

# Run with coverage
python -m pytest --cov=src tests/

# Run linting
ruff check src tests

# Run type checking
mypy src
```

## Workflow Configuration

### Modifying the Workflows

The workflow files are located in `.github/workflows/`. To modify them:

1. Edit the YAML files
2. Commit and push changes
3. The updated workflow will be used for subsequent runs

### Current Settings

- **Python Version**: 3.13
- **Test Framework**: pytest
- **Coverage Tool**: pytest-cov
- **Linter**: ruff
- **Type Checker**: mypy
- **Security Scanner**: pip-audit

## Troubleshooting Common Issues

### Failed Tests

If tests fail in CI but pass locally:
- Check for environment-specific code
- Verify dependencies match between CI and local environments
- Look for path-related issues

### Slow Builds

If workflows are taking too long:
- Consider running only unit tests on feature branches
- Cache dependencies and test results
- Split workflow into parallel jobs

## Best Practices

1. **Never Disable Tests**: If a test is failing, fix the code, not the test
2. **Maintain High Coverage**: Aim for at least 80% code coverage
3. **Write Regression Tests**: When fixing bugs, add a test to prevent recurrence
4. **Keep CI Fast**: Optimize workflows to run quickly
5. **Pay Attention to Warnings**: Address lint and type warnings, even when they don't fail the build

## Next Steps for CI/CD Improvement

1. Add performance benchmarking tests
2. Set up automatic deployment to game distribution platforms
3. Implement pre-commit hooks for local checks before pushing
4. Add visual testing for UI/UX components

---

By following these CI/CD practices, Jammin' Eats maintains professional game development standards, ensuring code quality and stability throughout the development lifecycle.
