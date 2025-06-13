# Changelog

## [0.9.4-alpha] - 2025-06-13

### Added
- Modular code architecture with game.py split into core components:
  - game.py: Core game engine and state management
  - game_renderer.py: Rendering logic
  - game_world.py: World object management and physics
- Complete database schema with critical fixes:
  - Added missing 'money' column to player_profile table
  - Added missing 'successful_deliveries' column to player_profile table
  - Added 'save_games' table for game state persistence
- Enhanced test infrastructure:
  - Restored test_states.py and test_tutorial_completion.py
  - Added run_test.py for detailed test diagnostics and logging
  - Fixed mocking and fixtures for reliable state transition testing

### Fixed
- Database initialization and schema issues resolved
- All test files now pass with proper fixtures and mocks
- Tutorial state transition tests no longer skipped
- Missing draw_current_state method issue resolved through refactoring

### Improved
- Comprehensive documentation updates to reflect current architecture:
  - Updated technical_overview.md with current module structure
  - Updated folder_structure.md with accurate project organization
  - Enhanced pytest_workflow.md with new testing procedures
  - Updated CORE_SYSTEM_VALIDATION_CHECKLIST.md with current status
  - Updated DEVELOPMENT_ROADMAP.md to track completed tasks
- Code organization and structure matches professional game development practices
- Clear separation of rendering, world management, and game logic

## [0.9.3-alpha] - 2025-06-09

### Added
- Robust, modular Title Screen menu with all main options (New Game, Continue, Load, Options, Quit)
- Placeholder BlackScreenGameplayState for isolated state transition testing
- Fallback and dual persistence handling (DataAccessLayer and GamePersistence)
- Extensive logging and error handling for all menu and state transitions
- Automated test coverage for database initialization and persistence

### Fixed
- New Game button now reliably transitions to Tutorial or Gameplay based on tutorial completion
- Options button is visible and functional on Title Screen
- Import path mismatches for BlackScreenGameplayState and persistence modules
- Defensive handling for missing or failed persistence layer

### Improved
- Modular state transition logic using next_state pattern
- Menu item enable/disable logic based on player progress
- Logging granularity and diagnostic output for all core operations
- Professional, maintainable code structure and TDD workflow



### Added
- Professional game development approach with "vertical slice" methodology implemented
- Comprehensive state machine transition handling in Game.run method
- Diagnostic debug launcher (debug_game.py) for development and testing
- Detailed implementation plan for all menu options and state transitions

### Fixed
- Tutorial completion state transitions now properly return to title screen
- Tutorial completion now requires meeting both delivery and money goals
- Black screen issue after tutorial completion resolved
- Transition between states using next_state property now properly handled

### Improved
- State transition logging and error handling
- Tutorial progression feedback and progress tracking
- Robustness of state machine architecture
- Detailed implementation roadmap following professional game dev practices

## [0.9.1-alpha] - 2025-06-03

### Added
- Detailed implementation plan for completing Title → Gameplay transition (see checklist section 3A).
- Project documentation and validation checklist updates for team review.

### Fixed
- ShopOverlay AttributeError (missing `visible` property) and gameplay state transition bugs.

### Improved
- Robustness of database initialization and asset loading logic.
- Logging and diagnostics for state transitions and asset failures.

## [0.9.0-alpha] - 2025-06-01

### Added
- Persistence layer with SQLite database
- Player profile and settings storage
- Upgrade ownership persistence
- Run history tracking for analytics
- High score system
- Database migration pipeline

### Changed
- Game state now loads from and saves to database
- Upgrades persist between game sessions

## [0.8.0-alpha] - 2025-05-31

### Added
- Progression and upgrade system for player improvements
- Upgrade shop UI with item catalog
- Player stat modifier system (speed, inventory capacity)
- Economic balance for progression pacing
- Persistent upgrade tracking

## [0.7.0] - 2025-05-31

### Added
- New food animation system: Each food cycles through 3 frames, with a distinct explosion/impact frame at the end of its flight.
- Animation speed is now decoupled from projectile lifespan for a smoother, more polished look.
- Inventory HUD improvements: Selected food is only shown in the bottom HUD, with clear key bindings, stock counts, and color-coded status.
- Improved gameplay polish: Animation, collision, and inventory feedback are thoroughly tested for clarity and smoothness.

