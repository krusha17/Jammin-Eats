"""
Fix the database schema for Jammin' Eats
"""

import os
import sqlite3


def main():
    print("\n===== FIXING DATABASE SCHEMA =====")

    # Define database path
    db_path = "data/jammin.db"
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

    print(f"Database path: {full_path}")

    # Check if file exists
    if not os.path.exists(full_path):
        print(f"ERROR: Database file does not exist: {full_path}")
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")

    # Try connecting to database
    try:
        print("\nConnecting to database...")
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        print("- Connection successful")

        # Backup existing data
        print("- Backing up player_profile data...")
        cursor.execute("SELECT * FROM player_profile")
        existing_data = cursor.fetchall()
        print(f"- Found {len(existing_data)} player records")
        if existing_data:
            # Get column names
            cursor.execute("PRAGMA table_info(player_profile)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"- Current columns: {columns}")

        # Check if we need to fix the table
        if "id" not in [col.lower() for col in columns]:
            print("- The 'id' column is missing, recreating the table...")

            # Drop and recreate the table with the correct schema
            try:
                print("- Creating temporary table...")
                cursor.execute(
                    "CREATE TABLE player_profile_temp (id INTEGER PRIMARY KEY, name TEXT NOT NULL, tutorial_complete INTEGER DEFAULT 0)"
                )

                # Copy data if possible
                if "name" in columns and "tutorial_complete" in columns:
                    print("- Migrating existing data...")
                    name_index = columns.index("name")
                    tutorial_index = columns.index("tutorial_complete")

                    for i, record in enumerate(existing_data):
                        name = (
                            record[name_index] if len(record) > name_index else "Player"
                        )
                        tutorial = (
                            record[tutorial_index]
                            if len(record) > tutorial_index
                            else 0
                        )
                        cursor.execute(
                            "INSERT INTO player_profile_temp (id, name, tutorial_complete) VALUES (?, ?, ?)",
                            (i + 1, name, tutorial),
                        )

                # Drop the old table and rename the new one
                print("- Replacing old table with new one...")
                cursor.execute("DROP TABLE player_profile")
                cursor.execute(
                    "ALTER TABLE player_profile_temp RENAME TO player_profile"
                )
                conn.commit()
                print("- Table structure fixed successfully")

            except sqlite3.OperationalError as e:
                print(f"- ERROR updating table structure: {e}")
                conn.rollback()
        else:
            print("- Table structure is correct, no changes needed")

        # Verify the table structure
        cursor.execute("PRAGMA table_info(player_profile)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"- Current columns: {columns}")

        # Ensure we have at least one player record
        cursor.execute("SELECT COUNT(*) FROM player_profile")
        count = cursor.fetchone()[0]

        if count == 0:
            print("- No player records found, creating default player...")
            cursor.execute(
                "INSERT INTO player_profile (id, name, tutorial_complete) VALUES (1, 'Player', 0)"
            )
            conn.commit()
            print("- Created default player record")

        # Check tutorial completion status
        cursor.execute("SELECT id, tutorial_complete FROM player_profile")
        players = cursor.fetchall()
        for player in players:
            player_id, tutorial_status = player
            print(
                f"- Player ID: {player_id}, Tutorial completed: {bool(tutorial_status)}"
            )

        # Reset tutorial status for testing
        print("\nResetting tutorial completion status for all players...")
        cursor.execute("UPDATE player_profile SET tutorial_complete = 0")
        conn.commit()
        print("- Tutorial status reset")

        # Close connection
        conn.close()

    except Exception as e:
        print(f"- ERROR: {e}")

    print("\n===== DATABASE FIX COMPLETE =====")


if __name__ == "__main__":
    main()
