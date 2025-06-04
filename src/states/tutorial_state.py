"""Tutorial state for Jammin' Eats.

Handles the tutorial gameplay and tutorial completion detection.
Players must achieve specific goals to graduate from the tutorial.
"""

import pygame

# Use flexible import system to support both direct and src-prefixed imports
try:
    # Try direct imports first
    from states.state import GameState
    from states.tutorial_complete_state import TutorialCompleteState
    from core.constants import WIDTH, HEIGHT, BLACK, WHITE
except ImportError:
    # Fall back to src-prefixed imports
    from src.states.state import GameState
    from src.states.tutorial_complete_state import TutorialCompleteState  
    from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE

# Set up a simple logger if the main one isn't available
try:
    from debug.logger import game_logger
except ImportError:
    try:
        from src.debug.logger import game_logger
    except ImportError:
        import logging
        game_logger = logging.getLogger("TutorialState")
        game_logger.info = lambda msg, *args, **kwargs: print(f"[INFO] {msg}")
        game_logger.debug = lambda msg, *args, **kwargs: print(f"[DEBUG] {msg}")
        game_logger.error = lambda msg, *args, **kwargs: print(f"[ERROR] {msg}")
        game_logger.warning = lambda msg, *args, **kwargs: print(f"[WARNING] {msg}")

