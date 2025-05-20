# Jammin' Eats: Modular Architecture

## Overview
This document explains the new modular architecture implemented for the Jammin' Eats game. The code has been reorganized from a single large file into a structured, maintainable codebase following professional game development practices.

## Project Structure

```
Jammin-Eats/
├── assets/              # Game assets (images, sounds, maps)
├── src/                # Source code directory
│   ├── core/           # Core game components
│   │   ├── constants.py  # Game constants and configuration
│   │   ├── game.py       # Main game engine and loop
│   ├── debug/          # Debugging tools
│   │   ├── debug_tools.py # Debug mode and visualization
│   ├── map/            # Map handling
│   │   ├── tilemap.py  # TiledMap class for TMX maps
│   ├── sprites/        # Game entities
│   │   ├── player.py   # Player class
│   │   ├── customer.py # Customer class
│   │   ├── food.py     # Food projectile class
│   │   ├── particle.py # Particle effects
│   ├── ui/             # User interface
│   │   ├── button.py   # Button class
│   │   ├── text.py     # Text rendering utilities
│   ├── utils/          # Utility functions
│   │   ├── sounds.py   # Sound loading and playback
│   │   ├── resource_path.py # Resource pathing for deployment
│   ├── main.py         # Entry point for the src package
├── new_main.py         # New game entry point
├── main.py             # Original single-file version (kept for reference)
├── setup.py            # For packaging and distribution
├── requirements.txt    # Dependencies
└── README.md           # Project documentation
```

## Benefits of Modular Architecture

1. **Maintainability**: Each module has a single responsibility, making the code easier to understand and modify.

2. **Testability**: Individual components can be tested in isolation.

3. **Collaboration**: Multiple developers can work on different modules simultaneously.

4. **Reusability**: Modules can be reused in other projects or parts of the same project.

5. **Scalability**: It's easier to add new features by creating new modules or extending existing ones.

## Running the Game

### Development Mode
```bash
python new_main.py
```

### Installation (Optional)
```bash
pip install -e .
```

This will install the game in development mode, allowing you to run it with:
```bash
jammin-eats
```

## Debug Mode

Press F12 or D during gameplay to toggle debug mode, which shows:
- Walkable areas
- Spawn points
- Visual debug indicators
- Console logs with performance metrics

## Architecture Details

### Core Module
Contains the central game logic, state management, and main loop. The `Game` class in `game.py` orchestrates the entire game.

### Sprites Module
Contains all game entities as separate classes:
- `Player`: Handles movement, animation, and food throwing
- `Customer`: Manages customer behavior, preferences, and interactions
- `Food`: Controls food projectiles and collision detection
- `Particle`: Creates visual effects for spawns and successful deliveries

### Map Module
Manages the game world:
- `TiledMap`: Loads and renders the TMX map, handles collision detection and spawn points

### UI Module
Manages user interface elements:
- `Button`: Interactive buttons for menus
- Text utilities for rendering text on screen

### Debug Module
Provides tools for development and troubleshooting:
- Toggle debug mode
- Performance logging
- Visual debugging (walkable areas, spawn points)

### Utils Module
Contains helper functions:
- Sound loading and playback
- Resource path handling for packaging

## Future Development

This modular architecture makes it easier to:
1. Add new customer types
2. Create additional levels
3. Implement power-ups
4. Add new food types
5. Extend the UI with more sophisticated menus
6. Implement save/load functionality

## Transitioning from Legacy Code

The original `main.py` has been kept for reference, but all new development should use the modular structure in `src/`. Over time, you can phase out the original file entirely.
