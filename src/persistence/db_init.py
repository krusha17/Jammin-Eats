"""Database initialization module for Jammin' Eats

Follows professional game development practices with robust error handling,
directory creation, and schema validation.
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
    # Try different methods to find the project root
    try:
        # Method 1: From the current file location
        project_root = Path(__file__).parent.parent.parent
        log(f"Method 1 - Project root from __file__: {project_root}")
        
        # Method 2: Try from current working directory
        cwd_root = Path.cwd()
        while cwd_root.name and not (cwd_root / "src").exists():
            parent = cwd_root.parent
            if parent == cwd_root:  # Reached filesystem root
                break
            cwd_root = parent
        log(f"Method 2 - Project root from cwd: {cwd_root}")
        
        # Determine which root is most likely correct
        if (project_root / "src").exists():
            chosen_root = project_root
            log("Using project root from file path")
        elif (cwd_root / "src").exists():
            chosen_root = cwd_root
            log("Using project root from current working directory")
        else:
            chosen_root = project_root  # Fallback to method 1
            log("Falling back to file path method")
        
        log(f"Selected project root: {chosen_root}")
        
        # Ensure data directory exists
        data_dir = chosen_root / "data"
        log(f"Target data directory: {data_dir}")
        
        # Ensure data directory exists
        if not data_dir.exists():
            log(f"Data directory not found, creating: {data_dir}")
            data_dir.mkdir(parents=True, exist_ok=True)
            if data_dir.exists():
                log(f"Successfully created data directory: {data_dir}")
            else:
                log_error(f"Failed to create data directory at: {data_dir}")
                raise OSError(f"Could not create data directory: {data_dir}")
        
        # Set the database path - explicitly use .db extension
        db_path = data_dir / "jammin.db"  # Ensure .db extension
        log(f"Database path set to: {db_path}")
        
        # Try to create a test file to verify write permissions
        test_file = data_dir / ".db_test"
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()  # Remove test file
            log("Write permissions verified in data directory")
        except Exception as e:
            log_error(f"Warning: Cannot write to data directory: {e}")
            # Continue anyway, maybe sqlite can still write there
        
        # Make sure we return a string for sqlite3.connect
        return str(db_path)
    except Exception as e:
        log_error(f"Failed to configure database path: {e}")
        # Fallback to current working directory
        fallback = Path.cwd() / "jammin.db"
        log(f"Using fallback database path: {fallback}")
        return str(fallback)  # Return as string

# Initialize the path at module load time
DB_PATH = get_database_path()

# Add absolute path constant for more reliable access
ABSOLUTE_DB_PATH = os.path.abspath(DB_PATH)

# SQL statements to create necessary tables
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS player_profile (
        id INTEGER PRIMARY KEY,
        name TEXT DEFAULT 'Player',
        high_score INTEGER DEFAULT 0,
        tutorial_complete INTEGER DEFAULT 0,
        money INTEGER DEFAULT 0,
        successful_deliveries INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS save_games (
        save_id INTEGER PRIMARY KEY,
        player_id INTEGER,
        save_date TEXT DEFAULT CURRENT_TIMESTAMP,
        game_state TEXT,
        inventory TEXT,
        position TEXT,
        FOREIGN KEY (player_id) REFERENCES player_profile(id)
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
        FOREIGN KEY (player_id) REFERENCES player_profile(id)
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
        FOREIGN KEY (player_id) REFERENCES player_profile(id)
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
        FOREIGN KEY (player_id) REFERENCES player_profile(id)
    )
    """
]

