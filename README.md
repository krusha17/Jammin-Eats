🎮 Jammin' Eats

## Tutorial Mode

> **Note:** Project is currently in the core system validation (graybox) phase. See `CORE_SYSTEM_VALIDATION_CHECKLIST.md` for details.


The tutorial graduation system is fully implemented and validated. On first launch, players must complete a short tutorial (deliveries or money goal) before accessing the main game. Completion is persisted in the database and skips on future launches.

- Tutorial overlays and state transitions are fully functional.
- Graybox mechanics (no assets) are used to validate logic and persistence.
- Press SPACE to simulate deliveries/money in the tutorial.
- Press ENTER to advance from the completion overlay.

## Current Development Stage

- **Core systems (tutorial, DAL, state machine, persistence) are complete and validated.**
- **Title → Gameplay Transition milestone is IN PROGRESS.**
- **Current blockers:** Map is not loading, missing HUD, food/customer sprites, and shop content.
- See `CORE_SYSTEM_VALIDATION_CHECKLIST.md` for the detailed implementation plan and blockers table.
- **Asset integration and polish are deferred** until all checklist items are green.

## System Validation Checklist
See `CORE_SYSTEM_VALIDATION_CHECKLIST.md` for a step-by-step, test-driven guide to validating every core system before moving to the next milestone.

## Next Steps for Contributors
- Review the new implementation plan in `CORE_SYSTEM_VALIDATION_CHECKLIST.md` (section 3A) and coordinate fixes for the Title → Gameplay transition.
- Use the debug launcher (`debug_main.py`) to run diagnostics and validate asset loading and state transitions.
- Only begin asset, sound, and polish integration once all core systems are stable and tested.
- See DEVELOPMENT_ROADMAP.md for future features and expansion plans. & Progression

Jammin' Eats features a **Tutorial System** designed to help new players learn the game mechanics in a forgiving environment and then graduate to the full game experience.

### Tutorial Mechanics
- **No Penalties for Wrong Food:**
  - Giving a customer the wrong food will not increase the "Wrong Food" counter or result in a game over.
  - Customers may still react (e.g., appear angry), but you are free to experiment without failing.
- **Timer Behavior:**
  - The in-game timer is still visible and counts up, but there is no time pressure or penalty for slow play.
- **Economy and Purchases:**
  - All food is free during the tutorial phase. You cannot run out of money.
- **Tutorial Goals:**
  - Successfully serve 5 customers with the correct food items, OR
  - Earn $50 in the tutorial economy

### Tutorial Graduation
- Once you achieve either tutorial goal, a "Tutorial Complete!" overlay will appear
- Your tutorial completion is saved to the database, so you won't have to repeat it
- After completing the tutorial, the title screen will show a "Continue" option
- New players will automatically start in tutorial mode
- Returning players can choose to start a new game or continue with normal gameplay

### State Management
- The game uses a state machine architecture to manage different game states:
  - `TutorialState`: Tracks progress toward tutorial goals
  - `TutorialCompleteState`: Displays completion overlay
  - `TitleState`: Main menu with options based on tutorial completion

### Technical Implementation
- Tutorial completion is stored in the `player_profile` table
- The `dal.py` module provides `is_tutorial_complete()` and `mark_tutorial_complete()` functions
- Tutorial state is automatically determined when the game starts

---

## Diagnostics & Validation

- Run `python debug_main.py` to launch the game in debug/diagnostic mode.
- Check logs for asset loading errors, missing sprites, or state transition issues.
- Use the checklist in `CORE_SYSTEM_VALIDATION_CHECKLIST.md` to validate each system before moving to the next milestone.

A Neon-Retro, Reggae-Cyberpunk Food Delivery Adventure!
Welcome to Jammin' Eats, a vibrant and exciting 2D top-down game set in a neon-lit futuristic beach city where reggae rhythms blend harmoniously with cyberpunk aesthetics. Inspired by classic arcade games like Paperboy, Jammin' Eats offers immersive gameplay, dynamic animation, and an infectious tropical vibe!

🚀 Overview

In Jammin' Eats, players take on the role of Kai Irie, a cheerful, reggae-loving food truck driver. Deliver culturally diverse, reggae-themed dishes across an ever-changing urban landscape, meet quirky customers, and groove to the rhythm as you navigate through bustling city streets.

🌴 Game Features

🎯 Gameplay Mechanics

Directional Movement & Animation: Smooth, responsive movement with dynamic sprite animations for Kai and his food truck.
Interactive Customers: Serve diverse characters with unique tastes, preferences, and patience meters.
Food Throwing Mechanic: Deliver delicious dishes like Tropical Pizza Slice, Ska Smoothie, and Rasta Rice Pudding with fun, satisfying mechanics.
Dynamic Game States: Navigate seamlessly through menus, active gameplay, and game-over screens with immersive visual feedback.

🍕 Food Animation System

- Each food item cycles smoothly through 3 animation frames as it flies, with a visually distinct explosion or impact frame.
- Animation speed is decoupled from projectile lifespan for a polished, responsive feel.
- Asset management is streamlined: only 3 PNGs per food type are required, with fallback logic if assets are missing.

🧩 HUD & Inventory

- The selected food is now displayed only in the bottom inventory HUD, keeping the main HUD clean and focused.
- Inventory status shows key bindings, stock counts, and highlights out-of-stock items in red and current selection in green.

💡 Technical Highlights

Pixel-Perfect Graphics: Stunning top-down pixel art infused with neon-cyberpunk and tropical island aesthetics.
Vibrant, Seamless Environments: Procedurally generated backgrounds and assets designed to scale effortlessly.
Reggae-Cyberpunk Theme: Unique visual identity inspired by retro arcade classics, with a futuristic twist.

