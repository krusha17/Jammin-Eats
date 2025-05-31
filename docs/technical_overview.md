# Technical Overview

This document provides a high-level summary of the Jammin' Eats codebase and architecture.

## Code Structure
- Modular Python code, organized under `src/`:
  - `core/`: Game constants, main loop, core logic
  - `sprites/`: All sprite classes (player, food, customers, etc.)
  - `map/`: Map loading and handling (TMX, Tiled, etc.)
  - `utils/`: Utility functions (asset loading, sounds, logging)

## Main Technologies
- Python 3.8+
- Pygame (graphics, input, sound)
- PyTMX (Tiled map parsing)

## Entry Point
- `main.py` (modular version)
- (Legacy: `main.py`)

## Asset Loading
- All asset paths are managed via `src/core/constants.py` and helpers.
- Assets are loaded relative to the project root for consistency.

## Logging & Debugging
- Logging utilities in `src/debug/` help track asset loading and errors.

## Extending the Codebase
- Add new features as modules in `src/`.
- Follow the modular structure for maintainability.
- Document new modules in this folder.
