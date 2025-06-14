"""
Test script to verify database initialization.
This will create the database file and tables if they don't exist.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import the database initialization module
from src.persistence.db_init import (
    initialize_database,
    check_database_integrity,
    DB_PATH,
)


def main():
    print("=== Database Initialization Test ===")
    print(f"Database path: {DB_PATH}")

    # Check if the database file exists
    if os.path.exists(DB_PATH):
        print(f"Database file exists: {DB_PATH}")
    else:
        print(f"Database file does NOT exist: {DB_PATH}")
        print("Will attempt to create it...")

    # Initialize the database
    success = initialize_database()
    if success:
        print("Database initialization successful!")
    else:
        print("Database initialization failed!")
        return

    # Check database integrity
    integrity, missing = check_database_integrity()
    if integrity:
        print("Database integrity check passed!")
        print("All required tables exist.")
    else:
        print("Database integrity check failed!")
        print(f"Missing tables: {missing}")


if __name__ == "__main__":
    main()
