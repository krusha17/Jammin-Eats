"""
Complete database fix script for Jammin' Eats

This script:
1. Backs up the existing database (if any)
2. Creates a completely new database with the correct schema
3. Initializes default data using the corrected column names
"""

import sqlite3
import os
import shutil
from pathlib import Path
import time

# Path to the database
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "jammin.db"

# Ensure data directory exists
if not DB_DIR.exists():
    print(f"Creating data directory at {DB_DIR}")
    DB_DIR.mkdir(parents=True, exist_ok=True)

# Backup existing database if it exists
if DB_PATH.exists():
    backup_path = DB_PATH.with_name(f"jammin_backup_{int(time.time())}.db")
    print(f"Backing up existing database to {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print("Backup complete")

    # Remove existing database
    print(f"Removing existing database {DB_PATH}")
    os.remove(DB_PATH)

# Create new database with correct schema
print(f"Creating new database at {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables with correct schema
print("Creating tables with correct schema...")

# Player profile table
cursor.execute("""
CREATE TABLE IF NOT EXISTS player_profile (
    id INTEGER PRIMARY KEY,
    name TEXT DEFAULT 'Player',
    high_score INTEGER DEFAULT 0,
    tutorial_complete INTEGER DEFAULT 0
)
""")
print("✓ Created player_profile table")

# Player settings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS player_settings (
    setting_id INTEGER PRIMARY KEY,
    player_id INTEGER,
    music_volume REAL DEFAULT 0.7,
    sfx_volume REAL DEFAULT 1.0,
    fullscreen INTEGER DEFAULT 0,
    difficulty TEXT DEFAULT 'normal',
    FOREIGN KEY (player_id) REFERENCES player_profile(id)
)
""")
print("✓ Created player_settings table")

# Starting stock table
cursor.execute("""
CREATE TABLE IF NOT EXISTS starting_stock (
    item_id INTEGER PRIMARY KEY,
    food_type TEXT,
    initial_quantity INTEGER DEFAULT 0
)
""")
print("✓ Created starting_stock table")

# Upgrades owned table
cursor.execute("""
CREATE TABLE IF NOT EXISTS upgrades_owned (
    upgrade_id INTEGER PRIMARY KEY,
    player_id INTEGER,
    upgrade_name TEXT,
    purchase_date TEXT,
    FOREIGN KEY (player_id) REFERENCES player_profile(id)
)
""")
print("✓ Created upgrades_owned table")

# Run history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS run_history (
    run_id INTEGER PRIMARY KEY,
    player_id INTEGER,
    score INTEGER,
    money_earned INTEGER,
    missed_deliveries INTEGER,
    run_date TEXT,
    duration_sec REAL,
    FOREIGN KEY (player_id) REFERENCES player_profile(id)
)
""")
print("✓ Created run_history table")

# Insert default data
print("Inserting default data...")

# Player profile defaults
cursor.execute("""
INSERT INTO player_profile (id, name, high_score, tutorial_complete)
VALUES (1, 'Player', 0, 0)
""")
print("✓ Inserted default player profile")

# Player settings defaults
cursor.execute("""
INSERT INTO player_settings (player_id, music_volume, sfx_volume, fullscreen)
VALUES (1, 0.7, 1.0, 0)
""")
print("✓ Inserted default player settings")

# Starting stock defaults
cursor.execute("INSERT INTO starting_stock (food_type, initial_quantity) VALUES ('burger', 10)")
cursor.execute("INSERT INTO starting_stock (food_type, initial_quantity) VALUES ('pizza', 5)")
cursor.execute("INSERT INTO starting_stock (food_type, initial_quantity) VALUES ('taco', 5)")
cursor.execute("INSERT INTO starting_stock (food_type, initial_quantity) VALUES ('sushi', 3)")
print("✓ Inserted default starting stock")

# Commit changes and close
conn.commit()
conn.close()

print("\nDatabase created successfully with correct schema and default data.")
print(f"Database location: {DB_PATH}")

# Mark tutorial as incomplete to force it to run next time
print("\nResetting tutorial completion status...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("UPDATE player_profile SET tutorial_complete = 0 WHERE id = 1")
conn.commit()
conn.close()
print("✓ Tutorial reset to incomplete state. Tutorial will run on next game launch.")

print("\nComplete! You can now launch the game again.")
