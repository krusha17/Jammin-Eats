"""Example tests for Jammin' Eats tutorial system.

These tests demonstrate how to test the tutorial system while
integrating with the checklist validation framework.
"""

import pytest
import pygame
from src.states.tutorial_state import TutorialState
from src.states.tutorial_complete_state import TutorialCompleteState

# Note: No need to add @pytest.mark.parametrize here!
# The test_id fixture in conftest.py automatically maps test functions to checklist IDs


def test_space_increments_money(mock_game, test_id):
    """TG-02: Test that pressing SPACE increments money in tutorial."""
    # Setup
    tutorial = TutorialState(mock_game)
    assert mock_game.money == 0

    # Create a fake SPACE key event
    space_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})

    # Test handling the event
    tutorial.handle_event(space_event)

    # Verify money increased by $10
    assert mock_game.money == 10, "SPACE key should increment money by $10"
    assert (
        mock_game.successful_deliveries == 1
    ), "SPACE key should increment deliveries by 1"


def test_goal_reached_triggers_overlay(mock_game, test_id):
    """TG-03: Test that reaching tutorial goals triggers completion overlay."""
    # Setup
    tutorial = TutorialState(mock_game)
    assert tutorial.next_state is None

    # Simulate reaching money goal
    mock_game.money = 50
    tutorial.money_earned = 50

    # Update should trigger state change
    tutorial.update(0.1)  # dt = 0.1 seconds

    # Verify next_state is set to TutorialCompleteState
    assert tutorial.next_state is not None
    assert isinstance(tutorial.next_state, TutorialCompleteState)


def test_enter_persists_completion(monkeypatch, mock_game, test_id):
    """TG-04: Test that pressing ENTER persists tutorial completion."""
    # Setup - Replace actual DAL function with a mock that tracks calls
    mark_tutorial_called = False

    def mock_mark_tutorial_complete(player_id=1):
        nonlocal mark_tutorial_called
        mark_tutorial_called = True
        return True

    # Apply the monkeypatch
    monkeypatch.setattr(
        "src.states.tutorial_complete_state.mark_tutorial_complete",
        mock_mark_tutorial_complete,
    )

    # Create tutorial complete state
    complete_state = TutorialCompleteState(mock_game)

    # Simulate pressing ENTER
    enter_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
    complete_state.handle_event(enter_event)

    # Verify mark_tutorial_complete was called
    assert mark_tutorial_called, "ENTER should call mark_tutorial_complete"
    assert (
        mock_game.tutorial_completed is True
    ), "Game's tutorial_completed flag should be set"


# Demonstrate a test that would be skipped/mocked in graybox phase
@pytest.mark.skip(reason="Asset integration deferred until core systems validated")
def test_tutorial_hint_display(mock_game, test_id):
    """Test that tutorial hints are properly displayed and toggled."""
    # This would be implemented during asset integration phase
    tutorial = TutorialState(mock_game)
    assert tutorial.show_hint is True

    # Toggle hint visibility
    h_key_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_h})
    tutorial.handle_event(h_key_event)

    assert tutorial.show_hint is False
