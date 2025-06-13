"""Game rendering component for Jammin' Eats.

This module handles all rendering logic for the game, separated from core game logic.
It provides methods for drawing game states, UI elements, and managing the visual presentation.

Classes:
    GameRenderer: Handles rendering of game elements and UI components.
"""

import pygame
import traceback

# Import from either direct or src-prefixed paths
try:
    # Try direct imports first
    from debug.logger import game_logger
except ImportError:
    # Fall back to src-prefixed imports
    from src.debug.logger import game_logger

class GameRenderer:
    """Handles rendering and drawing operations for the game."""
    
    def __init__(self, game):
        """Initialize the renderer with a reference to the main game object.
        
        Args:
            game: Reference to the main Game instance
        """
        self.game = game
    
    def render(self, mouse_pos):
        """Render the game screen.
        
        Args:
            mouse_pos: Current mouse position tuple (x, y)
        """
        # First draw the base game state
        self.draw_current_state(self.game.screen)
        
        # Debug info and mouse hover effects would go here
        
        # Update the display
        pygame.display.flip()

    def draw_current_state(self, screen):
        """Draw the current game state - used by tutorial and other states.
        
        Args:
            screen: The surface to draw on
        """
        try:
            # Check if we have a current state to draw
            if hasattr(self.game, 'current_state') and self.game.current_state:
                # Let the state draw itself
                self.game.current_state.draw(screen)
                game_logger.debug(
                    f"Drew current state: {self.game.current_state.__class__.__name__}",
                    "GameRenderer"
                )
            else:
                # Fallback: draw basic background
                screen.fill((0, 0, 0))
                game_logger.warning("No current_state to draw", "GameRenderer")
                
                # Try to draw some minimal information if we have any
                try:
                    # If we have a font available, show an error message
                    font = pygame.font.SysFont(None, 36)
                    text = font.render(
                        "No active game state to display", 
                        True, 
                        (255, 0, 0)
                    )
                    screen.blit(
                        text, 
                        (
                            self.game.screen_width // 2 - text.get_width() // 2, 
                            self.game.screen_height // 2
                        )
                    )
                except Exception as font_error:
                    game_logger.error(
                        f"Could not draw error message: {font_error}", 
                        "GameRenderer"
                    )
        except Exception as e:
            game_logger.error(
                f"Error in draw_current_state: {e}", 
                "GameRenderer", 
                exc_info=True
            )
            # Try to display some kind of error on screen
            screen.fill((50, 0, 0))  # Dark red background to indicate error
