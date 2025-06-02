"""Unit tests for the state machine in Jammin' Eats.

These tests validate the state transitions and management system.
"""

import pytest
import pygame
from src.states.state_machine import StateMachine, GameState


# Mock game states for testing
class MockState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.entered = False
        self.exited = False
    
    def enter(self):
        self.entered = True
    
    def exit(self):
        self.exited = True
    
    def update(self, dt):
        return None
    
    def render(self, screen):
        pass
    
    def handle_event(self, event):
        pass


class TestStateMachine:
    """Tests for the state machine functionality."""
    
    def test_state_transitions(self, mock_game):
        """Test that state transitions work correctly."""
        # Create state machine
        state_machine = StateMachine()
        
        # Create mock states
        state1 = MockState(mock_game)
        state2 = MockState(mock_game)
        
        # Add states with transition rules
        state_machine.add_state("state1", state1, ["state2"])
        state_machine.add_state("state2", state2, ["state1"])
        
        # Initial transition to state1
        assert state_machine.transition_to("state1") is True
        assert state_machine.current_state == state1
        assert state1.entered is True
        
        # Transition from state1 to state2
        assert state_machine.transition_to("state2") is True
        assert state_machine.current_state == state2
        assert state1.exited is True
        assert state2.entered is True
        assert state_machine.previous_state == state1
        
        # Try invalid transition (not in allowed transitions)
        state_machine.add_state("state3", MockState(mock_game), [])
        assert state_machine.transition_to("state3") is False
        assert state_machine.current_state == state2, "State shouldn't change on invalid transition"
    
    def test_state_entry_exit_hooks(self, mock_game):
        """Test that enter and exit hooks are called correctly."""
        # Create state machine
        state_machine = StateMachine()
        
        # Create mock states
        state1 = MockState(mock_game)
        state2 = MockState(mock_game)
        
        # Add states
        state_machine.add_state("state1", state1, ["state2"])
        state_machine.add_state("state2", state2, ["state1"])
        
        # Initial transition
        state_machine.transition_to("state1")
        assert state1.entered is True
        assert state1.exited is False
        
        # Transition to state2
        state_machine.transition_to("state2")
        assert state1.exited is True
        assert state2.entered is True
        
        # Transition back to state1
        state_machine.transition_to("state1")
        assert state2.exited is True
        assert state1.entered is True