🧑‍💻 Modular Architecture & Error Handling

- **Codebase is fully modularized** under `src/` with clear separation for core logic, sprites, maps, utilities, and debug tools.
- **Professional, maintainable structure**: All gameplay, animation, and economy logic is modular and extensible.
- **Robust asset loading**: All assets are loaded relative to project root; missing assets trigger fallback visuals/sounds.
- **Fallback map system**: If a TMX map fails to load, a fallback map is generated to keep the game running.
- **Database integration**: If the database module is missing or fails, the game continues with persistence/logging disabled.
- **Sound loading**: Missing sound files are logged but do not crash the game.
- **Comprehensive error handling**: All critical game loop and rendering logic is wrapped to prevent crashes from unexpected exceptions.
- **Gameplay polish**: Food animation, collision, and inventory feedback are thoroughly tested for smoothness and clarity.
- **Debug mode**: Toggle with F12 or D for verbose error and event output.

🆘 Troubleshooting

- **Missing Sounds**: If you see errors about missing sound files, add or correct files in `assets/sounds/`. The game will continue without them.
- **Database Errors**: If `pyodbc` is not installed, database features are gracefully disabled.
- **Map Not Loading**: If a TMX file is missing or corrupt, a fallback map will be used and a warning printed.
- **Game Crashes on Start**: All known issues with game state transitions and map loading are now fixed. If you encounter a crash, check the console for error logs and verify asset/database presence.

🛠️ Current Development State

Fully playable prototype with core gameplay loops established.
Complete sprite animation system for main character and customers.
Functional game states including start menu, gameplay, and score tracking.

📊 Database Integration

Player profiles and progress management
Dynamic object creation and management (customers, food types, levels)
Leaderboards and achievement tracking
Persistent game settings and customization options

🌎 Expanded Game Universe

Additional themed levels and customer varieties
Advanced food truck customization and upgrades
Regular updates featuring special events, challenges, and unlockable content

🚧 Transition to 3D

Future scalability plans to evolve into a rich, immersive 3D experience while retaining original charm
Flexible data architecture designed from inception to facilitate seamless expansion

🤝 Community & Collaboration

Online leaderboards and social sharing features
Support for community-created custom levels
Active engagement with player feedback to continuously enhance the gaming experience

📂 Modular Project Structure

```text
Jammin-Eats/
├── assets/
│   ├── Food/              # Food item sprites organized by type
│   ├── Maps/              # TMX map files for levels
│   ├── sprites/
│   │   └── characters/    # Player and customer character sprites
│   ├── tiles/             # Tile assets for maps
│   └── tilesets/          # Tilesets for the map editor
├── src/                  # Modular source code structure
│   ├── core/             # Core game engine components
│   │   ├── constants.py  # Game constants and configuration
│   │   └── game.py       # Main game engine class
│   ├── debug/            # Debugging and development tools
│   │   └── debug_tools.py # Error tracking and debugging utilities
│   ├── map/              # Map loading and handling
│   │   └── tilemap.py    # TMX map loader with fallback capabilities
│   ├── sprites/          # Game entity classes
│   │   ├── customer.py   # Customer class with AI behaviors
│   │   ├── food.py       # Food projectile class
│   │   ├── particle.py   # Visual effects system
│   │   └── player.py     # Player character with controls
│   ├── ui/               # User interface components
│   │   ├── button.py     # Interactive button class
│   │   └── text.py       # Text rendering utilities
│   ├── utils/            # Utility functions and helpers
│   │   ├── asset_loader.py # Centralized asset loading system
│   │   └── sounds.py     # Sound loading and playback
│   └── main.py          # Entry point for the modular version
├── debug_main.py         # Enhanced debugging launcher
├── README.md
└── venv/                 # Python virtual environment
```

> **Heads up!**
> - The `.gitignore` is tuned to keep your `Backups/` folder out of version control—no worries, no clutter!
> - The backup script is jammin' too: it skips the `Backups/` folder so you don't back up your backups. Meta!
> - All your irie assets live in the `assets/` folder—don't break the rhythm, keep the structure!

🖥️ **How to Run the Game (Jammin' Style)**

1. **Clone this reggae adventure:**
   ```sh
   git clone https://github.com/YourUsername/Jammin-Eats.git
   ```
2. **Install the good vibes (dependencies):**
   ```sh
   pip install pygame pyodbc pytmx pyinstaller
   ```
3. **Start jammin'!**
   ```sh
   python main.py
   ```

🎛️ **Build the Standalone .exe (for your music producer or friends!)**

1. Run the build script in `Tools/Scripts/build/` or use PyInstaller directly:
   ```sh
   pyinstaller --onefile --windowed --add-data "assets;assets" --name "Jammin_Eats" main.py
   ```
2. Find your fresh-baked game in the `dist/` folder—ready to groove!

📝 **Dependencies**
- `pygame`
- `pyodbc` *(optional, for future database features)*
- `pytmx`
- `pyinstaller`
- See `Requirements.md` for details.

💻 **Platform**
- This project is tuned for **Windows** (PowerShell scripts, build process, etc.).

🌴 **Contributing & Community**

We're excited to collaborate! Feel free to open issues, submit pull requests, or suggest ideas. Join us in making Jammin' Eats a truly unforgettable gaming experience!

Stay irie, stay jammin'! 🌴🎵🍍🚚

We're excited to collaborate! Feel free to open issues, submit pull requests, or suggest ideas. Join us in making Jammin' Eats a truly unforgettable gaming experience!

Stay Jammin'! 🌴🎵🍍🚚
