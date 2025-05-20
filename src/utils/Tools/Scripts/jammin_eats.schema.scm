-- 1. Players Table
CREATE TABLE IF NOT EXISTS player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Game Session Table
CREATE TABLE IF NOT EXISTS game_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    final_score INTEGER DEFAULT 0,
    deliveries_made INTEGER DEFAULT 0,
    customers_missed INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0,
    FOREIGN KEY(player_id) REFERENCES player(player_id)
);

-- 3. Food Log Table (each food thrown during a session)
CREATE TABLE IF NOT EXISTS food_throw (
    food_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('pizza', 'smoothie', 'icecream', 'pudding')),
    name TEXT NOT NULL,
    thrown_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hit_customer BOOLEAN DEFAULT 0,
    matched_preference BOOLEAN DEFAULT 0,
    points_awarded INTEGER DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES game_session(session_id)
);

-- 4. Customer Interaction Table
CREATE TABLE IF NOT EXISTS customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    food_preference TEXT NOT NULL CHECK(food_preference IN ('pizza', 'smoothie', 'icecream', 'pudding')),
    patience_seconds REAL NOT NULL,
    expired BOOLEAN DEFAULT 0,
    fed BOOLEAN DEFAULT 0,
    fed_with TEXT,
    fed_at DATETIME,
    points_received INTEGER DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES game_session(session_id)
);
