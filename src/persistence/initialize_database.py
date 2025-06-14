#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats Database Initializer

This script creates the database and initializes all required tables
for the Jammin' Eats game. Run this script before starting the game
for the first time.
"""

import sqlite3
from pathlib import Path

# Ensure data directory exists
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Path to the database file
DB_PATH = data_dir / "jammin.db"


def initialize_database():
    """Create database and initialize all tables."""
    print(f"Initializing database at {DB_PATH}...")

    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create player_profile table with tutorial_complete column
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS player_profile (
        player_id INTEGER PRIMARY KEY,
        display_name TEXT NOT NULL,
        high_score INTEGER DEFAULT 0,
        tutorial_complete INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # Create player_settings table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS player_settings (
        setting_id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        music_volume REAL DEFAULT 0.7,
        sfx_volume REAL DEFAULT 0.7,
        fullscreen INTEGER DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """
    )

    # Create starting_stock table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS starting_stock (
        stock_id INTEGER PRIMARY KEY,
        food_type TEXT NOT NULL,
        quantity INTEGER DEFAULT 5,
        price INTEGER DEFAULT 50
    )
    """
    )

    # Create upgrades_owned table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS upgrades_owned (
        upgrade_id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        upgrade_name TEXT NOT NULL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """
    )

    # Create run_history table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS run_history (
        run_id INTEGER PRIMARY KEY,
        player_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        money_earned INTEGER NOT NULL,
        missed_deliveries INTEGER DEFAULT 0,
        duration_sec INTEGER NOT NULL,
        run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """
    )

    # Insert default player if not exists
    cursor.execute(
        """
    INSERT OR IGNORE INTO player_profile (player_id, display_name, high_score, tutorial_complete)
    VALUES (1, 'Player', 0, 0)
    """
    )

    # Insert default food stock items
    food_types = [
        ("Tropical Pizza Slice", 5, 50),
        ("Ska Smoothie", 5, 40),
        ("Island Ice Cream", 5, 30),
        ("Rasta Rice Pudding", 5, 35),
    ]

    cursor.execute("DELETE FROM starting_stock")
    for food_type, quantity, price in food_types:
        cursor.execute(
            """
        INSERT INTO starting_stock (food_type, quantity, price)
        VALUES (?, ?, ?)
        """,
            (food_type, quantity, price),
        )

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database initialization complete!")


if __name__ == "__main__":
    initialize_database()
