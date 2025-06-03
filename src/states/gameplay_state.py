"""Gameplay state for Jammin' Eats.

Handles the main gameplay loop including player movement, 
customer interactions, food delivery, and economy.
"""

import pygame
from src.states.state import GameState
from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE, GREEN, MENU, PLAYING
from src.debug.logger import game_logger

class GameplayState(GameState):
    """Main gameplay state."""
    
    def __init__(self, game):
        """Initialize the gameplay state.
        
        Args:
            game: The main Game instance this state belongs to
        """
        super().__init__(game)
        game_logger.info("Initializing GameplayState", "GameplayState")
        
        # Store references to game objects for easier access
        self.player = game.player
        self.game_map = game.game_map
        self.customers = game.customers
        self.foods = game.foods
        self.shop = getattr(game, 'shop', None)
        
        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        
        # Initialize customer spawn timer
        self.customer_spawn_timer = 0
        self.customer_spawn_interval = 5.0  # Spawn every 5 seconds initially
        
        game_logger.debug("GameplayState initialized", "GameplayState")
        
    def handle_event(self, event):
        """Handle gameplay events including player input."""
        # Handle shop events if shop is open
        if self.shop and self.shop.visible and self.shop.handle_event(event):
            return True
            
        # Toggle shop
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            if self.shop:
                self.shop.toggle()
                game_logger.debug("Shop toggled", "GameplayState")
                return True
                
        # Player movement and actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to title screen
                game_logger.info("ESC pressed, returning to title", "GameplayState")
                self.game.game_state = MENU
                self.next_state = None  # Trigger exit from gameplay
                return True
                
        # Let the player handle its own input events
        if self.player and hasattr(self.player, 'handle_event'):
            if self.player.handle_event(event):
                return True
                
        return False
        
    def update(self, dt):
        """Update game logic.
        
        Args:
            dt: Time delta in seconds
        """
        try:
            # Update player
            if self.player:
                self.player.update(dt)
                
            # Update customers
            for customer in list(self.customers):
                customer.update(dt)
                
            # Update food items
            for food in list(self.foods):
                food.update(dt)
                
            # Spawn customers on timer
            self.customer_spawn_timer += dt
            if self.customer_spawn_timer >= self.customer_spawn_interval:
                self.customer_spawn_timer = 0
                self.game.spawn_customer()
                game_logger.debug("Customer spawned on timer", "GameplayState")
                
            # Update any particles or effects
            if hasattr(self.game, 'particles'):
                self.game.particles.update(dt)
                
            # Check for player-customer interactions
            self._check_interactions()
            
        except Exception as e:
            game_logger.error(f"Error in gameplay update: {e}", "GameplayState", exc_info=True)
            
    def draw(self, screen):
        """Draw the gameplay state.
        
        Args:
            screen: The surface to draw on
        """
        try:
            # Clear screen
            screen.fill(BLACK)
            
            # Draw map
            if self.game_map:
                self.game_map.draw(screen)
                
            # Draw game objects
            if self.customers:
                self.customers.draw(screen)
                
            if self.foods:
                self.foods.draw(screen)
                
            if self.player:
                self.player.draw(screen)
                
            # Draw particles if available
            if hasattr(self.game, 'particles'):
                self.game.particles.draw(screen)
                
            # Draw UI
            self._draw_ui(screen)
            
            # Draw shop if open
            if self.shop and self.shop.visible:
                self.shop.draw(screen)
                
        except Exception as e:
            game_logger.error(f"Error in gameplay drawing: {e}", "GameplayState", exc_info=True)
            
    def enter(self):
        """Called when entering the gameplay state."""
        game_logger.info("Entering GameplayState", "GameplayState")
        
        # Ensure necessary game objects are initialized
        if not self.player or not self.game_map:
            game_logger.warning("Missing required game objects, attempting to initialize", "GameplayState")
            self.game.reset_game()
            # Refresh our object references
            self.player = self.game.player
            self.game_map = self.game.game_map
            self.customers = self.game.customers
            self.foods = self.game.foods
            self.shop = getattr(self.game, 'shop', None)
        
        # Set game state to playing
        self.game.game_state = PLAYING
        
        # Reset player position
        if self.player:
            self.player.reset_position()
            game_logger.debug("Player position reset", "GameplayState")
            
        # Clear any existing customers and spawn initial ones
        self.customers.empty()
        self.foods.empty()
        self.game.spawn_customer()
        game_logger.debug("Initial customer spawned", "GameplayState")
        
    def exit(self):
        """Called when exiting the gameplay state."""
        game_logger.info("Exiting GameplayState", "GameplayState")
        
    def _check_interactions(self):
        """Check for interactions between game objects."""
        try:
            if not self.player:
                return
                
            # Player-customer interactions
            for customer in list(self.customers):
                if pygame.sprite.collide_rect(self.player, customer):
                    if hasattr(customer, 'interact'):
                        customer.interact(self.player, self.game)
                        
            # Player-food interactions
            for food in list(self.foods):
                if pygame.sprite.collide_rect(self.player, food):
                    if hasattr(food, 'interact'):
                        food.interact(self.player, self.game)
                        
        except Exception as e:
            game_logger.error(f"Error checking interactions: {e}", "GameplayState", exc_info=True)
            
    def _draw_ui(self, screen):
        """Draw UI elements like money and selected food."""
        try:
            # Draw money
            money_text = self.font.render(f'${self.game.money}', True, WHITE)
            screen.blit(money_text, (10, 10))
            
            # Draw selected food indicator
            if self.game.selected_food:
                selected_text = self.font.render(f'Selected: {self.game.selected_food}', True, WHITE)
                screen.blit(selected_text, (10, 40))
                
            # Draw shop hint
            shop_text = self.font.render('Press B to open shop', True, (200, 200, 200))
            screen.blit(shop_text, (10, HEIGHT - 30))
            
            # Draw key commands
            help_text = self.font.render('ESC: Menu | ARROWS: Move', True, (200, 200, 200))
            screen.blit(help_text, (WIDTH - 250, HEIGHT - 30))
            
        except Exception as e:
            game_logger.error(f"Error drawing UI: {e}", "GameplayState", exc_info=True)
