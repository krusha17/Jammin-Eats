# Tutorial Graduation System Test Plan

## Overview

This test plan outlines the testing approach for the Jammin' Eats Tutorial Graduation System. The system allows new players to learn game mechanics in a forgiving environment and then transition to normal gameplay once they've met specific goals.

## Test Environments

- **Development**: Local Windows environment with Python 3.8+
- **Testing**: Clean installation on Windows with minimal dependencies

## Test Categories

### 1. Unit Tests

#### Database Layer Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| UT-DB-01 | Test `is_tutorial_complete()` with new player | Should return `False` | 🔲 |
| UT-DB-02 | Test `mark_tutorial_complete()` | Should update DB flag to `True` | 🔲 |
| UT-DB-03 | Test `is_tutorial_complete()` after marking complete | Should return `True` | 🔲 |
| UT-DB-04 | Test database migration for `tutorial_complete` column | Column should exist with default value `False` | 🔲 |

#### Tutorial State Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| UT-TS-01 | Test tutorial progress tracking for deliveries | Counter should increment correctly | 🔲 |
| UT-TS-02 | Test tutorial progress tracking for money | Money counter should increment correctly | 🔲 |
| UT-TS-03 | Test tutorial goal detection (5 deliveries) | Should trigger completion | 🔲 |
| UT-TS-04 | Test tutorial goal detection ($50 earned) | Should trigger completion | 🔲 |
| UT-TS-05 | Test transition to `TutorialCompleteState` | Should transition correctly | 🔲 |

#### Tutorial Complete State Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| UT-TC-01 | Test overlay rendering | Should display correctly | 🔲 |
| UT-TC-02 | Test input handling (ENTER key) | Should mark complete and transition to title | 🔲 |
| UT-TC-03 | Test database update on confirmation | Should update player profile | 🔲 |

#### Title State Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| UT-TI-01 | Test menu options with tutorial incomplete | "Continue" should be disabled | 🔲 |
| UT-TI-02 | Test menu options with tutorial complete | "Continue" should be enabled | 🔲 |
| UT-TI-03 | Test navigation and selection | Should respond to keyboard input | 🔲 |

### 2. Integration Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| IT-01 | Test full tutorial completion flow | Should progress through all states correctly | 🔲 |
| IT-02 | Test game restart after tutorial completion | Should skip tutorial and show title screen | 🔲 |
| IT-03 | Test "Continue" option after tutorial completion | Should start normal gameplay | 🔲 |
| IT-04 | Test "New Game" option after tutorial completion | Should reset progress but not require tutorial again | 🔲 |

### 3. User Experience Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| UX-01 | Test tutorial instructions clarity | Users should understand objectives | 🔲 |
| UX-02 | Test tutorial completion overlay visibility | Should be clearly visible and readable | 🔲 |
| UX-03 | Test menu option clarity | Users should understand available options | 🔲 |
| UX-04 | Test transition smoothness | State transitions should be smooth and clear | 🔲 |

### 4. Regression Tests

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| RT-01 | Test core gameplay after tutorial changes | Should function identically to before | 🔲 |
| RT-02 | Test database operations with other tables | Should not affect other database operations | 🔲 |
| RT-03 | Test performance with tutorial states | No performance degradation | 🔲 |

### 5. Edge Cases

| Test ID | Description | Expected Result | Status |
|---------|-------------|-----------------|--------|
| EC-01 | Test with corrupted player profile | Should handle gracefully | 🔲 |
| EC-02 | Test with database connection loss | Should handle gracefully | 🔲 |
| EC-03 | Test rapid state transitions | Should handle without errors | 🔲 |
| EC-04 | Test with missing tutorial assets | Should use fallbacks | 🔲 |

## Test Execution

### Test Procedure

1. Run unit tests with pytest
2. Execute integration tests manually following test scripts
3. Conduct UX testing with sample users
4. Run regression tests to ensure no functionality is broken

### Test Data

- Clean database with new player profile
- Database with existing player profile (tutorial complete)
- Database with existing player profile (tutorial incomplete)

## Defect Management

- Log all defects with reproducible steps
- Categorize by severity (Critical, Major, Minor, Cosmetic)
- Include screenshots or videos when possible

## Exit Criteria

- All unit and integration tests pass
- No critical or major defects remain
- UX testing shows clear understanding of tutorial flow

## Test Reporting

- Generate test summary with pass/fail counts
- Document any workarounds implemented
- Provide recommendations for future improvements

---

*This test plan is specific to the Tutorial Graduation System and should be executed before merging this feature to the main branch.*