### Changed
- Modular code structure further improved for maintainability and extensibility.
- Enhanced error handling and fallback logic throughout all modules.
- Updated README to reflect new features and gameplay improvements.

## [0.6.0] - 2025-05-31

### Fixed
- Game no longer crashes after pressing Start due to robust error handling in game loop, player, and map logic.
- All map, player, and economy logic now have fallback mechanisms for missing/corrupt assets and database failures.
- Fixed AttributeError in `_render` for economy phase display.

### Changed
- Improved modularization and code organization.
- Added comprehensive error logging for asset loading, sound, and database operations.
- Updated documentation (README) with troubleshooting, error handling, and fallback system info.


All notable changes to the Jammin' Eats project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-05-20

### Added
- Complete modular architecture with separate components:
  - Core game engine module
  - Sprites module (Player, Customer, Food, Particle)
  - Map handling module
  - UI components module
  - Debug tools module
  - Utility functions module
- New entry point (`new_main.py`) for the modular version
- Improved debugging system with on-screen logs
- Setup.py for proper packaging and installation
- Comprehensive documentation in README_MODULAR.md

### Changed
- Organized code into a professional, maintainable structure
- Improved error handling and fallbacks throughout the codebase
- Enhanced debug tools with performance logging
- Kept original main.py for backward compatibility and reference

## [0.4.0] - 2025-05-20

### Fixed
- Resolved Git merge conflicts in TiledMap class implementation
- Fixed syntax errors with improperly indented methods from merge conflict
- Fixed variable scope issue with spawn_time causing runtime errors
- Improved debug mode functionality for better development experience

### Added
- Enhanced debug mode toggle to support both F12 and D keys for activation
- Added visual on-screen indicator when debug mode is active
- Added sound feedback when toggling debug mode 
- Created a _check_walkability helper method to improve code organization

### Changed
- Cleaned up duplicate code in debug visualization
- Improved error handling for customer spawning system

## [0.3.0] - 2025-05-17

### Fixed
- Corrected indentation issues in several class methods in main.py
- Fixed UnboundLocalError with debug_mode variable by adding it to the global statement in main()
- Resolved runtime errors related to variable scope
- Added proper access to global variables in function scope

### Changed
- Updated requirements.txt to remove unused dependencies (pyodbc)
- Added version constraints for pytmx (>=3.31) and pyinstaller (>=5.6.2)
- Reorganized code to ensure proper variable scope

## [0.1.0] - 2025-03-22

### Added
- Initial game setup with Pygame
- Basic character movement in four directions
- Character sprite animations with directional changes
- Menu, gameplay, and game over states
- Customer spawning system with patience mechanics
- Food throwing mechanics in four directions
- Four food types: Tropical Pizza Slice, Ska Smoothie, Island Ice Cream Jam, and Rasta Rice Pudding
- Customer preferences for specific food types
- Visual indicators for customer patience
- Score tracking system with bonuses for preference matching
- Particle effects for successful deliveries
- Interactive menu buttons with hover effects
- High score tracking
- Game over screen with statistics
- Fallback systems for missing assets

### Fixed
- File path resolution for assets
- Main game loop execution with proper entry point
- Collision detection with boundaries
- Diagonal movement speed normalization
- Error handling for missing asset files

### Changed
- Reorganized file structure for better asset management
- Temporary disabled food truck until sprite is available
- Implemented procedurally generated elements for missing assets

## [0.2.0] - 2025-04-26

### Added
- Updated and documented the current folder structure for the project, ensuring all directories and subdirectories are accurately represented.
- Created a detailed text version of the folder structure for reference and future PDF export.

### Changed
- Improved the backup script (`backup_script.ps1`) to exclude the `Backups` folder from backups, preventing redundant storage.
- Updated `.gitignore` to ignore the top-level `Backups` directory, improving version control hygiene.
- Refined file path resolution for assets, especially TMX map and tileset references, to ensure robust resource loading across environments.
- Adjusted `Level_1_Frame_1.tmx` to correctly reference the tileset with a relative path fix.

### Fixed
- Bug where the game could not find the tileset file due to incorrect TMX pathing.
- File path errors related to map and resource loading in Pygame.

## [Upcoming]

### Planned
- Food truck sprite integration
- Database integration for persistent storage
- Additional customer types and behaviors
- More levels with different backgrounds
- Power-up system
- Day/night cycle
- Special events and challenges
- Refactoring code into modular structure
- Full sound system implementation
