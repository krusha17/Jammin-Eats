"""Database initialization module for Jammin' Eats.

This module creates the database file and required tables if they don't exist.
It should be run when the game starts to ensure all necessary database structures
are in place before any data access operations are attempted.
"""

import sqlite3
import os
from pathlib import Path

# Import logger if available
try:
    from src.debug.logger import log, log_error
except ImportError:
    def log(message): print(f"[LOG] {message}")
    def log_error(message): print(f"[ERROR] {message}")

# Path to the database file
DB_PATH = Path(__file__).parent.parent.parent / "data" / "jammin.db"

# SQL statements to create necessary tables
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS player_profile (
        player_id INTEGER PRIMARY KEY,
        display_name TEXT DEFAULT 'Player',
        high_score INTEGER DEFAULT 0,
        tutorial_complete INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS player_settings (
        setting_id INTEGER PRIMARY KEY,
        player_id INTEGER,
        music_volume REAL DEFAULT 0.7,
        sfx_volume REAL DEFAULT 1.0,
        fullscreen INTEGER DEFAULT 0,
        difficulty TEXT DEFAULT 'normal',
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS starting_stock (
        item_id INTEGER PRIMARY KEY,
        food_type TEXT,
        initial_quantity INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS upgrades_owned (
        upgrade_id INTEGER PRIMARY KEY,
        player_id INTEGER,
        upgrade_name TEXT,
        purchase_date TEXT,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_history (
        run_id INTEGER PRIMARY KEY,
        player_id INTEGER,
        score INTEGER,
        money_earned INTEGER,
        missed_deliveries INTEGER,
        run_date TEXT,
        duration_sec REAL,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """
]

# Default data to insert
DEFAULT_DATA = [
    # Player profile defaults
    "INSERT OR IGNORE INTO player_profile (player_id, display_name, high_score, tutorial_complete) "
    "VALUES (1, 'Player', 0, 0)",
    
    # Player settings defaults
    "INSERT OR IGNORE INTO player_settings (player_id, music_volume, sfx_volume, fullscreen) "
    "VALUES (1, 0.7, 1.0, 0)",
    
    # Starting stock defaults
    "INSERT OR IGNORE INTO starting_stock (food_type, initial_quantity) VALUES "
    "('burger', 10)",
    "INSERT OR IGNORE INTO starting_stock (food_type, initial_quantity) VALUES "
    "('pizza', 5)",
    "INSERT OR IGNORE INTO starting_stock (food_type, initial_quantity) VALUES "
    "('taco', 5)",
    "INSERT OR IGNORE INTO starting_stock (food_type, initial_quantity) VALUES "
    "('sushi', 3)"
]


def ensure_data_directory():
    """Ensure the data directory exists."""
    data_dir = DB_PATH.parent
    try:
        if not data_dir.exists():
            log(f"Data directory not found, creating: {data_dir}")
            data_dir.mkdir(parents=True, exist_ok=True)
            log(f"Created data directory: {data_dir}")
        else:
            log(f"Data directory exists at: {data_dir}")
        return True
    except Exception as e:
        log_error(f"Failed to create data directory: {e}")
        return False


def initialize_database():
    """Initialize the database with required tables."""
    # First ensure data directory exists
    if not ensure_data_directory():
        return False
    
    # Connect to database (creates file if it doesn't exist)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        for create_statement in CREATE_TABLES:
            try:
                cursor.execute(create_statement)
                log(f"Created table: {create_statement.split('EXISTS')[1].split('(')[0].strip()}")
            except sqlite3.Error as e:
                log_error(f"Failed to create table: {e}")
        
        # Insert default data
        for insert_statement in DEFAULT_DATA:
            try:
                cursor.execute(insert_statement)
            except sqlite3.Error as e:
                log_error(f"Failed to insert default data: {e}")
        
        conn.commit()
        conn.close()
        
        log(f"Database initialized successfully at {DB_PATH}")
        return True
    except sqlite3.Error as e:
        log_error(f"Database initialization failed: {e}")
        return False


def check_database_integrity():
    """Check if all required tables exist in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check each required table
        tables = [
            "player_profile", 
            "player_settings", 
            "starting_stock", 
            "upgrades_owned",
            "run_history"
        ]
        
        missing_tables = []
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                missing_tables.append(table)
        
        conn.close()
        
        if missing_tables:
            log_error(f"Missing tables: {', '.join(missing_tables)}")
            return False, missing_tables
        
        return True, None
    except sqlite3.Error as e:
        log_error(f"Database integrity check failed: {e}")
        return False, str(e)


# For direct execution
if __name__ == "__main__":
    initialize_database()
    integrity, missing = check_database_integrity()
    if integrity:
        print("Database is ready for use.")
    else:
        print(f"Database issues detected: {missing}")
