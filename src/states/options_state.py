"""
Options State for Jammin' Eats

Handles the display and configuration of game options and settings.
Part of the professional game development implementation plan.
"""

import pygame
from src.states.game_state import GameState
from src.debug.logger import game_logger


class OptionsState(GameState):
    """
    State for displaying and configuring game options.
    Includes audio, display, and gameplay settings.
    """

    def __init__(self, game):
        """Initialize the options menu state."""
        super().__init__(game)
        game_logger.info("Initializing OptionsState", "OptionsState")

        # Menu configuration
        self.title = "Options"
        self.categories = [
            {"id": "audio", "text": "Audio Settings", "enabled": True},
            {"id": "display", "text": "Display Settings", "enabled": True},
            {"id": "gameplay", "text": "Gameplay Settings", "enabled": True},
            {"id": "back", "text": "Back to Title", "enabled": True},
        ]
        self.current_category = 0

        # UI properties
        self.title_color = (255, 215, 0)  # Gold
        self.option_color = (255, 255, 255)  # White
        self.selected_color = (0, 255, 255)  # Cyan
        self.background_color = (0, 0, 80)  # Dark blue

        # Settings state
        self.settings = {
            "audio": {"music_volume": 0.7, "sfx_volume": 0.8, "mute": False},
            "display": {
                "fullscreen": False,
                "resolution": "800x600",
                "show_fps": False,
            },
            "gameplay": {"difficulty": "Normal", "show_hints": True, "auto_save": True},
        }

        # Active settings category and option
        self.active_category = None
        self.active_option_index = 0

    def enter(self):
        """Called when entering this state."""
        game_logger.info("Entering OptionsState", "OptionsState")
        # Load current settings from database (placeholder)

    def exit(self):
        """Called when exiting this state."""
        game_logger.info("Exiting OptionsState", "OptionsState")
        # Save settings if changed
        self._save_settings()

    def _save_settings(self):
        """Save current settings to the database."""
        try:
            game_logger.info("Saving settings", "OptionsState")
            # For now, just log what would be saved
            game_logger.debug(f"Would save settings: {self.settings}", "OptionsState")
            # TODO: Implement actual settings persistence
        except Exception as e:
            game_logger.error(
                f"Error saving settings: {e}", "OptionsState", exc_info=True
            )

    def update(self, dt):
        """Update logic for the options state."""
        pass  # No ongoing updates needed for this menu

    def draw(self, screen):
        """Draw the options menu."""
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

            if self.active_category is None:
                # Main category menu
                self._draw_categories(screen, width, height, option_font)
            else:
                # Settings for the selected category
                self._draw_category_settings(screen, width, height, option_font)

            # Render instructions at the bottom
            instruction_font = pygame.font.Font(None, 24)
            if self.active_category is None:
                instructions = "↑/↓: Navigate   Enter: Select   Esc: Return to Title"
            else:
                instructions = (
                    "↑/↓: Navigate   ←/→: Change Value   Enter: Save   Esc: Back"
                )
            instruction_surf = instruction_font.render(
                instructions, True, (200, 200, 200)
            )
            instruction_rect = instruction_surf.get_rect(
                center=(width // 2, height - 40)
            )
            screen.blit(instruction_surf, instruction_rect)

        except Exception as e:
            game_logger.error(
                f"Error drawing OptionsState: {e}", "OptionsState", exc_info=True
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

    def _draw_categories(self, screen, width, height, font):
        """Draw the category selection menu."""
        y_pos = 180
        for i, category in enumerate(self.categories):
            text = category["text"]
            color = (
                self.selected_color if i == self.current_category else self.option_color
            )

            option_surf = font.render(text, True, color)
            option_rect = option_surf.get_rect(center=(width // 2, y_pos))
            screen.blit(option_surf, option_rect)
            y_pos += 60

    def _draw_category_settings(self, screen, width, height, font):
        """Draw the settings for the selected category."""
        # Header for the category
        category_name = next(
            (
                cat["text"]
                for cat in self.categories
                if cat["id"] == self.active_category
            ),
            "Settings",
        )
        header_surf = font.render(category_name, True, self.title_color)
        header_rect = header_surf.get_rect(center=(width // 2, 160))
        screen.blit(header_surf, header_rect)

        # Get settings for this category
        category_settings = self.settings.get(self.active_category, {})

        # Draw each setting
        y_pos = 220
        for i, (key, value) in enumerate(category_settings.items()):
            # Format the setting name nicely
            setting_name = key.replace("_", " ").title()

            # Format the value based on its type
            if isinstance(value, bool):
                value_text = "On" if value else "Off"
            elif isinstance(value, float) and 0 <= value <= 1:
                value_text = f"{int(value * 100)}%"
            else:
                value_text = str(value)

            # Determine text color
            color = (
                self.selected_color
                if i == self.active_option_index
                else self.option_color
            )

            # Draw the setting name and value
            setting_text = f"{setting_name}: {value_text}"
            setting_surf = font.render(setting_text, True, color)
            setting_rect = setting_surf.get_rect(center=(width // 2, y_pos))
            screen.blit(setting_surf, setting_rect)
            y_pos += 50

    def handle_event(self, event):
        """Handle input events."""
        try:
            if event.type == pygame.KEYDOWN:
                if self.active_category is None:
                    # Main category menu navigation
                    return self._handle_category_navigation(event)
                else:
                    # Setting adjustment navigation
                    return self._handle_setting_navigation(event)
        except Exception as e:
            game_logger.error(
                f"Error handling event in OptionsState: {e}",
                "OptionsState",
                exc_info=True,
            )
            # Return to category menu in case of error
            self.active_category = None

        return False  # Event not consumed

    def _handle_category_navigation(self, event):
        """Handle navigation in the main category menu."""
        if event.key == pygame.K_UP:
            # Move selection up
            self.current_category = (self.current_category - 1) % len(self.categories)
            return True

        elif event.key == pygame.K_DOWN:
            # Move selection down
            self.current_category = (self.current_category + 1) % len(self.categories)
            return True

        elif event.key == pygame.K_RETURN:
            # Select the current category
            category = self.categories[self.current_category]
            if category["id"] == "back":
                # Return to title screen
                from src.states.title_state import TitleState

                self.next_state = TitleState(self.game)
                game_logger.info("Returning to title screen", "OptionsState")
            else:
                # Enter the selected category
                self.active_category = category["id"]
                self.active_option_index = 0
                game_logger.debug(
                    f"Selected category: {category['id']}", "OptionsState"
                )
            return True

        elif event.key == pygame.K_ESCAPE:
            # Return to title screen
            from src.states.title_state import TitleState

            self.next_state = TitleState(self.game)
            game_logger.info("Returning to title screen", "OptionsState")
            return True

        return False

    def _handle_setting_navigation(self, event):
        """Handle navigation in a settings category."""
        # Get settings for this category
        category_settings = self.settings.get(self.active_category, {})
        # Get the list of setting keys
        setting_keys = list(category_settings.keys())

        if not setting_keys:
            # No settings to navigate, go back to category menu
            self.active_category = None
            return True

        if event.key == pygame.K_UP:
            # Move selection up
            self.active_option_index = (self.active_option_index - 1) % len(
                setting_keys
            )
            return True

        elif event.key == pygame.K_DOWN:
            # Move selection down
            self.active_option_index = (self.active_option_index + 1) % len(
                setting_keys
            )
            return True

        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            # Adjust the selected setting
            current_key = setting_keys[self.active_option_index]
            current_value = category_settings[current_key]

            # Modify based on value type
            if isinstance(current_value, bool):
                # Toggle boolean value
                category_settings[current_key] = not current_value
            elif isinstance(current_value, float) and 0 <= current_value <= 1:
                # Adjust volume type value
                step = 0.1
                if event.key == pygame.K_LEFT:
                    new_value = max(0.0, current_value - step)
                else:
                    new_value = min(1.0, current_value + step)
                category_settings[current_key] = new_value
            elif isinstance(current_value, str) and current_key == "difficulty":
                # Cycle through difficulty options
                difficulties = ["Easy", "Normal", "Hard"]
                current_idx = (
                    difficulties.index(current_value)
                    if current_value in difficulties
                    else 0
                )
                if event.key == pygame.K_LEFT:
                    new_idx = (current_idx - 1) % len(difficulties)
                else:
                    new_idx = (current_idx + 1) % len(difficulties)
                category_settings[current_key] = difficulties[new_idx]

            # Log the change
            game_logger.debug(
                f"Changed {current_key} to {category_settings[current_key]}",
                "OptionsState",
            )
            return True

        elif event.key == pygame.K_RETURN:
            # Save settings and return to category menu
            self._save_settings()
            self.active_category = None
            return True

        elif event.key == pygame.K_ESCAPE:
            # Return to category menu without saving
            self.active_category = None
            game_logger.debug(
                "Returned to category menu without saving", "OptionsState"
            )
            return True

        return False
