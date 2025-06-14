# Jammin' Eats Folder Structure

This document describes the organization of the Jammin' Eats project, following industry-standard practices for professional game development with integrated code quality automation.

## Root Structure

```
Jammin-Eats/
├── .venv/                     # Python virtual environment (local only)
├── assets/                    # All game assets (images, sounds, maps, etc.)
│   ├── Food/                  # Food item sprites organized by type
│   │   ├── Island_Ice_Cream/
│   │   ├── Rasta_Rice_Pudding/
│   │   ├── Reggae_Rasgulla/
│   │   ├── Ska_Smoothie/
│   │   └── Tropical_Pizza_Slice/
│   ├── sprites/               # Character and UI sprites
│   │   └── characters/        # Player and customer sprites
│   ├── sounds/                # Audio files
│   │   ├── characters/
│   │   ├── ui/
│   │   └── vehicles/
│   ├── Maps/                  # TMX map files for levels
│   │   └── level1/
│   ├── tiles/                 # Tile assets for maps
│   │   ├── Cloud/
│   │   ├── Decorations/
│   │   ├── Grass/
│   │   ├── Road/
│   │   ├── Sand/
│   │   ├── Sky/
│   │   └── Water/
│   └── tilesets/              # Tilesets for map editor
├── data/                      # Game data files
│   ├── jammin.db              # SQLite database for game persistence
│   └── jammin_backup_*.db     # Database backups
├── src/                       # Modular source code structure
│   ├── core/                  # Core game engine components
│   │   ├── constants.py       # Game constants and configuration
│   │   ├── game.py           # Main game engine and state management
│   │   ├── game_renderer.py   # Rendering logic and visual output
│   │   └── game_world.py      # World object management and physics
│   ├── states/                # Game state management classes
│   │   ├── title_state.py     # Title screen state
│   │   ├── tutorial_state.py  # Tutorial state with completion tracking
│   │   ├── gameplay_state.py  # Main gameplay state
│   │   └── __init__.py        # Package initialization
│   ├── sprites/               # Game entity classes
│   │   ├── player.py          # Player character with controls
│   │   ├── customer.py        # Customer AI and behavior
│   │   ├── food.py           # Food projectile mechanics
│   │   └── particle.py        # Visual effects system
│   ├── ui/                    # User interface components
│   │   ├── button.py          # Interactive button class
│   │   └── text.py           # Text rendering utilities
│   ├── map/                   # Map loading and management
│   │   └── tilemap.py         # TMX map loader with fallback capabilities
│   ├── utils/                 # Utility functions and helpers
│   │   ├── asset_loader.py    # Centralized asset loading system
│   │   └── sounds.py          # Sound loading and playback
│   ├── debug/                 # Debugging and development tools
│   │   └── debug_tools.py     # Error tracking and debugging utilities
│   ├── persistence/           # Game persistence layer
│   │   ├── dal.py            # Data Access Layer
│   │   ├── db_init.py        # Database initialization and migration
│   │   └── game_persistence.py # Game save/load functionality
│   └── __init__.py           # Package initialization
├── tests/                     # Comprehensive test suite
│   ├── unit/                  # Unit tests for individual modules
│   │   ├── test_db.py
│   │   └── test_db_fix.py
│   ├── integration/           # Integration tests for module interactions
│   ├── fixtures/              # Test data and mock objects
│   ├── test_dal.py           # Database layer tests
│   ├── test_tutorial_system.py # Tutorial system tests
│   └── conftest.py           # Test configuration and fixtures
├── docs/                      # Project documentation
│   ├── ci_cd_guide.md        # Development workflow and quality assurance
│   ├── folder_structure.md   # This document
│   ├── technical_overview.md # Technical architecture overview
│   ├── pytest_workflow.md   # Testing guidelines
│   ├── CORE_SYSTEM_VALIDATION_CHECKLIST.md # Development checklist
│   └── DEVELOPMENT_ROADMAP.md # Project roadmap
├── tools/                     # Development and utility tools
│   └── checklist_validator.py # Checklist validation utility
├── migrations/                # Database migration scripts
│   └── migration_001_initial.sql
├── logs/                     # Application logs (local only)
├── reports/                  # Generated reports and analysis
├── main.py                   # Main entry point for the game
├── debug_main.py            # Debug launcher with enhanced diagnostics
├── run_test.py              # Test runner with enhanced diagnostics
├── diagnose_db.py           # Database diagnostic utility
├── build_game.bat           # Windows build script
├── requirements.txt         # Production Python dependencies
├── requirements-dev.txt     # Development dependencies
├── .pre-commit-config.yaml  # Pre-commit hook configuration
├── mypy.ini                 # Type checking configuration
├── .pylintrc                # Static analysis rules
├── pyproject.toml           # Project configuration and tool settings
├── .gitignore               # Git ignore rules
├── README.md                # Main project documentation
├── changelog.md             # Project changelog
└── LICENSE.txt              # Project license
```

