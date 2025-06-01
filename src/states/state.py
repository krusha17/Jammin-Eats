"""Base state class for the game state machine.

This module provides the foundation for all game states.
Each state handles its own events, updates, and rendering.
"""

import pygame

class GameState:
    """Base class for all game states.
    
    All game states should inherit from this class and implement
    the required methods. This provides a clean separation of concerns
    and allows for easy state transitions.
    """
    
    def __init__(self, game):
        """Initialize the state.
        
        Args:
            game: The main Game instance this state belongs to
        """
        self.game = game
        self.next_state = None
    
    def handle_event(self, event):
        """Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        return False
    
    def update(self, dt):
        """Update the state logic.
        
        Args:
            dt: Time delta in seconds since last update
        """
        pass
    
    def draw(self, screen):
        """Draw the state to the screen.
        
        Args:
            screen: The pygame surface to draw on
        """
        pass
    
    def enter(self):
        """Called when this state becomes the active state."""
        pass
    
    def exit(self):
        """Called when this state is no longer the active state."""
        pass
