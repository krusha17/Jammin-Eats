-- Migration: init
-- Version: 1
-- Created: 2025-06-01 00:32:00

--UP--
-- Player Profile table - Stores basic player information
CREATE TABLE player_profile (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT DEFAULT 'Player',
    high_score INTEGER DEFAULT 0
);

-- Insert default player
INSERT INTO player_profile (player_id, display_name, high_score)
VALUES (1, 'Player', 0);

-- Player Settings table - Global settings affecting gameplay
CREATE TABLE player_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensure single row
    starting_money INTEGER DEFAULT 0,
    max_stock INTEGER DEFAULT 10,
    tutorial_mode BOOLEAN DEFAULT 1
);

-- Insert default settings
INSERT INTO player_settings (id, starting_money, max_stock, tutorial_mode)
VALUES (1, 0, 10, 1);

-- Starting Stock table - Default inventory configuration
CREATE TABLE starting_stock (
    food TEXT PRIMARY KEY,
    qty INTEGER DEFAULT 5,
    CONSTRAINT positive_qty CHECK (qty >= 0)
);

-- Insert default starting stock
INSERT INTO starting_stock (food, qty) VALUES ('Tropical Pizza', 5);
INSERT INTO starting_stock (food, qty) VALUES ('Ska Smoothie', 5);
INSERT INTO starting_stock (food, qty) VALUES ('Island Ice Cream', 5);

-- Upgrades Owned table - Tracks purchased upgrades
CREATE TABLE upgrades_owned (
    player_id INTEGER,
    upg_id TEXT,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, upg_id),
    FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
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

--DOWN--
DROP INDEX IF EXISTS idx_run_history_date;
DROP INDEX IF EXISTS idx_run_history_player_score;
DROP TABLE IF EXISTS run_history;
DROP TABLE IF EXISTS upgrades_owned;
DROP TABLE IF EXISTS starting_stock;
DROP TABLE IF EXISTS player_settings;
DROP TABLE IF EXISTS player_profile;
