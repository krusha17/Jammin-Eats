# Jammin' Eats: Phase 3 Design - Progression & Upgrades

## Overview

The progression and upgrade system allows players to invest earnings into permanent improvements,
driving engagement through progression and customization while providing economic depth to the game.

## Upgrade Catalog

| ID | Item | Effect | Cost ($) | Prereq |
|----|------|--------|----------|--------|
| UP_SKATE | Skateboard | +25% player speed | 150 | — |
| UP_BLADE | Rollerblades | +25% player speed (stack) | 200 | UP_SKATE |
| UP_JETS | Jet-powered Skates | +50% player speed (stack) | 350 | UP_BLADE |
| UP_TRUCK | Food-truck rooftop table | +5 MAX_STOCK | 300 | — |
| UP_FRIDGE | Refrigerated Storage | +5 MAX_STOCK | 450 | UP_TRUCK |
| UP_FREEZE | Industrial Freezer | +10 MAX_STOCK | 600 | UP_FRIDGE |
| UP_BAG | Insulated Delivery Bag | +2s food lifespan | 200 | — |
| UP_CART | Serving Cart | -25% customer patience decay | 250 | — |

## Economic Balance

### Target Progression Metrics

- Average earnings per game session: $100-150
- First upgrade (UP_SKATE) attainable after ~1-2 good game sessions
- Most expensive upgrade (UP_FREEZE) attainable after ~15-20 cumulative sessions
- Mid-tier upgrades (UP_TRUCK, UP_BAG) attainable after ~3-5 sessions

### Player Experience Goals

- Early progress feels rewarding (first upgrade within 15-20 minutes of play)
- Steady sense of progression with each game session adding meaningful progress
- Clear visual feedback when upgrades are applied
- Strategic choices between different upgrade paths

## UI Design

### Shop Interface

- Accessible by pressing 'B' key during gameplay
- Pauses game and dims the background
- Displays all available upgrades with:
  - Name and description
  - Cost
  - Current effect
  - Prerequisites (if any)
- Color-coding:
  - Owned: Green
  - Available and affordable: White
  - Available but too expensive: Yellow
  - Locked (missing prerequisites): Gray
- Can be closed with 'B' key, 'ESC' key, or clicking the close button
## Implementation Details

### Core Components

1. **Upgrade Data**
   - Defined in `constants.py` as `UPGRADE_DATA` dictionary
   - Each upgrade entry includes ID, name, description, cost, modifiers, and prerequisites
   - Modifiers affect player speed, inventory capacity, food lifespan, and customer patience

2. **UpgradeManager Class**
   - Located in `src/core/upgrade_manager.py`
   - Handles tracking owned upgrades
   - Provides methods for querying upgrades (owned, available, affordable)
   - Handles purchase logic with prerequisite checking
   - Applies upgrade effects to game object

3. **Shop UI**
   - Implemented in `src/ui/shop.py`
   - `ShopOverlay` class manages the shop interface
   - `ShopButton` class represents individual upgrade buttons
   - Toggle with 'B' key during gameplay
   - Visual feedback on upgrade status (owned, affordable, locked)

4. **Game Integration**
   - Game class initializes UpgradeManager and ShopOverlay
   - Upgrades persist between game sessions (not reset on restart)
   - Upgrade effects applied to game state and player
   - Economic integration for purchase transactions

### Testing

- Comprehensive unit tests in `tests/test_upgrade_manager.py`
- Tests cover initialization, ownership checks, availability, affordability, and purchases

### Future Enhancements

- Persistent storage of owned upgrades via database (Phase 4)
- Visual icons for upgrades
- Sound effects for purchases
- Particle effects for upgrade application

### Visual Feedback

- Player character visual changes with movement upgrades
- HUD elements update to reflect new capacities
- Brief celebratory animation when upgrade purchased

## Implementation Notes

- All upgrades should persist between game sessions
- Upgrades should be stackable where appropriate
- Code should be data-driven to easily add new upgrades
- Maintain upgrade balance with the economy system
