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
├── data/                  # Game data files
│   └── jammin.db          # SQLite database for game persistence
├── src/                   # All source code (modularized)
│   ├── core/              # Core game components
│   │   ├── game.py        # Main game engine and state management
│   │   ├── game_renderer.py # Rendering logic and visual output
│   │   ├── game_world.py  # World object management and physics
│   │   └── constants.py   # Game constants and configuration
│   ├── states/            # Game state management classes
│   │   ├── title_state.py # Title screen state
│   │   ├── tutorial_state.py # Tutorial state
│   │   └── gameplay_state.py # Main gameplay state
│   ├── sprites/           # Sprite classes
│   │   ├── player.py      # Player character
│   │   ├── customer.py    # Customer AI and behavior
│   │   └── food.py        # Food projectile mechanics
│   ├── map/               # Map loading and management
│   │   └── tilemap.py     # TMX map loading
│   ├── utils/             # Utility functions
│   │   ├── asset_loader.py # Asset loading system
│   │   └── sounds.py      # Sound management
│   └── persistence/       # Game persistence layer
│       ├── dal.py         # Data Access Layer
│       ├── db_init.py     # Database initialization and migration
│       └── game_persistence.py # Game save/load functionality
├── main.py                # Main entry point for the game
├── debug_main.py          # Debug launcher
├── run_test.py            # Test runner with enhanced diagnostics
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── README.md              # Main documentation
├── changelog.md           # Project changelog
├── .gitignore             # Git ignore rules
├── docs/                  # Additional documentation, diagrams, etc.
│   ├── folder_structure.md # This document
│   ├── technical_overview.md # Technical architecture overview
│   ├── pytest_workflow.md # Testing guidelines
│   └── ...
├── tests/                 # Automated test files (organized by type)
│   ├── unit/              # Unit tests for isolated components
│   │   ├── test_database.py
│   │   └── ...
│   └── integration/       # Integration tests for combined features
├── test_states.py         # Root-level state transition tests
├── test_tutorial_completion.py # Root-level tutorial tests
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
- **data/**: Game data files, including the SQLite database.
- **src/**: Modular game source code, organized by feature or responsibility.
  - **core/**: Core game engine, rendering, physics, and constants.
  - **states/**: Game state classes (title, tutorial, gameplay).
  - **sprites/**: Character and object classes.
  - **map/**: Map loading and management.
  - **utils/**: Helper utilities.
  - **persistence/**: Database and save game management.
- **docs/**: Documentation for developers, designers, and contributors.
- **tests/**: Automated test files organized by type (unit, integration).
- **Root-level tests**: Critical system validation tests that run against the main game.
- **tools/**: Utility scripts for development, database management, asset conversion, etc.
- **Backups/, Archive/, PDFs for note attachments/**: Old or archived materials (not tracked by git).

## Running Tests
- To run all tests with pytest:
  ```sh
  pytest
  ```
- To run tests with detailed logging (recommended for troubleshooting):
  ```sh
  python run_test.py
  ```
- To run a specific test file:
  ```sh
  pytest test_states.py
  ```
- You do **not** need to move test files out of `tests/` to run them. Modern test runners will find them automatically.

## Notes
- Only `main.py`, `debug_main.py`, and `run_test.py` should be in the project root as entry points, along with critical system test files.
- All other Python modules/scripts should be organized into `src/`, `tools/`, or `tests/`.
- All runtime constants (paths, settings, etc.) belong in `src/core/constants.py`.
- Database schema changes should be implemented as migrations in `src/persistence/db_init.py`.
- Documentation and diagrams for humans belong in `docs/`.
- Test helper functions should go in a dedicated test utilities module.
- Update this file if you add or reorganize major folders.
