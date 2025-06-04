"""
Base game state class for Jammin' Eats.

This module provides the GameState abstract base class that all game states must inherit from.
"""

class GameState:
    """Abstract base class for all game states.
    
    This class defines the interface that all game states must implement.
    Each state represents a distinct mode of the game, such as the title screen,
    gameplay, tutorial, etc.
    """
    
    def __init__(self, game):
        """Initialize the game state.
        
        Args:
            game: The main Game instance this state belongs to
        """
        self.game = game
        self.next_state = None
    
    def handle_event(self, event):
        """Handle input events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
    
    def update(self, dt):
        """Update game state logic.
        
        Args:
            dt: Time delta in seconds
        """
        pass
    
    def draw(self, screen):
        """Draw the state.
        
        Args:
            screen: Pygame surface to draw on
        """
        pass
    
    def enter(self):
        """Called when entering this state."""
        pass
    
    def exit(self):
        """Called when exiting this state."""
        pass
