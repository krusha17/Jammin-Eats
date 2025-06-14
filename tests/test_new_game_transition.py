"""
Test suite for validating the Title → New Game transition.
Follows professional game development practices with test-driven development.
"""

import os
import sys
import unittest
import pygame
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import game modules (with fallbacks for different import patterns)
try:
    from src.core.game import Game
    from src.states.title_state import TitleState
    from src.states.black_screen_gameplay_state import BlackScreenGameplayState
    from src.persistence.dal import DataAccessLayer
except ImportError:
    # Direct imports as fallback
    from core.game import Game
    from states.title_state import TitleState
    from states.black_screen_gameplay_state import BlackScreenGameplayState
    from persistence.dal import DataAccessLayer


class TestNewGameTransition(unittest.TestCase):
    """Test the transition from Title screen to a new game."""

    def setUp(self):
        """Initialize pygame and mock necessary objects before each test."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))

        # Create a mock DAL with a functioning is_tutorial_complete method
        self.mock_dal = MagicMock(spec=DataAccessLayer)
        self.mock_dal.is_tutorial_complete.return_value = (
            True  # Assume tutorial completed
        )

        # Create a test game instance with mock components
        self.game = MagicMock(spec=Game)
        self.game.screen = self.screen
        self.game.persistence = self.mock_dal

        # Create the title state we'll test
        self.title_state = TitleState(self.game)

    def tearDown(self):
        """Clean up after each test."""
        pygame.quit()

    def test_new_game_selection(self):
        """Test that selecting 'New Game' creates the appropriate next_state."""
        # Simulate selecting the "New Game" option
        self.title_state.current_option = self.title_state.options.index("new game")

        # Create a mock event for pressing Enter
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN

        # Handle the event
        self.title_state.handle_event(mock_event)

        # Verify next_state is set to a gameplay state
        self.assertIsNotNone(self.title_state.next_state, "next_state should be set")
        self.assertIsInstance(
            self.title_state.next_state,
            BlackScreenGameplayState,
            "next_state should be a BlackScreenGameplayState instance",
        )

    def test_new_game_resets_database(self):
        """Test that a new game properly resets player data in the database."""
        # Simulate new game selection
        self.title_state.current_option = self.title_state.options.index("new game")

        # Create a mock event for pressing Enter
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN

        # Handle the event
        self.title_state.handle_event(mock_event)

        # Verify DAL was called to reset player progress
        self.mock_dal.reset_player_progress.assert_called_once()

    def test_error_handling(self):
        """Test error handling if the state transition fails."""
        # Force DAL to raise an exception when reset_player_progress is called
        self.mock_dal.reset_player_progress.side_effect = Exception("Database error")

        # Simulate new game selection
        self.title_state.current_option = self.title_state.options.index("new game")

        # Create a mock event for pressing Enter
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN

        # Handle the event - should not raise an exception due to error handling
        self.title_state.handle_event(mock_event)

        # Title state should log the error and remain in the title screen
        self.assertIsNone(
            self.title_state.next_state, "next_state should be None after error"
        )


if __name__ == "__main__":
    unittest.main()
