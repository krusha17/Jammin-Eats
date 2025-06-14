"""Test configuration and fixtures for Jammin' Eats.

Provides common fixtures and configurations for all test modules.
"""

import pytest
import os
import sys
import pygame
import tempfile
import shutil
from pathlib import Path

# Add src directory to path to allow importing game modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Initialize pygame for tests that need it
pygame.init()


@pytest.fixture(autouse=True)
def test_id(request):
    """Automatically map test functions to checklist IDs for validation.

    This fixture maps test function names to their corresponding
    checklist items in CORE_SYSTEM_VALIDATION_CHECKLIST.md.

    The checklist_validator.py script uses these IDs to update
    the checklist with test results.
    """
    test_name = request.function.__name__

    # Map from test names to checklist IDs
    # Format: "test_function_name": "XX-##"
    # XX = category code (ENV, DB, TG, etc.)
    # ## = item number
    id_mapping = {
        # Environment / Build Pipeline
        "test_clean_install": "ENV-01",
        "test_db_fallback": "ENV-02",
        "test_pygame_init": "ENV-03",
        # Database & Persistence
        "test_player_profile_default": "DB-01",
        "test_tutorial_completion_flag": "DB-02",
        "test_high_score_update": "DB-03",
        # Tutorial Graduation Flow
        "test_initial_launch_shows_tutorial": "TG-01",
        "test_space_increments_money": "TG-02",
        "test_goal_reached_triggers_overlay": "TG-03",
        "test_enter_persists_completion": "TG-04",
        "test_skip_tutorial_on_relaunch": "TG-05",
        # Title -> Gameplay Transition
        "test_start_new_game": "TP-01",
        "test_exit_button": "TP-02",
        # More mappings can be added as needed...
    }

    if test_name in id_mapping:
        return id_mapping[test_name]
    return None


@pytest.fixture
def temp_game_dir():
    """Create isolated game directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_database(temp_game_dir):
    """Create and initialize a temporary SQLite database for testing."""
    # Create data directory
    data_dir = temp_game_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Define database path
    db_path = data_dir / "test.db"

    # Initialize with required tables
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables matching our schema
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
    """
    )

    # Add any other tables needed for tests
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS player_settings (
        setting_id INTEGER PRIMARY KEY,
        player_id INTEGER,
        music_volume REAL DEFAULT 0.7,
        sfx_volume REAL DEFAULT 1.0,
        FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
    )
    """
    )

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_db_connection():
    """Provide a mock DB connection for testing DAL functions."""

    # This would use a proper mock or in-memory DB in a real implementation
    class MockConnection:
        def cursor(self):
            return MockCursor()

        def commit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class MockCursor:
        def execute(self, *args):
            pass

        def fetchone(self):
            return {"tutorial_complete": 0, "high_score": 0}

    return MockConnection()


@pytest.fixture
def mock_game():
    """Provide a mock Game object for testing states."""

    class MockGame:
        def __init__(self):
            self.money = 0
            self.successful_deliveries = 0
            self.persistence = MockPersistence()

        def draw_current_state(self, screen):
            pass

    class MockPersistence:
        def __init__(self):
            self.player_id = 1

    return MockGame()
