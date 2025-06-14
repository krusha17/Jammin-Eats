"""
Simple diagnostic script to verify the database setup and fix any issues.
"""

import os
import sys
import traceback

# Add the root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_database():
    """Verify database exists and has required tables."""
    try:
        print("\n=== DATABASE DIAGNOSTIC ===")

        # Import with proper path handling
        try:
            from src.persistence.db_init import (
                DB_PATH,
                initialize_database,
                check_database_integrity,
            )
            from src.debug.logger import game_logger

            print("Successfully imported database modules")
        except ImportError as e:
            print(f"Import error: {e}")
            return False

        # Check if DB file exists
        print(f"\nChecking if database exists at: {DB_PATH}")
        if os.path.exists(DB_PATH):
            print(f"✓ Database file found: {DB_PATH}")
            print(f"  - File size: {os.path.getsize(DB_PATH)} bytes")
        else:
            print(f"✗ Database file NOT found: {DB_PATH}")

            # Check if data directory exists
            data_dir = os.path.dirname(DB_PATH)
            if not os.path.exists(data_dir):
                print(f"  - Data directory does not exist: {data_dir}")
                try:
                    os.makedirs(data_dir, exist_ok=True)
                    print(f"  - Created data directory: {data_dir}")
                except Exception as e:
                    print(f"  - Failed to create data directory: {e}")

        # Initialize database
        print("\nAttempting to initialize database...")
        try:
            result = initialize_database()
            if result:
                print("✓ Database initialized successfully")
            else:
                print("✗ Database initialization failed")
        except Exception as e:
            print(f"✗ Error during database initialization: {e}")
            traceback.print_exc()

        # Check database integrity
        print("\nChecking database integrity...")
        try:
            integrity_result, missing_tables = check_database_integrity()
            if integrity_result:
                print("✓ Database integrity check passed")
            else:
                print(
                    f"✗ Database integrity check failed. Missing tables: {missing_tables}"
                )

                # Try to fix by reinitializing
                print("  - Attempting to fix by reinitializing database...")
                initialize_database(force=True)

                # Check again
                integrity_result, missing_tables = check_database_integrity()
                if integrity_result:
                    print("✓ Database fixed successfully")
                else:
                    print(
                        f"✗ Database still has issues. Missing tables: {missing_tables}"
                    )
        except Exception as e:
            print(f"✗ Error during integrity check: {e}")
            traceback.print_exc()

        # Test tutorial completion flag
        print("\nChecking tutorial completion functionality...")
        try:
            from src.persistence.dal import is_tutorial_complete, mark_tutorial_complete

            # Check current status
            tutorial_status = is_tutorial_complete(1)  # Default player ID
            print(f"- Current tutorial completion status: {tutorial_status}")

            # Test marking as complete
            print("- Testing mark_tutorial_complete()...")
            result = mark_tutorial_complete(1)
            if result:
                print("✓ Successfully marked tutorial as complete")
            else:
                print("✗ Failed to mark tutorial as complete")

            # Verify it worked
            tutorial_status = is_tutorial_complete(1)
            if tutorial_status:
                print("✓ Tutorial status verified as complete")
            else:
                print("✗ Tutorial status verification failed")

            # Reset to original state if needed
            from src.persistence.reset_tutorial import reset_tutorial_completion

            reset_result = reset_tutorial_completion()
            print(f"- Reset tutorial completion: {reset_result}")

        except Exception as e:
            print(f"✗ Error testing tutorial completion: {e}")
            traceback.print_exc()

        print("\n=== DATABASE DIAGNOSTIC COMPLETE ===\n")
        return True

    except Exception as e:
        print(f"Unexpected error during database check: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
