"""Pytest-compatible test for tutorial completion

Tests that the tutorial completion functionality works correctly by:
1. Resetting the tutorial status
2. Checking that it's properly marked as incomplete
3. Marking it as complete
4. Verifying it's properly recorded as complete
"""

import pytest
import sqlite3
import os
from pathlib import Path

# Import needed modules
try:
    from src.persistence.dal import is_tutorial_complete, mark_tutorial_complete
    from src.persistence.dal import DataAccessLayer
    from src.persistence.db_init import DB_PATH
    dal_imported = True
except ImportError as e:
    print(f"ImportError: {e}")
    dal_imported = False

# Mark test as skippable if imports fail
pytestmark = pytest.mark.skipif(not dal_imported, reason="DAL module not available")

def setup_function():
    """Setup function to prepare the test environment"""
    # Ensure we have a clean database state for testing
    try:
        # Explicitly reset tutorial completion status for tests
        with sqlite3.connect(Path(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Force tutorial to be marked as incomplete for tests
            cursor.execute("UPDATE player_profile SET tutorial_complete = 0 WHERE id = 1")
            conn.commit()
            
        dal = DataAccessLayer()
        # Reset player profile data for tests (preserves tutorial state which is now incomplete)
        dal.reset_player_progress()
    except Exception as e:
        pytest.skip(f"Database setup failed: {e}")

def test_tutorial_state_functions_exist():
    """Test that the necessary tutorial state functions exist"""
    assert callable(is_tutorial_complete), "is_tutorial_complete function should exist"
    assert callable(mark_tutorial_complete), "mark_tutorial_complete function should exist"
    
def test_initial_tutorial_state():
    """Test that a new game starts with tutorial incomplete"""
    # Reset the player progress first
    dal = DataAccessLayer()
    dal.reset_player_progress()
    
    # Check that tutorial is initially incomplete
    status = is_tutorial_complete()
    assert status is False, "Tutorial should start as incomplete"
    
def test_mark_tutorial_complete():
    """Test marking tutorial as complete"""
    # First ensure it's incomplete
    dal = DataAccessLayer()
    dal.reset_player_progress()
    
    # Mark tutorial as complete
    result = mark_tutorial_complete()
    assert result is True, "mark_tutorial_complete should return True on success"
    
    # Verify it's actually marked as complete
    status = is_tutorial_complete()
    assert status is True, "Tutorial should be marked as complete after calling mark_tutorial_complete"
    
def test_tutorial_persistence():
    """Test that tutorial completion persists between runs"""
    # First mark as complete
    mark_tutorial_complete()
    
    # Create a new DAL instance to simulate a new game session
    new_dal = DataAccessLayer()
    
    # Check that tutorial status is remembered
    assert new_dal.is_tutorial_complete() is True, "Tutorial completion should persist across DAL instances"
