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

# Path to the database file - improved path detection
DB_PATH = None

# Try multiple possible locations to find or create the database
def get_database_path():
    global DB_PATH
    # Try the proper project structure first
    project_root = Path(__file__).parent.parent.parent
    # Ensure data directory exists
    data_dir = project_root / "data"
    
    try:
        # Print the paths being checked to help with debugging
        log(f"Checking project root at: {project_root}")
        log(f"Looking for data directory at: {data_dir}")
        
        # Ensure data directory exists
        if not data_dir.exists():
            log(f"Data directory not found, creating: {data_dir}")
            data_dir.mkdir(parents=True, exist_ok=True)
            log(f"Created data directory: {data_dir}")
        
        # Set the database path
        db_path = data_dir / "jammin.db"
        log(f"Database path set to: {db_path}")
        
        return db_path
    except Exception as e:
        log_error(f"Failed to configure database path: {e}")
        # Fallback to current working directory
        fallback = Path.cwd() / "jammin.db"
        log(f"Using fallback database path: {fallback}")
        return fallback

# Initialize the path at module load time
DB_PATH = get_database_path()

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
    global DB_PATH
    
    # Make sure we have a valid database path
    if DB_PATH is None:
        DB_PATH = get_database_path()
        log(f"Reset database path to: {DB_PATH}")
    
    # Connect to database (creates file if it doesn't exist)
    try:
        log(f"Attempting to connect to database at: {DB_PATH}")
        conn = sqlite3.connect(str(DB_PATH))  # Convert Path to string for sqlite3
        cursor = conn.cursor()
        log("Database connection established successfully")
        
        # Create tables with better error handling
        for create_statement in CREATE_TABLES:
            try:
                # Extract table name for logging
                table_name = create_statement.split('EXISTS')[1].split('(')[0].strip() if 'EXISTS' in create_statement else "unknown table"
                log(f"Creating table: {table_name}")
                
                cursor.execute(create_statement)
                log(f"✓ Created table: {table_name}")
            except sqlite3.Error as e:
                log_error(f"Failed to create table {table_name}: {e}")
                # Continue with other tables rather than failing entirely
        
        # Insert default data with better error handling
        for insert_statement in DEFAULT_DATA:
            try:
                # Extract table name for better logging
                table_name = "unknown"
                if "INTO" in insert_statement:
                    table_name = insert_statement.split("INTO")[1].split("(")[0].strip()
                
                log(f"Inserting default data into {table_name}")
                cursor.execute(insert_statement)
                log(f"✓ Inserted default data into {table_name}")
            except sqlite3.Error as e:
                log_error(f"Failed to insert default data into {table_name}: {e}")
                # Continue with other inserts rather than failing completely
        
        # Verify player_profile table exists and has at least one row
        cursor.execute("SELECT COUNT(*) FROM player_profile")
        count = cursor.fetchone()[0]
        if count == 0:
            log("No player profiles found, creating default profile")
            cursor.execute("INSERT INTO player_profile (player_id, display_name, high_score, tutorial_complete) "
                          "VALUES (1, 'Player', 0, 0)")
        else:
            log(f"Found {count} player profiles in database")
        
        conn.commit()
        log("All database changes committed successfully")
        conn.close()
        
        log(f"Database initialized successfully at {DB_PATH}")
        return True
        
    except sqlite3.Error as e:
        log_error(f"Database initialization failed: {e}")
        try:
            # Try to create an emergency fallback database in current directory
            emergency_path = Path.cwd() / "emergency_jammin.db"
            log(f"Attempting emergency database creation at: {emergency_path}")
            
            conn = sqlite3.connect(str(emergency_path))
            cursor = conn.cursor()
            
            # Create minimal player_profile table for tutorial check
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_profile (
                    player_id INTEGER PRIMARY KEY,
                    display_name TEXT DEFAULT 'Player',
                    high_score INTEGER DEFAULT 0,
                    tutorial_complete INTEGER DEFAULT 0
                )
            """)
            cursor.execute("INSERT INTO player_profile (player_id, tutorial_complete) VALUES (1, 0)")
            conn.commit()
            conn.close()
            
            # Update global path
            DB_PATH = emergency_path
            log(f"Emergency database created at: {DB_PATH}")
            return True
        except Exception as emergency_error:
            log_error(f"Emergency database creation also failed: {emergency_error}")
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
