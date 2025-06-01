# Jammin' Eats: Phase 4 - Persistence & Meta-Progression

## Overview

This document outlines the persistence layer for Jammin' Eats, which will store player progress, upgrades, settings, and run history. The persistence layer uses SQLite for local storage with a clean data access layer and migration system.

## Database Schema

### Entity-Relationship Diagram

```
+------------------+     +-------------------+     +----------------+
| player_profile   |     | upgrades_owned    |     | player_settings|
+------------------+     +-------------------+     +----------------+
| player_id (PK)   |<-+  | player_id (FK)    |     | id (PK)        |
| display_name     |  |  | upg_id (PK,FK)    |     | starting_money |
| high_score       |  |  | acquired_at       |     | max_stock      |
+------------------+  |  +-------------------+     | tutorial_mode  |
                      |                            +----------------+
                      |
                      |  +-------------------+     +----------------+
                      |  | run_history       |     | starting_stock |
                      +->+-------------------+     +----------------+
                         | run_id (PK)       |     | food (PK)      |
                         | player_id (FK)    |     | qty            |
                         | score             |     +----------------+
                         | money_earned      |
                         | missed            |
                         | duration_sec      |
                         | run_date          |
                         +-------------------+
```

### Tables Definition (DDL)

```sql
-- Player Profile table - Stores basic player information
CREATE TABLE player_profile (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT DEFAULT 'Player',
    high_score INTEGER DEFAULT 0
);

-- Player Settings table - Global settings affecting gameplay
CREATE TABLE player_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensure single row
    starting_money INTEGER DEFAULT 0,
    max_stock INTEGER DEFAULT 10,
    tutorial_mode BOOLEAN DEFAULT 1
);

-- Starting Stock table - Default inventory configuration
CREATE TABLE starting_stock (
    food TEXT PRIMARY KEY,
    qty INTEGER DEFAULT 5,
    CONSTRAINT positive_qty CHECK (qty >= 0)
);

-- Upgrades Owned table - Tracks purchased upgrades
CREATE TABLE upgrades_owned (
    player_id INTEGER,
    upg_id TEXT,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, upg_id),
    FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    -- Note: upg_id foreign key is conceptual, refers to constants.py UPGRADE_DATA
);

-- Run History table - Game session analytics
CREATE TABLE run_history (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    score INTEGER DEFAULT 0,
    money_earned INTEGER DEFAULT 0,
    missed INTEGER DEFAULT 0,
    duration_sec REAL DEFAULT 0.0,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
);

-- Indexes for faster queries
CREATE INDEX idx_run_history_player_score ON run_history(player_id, score DESC);
CREATE INDEX idx_run_history_date ON run_history(run_date DESC);
```

## Data Flow

### Loading Game State
1. Game initialization queries `player_settings` for global defaults
2. Inventory is populated based on `starting_stock`
3. `upgrades_owned` determines available modifiers
4. Game applies all upgrades effects from owned upgrades

### Saving Game State
1. When a run ends, statistics are recorded in `run_history`
2. If high score is beaten, `player_profile` is updated
3. When upgrades are purchased, `upgrades_owned` is updated

### High Score Handling
1. After each run, score is compared with `player_profile.high_score`
2. If higher, the new score becomes the player's high score
3. Leaderboard screen displays top scores from `run_history`

## Migration System

Alembic will be used for database migrations:

1. Initial migration creates the schema described above
2. Migration scripts are stored in `migrations/` directory
3. Upgrade and downgrade paths support schema evolution over time

## Security Considerations

1. All database queries use parameterized queries to prevent SQL injection
2. Database file is stored in user's application data folder for proper permissions
3. Backup system creates copies of the database on graceful shutdown

## Performance Optimizations

1. Connection pooling minimizes overhead
2. Indexes on frequently queried fields (`run_history.player_id`, `run_history.run_date`)
3. In-memory caching of frequently accessed data (player profile, owned upgrades)

## Integration Points

The database layer integrates with:

1. **Game Initialization**: Loading starting money, inventory stock
2. **UpgradeManager**: Loading owned upgrades, saving new purchases
3. **Game Over**: Recording run statistics
4. **Leaderboard UI**: Displaying high scores
