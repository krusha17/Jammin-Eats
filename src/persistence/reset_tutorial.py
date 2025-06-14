"""
Reset the tutorial flag for Jammin' Eats.

This script sets tutorial_complete = 0 for id = 1 in the jammin.db database,
so the tutorial will run again on next game launch.
"""

import sqlite3
from pathlib import Path

# Use the same DB_PATH as in dal.py/db_init.py

# Set DB_PATH to the absolute path of the database file at the project root data directory
DB_PATH = Path(__file__).parent.parent.parent / "data" / "jammin.db"


def reset_tutorial_flag(player_id=1):
    import os

    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Is the game initialized?")
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE player_profile SET tutorial_complete = 0 WHERE id = ?", (player_id,)
        )
        conn.commit()
        conn.close()
        print(
            f"Tutorial flag reset for player_id={player_id}. Tutorial will play on next launch."
        )
        return True
    except Exception as e:
        print(f"Error resetting tutorial flag: {e}")
        return False


if __name__ == "__main__":
    reset_tutorial_flag()
