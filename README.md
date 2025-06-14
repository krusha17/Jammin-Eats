🎮 Jammin' Eats

A Neon-Retro, Reggae-Cyberpunk Food Delivery Adventure!

Welcome to Jammin' Eats, a vibrant and exciting 2D top-down game set in a neon-lit futuristic beach city where reggae rhythms blend harmoniously with cyberpunk aesthetics. Inspired by classic arcade games like Paperboy, Jammin' Eats offers immersive gameplay, dynamic animation, and an infectious tropical vibe!

## 🚀 Current State (0.9.4-alpha)

**Professional Game Development Setup**
- ✅ **Pre-commit Hooks**: Fully functional for both CLI and GUI Git operations
- ✅ **Code Quality**: Ruff (linting), Black (formatting), Pylint (static analysis), MyPy (type checking)
- ✅ **Testing Suite**: Comprehensive tests with robust fixtures and mocking
- ✅ **Modular Architecture**: Clean separation of concerns following game dev best practices
- ✅ **Database Integration**: Complete schema with persistence and migration system

**Game Features**
- Complete database schema with all required tables (player_profile, save_games)
- Robust migration system for schema updates  
- Title Screen menu with full functionality (New Game, Continue, Load, Options, Quit)
- Tutorial system with graduation mechanics and persistent completion tracking
- Modular code architecture with clear separation of game systems
- Comprehensive error handling and fallback systems
- Asset loading system with graceful degradation

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git for Windows (with Unix shell tools)
- Visual Studio Code or preferred IDE

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/Jammin-Eats.git
   cd Jammin-Eats
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Run the game:**
   ```bash
   python main.py
   ```

### Development Workflow

**Code Quality & Testing**
- Pre-commit hooks automatically run on every commit (CLI and GUI)
- All code passes Ruff linting, Black formatting, Pylint analysis, and MyPy type checking
- Run tests with: `python -m pytest tests/`
- Debug mode available with: `python debug_main.py`

**Professional Standards**
- Follow "vertical slice" game development approach
- Logic-first development with incremental testing
- Comprehensive error handling and fallback systems
- Modular, maintainable code structure

## 🎯 Tutorial System

Jammin' Eats features a comprehensive **Tutorial System** that guides new players through game mechanics:

### Tutorial Mechanics
- **Forgiving Learning Environment**: Wrong food selections don't cause game over
- **No Time Pressure**: Timer visible but no penalties for slow play  
- **Free Economy**: All food is free during tutorial phase
- **Clear Goals**: Serve 5 customers correctly OR earn $50

### Progression System
- Tutorial completion persists in database
- Automatic graduation to main game
- Title screen adapts based on player progress
- One-time tutorial experience per player

## 🏗️ Architecture

### Project Structure
```
Jammin-Eats/
├── .venv/                 # Python virtual environment
├── assets/                # Game assets (sprites, sounds, maps)
│   ├── Food/             # Food item sprites
│   ├── sprites/          # Character and UI sprites  
│   ├── sounds/           # Audio files
│   └── Maps/             # TMX map files
├── src/                  # Modular source code
│   ├── core/            # Core game engine
│   ├── sprites/         # Game entities
│   ├── ui/              # User interface
│   ├── utils/           # Utility functions
│   └── debug/           # Development tools
├── tests/               # Comprehensive test suite
├── docs/                # Documentation (guides, technical docs, Archive/ for legacy)
├── data/                # Database files
├── .pre-commit-config.yaml  # Code quality automation
├── mypy.ini             # Type checking configuration
├── .pylintrc            # Static analysis rules
└── pyproject.toml       # Project configuration
```

### Core Systems
- **State Machine**: Clean transitions between game states
- **Data Access Layer**: Robust database operations with error handling
- **Asset Loader**: Centralized loading with fallback capabilities
- **Game Renderer**: Modular rendering system
- **Debug Tools**: Comprehensive diagnostics and validation

## 🎮 Game Features

### Gameplay Mechanics
- **Directional Movement**: Smooth, responsive controls with dynamic animations
- **Food Delivery System**: Throw various reggae-themed dishes to customers
- **Customer AI**: Diverse characters with unique preferences and behaviors
- **Economy System**: Money management and progression tracking

### Technical Highlights
- **Pixel-Perfect Graphics**: Neon-cyberpunk and tropical aesthetics
- **Robust Error Handling**: Graceful degradation for missing assets
- **Database Integration**: Persistent player profiles and game state
- **Modular Design**: Clean, maintainable, and extensible codebase

## 🧪 Testing & Quality Assurance

### Testing Framework
- **Comprehensive Suite**: Unit and integration tests for all core systems
- **Robust Mocking**: Isolated testing of game components
- **CI/CD Ready**: Pre-commit hooks ensure code quality
- **Debug Tools**: Enhanced diagnostics and validation utilities

### Code Quality Standards
- **Linting**: Ruff for Python code analysis
- **Formatting**: Black for consistent code style  
- **Type Checking**: MyPy for static type analysis
- **Static Analysis**: Pylint for code quality metrics

## 🚧 Current Development Focus

**Completed Milestones**
- ✅ Core system architecture and modularization
- ✅ Tutorial system with persistent completion
- ✅ Database schema and migration system
- ✅ Pre-commit hooks and code quality automation
- ✅ Comprehensive testing infrastructure

**In Progress**
- 🔄 Title → Gameplay transition improvements
- 🔄 Asset integration and map loading optimization
- 🔄 HUD and inventory system enhancements

**Future Plans**
- 📋 Advanced customer AI and behavior systems
- 📋 Enhanced visual effects and animation
- 📋 Sound system integration
- 📋 Performance optimization and polish

## 🤝 Contributing

We follow professional game development standards:

1. **Fork** the repository
2. **Create** a feature branch
3. **Write** tests for new features
4. **Ensure** pre-commit hooks pass
5. **Submit** a pull request

All contributions are automatically validated through our pre-commit hook system.

## 📊 Technical Requirements

### Dependencies
- `pygame` - Game engine
- `pytmx` - TMX map loading
- `pyodbc` - Database connectivity (optional)
- `pre-commit` - Code quality automation
- `pytest` - Testing framework

### Platform Support
- **Primary**: Windows 10/11
- **Python**: 3.8+
- **Git**: Required for development workflow

## 🎵 Game Universe

In Jammin' Eats, you play as **Kai Irie**, a reggae-loving food truck driver delivering culturally diverse dishes across a vibrant cyberpunk beach city. Navigate through neon-lit streets, serve unique customers, and groove to the rhythm while building your food delivery empire!

### Featured Dishes
- 🍕 Tropical Pizza Slice
- 🥤 Ska Smoothie  
- 🍚 Rasta Rice Pudding
- 🍦 Island Ice Cream
- 🥟 Reggae Rasgulla

---

**Stay irie, stay jammin'! 🌴🎵🍍🚚**

> **Note**: This project follows professional game development best practices with a "vertical slice" approach. See documentation in `docs/` for detailed implementation guides and development processes.
