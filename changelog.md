# Changelog

All notable changes to the Jammin' Eats project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
