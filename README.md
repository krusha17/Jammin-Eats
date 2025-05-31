🎮 Jammin' Eats

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

💡 Technical Highlights

Developed using Python and Pygame, ensuring fluid gameplay and easy scalability.
Integrated particle effects and visual indicators for enhanced player feedback.
Structured for future database integration using SQL Server (SSMS) and PyODBC, enabling robust game state management.

🎨 Visual & Artistic Direction

Pixel-Perfect Graphics: Stunning top-down pixel art infused with neon-cyberpunk and tropical island aesthetics.
Vibrant, Seamless Environments: Procedurally generated backgrounds and assets designed to scale effortlessly.
Reggae-Cyberpunk Theme: Unique visual identity inspired by retro arcade classics, with a futuristic twist.

🛠️ Current Development State

Fully playable prototype with core gameplay loops established.
Complete sprite animation system for main character and customers.
Functional game states including start menu, gameplay, and score tracking.

📌 Future Development Goals

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

🔄 **Development Workflow**

We follow a professional branching strategy to ensure code quality and collaboration:

- `main`: Production-ready code only. Stable releases with version tags.
- `develop`: Integration branch where completed features are combined.
- `test`: QA branch for testing before merging to main.
- `feature/<name>`: For developing new features (e.g., `feature/new-enemy-type`).
- `bugfix/<name>`: For fixing specific bugs.
- `hotfix/<name>`: For critical fixes to production code.

**Workflow for Contributors:**

1. Create a new feature or bugfix branch from `develop`.
2. Implement your changes with descriptive commits.
3. Open a Pull Request to the `develop` branch.
4. After code review and approval, your code will be merged.
5. Periodically, `develop` is merged to `test` for QA.
6. Once tested, changes are merged to `main` and tagged with a version.

We're excited to collaborate! Feel free to open issues, submit pull requests, or suggest ideas. Join us in making Jammin' Eats a truly unforgettable gaming experience!

Stay Jammin'! 🌴🎵🍍🚚
