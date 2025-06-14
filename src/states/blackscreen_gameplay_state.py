"""
Black Screen Gameplay State for Jammin' Eats.

A simplified placeholder gameplay state that displays just a black screen
with minimal text feedback. Used for testing state transitions and isolated
validation of the state machine without requiring full gameplay implementation.

Following professional game development practices with:
- Clear separation of concerns
- Proper state initialization and cleanup
- Detailed logging for debugging
- Error handling with fallbacks
"""

import pygame
from datetime import datetime

# Use flexible import system to support both direct and src-prefixed imports
try:
    # Try direct imports first
    from states.state import GameState
    from core.constants import WIDTH, HEIGHT, BLACK, WHITE, PLAYING
    from debug.logger import game_logger
except ImportError:
    # Fall back to src-prefixed imports
    from src.states.state import GameState
    from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE, PLAYING
    from src.debug.logger import game_logger


class BlackScreenGameplayState(GameState):
    """
    Simplified placeholder gameplay state showing only a black screen with minimal UI.

    Used for testing state transitions without requiring full gameplay implementation.
    """

    def __init__(self, game):
        """Initialize the black screen gameplay state.

        Args:
            game: The main Game instance this state belongs to
        """
        super().__init__(game)
        game_logger.info(
            "Initializing BlackScreenGameplayState", "BlackScreenGameplayState"
        )

        # Basic setup
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

        # State tracking
        self.start_time = datetime.now()
        self.elapsed_seconds = 0

        # Debug info
        self.show_debug = True
        self.next_state = None

        game_logger.debug(
            "BlackScreenGameplayState initialized", "BlackScreenGameplayState"
        )

    def handle_event(self, event):
        """Handle events for the black screen state.

        Args:
            event: Pygame event to process

        Returns:
            bool: True if event was handled, False otherwise
        """
        try:
            # Handle ESC key to return to title screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_logger.info(
                        "ESC key pressed, returning to title",
                        "BlackScreenGameplayState",
                    )

                    # Import here to avoid circular imports
                    try:
                        from src.states.title_state import TitleState

                        self.next_state = TitleState(self.game)
                        return True
                    except Exception as e:
                        game_logger.error(
                            f"Error creating TitleState: {e}",
                            "BlackScreenGameplayState",
                            exc_info=True,
                        )

                # Toggle debug info with D key
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                    game_logger.debug(
                        f"Debug display toggled: {self.show_debug}",
                        "BlackScreenGameplayState",
                    )
                    return True

        except Exception as e:
            game_logger.error(
                f"Error handling event: {e}", "BlackScreenGameplayState", exc_info=True
            )

        return False

    def update(self, dt):
        """Update the black screen state.

        Args:
            dt: Time delta in seconds
        """
        try:
            # Update elapsed time
            self.elapsed_seconds += dt

            # After 60 seconds, you could automatically transition back to title
            # Uncomment for automatic return to title after timeout
            # if self.elapsed_seconds > 60:
            #     from src.states.title_state import TitleState
            #     self.next_state = TitleState(self.game)

        except Exception as e:
            game_logger.error(
                f"Error in update: {e}", "BlackScreenGameplayState", exc_info=True
            )

    def draw(self, screen):
        """Draw the black screen state.

        Args:
            screen: Pygame surface to draw on
        """
        try:
            # Fill the screen with black
            screen.fill(BLACK)

            # Draw placeholder text
            title_text = self.font.render("Placeholder Gameplay", True, WHITE)
            screen.blit(
                title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3)
            )

            # Instructions
            instructions = self.small_font.render(
                "Press ESC to return to title screen", True, WHITE
            )
            screen.blit(
                instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2)
            )

            # Show elapsed time
            time_text = self.small_font.render(
                f"Time in state: {self.elapsed_seconds:.1f}s", True, WHITE
            )
            screen.blit(
                time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 40)
            )

            # Debug info (toggled with D key)
            if self.show_debug:
                debug_lines = [
                    f"Game state: {getattr(self.game, 'game_state', 'unknown')}",
                    f"Next state: {self.next_state.__class__.__name__ if self.next_state else 'None'}",
                    f"Start time: {self.start_time.strftime('%H:%M:%S')}",
                ]

                for i, line in enumerate(debug_lines):
                    debug_text = self.small_font.render(line, True, (200, 200, 200))
                    screen.blit(debug_text, (20, HEIGHT - 100 + i * 25))

        except Exception as e:
            game_logger.error(
                f"Error drawing: {e}", "BlackScreenGameplayState", exc_info=True
            )
            # Fallback - at least draw something to indicate an error
            error_text = self.font.render("Drawing Error", True, (255, 0, 0))
            screen.blit(
                error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 2)
            )

    def enter(self):
        """Called when entering the black screen state."""
        game_logger.info(
            "Entering BlackScreenGameplayState", "BlackScreenGameplayState"
        )

        # Reset timer
        self.start_time = datetime.now()
        self.elapsed_seconds = 0

        # Set game's current state
        self.game.game_state = PLAYING

        # Clear the next_state to avoid unintended transitions
        self.next_state = None

    def exit(self):
        """Called when exiting the black screen state."""
        game_logger.info("Exiting BlackScreenGameplayState", "BlackScreenGameplayState")
        game_logger.debug(
            f"Total time in state: {self.elapsed_seconds:.1f}s",
            "BlackScreenGameplayState",
        )
