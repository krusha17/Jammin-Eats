# Pytest Workflow Guide for Jammin' Eats

This guide explains how to use [pytest](https://docs.pytest.org/) for running, writing, and integrating tests in the Jammin' Eats project.

---

## 1. Installing Pytest

Install pytest if you haven't already:
```sh
pip install pytest
```

---

## 2. Organizing Tests

- All test files should be placed in the `tests/` directory.
- Test file names should start with `test_` (e.g., `test_gameplay.py`).
- Test functions and classes should also start with `test_`.
- You can organize tests into subfolders like `tests/unit/`, `tests/integration/`, etc.

Example structure:
```
Jammin-Eats/
├── src/
├── tests/
│   ├── test_database_initialization.py
│   ├── unit/
│   │   └── test_state_machine.py
│   └── integration/
│       └── test_tutorial_flow.py
```

---

## 3. Running Tests

- Run **all tests**:
  ```sh
  pytest
  ```
- Run tests in a specific file:
  ```sh
  pytest tests/test_database_initialization.py
  ```
- Run tests in a specific folder:
  ```sh
  pytest tests/unit/
  ```
- Show extra info (verbose):
  ```sh
  pytest -v
  ```

---

## 4. Writing New Tests

- Create a new file in `tests/` or a subfolder, named `test_something.py`.
- Write test functions starting with `test_`:
  ```python
  def test_example():
      assert 1 + 1 == 2
  ```
- You can use fixtures for setup/teardown (see Pytest docs for advanced usage).

---

## 5. Integrating New Tests

- Place new test files in the `tests/` folder or an appropriate subfolder.
- Make sure the test file and function names start with `test_`.
- Run `pytest` to verify your new tests are discovered and executed.
- If you want to run both `unittest` and `pytest` tests, pytest will auto-discover both.

---

## 6. Continuous Integration (CI)

- Add `pytest` to your `requirements.txt` or development dependencies.
- In your CI pipeline, use the command:
  ```sh
  pytest
  ```
- This will ensure all tests are run automatically on every push or pull request.

---

## 7. Additional Tips

- Use `pytest --maxfail=1 --disable-warnings -v` for fast feedback.
- Use markers (e.g., `@pytest.mark.slow`) to categorize tests.
- See [pytest documentation](https://docs.pytest.org/) for advanced features.

---

**Stay modular, keep your tests organized, and enjoy reliable development!**
