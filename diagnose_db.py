"""
Database diagnostic script for Jammin' Eats
Checks database connection, tables, schema, and attempts basic operations
"""

import os
import sqlite3
import sys
from pathlib import Path

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run database diagnostics"""
    print("=" * 50)
    print("JAMMIN' EATS DATABASE DIAGNOSTIC")
    print("=" * 50)
    
    # Check if database file exists
    db_path = Path("data/jammin.db")
    print(f"DB Path: {db_path.absolute()}")
    print(f"DB Exists: {db_path.exists()}")
    
    # Create database connection
    try:
        print("\nAttempting direct SQLite connection...")
        conn = sqlite3.connect(str(db_path.absolute()))
        cursor = conn.cursor()
        print("Connection successful!")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in database ({len(tables)}):")
        for table in tables:
            print(f"- {table[0]}")
            # Show schema for each table
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"  Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        # Check if player_profile exists and has required fields
        print("\nChecking player_profile table...")
        if ('player_profile',) in tables:
            cursor.execute("PRAGMA table_info(player_profile)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Fields: {', '.join(column_names)}")
            
            # Check for the money column specifically
            if 'money' in column_names:
                print("'money' column found in player_profile")
            else:
                print("WARNING: 'money' column NOT found in player_profile")
                
            # Check tutorial completion column
            if 'tutorial_completed' in column_names:
                print("'tutorial_completed' column found in player_profile")
            else:
                print("WARNING: 'tutorial_completed' column NOT found in player_profile")
        else:
            print("WARNING: player_profile table not found!")
        
        # Try getting player profile data
        print("\nAttempting to read player_profile data...")
        try:
            cursor.execute("SELECT * FROM player_profile LIMIT 1")
            row = cursor.fetchone()
            if row:
                print(f"Found player profile: {row}")
            else:
                print("No player profiles found in database")
        except sqlite3.OperationalError as e:
            print(f"Error reading player_profile: {e}")
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
    # Try using the DAL for comparison
    try:
        print("\nAttempting connection via DAL...")
        from src.persistence.dal import DataAccessLayer
        dal = DataAccessLayer()
        print("DAL initialized successfully")
        
        # Try checking tutorial completion
        from src.persistence.dal import is_tutorial_complete
        try:
            result = is_tutorial_complete()
            print(f"Tutorial completion check: {result}")
        except Exception as e:
            print(f"Error checking tutorial completion: {e}")
            
        # Try resetting player progress
        try:
            print("\nTesting reset_player_progress...")
            result = dal.reset_player_progress()
            print(f"Reset player progress: {'Success' if result else 'Failed'}")
        except Exception as e:
            print(f"Error in reset_player_progress: {e}")
            
    except ImportError as e:
        print(f"Import error with DAL: {e}")
    except Exception as e:
        print(f"Error using DAL: {e}")

if __name__ == "__main__":
    main()
