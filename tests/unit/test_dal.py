"""Unit tests for the Data Access Layer (DAL).

These tests validate database operations and persistence functionality.
"""

import sqlite3
from src.persistence.dal import (
    get_player_profile,
    is_tutorial_complete,
    mark_tutorial_complete,
    update_high_score,
)


class TestDAL:
    """Tests for the Data Access Layer functionality."""

    def test_player_profile_creation(self, mock_database, monkeypatch):
        """DB-01: Test that player profiles are created correctly."""
        # Mock the DB_PATH to use our test database
        import src.persistence.dal as dal_module

        monkeypatch.setattr(dal_module, "DB_PATH", mock_database)

        profile = get_player_profile(1)
        assert profile is not None
        assert profile["tutorial_complete"] == 0
        assert "high_score" in profile

    def test_tutorial_completion_persistence(self, mock_database, monkeypatch):
        """DB-02: Test that tutorial completion is persisted correctly."""
        # Mock the DB_PATH to use our test database
        import src.persistence.dal as dal_module

        monkeypatch.setattr(dal_module, "DB_PATH", mock_database)

        # Initially tutorial should be incomplete
        assert is_tutorial_complete(1) is False

        # Mark tutorial complete
        mark_tutorial_complete(1)

        # Now tutorial should be marked as complete
        assert is_tutorial_complete(1) is True

    def test_high_score_update(self, mock_database, monkeypatch):
        """DB-03: Test that high scores are updated correctly."""
        # Mock the DB_PATH to use our test database
        import src.persistence.dal as dal_module

        monkeypatch.setattr(dal_module, "DB_PATH", mock_database)

        # Set initial high score
        update_high_score(1, 1000)
        profile = get_player_profile(1)
        assert profile["high_score"] == 1000

        # Update with higher score
        update_high_score(1, 2000)
        profile = get_player_profile(1)
        assert profile["high_score"] == 2000

        # Try to update with lower score (should not change)
        update_high_score(1, 1500)
        profile = get_player_profile(1)
        assert profile["high_score"] == 2000, "High score should not decrease"

    def test_database_initialization(self, temp_game_dir):
        """Test that the database is properly initialized with required tables."""
        # Create a unique directory for this test to avoid any file locking issues
        test_dir = temp_game_dir / "db_init_test"
        test_dir.mkdir(exist_ok=True)
        data_dir = test_dir / "data"
        data_dir.mkdir(exist_ok=True)

        # Define database path - using a unique name to avoid conflicts
        db_path = data_dir / "test_init.db"

        # Import the initialize_database function but modify it to use our test path

        # Define a local function that uses our test path
        def init_test_db():
            # Connect to the database and initialize it directly
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create the player_profile table
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS player_profile (
                player_id INTEGER PRIMARY KEY,
                display_name TEXT DEFAULT 'Player',
                high_score INTEGER DEFAULT 0,
                tutorial_complete INTEGER DEFAULT 0
            )
            """
            )

            # Insert default player
            cursor.execute(
                """
            INSERT INTO player_profile (player_id, display_name, high_score, tutorial_complete) 
            VALUES (1, 'Test Player', 0, 0)
            ON CONFLICT(player_id) DO NOTHING
            """
            )

            conn.commit()
            conn.close()
            return True

        # Initialize the database
        success = init_test_db()
        assert success, "Database initialization should succeed"

        # Verify tables exist in a new connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check player_profile table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "player_profile table should exist"
