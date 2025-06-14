# Technical Overview

This document provides a high-level summary of the Jammin' Eats codebase, architecture, and development workflow following professional game development standards.

## Project Architecture

Jammin' Eats follows a **modular, state-driven architecture** with comprehensive quality assurance automation and clean separation of concerns.

### Core System Design

```
Game Engine (src/core/)
├── State Machine → Title/Tutorial/Gameplay States
├── Rendering Pipeline → Visual output and effects
├── World Management → Physics and object interactions
└── Asset Loading → Centralized resource management

Persistence Layer (src/persistence/)
├── Data Access Layer → Database operations
├── Save/Load System → Game state persistence
└── Tutorial Tracking → Progress validation

Quality Assurance
├── Pre-commit Hooks → Automated code validation
├── Testing Framework → Unit and integration tests
└── Static Analysis → Type checking and linting
```

## Code Structure

### Modular Organization (`src/`)

- **`core/`**: Game engine fundamentals
  - `game.py`: Main game engine and state management
  - `game_renderer.py`: Rendering pipeline and visual effects
  - `game_world.py`: World object management and physics simulation
  - `constants.py`: Global constants and configuration settings

- **`states/`**: State machine implementation
  - `title_state.py`: Main menu and navigation
  - `tutorial_state.py`: Tutorial system with completion tracking
  - `gameplay_state.py`: Core game mechanics and interaction

- **`sprites/`**: Game entity classes
  - `player.py`: Player character with movement and actions
  - `customer.py`: AI-driven customer behavior and satisfaction
  - `food.py`: Food projectile mechanics and collision detection
  - `particle.py`: Visual effects and animations

- **`ui/`**: User interface components
  - `button.py`: Interactive button system
  - `text.py`: Text rendering and formatting utilities

- **`utils/`**: Shared utility functions
  - `asset_loader.py`: Centralized asset loading with fallback support
  - `sounds.py`: Audio management and playback

- **`persistence/`**: Data persistence layer
  - `dal.py`: Data Access Layer for database operations
  - `db_init.py`: Database schema and migration management
  - `game_persistence.py`: Save/load functionality

- **`debug/`**: Development and debugging tools
  - `debug_tools.py`: Error tracking and development utilities

## Technology Stack

### Core Technologies
- **Python 3.13+**: Main development language
- **Pygame**: Graphics rendering, input handling, and audio
- **PyTMX**: Tiled map file parsing and level management
- **SQLite**: Local database for game persistence and progress tracking

### Development Tools
- **Pre-commit Hooks**: Automated code quality validation
  - **Ruff**: Fast Python linting and code style enforcement
  - **Black**: Automatic code formatting
  - **Pylint**: Static analysis and code quality metrics
  - **MyPy**: Type checking and validation
- **Pytest**: Comprehensive testing framework
- **Git**: Version control with quality gates

### Configuration Management
- **`.pre-commit-config.yaml`**: Hook configuration
- **`mypy.ini`**: Type checking settings
- **`.pylintrc`**: Static analysis rules
- **`pyproject.toml`**: Centralized project configuration

## Development Workflow

### Quality Assurance Pipeline

1. **Code Development**: Write code using modular architecture principles
2. **Pre-commit Validation**: Automatic quality checks on every commit
   - Linting (Ruff)
   - Formatting (Black)
   - Static Analysis (Pylint)
   - Type Checking (MyPy)
3. **Testing**: Comprehensive unit and integration tests
4. **Documentation**: Maintained alongside code changes

### Entry Points

- **`main.py`**: Production game launcher
- **`debug_main.py`**: Development launcher with enhanced diagnostics
- **`run_test.py`**: Test runner with detailed logging

## Asset Management

### Asset Loading System
- **Centralized Loading**: All assets managed through `asset_loader.py`
- **Fallback Support**: Graceful handling of missing assets
- **Path Management**: Consistent relative path resolution
- **Error Handling**: Comprehensive asset loading error recovery

### Asset Organization
```
assets/
├── Food/               # Game items organized by type
├── sprites/           # Character and UI graphics
├── sounds/            # Audio files by category
├── Maps/              # Level data (TMX format)
├── tiles/             # Map building components
└── tilesets/          # Map editor resources
```

## Database Architecture

### SQLite Schema
- **Player Profiles**: User progress and settings
- **Tutorial Completion**: Progress tracking and validation
- **Game State**: Save/load functionality
- **High Scores**: Achievement tracking

### Data Access Layer (DAL)
- **Abstracted Operations**: Clean separation between game logic and data
- **Transaction Management**: Consistent database operations
- **Migration Support**: Schema versioning and updates
- **Backup System**: Automatic database backups

## State Management

### State Machine Pattern
The game uses a robust state machine for managing different game modes:

1. **Title State**: Main menu and navigation
2. **Tutorial State**: Interactive tutorial with completion tracking
3. **Gameplay State**: Core game mechanics and customer interaction

### State Transitions
- Clean transitions between states
- Persistent data across state changes
- Tutorial completion validation
- Progress saving and restoration

## Error Handling and Logging

### Comprehensive Error Management
- **Asset Loading**: Fallback systems for missing resources
- **Database Operations**: Transaction rollback and error recovery
- **State Transitions**: Graceful handling of invalid state changes
- **User Input**: Validation and sanitization

### Development Debugging
- **Debug Tools**: Enhanced logging and error tracking
- **Diagnostic Utilities**: Database inspection and validation
- **Test Utilities**: Comprehensive test coverage and reporting

## Performance Considerations

### Optimization Strategies
- **Asset Caching**: Efficient resource loading and reuse
- **Sprite Management**: Optimized rendering pipeline
- **Database Queries**: Indexed operations and prepared statements
- **Memory Management**: Proper cleanup and resource disposal

### Code Quality Metrics
- **Pre-commit Hook Performance**: Typically 2-5 seconds per commit
- **Test Coverage**: Comprehensive coverage of critical systems
- **Static Analysis**: Continuous code quality monitoring
- **Type Safety**: Strong typing throughout the codebase

## Professional Standards

### Code Quality
- **Automated Validation**: Pre-commit hooks prevent quality issues
- **Consistent Formatting**: Black ensures uniform code style
- **Type Safety**: MyPy provides static type validation
- **Documentation**: Comprehensive inline and external documentation

### Testing Strategy
- **Unit Tests**: Individual module validation
- **Integration Tests**: System interaction testing
- **Regression Testing**: Continuous validation of existing functionality
- **Coverage Analysis**: Ensuring comprehensive test coverage

### Version Control
- **Quality Gates**: Pre-commit hooks prevent low-quality commits
- **Modular Commits**: Clean, focused change sets
- **Documentation**: Changes documented alongside code
- **Backup Systems**: Database and configuration backups

---

> **Note**: This architecture supports rapid development while maintaining professional game development standards. The modular design enables easy feature expansion and maintenance, while automated quality assurance ensures code reliability and consistency.
