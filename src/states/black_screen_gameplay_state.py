"""Black screen gameplay state for testing game mechanics without assets.

This simplified state renders only basic shapes and text to allow testing the core
game logic without relying on assets or complex rendering.
"""

import pygame
from pygame.locals import *

# Try both import paths for compatibility
try:
    # Direct import
    from states.game_state import GameState
    from debug.logger import game_logger
    from core.constants import WIDTH, HEIGHT, WHITE, BLACK
except ImportError:
    # Src-prefixed import
    from src.states.game_state import GameState
    from src.debug.logger import game_logger
    from src.core.constants import WIDTH, HEIGHT, WHITE, BLACK

class BlackScreenGameplayState(GameState):
    """Minimalistic gameplay state with black background and simple shapes.
    
    This state is designed for testing game mechanics without requiring assets.
    Only basic shapes and text will be used to represent game objects.
    """
    
    def __init__(self, game):
        """Initialize the black screen gameplay state.
        
        Args:
            game: The main Game instance this state belongs to
        """
        super().__init__(game)
        game_logger.info("Initializing BlackScreenGameplayState", "BlackScreenGameplayState")
        
        # Font for rendering text
        self.font = pygame.font.SysFont(None, 24)
        self.debug_font = pygame.font.SysFont(None, 16)
        
        # Store references to game objects for easier access
        self.player_rect = pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40)
        self.player_speed = 300  # pixels per second
        self.money = getattr(game, 'money', 0)
        self.score = getattr(game, 'score', 0)
        
        # Simple representation of food types
        self.food_types = ['burger', 'pizza', 'taco', 'sushi']
        self.selected_food_index = 0
        self.selected_food = self.food_types[self.selected_food_index]
        
        # Customer simulation
        self.customers = []
        self.spawn_timer = 0
        self.spawn_interval = 3.0  # seconds
        
        # Debug info
        self.show_debug = True
        self.debug_info = []
    
    def handle_event(self, event):
        """Handle input events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.debug_info.append("Move UP")
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.debug_info.append("Move DOWN")
                return True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.debug_info.append("Move LEFT")
                return True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.debug_info.append("Move RIGHT")
                return True
            elif event.key == pygame.K_SPACE:
                # Simulate successful delivery
                self.money += 10
                self.score += 1
                game_logger.debug(f"Added money: ${self.money}, score: {self.score}", "BlackScreenGameplayState")
                self.debug_info.append(f"Food delivered! Money: ${self.money}")
                
                # Update game state values as well
                self.game.money = self.money
                self.game.successful_deliveries = self.score
                return True
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                # Change selected food
                self.selected_food_index = event.key - pygame.K_1
                if self.selected_food_index < len(self.food_types):
                    self.selected_food = self.food_types[self.selected_food_index]
                    game_logger.debug(f"Selected food: {self.selected_food}", "BlackScreenGameplayState")
                    self.debug_info.append(f"Selected: {self.selected_food}")
                    self.game.selected_food = self.selected_food
                return True
            elif event.key == pygame.K_h:
                # Toggle debug info
                self.show_debug = not self.show_debug
                return True
            elif event.key == pygame.K_b:
                # Simulate shop interaction
                self.debug_info.append("Shop attempted")
                return True
                
        return False
    
    def update(self, dt):
        """Update game logic.
        
        Args:
            dt: Time delta in seconds
        """
        # Update player position based on key states
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_rect.y -= int(self.player_speed * dt)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_rect.y += int(self.player_speed * dt)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_rect.x -= int(self.player_speed * dt)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_rect.x += int(self.player_speed * dt)
        
        # Keep player on screen
        self.player_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        # Update customer spawn timer
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            self._spawn_customer()
            
        # Update customers
        for customer in self.customers[:]:
            customer['timer'] -= dt
            if customer['timer'] <= 0:
                self.customers.remove(customer)
        
        # Limit debug info list length
        if len(self.debug_info) > 10:
            self.debug_info = self.debug_info[-10:]
    
    def draw(self, screen):
        """Draw the gameplay state.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear screen
        screen.fill(BLACK)
        
        # Draw player
        pygame.draw.rect(screen, (0, 255, 0), self.player_rect)
        
        # Draw customers
        for i, customer in enumerate(self.customers):
            pos = customer['pos']
            size = (30, 30)
            rect = pygame.Rect(pos[0] - size[0] // 2, pos[1] - size[1] // 2, *size)
            pygame.draw.rect(screen, (255, 0, 0), rect)
            
            # Draw customer food desire
            food_text = self.font.render(customer['wants'], True, WHITE)
            screen.blit(food_text, (pos[0] - food_text.get_width() // 2, pos[1] - 40))
            
            # Draw timer bar
            timer_width = 50 * (customer['timer'] / customer['duration'])
            pygame.draw.rect(screen, (255, 255, 0), (pos[0] - 25, pos[1] + 20, timer_width, 5))
        
        # Draw HUD
        self._draw_hud(screen)
        
        # Draw debug info
        if self.show_debug:
            self._draw_debug_info(screen)
    
    def _draw_hud(self, screen):
        """Draw the heads-up display.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw money and score
        money_text = self.font.render(f"Money: ${self.money}", True, WHITE)
        screen.blit(money_text, (10, 10))
        
        score_text = self.font.render(f"Deliveries: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 40))
        
        # Draw selected food indicator
        selected_text = self.font.render(f"Selected: {self.selected_food}", True, WHITE)
        screen.blit(selected_text, (WIDTH - selected_text.get_width() - 10, 10))
        
        # Draw controls legend
        controls = [
            "Controls:",
            "WASD/Arrows - Move",
            "Space - Deliver food",
            "1-4 - Select food",
            "B - Shop",
            "H - Toggle debug"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = self.debug_font.render(text, True, WHITE)
            screen.blit(ctrl_text, (WIDTH - ctrl_text.get_width() - 10, 40 + i * 20))
    
    def _draw_debug_info(self, screen):
        """Draw debug information.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw recent events
        for i, info in enumerate(self.debug_info):
            text = self.debug_font.render(info, True, (200, 200, 200))
            screen.blit(text, (10, HEIGHT - 20 * (len(self.debug_info) - i)))
            
        # Draw mouse position
        mouse_pos = pygame.mouse.get_pos()
        pos_text = self.debug_font.render(f"Mouse: {mouse_pos}", True, (200, 200, 200))
        screen.blit(pos_text, (10, HEIGHT - 20 * (len(self.debug_info) + 1)))
        
        # Draw FPS
        if hasattr(self.game, 'clock'):
            fps = int(self.game.clock.get_fps())
            fps_text = self.debug_font.render(f"FPS: {fps}", True, (200, 200, 200))
            screen.blit(fps_text, (10, HEIGHT - 20 * (len(self.debug_info) + 2)))
    
    def _spawn_customer(self):
        """Spawn a new customer at a random position."""
        import random
        
        # Generate a random position along the edges of the screen
        edge = random.choice(['top', 'right', 'bottom', 'left'])
        if edge == 'top':
            pos = (random.randint(50, WIDTH - 50), 50)
        elif edge == 'right':
            pos = (WIDTH - 50, random.randint(50, HEIGHT - 50))
        elif edge == 'bottom':
            pos = (random.randint(50, WIDTH - 50), HEIGHT - 50)
        else:  # left
            pos = (50, random.randint(50, HEIGHT - 50))
        
        # Create a new customer with random food desire
        wanted_food = random.choice(self.food_types)
        customer_duration = random.uniform(8.0, 15.0)
        
        self.customers.append({
            'pos': pos,
            'wants': wanted_food,
            'timer': customer_duration,
            'duration': customer_duration
        })
        
        self.debug_info.append(f"Customer wants {wanted_food}")
    
    def enter(self):
        """Called when entering this state."""
        game_logger.info("Entered BlackScreenGameplayState", "BlackScreenGameplayState")
        self.debug_info.append("Started black screen mode")
        
        # Ensure properties required by tutorial completion are initialized
        self.game.successful_deliveries = getattr(self.game, 'successful_deliveries', 0)
        self.game.money = getattr(self.game, 'money', 0)
        self.game.selected_food = getattr(self.game, 'selected_food', 'burger')
    
    def exit(self):
        """Called when exiting this state."""
        game_logger.info("Exited BlackScreenGameplayState", "BlackScreenGameplayState")
        
        # Persist state back to game
        self.game.money = self.money
        self.game.successful_deliveries = self.score
