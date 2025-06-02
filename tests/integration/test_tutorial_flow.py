"""Integration tests for the tutorial flow in Jammin' Eats.

These tests validate the complete tutorial experience from start to finish,
ensuring proper state transitions and data persistence.
"""

import pytest
import pygame
from src.states.tutorial_state import TutorialState
from src.states.tutorial_complete_state import TutorialCompleteState
from src.game import Game
from src.persistence.dal import DataAccessLayer


class TestTutorialFlow:
    """Tests for the complete tutorial flow and integration."""
    
    def test_initial_launch_shows_tutorial(self, monkeypatch):
        """TG-01: Test that initial launch shows the tutorial."""
        # Setup a mock for is_tutorial_complete that returns False
        def mock_is_tutorial_complete(*args):
            return False
        
        monkeypatch.setattr(
            "src.persistence.dal.DataAccessLayer.is_tutorial_complete", 
            mock_is_tutorial_complete
        )
        
        # Create a game instance
        game = Game()
        
        # Initialize game (this should set initial state to Tutorial)
        game.initialize()
        
        # Verify the current state is TutorialState
        assert isinstance(game.state, TutorialState), "Initial state should be TutorialState"
    
    def test_tutorial_progression(self, monkeypatch):
        """Test the complete tutorial progression from start to finish."""
        # Setup a persistent record of what methods were called
        calls = []
        
        # Mock persistence functions
        def mock_is_tutorial_complete(*args):
            calls.append("is_tutorial_complete")
            return False
        
        def mock_mark_tutorial_complete(*args):
            calls.append("mark_tutorial_complete")
            return True
        
        monkeypatch.setattr(
            "src.persistence.dal.DataAccessLayer.is_tutorial_complete", 
            mock_is_tutorial_complete
        )
        monkeypatch.setattr(
            "src.persistence.dal.DataAccessLayer.mark_tutorial_complete", 
            mock_mark_tutorial_complete
        )
        
        # Create a game instance
        game = Game()
        game.initialize()
        
        # 1. Verify we start in tutorial state
        assert isinstance(game.state, TutorialState)
        
        # 2. Simulate earning money in tutorial
        tutorial_state = game.state
        
        # Simulate multiple deliveries to reach goal
        for _ in range(5):  # Assuming $10 per delivery and $50 goal
            space_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
            tutorial_state.handle_event(space_event)
        
        # 3. Update state to trigger completion check
        tutorial_state.update(0.1)  # dt = 0.1 seconds
        
        # 4. Verify transition to tutorial complete state
        assert isinstance(game.state, TutorialCompleteState)
        
        # 5. Press ENTER to complete tutorial
        enter_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        game.state.handle_event(enter_event)
        
        # 6. Verify persistence was called
        assert "mark_tutorial_complete" in calls, "mark_tutorial_complete should be called"
    
    def test_skip_tutorial_on_relaunch(self, monkeypatch):
        """TG-05: Test that tutorial is skipped on relaunch after completion."""
        # Setup a mock for is_tutorial_complete that returns True
        def mock_is_tutorial_complete(*args):
            return True
        
        monkeypatch.setattr(
            "src.persistence.dal.DataAccessLayer.is_tutorial_complete", 
            mock_is_tutorial_complete
        )
        
        # Create a game instance
        game = Game()
        
        # Initialize game (this should bypass tutorial)
        game.initialize()
        
        # Verify the current state is NOT TutorialState
        assert not isinstance(game.state, TutorialState), "Tutorial should be skipped"
