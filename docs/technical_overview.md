# Technical Overview

This document provides a high-level summary of the Jammin' Eats codebase and architecture.

## Code Structure
- Modular Python code, organized under `src/`:
  - `core/`: Game constants, main loop, core logic
    - `game.py`: Core game engine and state management
    - `game_renderer.py`: Rendering logic and visual output
    - `game_world.py`: World object management and physics
    - `constants.py`: Global constants and configuration
  - `states/`: Game state management
    - Various state classes (TitleState, GameplayState, etc.)
  - `sprites/`: All sprite classes (player, food, customers, etc.)
  - `map/`: Map loading and handling (TMX, Tiled, etc.)
  - `utils/`: Utility functions (asset loading, sounds, logging)
  - `persistence/`: Database and save game handling
    - `dal.py`: Data Access Layer for database operations
    - `db_init.py`: Database initialization and migration 
    - `game_persistence.py`: Game save/load functionality

## Main Technologies
- Python 3.8+
- Pygame (graphics, input, sound)
- PyTMX (Tiled map parsing)
- SQLite (database persistence)

## Entry Point
- `main.py` (modular version)
- (Legacy: `main.py`)

## Asset Loading
- All asset paths are managed via `src/core/constants.py` and helpers.
- Assets are loaded relative to the project root for consistency.
- The system includes robust fallbacks for missing assets.

## Logging & Debugging
- Logging utilities in `src/debug/` help track asset loading, state transitions, and database operations.
- Comprehensive error handling throughout the codebase ensures graceful failure.
- The `run_test.py` utility provides detailed logging for troubleshooting test failures.

## Database & Persistence
- SQLite database (`data/jammin.db`) stores player progress and game state.
- Database schema includes:
  - `player_profile` table: Tracks player progress, tutorial completion, money, and delivery statistics
  - `save_games` table: Stores game save slots for loading/resuming games
  - Migration system for schema updates
- Dual persistence architecture with DataAccessLayer (DAL) and GamePersistence classes

## 0.9.4-alpha: Modular Architecture & Test Improvements
- Code fully refactored into a modular structure:
  - Game.py split into game.py, game_renderer.py, and game_world.py
  - State management moved to dedicated state classes
  - Persistence layer with full database support
- Database schema expanded and stabilized:
  - Added missing columns (money, successful_deliveries)
  - Added save_games table for save/load functionality
  - Robust migration system for schema updates
- Comprehensive test suite:
  - Fixed and expanded test coverage
  - Improved test fixtures and mocks
  - Added detailed test diagnostics and logging
- TitleState and menu transitions refactored for modularity and reliability
- Robust error handling and logging for all state transitions
- Dual persistence support: fallback between DataAccessLayer and GamePersistence

## Extending the Codebase
- Add new features as modules in `src/`.
- Follow the modular structure for maintainability.
- Document new modules in this folder.
- Write tests for new functionality in the `tests/` directory.
- Use the State pattern for new game screens or modes.
- For database changes, add migrations in `db_init.py`.

## Testing
- Comprehensive test suite using pytest.
- Tests are organized in the `tests/` directory with subdirectories for unit and integration tests.
- Run tests with `pytest` or use `run_test.py` for detailed diagnostics.
- Custom test fixtures provide consistent test environment setup.
- See `pytest_workflow.md` for more details on writing and running tests.
