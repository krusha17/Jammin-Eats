"""Tutorial completion state.

Displays an overlay when the player completes the tutorial,
allowing them to acknowledge and proceed to the main game.
"""

import pygame
from src.states.state import GameState
from src.persistence.dal import mark_tutorial_complete
from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE

class TutorialCompleteState(GameState):
    """State shown when the player successfully completes the tutorial."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font_large = pygame.font.SysFont(None, 64)
        self.font_small = pygame.font.SysFont(None, 32)
        
        # Create translucent overlay surface
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Black with alpha for translucency
        
        # Text elements
        self.title_text = self.font_large.render('Tutorial Complete!', True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        
        self.instruction_text = self.font_small.render('Press ENTER to continue', True, WHITE)
        self.instruction_rect = self.instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        
        # Animation variables
        self.alpha = 0  # Start fully transparent
        self.fade_in = True
        self.fade_speed = 5
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Mark tutorial as complete in database
                mark_tutorial_complete()
                
                # Update the game's state
                self.game.tutorial_completed = True
                
                # Return to main game
                from src.states.title_state import TitleState
                self.next_state = TitleState(self.game)
                return True
        return False
    
    def update(self, dt):
        """Update the overlay animation."""
        if self.fade_in and self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
    
    def draw(self, screen):
        """Draw the overlay with the completion message."""
        # First draw the game screen underneath
        self.game.draw_current_state(screen)
        
        # Draw our overlay with current alpha
        temp_overlay = self.overlay.copy()
        temp_overlay.set_alpha(self.alpha)
        screen.blit(temp_overlay, (0, 0))
        
        # Only draw text when overlay is visible enough
        if self.alpha > 100:
            # Apply a pulsing effect to the instruction text
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            pulse_value = abs(pulse - 0.5) * 2  # Oscillate between 0 and 1
            instruction_alpha = 128 + int(127 * pulse_value)  # Oscillate between 128 and 255
            
            # Draw title and instruction with appropriate alpha
            screen.blit(self.title_text, self.title_rect)
            
            # Create a copy of instruction text with pulsing alpha
            pulsing_text = self.instruction_text.copy()
            pulsing_text.set_alpha(instruction_alpha)
            screen.blit(pulsing_text, self.instruction_rect)
    
    def enter(self):
        """Reset animation state when entering this state."""
        self.alpha = 0
        self.fade_in = True
