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
├── src/                   # All source code (modularized)
│   ├── core/
│   ├── sprites/
│   ├── map/
│   ├── utils/
│   └── ...
├── main.py                # (Legacy, monolithic)
├── new_main.py            # Modular entry point
├── requirements.txt       # Python dependencies
├── README.md              # Main documentation
├── changelog.md           # Project changelog
├── .gitignore             # Git ignore rules
├── setup.py               # (Optional) For packaging/distribution
├── docs/                  # Additional documentation, diagrams, etc.
│   ├── folder_structure.md
│   └── ...
├── LICENSE                # License file
└── (Backups/, Archive/, PDFs for note attachments/ - archived or ignored)
```

## Folder Purpose
- **assets/**: All images, sounds, and map files used by the game.
- **src/**: Modular game source code, organized by feature or responsibility.
- **docs/**: Documentation for developers, designers, and contributors.
- **Backups/, Archive/, PDFs for note attachments/**: Old or archived materials (not tracked by git).

## Notes
- All runtime constants (paths, settings, etc.) belong in `src/core/constants.py`.
- Documentation and diagrams for humans belong in `docs/`.
- Update this file if you add or reorganize major folders.
