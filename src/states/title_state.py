"""Title screen state for Jammin' Eats.

Handles the main menu with options for Continue, New Game, Load, and Quit.
Continue option is only enabled if the tutorial has been completed.
"""

import pygame
from src.states.state import GameState
from src.persistence.dal import is_tutorial_complete
from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE, BLUE, GREEN
from src.debug.logger import game_logger

# Import states for transitions
try:
    from src.states.black_screen_gameplay_state import BlackScreenGameplayState
    from src.states.tutorial_state import TutorialState
except ImportError:
    # Try direct import as fallback
    try:
        from states.black_screen_gameplay_state import BlackScreenGameplayState
        from states.tutorial_state import TutorialState
    except ImportError:
        game_logger.error("Could not import necessary state classes", "TitleState")

class TitleState(GameState):
    """Main menu/title screen state."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_menu = pygame.font.SysFont(None, 48)
        
        # Title text
        self.title_text = self.font_title.render('Jammin\'  Eats', True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(WIDTH // 2, 150))
        
        # Enable/disable menu options based on tutorial completion
        try:
            # Check if game has tutorial_completed property already (might be set from TutorialCompleteState)
            game_value = getattr(self.game, 'tutorial_completed', None)
            
            # If game doesn't have it set, check database
            if game_value is None:
                # Get player ID safely
                player_id = 1  # Default player ID
                if hasattr(self.game, 'persistence') and self.game.persistence is not None:
                    player_id = getattr(self.game.persistence, 'player_id', 1)
                
                # Check database status
                game_logger.debug(f"Checking tutorial completion for player_id={player_id}", "TitleState")
                tutorial_complete = is_tutorial_complete(player_id) 
                
                # Update game object for future reference
                self.game.tutorial_completed = tutorial_complete
            else:
                tutorial_complete = game_value
                game_logger.debug(f"Using cached tutorial_completed={tutorial_complete} from game object", "TitleState")
                
            game_logger.info(f"Tutorial completion status: {tutorial_complete}", "TitleState")
        except Exception as e:
            game_logger.error(f"Error checking tutorial completion: {e}", "TitleState", exc_info=True)
            tutorial_complete = False  # Default to false if there's an error
            
        # Enable/disable menu options based on tutorial completion
        self.menu_items_enabled = {
            'continue': tutorial_complete,
            'new game': True,
            'load': tutorial_complete,
            'exit': True
        }
        game_logger.debug(f"Menu items enabled: {self.menu_items_enabled}", "TitleState")
        
        # Menu options
        self.menu_items = [
            {"id": "continue", "text": "Continue", "enabled": self.menu_items_enabled['continue']},
            {"id": "new_game", "text": "New Game", "enabled": self.menu_items_enabled['new game']},
            {"id": "load", "text": "Load", "enabled": self.menu_items_enabled['load']},
            {"id": "quit", "text": "Quit", "enabled": self.menu_items_enabled['exit']}
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
        """Handle input events for the title menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                # Move selection up, skipping disabled items
                original_index = self.selected_index
                while True:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    if self.menu_items[self.selected_index]["enabled"] or self.selected_index == original_index:
                        break
                game_logger.debug(f"Menu selection moved to: {self.menu_items[self.selected_index]['id']}", "TitleState")
                return True
                
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                # Move selection down, skipping disabled items
                original_index = self.selected_index
                while True:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    if self.menu_items[self.selected_index]["enabled"] or self.selected_index == original_index:
                        break
                game_logger.debug(f"Menu selection moved to: {self.menu_items[self.selected_index]['id']}", "TitleState")
                return True
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Process selected menu item
                selected_item = self.menu_items[self.selected_index]
                menu_id = selected_item["id"]
                is_enabled = selected_item["enabled"]
                
                game_logger.info(f"Menu item selected: {menu_id} (enabled: {is_enabled})", "TitleState")
                
                if not is_enabled:
                    game_logger.warning(f"Attempted to select disabled menu item: {menu_id}", "TitleState")
                    return True
                
                # Process enabled menu options
                try:
                    if menu_id == "continue":
                        # Continue game where left off (requires tutorial completed)
                        try:
                            game_logger.info("Continue selected - transitioning to gameplay", "TitleState")
                            self.game.tutorial_mode = False
                            self.game.use_simplified_gameplay = True
                            
                            # Use next_state pattern for proper transition
                            self.next_state = BlackScreenGameplayState(self.game)
                            game_logger.debug("Set next_state to BlackScreenGameplayState", "TitleState")
                            
                            # Load the latest saved game data
                            if hasattr(self.game, 'persistence') and self.game.persistence:
                                self.game.persistence.load_latest_save()
                                game_logger.info("Loaded latest save from database", "TitleState")
                        except Exception as e:
                            game_logger.error(f"Error transitioning to continue game: {e}", "TitleState", exc_info=True)
                        
                    elif menu_id == "new_game":
                        # Start new game (tutorial if not done, gameplay if tutorial done)
                        try:
                            # Check if tutorial is needed
                            tutorial_needed = False
                            if hasattr(self.game, 'persistence') and self.game.persistence:
                                tutorial_needed = not self.game.persistence.is_tutorial_complete()
                                
                                # Reset player progress in database for new game
                                self.game.persistence.reset_player_progress()
                                game_logger.info("Reset player progress for new game", "TitleState")
                            
                            game_logger.info(f"New Game selected - tutorial_needed: {tutorial_needed}", "TitleState")
                            
                            # Reset game properties for a new game
                            self.game.money = 0
                            self.game.successful_deliveries = 0
                            
                            # Set tutorial mode based on completion status
                            self.game.tutorial_mode = tutorial_needed
                            self.game.use_simplified_gameplay = True
                        
                            # Use next_state pattern for proper transition
                            if tutorial_needed:
                                self.next_state = TutorialState(self.game)
                                game_logger.info("Starting tutorial state", "TitleState")
                            else:
                                self.next_state = BlackScreenGameplayState(self.game)
                                game_logger.info("Starting gameplay state", "TitleState")
                        except Exception as e:
                            game_logger.error(f"Error starting new game: {e}", "TitleState", exc_info=True)
                        
                    elif menu_id == "load":
                        try:
                            # Transition to load game menu
                            game_logger.info("Load selected - transitioning to load game menu", "TitleState")
                            from src.states.load_game_state import LoadGameState
                            self.next_state = LoadGameState(self.game)
                        except Exception as e:
                            game_logger.error(f"Error transitioning to load game menu: {e}", "TitleState", exc_info=True)
                        
                    elif menu_id == "options":
                        try:
                            # Transition to options menu
                            game_logger.info("Options selected - transitioning to options menu", "TitleState")
                            from src.states.options_state import OptionsState
                            self.next_state = OptionsState(self.game)
                        except Exception as e:
                            game_logger.error(f"Error transitioning to options menu: {e}", "TitleState", exc_info=True)
                            
                    elif menu_id == "quit":
                        # Exit game
                        game_logger.info("Quit selected - exiting game", "TitleState")
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                        
                except Exception as e:
                    game_logger.error(f"Error processing menu selection '{menu_id}': {e}", "TitleState", exc_info=True)
                
                return True
        
        return False
        
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
