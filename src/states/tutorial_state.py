"""Tutorial state for Jammin' Eats.

Handles the tutorial gameplay and tutorial completion detection.
Players must achieve specific goals to graduate from the tutorial.
"""

import pygame
from src.states.state import GameState
from src.states.tutorial_complete_state import TutorialCompleteState
from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE

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
        """Pass events to the main game."""
        # Just pass through to the underlying game
        return False
    
    def update(self, dt):
        """Check for tutorial completion and update hints."""
        # Update hint timer and fade out
        if self.show_hint:
            self.hint_timer -= dt
            if self.hint_timer <= 0:
                self.show_hint = False
        
        # Get current game stats to check for completion
        self.served_correct = self.game.successful_deliveries
        self.money_earned = self.game.money
        
        # Check if either tutorial goal has been met
        if self.served_correct >= self.target_deliveries or self.money_earned >= self.target_money:
            # Show the tutorial completion overlay
            self.next_state = TutorialCompleteState(self.game)
    
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
        # Ensure tutorial mode flag is set
        self.game.tutorial_mode = True
        # Reset tutorial tracking
        self.served_correct = 0
        self.money_earned = 0
        self.show_hint = True
        self.hint_timer = 15.0
