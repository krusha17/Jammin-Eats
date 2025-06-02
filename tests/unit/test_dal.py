"""Unit tests for the Data Access Layer (DAL).

These tests validate database operations and persistence functionality.
"""

import pytest
import os
import sqlite3
from pathlib import Path
from src.persistence.dal import DataAccessLayer


class TestDAL:
    """Tests for the Data Access Layer functionality."""
    
    def test_player_profile_creation(self, mock_database):
        """DB-01: Test that player profiles are created correctly."""
        dal = DataAccessLayer(mock_database)
        profile = dal.get_player_profile(1)
        assert profile is not None
        assert profile['tutorial_complete'] == 0
        assert 'high_score' in profile
    
    def test_tutorial_completion_persistence(self, mock_database):
        """DB-02: Test that tutorial completion is persisted correctly."""
        dal = DataAccessLayer(mock_database)
        # Initially tutorial should be incomplete
        assert dal.is_tutorial_complete(1) is False
        
        # Mark tutorial complete
        dal.mark_tutorial_complete(1)
        
        # Now tutorial should be marked as complete
        assert dal.is_tutorial_complete(1) is True
    
    def test_high_score_update(self, mock_database):
        """DB-03: Test that high scores are updated correctly."""
        dal = DataAccessLayer(mock_database)
        
        # Set initial high score
        dal.update_high_score(1, 1000)
        profile = dal.get_player_profile(1)
        assert profile['high_score'] == 1000
        
        # Update with higher score
        dal.update_high_score(1, 2000)
        profile = dal.get_player_profile(1)
        assert profile['high_score'] == 2000
        
        # Try to update with lower score (should not change)
        dal.update_high_score(1, 1500)
        profile = dal.get_player_profile(1)
        assert profile['high_score'] == 2000, "High score should not decrease"
    
    def test_database_initialization(self, temp_game_dir):
        """Test that the database is properly initialized with required tables."""
        # Create data directory
        data_dir = temp_game_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Define database path
        db_path = data_dir / "jammin.db"
        
        # Initialize DAL with this path
        dal = DataAccessLayer(db_path)
        
        # Connect to the database and verify tables exist
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check player_profile table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'"
            )
            assert cursor.fetchone() is not None, "player_profile table should exist"
            
            # Check player_profile has required columns
            cursor.execute("PRAGMA table_info(player_profile)")
            columns = {row[1] for row in cursor.fetchall()}
            required_columns = {'player_id', 'tutorial_complete', 'high_score'}
            assert required_columns.issubset(columns), f"Missing columns in player_profile: {required_columns - columns}"
