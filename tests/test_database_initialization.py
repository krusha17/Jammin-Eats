"""
Test suite for validating database initialization and DataAccessLayer functionality.
Follows professional game development practices with test-driven development.
"""

import os
import sys
import unittest
import tempfile
import sqlite3

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import modules to test
from src.persistence.db_init import initialize_database
from src.persistence.dal import DataAccessLayer


class TestDatabaseInitialization(unittest.TestCase):
    """Test the database initialization process."""

    def setUp(self):
        """Create a temporary database for testing."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        # Set up temp database path
        self.temp_db_path = os.path.join(self.temp_dir.name, "test_jammin.db")
        # Store original DB_PATH
        self.original_db_path = None
        if "DB_PATH" in sys.modules["src.persistence.db_init"].__dict__:
            self.original_db_path = sys.modules["src.persistence.db_init"].DB_PATH
        # Set the DB_PATH to our test path
        sys.modules["src.persistence.db_init"].DB_PATH = self.temp_db_path

    def tearDown(self):
        """Clean up the temporary database after testing."""
        # Restore original DB_PATH if it existed
        if self.original_db_path:
            sys.modules["src.persistence.db_init"].DB_PATH = self.original_db_path
        # Remove the temporary directory and its contents
        self.temp_dir.cleanup()

    def test_database_creation(self):
        """Test that the database is created successfully."""
        # Ensure the database doesn't exist
        self.assertFalse(os.path.exists(self.temp_db_path))

        # Initialize the database
        result = initialize_database()

        # Check database was created
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_db_path))

        # Verify we can connect to it
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # Check if player_profile table was created
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'"
        )
        self.assertIsNotNone(cursor.fetchone())

        # Clean up
        conn.close()

    def test_player_profile_schema(self):
        """Test that the player_profile table has the correct schema."""
        # Initialize the database
        initialize_database()

        # Connect to the database
        conn = sqlite3.connect(self.temp_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get player_profile schema
        cursor.execute("PRAGMA table_info(player_profile)")
        columns = {row["name"]: row for row in cursor.fetchall()}

        # Check required columns exist
        self.assertIn("id", columns)
        self.assertIn("name", columns)
        self.assertIn("high_score", columns)
        self.assertIn("tutorial_complete", columns)

        # Check column types
        self.assertEqual(columns["id"]["type"].upper(), "INTEGER")
        self.assertEqual(columns["name"]["type"].upper(), "TEXT")
        self.assertEqual(columns["tutorial_complete"]["type"].upper(), "INTEGER")

        # Clean up
        conn.close()

    def test_default_player_profile(self):
        """Test that a default player profile is created."""
        # Initialize the database
        initialize_database()

        # Create DAL instance for testing
        dal = DataAccessLayer()

        # Check that tutorial is initially not complete
        self.assertFalse(dal.is_tutorial_complete())

        # Mark tutorial as complete
        dal.mark_tutorial_complete()

        # Verify it was marked as complete
        self.assertTrue(dal.is_tutorial_complete())

        # Reset player progress
        dal.reset_player_progress()

        # Tutorial should still be marked as complete
        self.assertTrue(dal.is_tutorial_complete())


if __name__ == "__main__":
    unittest.main()
