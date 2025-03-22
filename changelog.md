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