# Default data to insert
DEFAULT_DATA = [
    # Player profile defaults
    "INSERT OR IGNORE INTO player_profile (id, name, high_score, tutorial_complete, money, successful_deliveries) "
    "VALUES (1, 'Player', 0, 0, 0, 0)",
    
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
    data_dir = Path(DB_PATH).parent
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


def migrate_database(conn):
    """Apply database migrations to add new columns or update schemas."""
    cursor = conn.cursor()
    log("Checking for required database migrations...")
    
    # Check if money column exists in player_profile
    cursor.execute("PRAGMA table_info(player_profile)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'money' not in columns:
        log("Migrating: Adding 'money' column to player_profile table")
        try:
            cursor.execute("ALTER TABLE player_profile ADD COLUMN money INTEGER DEFAULT 0")
            conn.commit()
            log("Migration successful: Added 'money' column to player_profile")
        except sqlite3.Error as e:
            log_error(f"Migration failed: Could not add 'money' column: {e}")
            conn.rollback()
            
    # Check if successful_deliveries column exists in player_profile
    if 'successful_deliveries' not in columns:
        log("Migrating: Adding 'successful_deliveries' column to player_profile table")
        try:
            cursor.execute("ALTER TABLE player_profile ADD COLUMN successful_deliveries INTEGER DEFAULT 0")
            conn.commit()
            log("Migration successful: Added 'successful_deliveries' column to player_profile")
        except sqlite3.Error as e:
            log_error(f"Migration failed: Could not add 'successful_deliveries' column: {e}")
            conn.rollback()
    
    log("Database migrations completed")


def initialize_database():
    """Initialize the database with required tables."""
    global DB_PATH
    
    # Ensure the data directory exists first
    ensure_data_directory()
    
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
                cursor.execute(insert_statement)
                log(f"✓ Inserted default data into table: {table_name}")
            except Exception as e:
                log_error(f"Error during table extraction: {e}")
        
        # Set row factory to return dictionaries
        conn.row_factory = sqlite3.Row
        
        # Create cursor
        cursor = conn.cursor()
        
        # Create tables with detailed logging
        for i, table_sql in enumerate(CREATE_TABLES):
            try:
                log(f"Creating table #{i+1}")
                cursor.execute(table_sql)
                log(f"Table #{i+1} created successfully")
            except sqlite3.Error as e:
                log_error(f"Error creating table #{i+1}: {e}")
                # Continue with other tables despite errors
        
        # Validate that tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log(f"Tables in database: {[t[0] for t in tables]}")
        
        # Insert default data with detailed logging
        for i, data_sql in enumerate(DEFAULT_DATA):
            try:
                cursor.execute(data_sql)
                log(f"Default data #{i+1} inserted successfully")
            except sqlite3.Error as e:
                log_error(f"Error inserting default data #{i+1}: {e}")
                # Continue with other data despite errors
        
        # Apply any necessary migrations
        migrate_database(conn)
        
        # Commit changes
        try:
            conn.commit()
            log("All changes committed successfully")
        except sqlite3.Error as e:
            log_error(f"Error committing changes: {e}")
        
        # Specifically verify player_profile table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'")
        if cursor.fetchone():
            log(" player_profile table exists")
            # Check if it has rows
            cursor.execute("SELECT COUNT(*) FROM player_profile")
            count = cursor.fetchone()[0]
            log(f"player_profile table has {count} rows")
            if count == 0:
                # Insert default player profile
                log("Creating default player profile")
                cursor.execute("INSERT INTO player_profile (id, name, high_score, tutorial_complete) VALUES (1, 'Player', 0, 0)")
                conn.commit()
                log("Default player profile created")
        else:
            log_error("player_profile table is missing - recreating")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_profile (
                    id INTEGER PRIMARY KEY,
                    name TEXT DEFAULT 'Player',
                    high_score INTEGER DEFAULT 0,
                    tutorial_complete INTEGER DEFAULT 0
                )
            """)
            cursor.execute("INSERT INTO player_profile (id, name, high_score, tutorial_complete) VALUES (1, 'Player', 0, 0)")
            conn.commit()
            log("Created player_profile table and default profile")
        
        # Validate schema
        validate_database_schema(conn)
        
        # Close connection
        conn.close()
        log("Database initialized successfully")
        
        return True
        
    except sqlite3.Error as e:
        log_error(f"Database initialization error: {e}")
        return False
    except Exception as e:
        log_error(f"Unexpected error during database initialization: {e}")
        return False
    finally:
        # Close connection if it was opened
        if 'conn' in locals() and conn:
            try:
                conn.close()
                log("Database connection closed")
            except Exception as e:
                log_error(f"Error closing database connection: {e}")


def validate_database_schema(conn):
    """Validate that all required tables and columns exist in the database."""
    cursor = conn.cursor()
    
    # Define expected tables and their required columns
    expected_schema = {
        'player_profile': ['id', 'name', 'high_score', 'tutorial_complete', 'money', 'successful_deliveries'],
        'player_settings': ['setting_id', 'player_id', 'music_volume', 'sfx_volume'],
        'starting_stock': ['item_id', 'food_type', 'initial_quantity'],
        'upgrades_owned': ['upgrade_id', 'player_id', 'upgrade_name'],
        'run_history': ['run_id', 'player_id', 'score', 'money_earned'],
        'save_games': ['save_id', 'player_id', 'save_date', 'game_state']
    }
    
    log("Validating database schema...")
    
    # Check for each table and its columns
    for table_name, expected_columns in expected_schema.items():
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                log_error(f"Table {table_name} is missing from database")
                continue
                
            # Check table columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]  # Column name is at index 1
            
            # Verify required columns exist
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                log_error(f"Table {table_name} is missing columns: {', '.join(missing_columns)}")
            else:
                log(f"✓ Table {table_name} schema is valid")
                
        except sqlite3.Error as e:
            log_error(f"Error validating {table_name}: {e}")
    
    # Special check for player_profile to ensure it exists with at least one row
    try:
        cursor.execute("SELECT COUNT(*) FROM player_profile")
        count = cursor.fetchone()[0]
        if count == 0:
            log_error("player_profile table exists but has no data")
            # Insert a default profile
            cursor.execute(
                "INSERT INTO player_profile (id, name, high_score, tutorial_complete) VALUES (?, ?, ?, ?)", 
                (1, "Player", 0, 0)
            )
            conn.commit()
            log("Created default player profile")
        else:
            log(f"✓ Found {count} player profiles in database")
    except sqlite3.Error as e:
        log_error(f"Error checking player_profile data: {e}")
    
    log("Database schema validation complete")


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
            "run_history",
            "save_games"
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