## Code Quality and Development Tools

### Configuration Files

- **`.pre-commit-config.yaml`**: Automated code quality checks (Ruff, Black, Pylint, MyPy)
- **`mypy.ini`**: Type checking settings and exclusions
- **`.pylintrc`**: Static analysis rules with game development customizations
- **`pyproject.toml`**: Centralized project configuration for all tools

### Development Workflow Files

- **`.venv/`**: Virtual environment (excluded from version control)
- **`requirements.txt`**: Production dependencies (pygame, pytmx, pyodbc)
- **`requirements-dev.txt`**: Development tools (pre-commit, pytest, mypy, pylint)

## Key Design Principles

### Modular Architecture

The `src/` directory follows a clean modular structure:

1. **`core/`**: Essential game engine components
2. **`states/`**: Game state machine implementation
3. **`sprites/`**: Game entities and objects
4. **`ui/`**: User interface components
5. **`utils/`**: Shared utility functions
6. **`persistence/`**: Data storage and retrieval
7. **`debug/`**: Development and debugging tools

### Asset Organization

Assets are organized by type and purpose:
- **Sprites**: Character and UI graphics in `assets/sprites/`
- **Food Items**: Individual food types in `assets/Food/`
- **Audio**: Sounds organized by category in `assets/sounds/`
- **Maps**: Level data in `assets/Maps/`
- **Tiles**: Map building blocks in `assets/tiles/`

### Testing Structure

Comprehensive testing follows best practices:
- **Unit Tests**: Individual module testing in `tests/unit/`
- **Integration Tests**: Module interaction testing
- **Fixtures**: Reusable test data and mocks
- **Coverage**: Code coverage analysis and reporting

### Professional Standards

The project maintains professional game development standards through:

1. **Automated Quality Assurance**: Pre-commit hooks ensure code quality
2. **Comprehensive Testing**: Full test coverage of critical systems
3. **Clean Architecture**: Modular design with clear separation of concerns
4. **Documentation**: Thorough documentation of systems and processes
5. **Version Control**: Proper Git workflow with quality gates

## File Naming Conventions

- **Python Files**: `snake_case.py` (e.g., `game_renderer.py`)
- **Classes**: `PascalCase` (e.g., `TutorialState`)
- **Functions/Variables**: `snake_case` (e.g., `is_tutorial_complete`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SCREEN_WIDTH`)
- **Assets**: `Pascal_Snake_Case` for folders, descriptive names for files

## Development Environment

### Virtual Environment
The project uses `.venv/` for dependency isolation:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pre-commit Hooks
Quality assurance is automated through pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files  # Test all files
```

### Database
Game persistence uses SQLite:
- **Location**: `data/jammin.db`
- **Backups**: Automatic backups in `data/` directory
- **Migrations**: Version-controlled schema changes in `migrations/`

---

> **Note**: This structure reflects the current state after comprehensive cleanup and modernization. The organization supports professional game development practices with automated quality assurance and maintainable code architecture.
