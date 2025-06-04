"""
Super simple database check - no dependencies on logging
"""
import os
import sys
import sqlite3

def main():
    print("\n===== SIMPLE DATABASE CHECK =====")
    
    # Define database path
    db_path = "data/jammin.db"
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
    
    print(f"Database path: {full_path}")
    
    # Check if file exists
    if os.path.exists(full_path):
        print(f"- Database file EXISTS: {full_path}")
        print(f"- Size: {os.path.getsize(full_path)} bytes")
    else:
        print(f"- Database file DOES NOT EXIST: {full_path}")
        
        # Check if directory exists and try to create it
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            print(f"- Creating directory: {dir_path}")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"- Directory created successfully")
            except Exception as e:
                print(f"- ERROR creating directory: {e}")
    
    # Try connecting to database
    try:
        print("\nAttempting to connect to database...")
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        print("- Connection successful")
        
        # Check for player_profile table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'")
        result = cursor.fetchone()
        if result:
            print("- player_profile table EXISTS")
            
            # Check tutorial_complete column
            try:
                cursor.execute("SELECT tutorial_complete FROM player_profile WHERE id=1")
                result = cursor.fetchone()
                if result is not None:
                    print(f"- Tutorial complete value: {bool(result[0])}")
                else:
                    print("- No player with id=1 found")
                    print("- Creating default player record...")
                    cursor.execute("INSERT INTO player_profile (id, name, tutorial_complete) VALUES (1, 'Player', 0)")
                    conn.commit()
                    print("- Default player created")
            except sqlite3.OperationalError as e:
                print(f"- ERROR querying player_profile: {e}")
        else:
            print("- player_profile table DOES NOT EXIST")
            
            # Create the table
            print("- Creating player_profile table...")
            try:
                cursor.execute("""
                CREATE TABLE player_profile (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    tutorial_complete INTEGER DEFAULT 0
                )
                """)
                conn.commit()
                print("- Created player_profile table")
                
                # Insert default player
                cursor.execute("INSERT INTO player_profile (id, name, tutorial_complete) VALUES (1, 'Player', 0)")
                conn.commit()
                print("- Created default player record")
            except sqlite3.OperationalError as e:
                print(f"- ERROR creating table: {e}")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"- ERROR connecting to database: {e}")
    
    print("\n===== CHECK COMPLETE =====")

if __name__ == "__main__":
    main()
