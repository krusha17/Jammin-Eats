"""Title screen state for Jammin' Eats.

Handles the main menu with options for Continue, New Game, Load, and Quit.
Continue option is only enabled if the tutorial has been completed.
"""

import pygame
from src.states.state import GameState
from src.persistence.dal import is_tutorial_complete
from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE, BLUE, GREEN
from src.debug.logger import game_logger

class TitleState(GameState):
    """Main menu/title screen state."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_menu = pygame.font.SysFont(None, 48)
        
        # Title text
        self.title_text = self.font_title.render('Jammin\'  Eats', True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(WIDTH // 2, 150))
        
        # Get tutorial completion status for menu options
        self.tutorial_complete = is_tutorial_complete()
        
        # Menu options
        self.menu_items = [
            {"id": "continue", "text": "Continue", "enabled": self.tutorial_complete},
            {"id": "new_game", "text": "New Game", "enabled": True},
            {"id": "load", "text": "Load", "enabled": True},
            {"id": "quit", "text": "Quit", "enabled": True}
        ]
        
        # Menu positioning
        self.menu_start_y = 300
        self.menu_spacing = 60
        self.menu_rects = []
        
        # Create text surfaces and rects for each menu item
        for i, item in enumerate(self.menu_items):
            color = WHITE if item["enabled"] else (100, 100, 100)  # Gray out disabled options
            text = self.font_menu.render(item["text"], True, color)
            rect = text.get_rect(center=(WIDTH // 2, self.menu_start_y + i * self.menu_spacing))
            self.menu_rects.append(rect)
        
        # Menu selection
        self.selected_index = 0
        # Skip disabled items
        while not self.menu_items[self.selected_index]["enabled"]:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
    
    def handle_event(self, event):
        """Handle menu selection and activation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Navigate up through enabled items
                original_index = self.selected_index
                while True:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    if self.menu_items[self.selected_index]["enabled"] or self.selected_index == original_index:
                        break
                return True
                
            elif event.key == pygame.K_DOWN:
                # Navigate down through enabled items
                original_index = self.selected_index
                while True:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    if self.menu_items[self.selected_index]["enabled"] or self.selected_index == original_index:
                        break
                return True
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Activate selected menu item
                selected_item = self.menu_items[self.selected_index]
                game_logger.info(f"Menu item activated: {selected_item['id']}", "TitleState")
                
                if selected_item["id"] == "continue" and selected_item["enabled"]:
                    # Load the most recent save and continue
                    game_logger.info("Continue option selected, resetting state and starting gameplay", "TitleState")
                    try:
                        self.game.reset_state()  # Reset game state but keep progress
                        self.game.tutorial_mode = False  # Ensure tutorial mode is off
                        
                        # Explicitly set to PLAYING to trigger state transition
                        from src.core.constants import PLAYING
                        self.game.game_state = PLAYING
                        game_logger.info(f"Game state explicitly set to PLAYING: {self.game.game_state}", "TitleState")
                    except Exception as e:
                        game_logger.error(f"Error during continue action: {e}", "TitleState", exc_info=True)
                    return True
                    
                elif selected_item["id"] == "new_game":
                    # Start a new game
                    game_logger.info("New Game option selected, resetting game and starting gameplay", "TitleState")
                    try:
                        game_logger.debug(f"Tutorial completion status: {self.tutorial_complete}", "TitleState")
                        self.game.reset_game()  # Full reset including progress
                        
                        if not self.tutorial_complete:
                            # First-time players go to tutorial
                            self.game.tutorial_mode = True
                            game_logger.info("First time player, starting tutorial", "TitleState")
                        else:
                            # Returning players skip tutorial
                            self.game.tutorial_mode = False
                            game_logger.info("Returning player, skipping tutorial", "TitleState")
                        
                        # Explicitly set to PLAYING to trigger state transition
                        from src.core.constants import PLAYING
                        self.game.game_state = PLAYING
                        game_logger.info(f"Game state explicitly set to PLAYING: {self.game.game_state}", "TitleState")
                    except Exception as e:
                        game_logger.error(f"Error during new game action: {e}", "TitleState", exc_info=True)
                    return True
                    
                elif selected_item["id"] == "load":
                    # TODO: Implement load game submenu
                    game_logger.warning("Load game not implemented yet", "TitleState")
                    print("Load game not implemented yet")
                    return True
                    
                elif selected_item["id"] == "quit":
                    game_logger.info("Quit option selected, exiting game", "TitleState")
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return True
        
        return False
    
    def update(self, dt):
        """Update title screen animations."""
        pass
    
    def draw(self, screen):
        """Draw the title screen and menu."""
        # Clear screen with background color
        screen.fill(BLACK)
        
        # Draw title
        screen.blit(self.title_text, self.title_rect)
        
        # Draw menu items
        for i, (item, rect) in enumerate(zip(self.menu_items, self.menu_rects)):
            # Determine text color based on selection and enabled state
            if i == self.selected_index and item["enabled"]:
                color = GREEN  # Highlight selected item
                # Draw selection indicator
                pygame.draw.rect(screen, GREEN, rect.inflate(20, 10), 2, border_radius=5)
            else:
                color = WHITE if item["enabled"] else (100, 100, 100)  # Gray out disabled options
            
            # Render and draw the menu text
            text = self.font_menu.render(item["text"], True, color)
            screen.blit(text, rect)
        
        # Draw version and copyright
        version_font = pygame.font.SysFont(None, 20)
        version_text = version_font.render('v0.8.0-beta', True, (150, 150, 150))
        copyright_text = version_font.render('© 2025 Jammin\'  Eats Team', True, (150, 150, 150))
        
        screen.blit(version_text, (10, HEIGHT - 40))
        screen.blit(copyright_text, (10, HEIGHT - 20))
    
    def enter(self):
        """Called when entering the title state."""
        game_logger.info("Entering title state", "TitleState")
        
        try:
            # Refresh tutorial completion status
            self.tutorial_complete = is_tutorial_complete()
            self.menu_items[0]["enabled"] = self.tutorial_complete
            game_logger.debug(f"Tutorial completion status: {self.tutorial_complete}", "TitleState")
        except Exception as e:
            game_logger.error(f"Error checking tutorial completion status: {e}", "TitleState", exc_info=True)
            # Default to not completed if there's an error
            self.tutorial_complete = False
            self.menu_items[0]["enabled"] = False