class TutorialState(GameState):
    """Tutorial gameplay state with success tracking."""
    
    def __init__(self, game):
        super().__init__(game)
        # Track tutorial success metrics
        self.served_correct = 0     # Number of correct food deliveries
        self.money_earned = 0       # Money earned during tutorial
        self.target_deliveries = 5  # Target: 5 correct deliveries
        self.target_money = 50      # Target: $50 earned
        
        # Display tutorial instructions
        self.font = pygame.font.SysFont(None, 24)
        self.instruction_text = [
            "Welcome to Jammin' Eats!",
            "Tutorial Goals:",
            f"1. Successfully serve {self.target_deliveries} customers",
            f"2. Earn ${self.target_money}",
            "",
            "Controls:",
            "WASD or Arrow Keys - Move",
            "Space - Throw food",
            "1-4 - Select food type",
            "B - Open shop"
        ]
        
        # Hint display variables
        self.show_hint = True
        self.hint_alpha = 200  # Semi-transparent
        self.hint_timer = 15.0  # Show hints for 15 seconds
    
    def handle_event(self, event):
        """Handle input events in tutorial."""
        # Toggle hints with H key
        if event.type == pygame.KEYDOWN:
            # Handle food selection with number keys (1-5)
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                food_idx = event.key - pygame.K_1
                food_types = ['burger', 'pizza', 'sushi', 'taco', 'hotdog']
                if food_idx < len(food_types):
                    selected = food_types[food_idx]
                    # Update both game and HUD with selection
                    self.game.selected_food = selected
                    if hasattr(self.game, 'hud'):
                        self.game.hud.set_selection(selected)
                        game_logger.debug(f"Selected food changed to {selected}", "TutorialState")
                    return True
                    
            # Toggle hints with H key
            elif event.key == pygame.K_h:
                self.show_hint = not self.show_hint
                game_logger.debug(f"Tutorial hints {'shown' if self.show_hint else 'hidden'}", "TutorialState")
                return True
                
            # Throw food with SPACE
            elif event.key == pygame.K_SPACE:
                # Simulate food delivery for tutorial purposes
                self.served_correct += 1
                self.game.successful_deliveries = self.served_correct
                self.money_earned += 10
                self.game.money = self.money_earned
                game_logger.debug(f"Tutorial food delivered! Total: {self.served_correct}", "TutorialState")
                
                # Create a particle effect if the system exists
                if hasattr(self.game, 'particles'):
                    try:
                        # Position the effect in front of the player
                        if self.game.player:
                            pos_x = self.game.player.rect.centerx
                            pos_y = self.game.player.rect.centery
                            self.game.particles.add_effect('success', pos_x, pos_y)
                    except Exception as e:
                        # Don't crash if particles fail
                        game_logger.error(f"Couldn't create particle effect: {e}", "TutorialState")
                return True
                
            # Shop key (B)
            elif event.key == pygame.K_b:
                game_logger.debug("Shop triggered in tutorial", "TutorialState")
                if hasattr(self.game, 'shop'):
                    self.game.shop.toggle_visibility()
                    return True
                
            # Skip tutorial with ESC key (for testing)
            elif event.key == pygame.K_ESCAPE:
                game_logger.info("Tutorial skipped with ESC key", "TutorialState")
                # Show the tutorial completion overlay
                self.next_state = TutorialCompleteState(self.game)
                return True
                
        return False
    
    def update(self, dt):
        """Check for tutorial completion and update hints."""
        # Check if hint timer should expire
        if self.hint_timer > 0:
            self.hint_timer -= dt
            if self.hint_timer <= 0:
                game_logger.debug("Tutorial hints timed out", "TutorialState")
                self.show_hint = False
        
        # Get current game stats to check for completion
        self.served_correct = getattr(self.game, 'successful_deliveries', 0)
        self.money_earned = getattr(self.game, 'money', 0)
        
        # Log current progress toward tutorial goals
        game_logger.debug(f"Tutorial progress: deliveries={self.served_correct}/{self.target_deliveries}, money=${self.money_earned}/${self.target_money}", "TutorialState")
        
        # Check if both tutorial goals have been met
        tutorial_complete_delivery = self.served_correct >= self.target_deliveries
        tutorial_complete_money = self.money_earned >= self.target_money
        
        if tutorial_complete_delivery and tutorial_complete_money:
            game_logger.info(f"All tutorial goals reached! deliveries={self.served_correct}/{self.target_deliveries}, money=${self.money_earned}/${self.target_money}", "TutorialState")
            
            # Only transition if we haven't already
            if not hasattr(self, 'next_state') or self.next_state is None:
                try:
                    # Show the tutorial completion overlay
                    game_logger.info("Transitioning to TutorialCompleteState", "TutorialState")
                    self.next_state = TutorialCompleteState(self.game)
                except Exception as e:
                    game_logger.error(f"Failed to transition to TutorialCompleteState: {e}", "TutorialState", exc_info=True)
        else:
            # Provide feedback on which goal(s) are still pending
            if not tutorial_complete_delivery and not tutorial_complete_money:
                remaining_msg = f"Still need {self.target_deliveries - self.served_correct} more deliveries and ${self.target_money - self.money_earned} more money"
            elif not tutorial_complete_delivery:
                remaining_msg = f"Still need {self.target_deliveries - self.served_correct} more deliveries"
            else:  # not tutorial_complete_money
                remaining_msg = f"Still need ${self.target_money - self.money_earned} more money"
                
            game_logger.debug(f"Tutorial not yet complete: {remaining_msg}", "TutorialState")
    
    def draw(self, screen):
        """Draw tutorial hints over the game screen."""
        # Let the game draw first
        self.game.draw_current_state(screen)
        
        # Draw tutorial progress in the top-right corner
        progress_bg = pygame.Surface((200, 60), pygame.SRCALPHA)
        progress_bg.fill((0, 0, 0, 150))
        screen.blit(progress_bg, (WIDTH - 220, 10))
        
        # Draw progress text
        progress_font = pygame.font.SysFont(None, 20)
        
        delivery_text = progress_font.render(
            f"Deliveries: {self.served_correct}/{self.target_deliveries}", 
            True, WHITE
        )
        money_text = progress_font.render(
            f"Money: ${self.money_earned}/${self.target_money}", 
            True, WHITE
        )
        
        screen.blit(delivery_text, (WIDTH - 210, 20))
        screen.blit(money_text, (WIDTH - 210, 40))
        
        # Draw initial tutorial hints
        if self.show_hint:
            # Create instruction panel
            hint_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            hint_surface.fill((0, 0, 0, self.hint_alpha))
            
            # Draw each line of instruction text
            y_offset = 20
            for line in self.instruction_text:
                text = self.font.render(line, True, WHITE)
                hint_surface.blit(text, (20, y_offset))
                y_offset += 25
            
            # Add dismiss hint
            dismiss_text = self.font.render("Press H to toggle hints", True, (200, 200, 0))
            hint_surface.blit(dismiss_text, (20, y_offset + 10))
            
            # Position and draw the hint panel
            screen.blit(hint_surface, (20, 20))
    
    def enter(self):
        """Set up the tutorial when entering this state."""
        game_logger.info("Entering tutorial state", "TutorialState")
        
        # Ensure tutorial mode flag is set
        self.game.tutorial_mode = True
        
        # Set up tutorial objects
        try:
            self.game.setup_tutorial_objects()
            game_logger.debug("Tutorial objects initialized successfully", "TutorialState")
        except Exception as e:
            game_logger.error(f"Error setting up tutorial objects: {e}", "TutorialState")
        
        # Initialize HUD with default food selection if needed
        if hasattr(self.game, 'hud'):
            game_logger.debug("Setting HUD default food selection to burger", "TutorialState")
            self.game.hud.set_selection('burger')
            # Also set the game's selected food
            self.game.selected_food = 'burger'
        
        # Reset tutorial tracking
        self.served_correct = 0
        self.money_earned = 0
        self.show_hint = True
        self.hint_timer = 15.0
        
        game_logger.info("Tutorial state setup complete", "TutorialState")
