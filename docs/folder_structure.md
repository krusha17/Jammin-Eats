# Jammin' Eats Folder Structure

This document describes the organization of the Jammin' Eats project, following industry-standard practices for professional game development.

## Root Structure

```
Jammin-Eats/
├── assets/                # All game assets (images, sounds, maps, etc.)
│   ├── food/
│   ├── tilesets/
│   ├── Maps/
│   └── ...
├── src/                   # All source code (modularized)
│   ├── core/
│   ├── sprites/
│   ├── map/
│   ├── utils/
│   └── ...
├── main.py                # (Legacy, monolithic)
├── main.py            # Modular entry point
├── requirements.txt       # Python dependencies
├── README.md              # Main documentation
├── changelog.md           # Project changelog
├── .gitignore             # Git ignore rules
├── main.py                # Main entry point for the game
├── docs/                  # Additional documentation, diagrams, etc.
│   ├── folder_structure.md
│   └── ...
├── src/                   # All game/application code (modularized)
│   ├── core/
│   ├── states/
│   ├── persistence/
│   ├── debug/
│   ├── ...
├── tests/                 # All automated test files (unittest/pytest)
│   ├── test_database_initialization.py
│   ├── test_gameplay.py
│   └── ...
├── tools/                 # Utility scripts (db migration, asset tools, etc.)
│   ├── checklist_validator.py
│   ├── db_migrate.py
│   └── ...
├── assets/                # Images, sounds, maps, etc.
├── LICENSE                # License file
└── (Backups/, Archive/, PDFs for note attachments/ - archived or ignored)
```

## Folder Purpose
- **assets/**: All images, sounds, and map files used by the game.
- **src/**: Modular game source code, organized by feature or responsibility. All .py files (except main.py/debug_main.py) live here.
- **docs/**: Documentation for developers, designers, and contributors.
- **tests/**: All automated test files for the project, organized by feature or type. Test runners will auto-discover tests here.
- **tools/**: Utility scripts for development, database management, asset conversion, etc.
- **Backups/, Archive/, PDFs for note attachments/**: Old or archived materials (not tracked by git).

## Running Tests
- To run all tests in the `tests/` folder:
  ```sh
  python -m unittest discover -s tests
  ```
- To run a specific test file:
  ```sh
  python -m unittest tests/test_database_initialization.py
  ```
- You do **not** need to move test files out of `tests/` to run them. Modern test runners will find them automatically.

## Notes
- Only `main.py` (and optionally `debug_main.py`) should be in the project root as entry points.
- All other Python modules/scripts should be organized into `src/`, `tools/`, or `tests/`.
- All runtime constants (paths, settings, etc.) belong in `src/core/constants.py`.
- Documentation and diagrams for humans belong in `docs/`.
- Update this file if you add or reorganize major folders.
