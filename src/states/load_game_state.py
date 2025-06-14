"""
Load Game State for Jammin' Eats

Handles the menu display and selection for loading saved games.
Part of the professional game development implementation plan.
"""

import pygame
from src.states.game_state import GameState
from src.debug.logger import game_logger
from src.persistence.dal import DataAccessLayer


class LoadGameState(GameState):
    """
    State for displaying and selecting save game slots.
    Shows up to 5 most recent saves with timestamps and metadata.
    """

    def __init__(self, game):
        """Initialize the load game menu state."""
        super().__init__(game)
        game_logger.info("Initializing LoadGameState", "LoadGameState")

        # Menu configuration
        self.title = "Load Game"
        self.save_slots = []
        self.current_selected = 0
        self.return_option_index = -1  # Will be set after loading save slots

        # UI properties
        self.title_color = (255, 215, 0)  # Gold
        self.option_color = (255, 255, 255)  # White
        self.selected_color = (0, 255, 255)  # Cyan
        self.background_color = (0, 0, 80)  # Dark blue

        # Load save data on initialization
        self._load_save_slots()

    def _load_save_slots(self):
        """Load available save game slots from the database."""
        try:
            game_logger.debug("Loading save game slots", "LoadGameState")

            # Create DAL if needed
            if not hasattr(self.game, "persistence") or not self.game.persistence:
                self.game.persistence = DataAccessLayer()

            # Clear existing slots
            self.save_slots = []

            # Attempt to load save slots (implement in DAL later)
            # For now, we'll create placeholder slots
            self.save_slots = [{"id": -1, "text": "Return to Title", "enabled": True}]

            # Set the return option index
            self.return_option_index = 0

            game_logger.debug(
                f"Loaded {len(self.save_slots)} save slots", "LoadGameState"
            )
        except Exception as e:
            game_logger.error(
                f"Error loading save slots: {e}", "LoadGameState", exc_info=True
            )
            # Always provide the Return option
            self.save_slots = [{"id": -1, "text": "Return to Title", "enabled": True}]
            self.return_option_index = 0

    def enter(self):
        """Called when entering this state."""
        game_logger.info("Entering LoadGameState", "LoadGameState")
        # Refresh save slots when entering the state
        self._load_save_slots()

    def exit(self):
        """Called when exiting this state."""
        game_logger.info("Exiting LoadGameState", "LoadGameState")

    def update(self, dt):
        """Update logic for the load game state."""
        pass  # No ongoing updates needed for this menu

    def draw(self, screen):
        """Draw the load game menu."""
        try:
            # Fill background
            screen.fill(self.background_color)

            # Calculate positions for rendering
            width, height = screen.get_size()
            title_font = pygame.font.Font(None, 64)
            option_font = pygame.font.Font(None, 36)

            # Render title
            title_surf = title_font.render(self.title, True, self.title_color)
            title_rect = title_surf.get_rect(center=(width // 2, 80))
            screen.blit(title_surf, title_rect)

            # Render save slot options
            y_pos = 180
            for i, slot in enumerate(self.save_slots):
                text = slot["text"]
                color = (
                    self.selected_color
                    if i == self.current_selected
                    else self.option_color
                )

                # Dim the text if the option is disabled
                if not slot.get("enabled", True):
                    # Create a dimmed version of the color
                    r, g, b = color
                    color = (r // 2, g // 2, b // 2)

                option_surf = option_font.render(text, True, color)
                option_rect = option_surf.get_rect(center=(width // 2, y_pos))
                screen.blit(option_surf, option_rect)
                y_pos += 60

            # Render instructions at the bottom
            instruction_font = pygame.font.Font(None, 24)
            instructions = "↑/↓: Navigate   Enter: Select   Esc: Return to Title"
            instruction_surf = instruction_font.render(
                instructions, True, (200, 200, 200)
            )
            instruction_rect = instruction_surf.get_rect(
                center=(width // 2, height - 40)
            )
            screen.blit(instruction_surf, instruction_rect)

        except Exception as e:
            game_logger.error(
                f"Error drawing LoadGameState: {e}", "LoadGameState", exc_info=True
            )
            # Draw fallback text in case of rendering error
            try:
                error_font = pygame.font.Font(None, 36)
                error_text = "Error loading menu. Press ESC to return."
                error_surf = error_font.render(error_text, True, (255, 0, 0))
                error_rect = error_surf.get_rect(center=(width // 2, height // 2))
                screen.blit(error_surf, error_rect)
            except Exception:
                pass  # Last resort if even fallback rendering fails

    def handle_event(self, event):
        """Handle input events."""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # Move selection up
                    self.current_selected = (self.current_selected - 1) % len(
                        self.save_slots
                    )
                    return True

                elif event.key == pygame.K_DOWN:
                    # Move selection down
                    self.current_selected = (self.current_selected + 1) % len(
                        self.save_slots
                    )
                    return True

                elif event.key == pygame.K_RETURN:
                    # Select the current option
                    if self.current_selected == self.return_option_index:
                        # Return to title screen
                        from src.states.title_state import TitleState

                        self.next_state = TitleState(self.game)
                        game_logger.info("Returning to title screen", "LoadGameState")
                    else:
                        # Selected a save slot - handle loading the game
                        slot = self.save_slots[self.current_selected]
                        if slot.get("enabled", True):
                            game_logger.info(
                                f"Selected save slot: {slot['id']}", "LoadGameState"
                            )
                            # TODO: Implement save game loading
                            # For now, just return to title
                            from src.states.title_state import TitleState

                            self.next_state = TitleState(self.game)
                    return True

                elif event.key == pygame.K_ESCAPE:
                    # Return to title screen
                    from src.states.title_state import TitleState

                    self.next_state = TitleState(self.game)
                    game_logger.info("Returning to title screen", "LoadGameState")
                    return True

        except Exception as e:
            game_logger.error(
                f"Error handling event in LoadGameState: {e}",
                "LoadGameState",
                exc_info=True,
            )
            # Return to title screen in case of error
            try:
                from src.states.title_state import TitleState

                self.next_state = TitleState(self.game)
            except Exception:
                pass  # Cannot handle further

        return False  # Event not consumed
