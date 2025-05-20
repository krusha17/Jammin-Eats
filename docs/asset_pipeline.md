# Asset Pipeline

This document describes how assets (images, sounds, maps, etc.) are organized, loaded, and managed in the Jammin' Eats project.

## Asset Organization
- All assets are stored in the `assets/` directory at the project root.
- Subfolders include:
  - `food/`: Sprites for food items
  - `tilesets/`: Tileset images for maps
  - `Maps/`: TMX files for Tiled maps
  - `sounds/`: Sound effects and music
  - (Add more as needed)

## Adding New Assets
1. Place the asset in the appropriate subfolder in `assets/`.
2. Reference the asset in your code using the correct path, typically via helpers in `src/core/constants.py` or `src/utils/asset_loader.py`.
3. Test asset loading in-game to verify correctness.

## Asset Loading in Code
- Asset loading is handled via utility classes and functions in `src/utils/` and `src/core/constants.py`.
- All paths should be constructed using the `BASE_DIR` constant to ensure cross-platform compatibility and avoid path issues.
- Example:
  ```python
  from src.core.constants import ASSETS_DIR
  food_image_path = os.path.join(ASSETS_DIR, 'food', 'pizza.png')
  ```

## Asset Naming Conventions
- Use lowercase and underscores for file names (e.g., `tropical_pizza_slice.png`).
- Keep names descriptive and organized by type.

## Best Practices
- Do not store unused or duplicate assets.
- Optimize images and sounds for performance.
- Document any new asset types or folders in this file.
