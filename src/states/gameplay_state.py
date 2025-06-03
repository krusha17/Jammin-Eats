"""Gameplay state for Jammin' Eats.

Handles the main gameplay loop including player movement, 
customer interactions, food delivery, economy, HUD, and shop interactions.
"""

import pygame

# Use flexible import system to support both direct and src-prefixed imports
try:
    # Try direct imports first
    from states.state import GameState
    from core.constants import WIDTH, HEIGHT, BLACK, WHITE, GREEN, MENU, PLAYING
    from debug.logger import game_logger
    from ui.hud import HUD
    # Import prefix for dynamic imports later
    IMPORT_PREFIX = ""
except ImportError:
    # Fall back to src-prefixed imports
    from src.states.state import GameState
    from src.core.constants import WIDTH, HEIGHT, BLACK, WHITE, GREEN, MENU, PLAYING
    from src.debug.logger import game_logger
    from src.ui.hud import HUD
    # Import prefix for dynamic imports later
    IMPORT_PREFIX = "src."

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
        
        # UI elements
        self.font = pygame.font.SysFont(None, 24)
        
        # Initialize the HUD
        self.hud = HUD(WIDTH, HEIGHT)
        if self.player:
            self.player.selected_food_type = 'burger'  # Default food type
            
        # Access or create shop
        self.shop = getattr(game, 'shop', None)
        if not self.shop and hasattr(game, 'initialize_shop'):
            game_logger.info("Creating shop instance", "GameplayState")
            game.initialize_shop()
            self.shop = game.shop
        
        # Initialize customer spawn timer
        self.customer_spawn_timer = 0
        self.customer_spawn_interval = 5.0  # Spawn every 5 seconds initially
        
        game_logger.debug("GameplayState initialized", "GameplayState")
        
    def handle_event(self, event):
        """Handle gameplay events including player input."""
        try:
            # Priority 1: Handle shop events if shop is open (shop captures all input when active)
            if self.shop and self.shop.visible:
                if self.shop.handle_event(event):
                    game_logger.debug("Event handled by shop", "GameplayState")
                    return True
                    
                # If shop is open, only allow ESC and shop toggle
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                        pass  # Allow these to be handled below
                    else:
                        return True  # Block all other inputs when shop is open
            
            # Priority 2: HUD input handling (food selection via number keys)
            if event.type == pygame.KEYDOWN and not (self.shop and self.shop.visible):
                # Handle food selection via the HUD (number keys 1-5)
                food_keys = {pygame.K_1: 'burger', pygame.K_2: 'pizza', 
                            pygame.K_3: 'hotdog', pygame.K_4: 'taco', 
                            pygame.K_5: 'sushi'}
                            
                if event.key in food_keys:
                    selected_food = food_keys[event.key]
                    # Update both game and player's selected food
                    self.game.selected_food = selected_food
                    
                    # Update player if the method exists
                    if hasattr(self.player, 'set_selected_food'):
                        self.player.set_selected_food(selected_food)
                    elif hasattr(self.player, 'selected_food_type'):
                        self.player.selected_food_type = selected_food
                        
                    game_logger.debug(f"Selected food: {selected_food}", "GameplayState")
                    
                    # Update HUD selection highlight
                    if hasattr(self, 'hud') and self.hud:
                        self.hud.set_selection(selected_food)
                        
                    return True
                
                # Throw food with space bar
                elif event.key == pygame.K_SPACE:
                    game_logger.debug("Player attempted to throw food", "GameplayState")
                    # Implement throwing food logic here if not already elsewhere
                    if hasattr(self.player, 'throw_food'):
                        self.player.throw_food()
                        return True
                
            # Priority 3: Game control keys
            if event.type == pygame.KEYDOWN:
                # Shop toggle
                if event.key == pygame.K_b and self.shop:
                    self.shop.toggle_visibility()
                    game_logger.info(f"Shop {'opened' if self.shop.visible else 'closed'}", "GameplayState")
                    return True
                    
                # Exit to menu
                if event.key == pygame.K_ESCAPE:
                    game_logger.info("ESC pressed, returning to title", "GameplayState")
                    self.game.game_state = MENU
                    
                    # Try to import title state with correct import style
                    try:
                        if IMPORT_PREFIX == "":
                            from states.title_state import TitleState
                        else:
                            from src.states.title_state import TitleState
                            
                        self.next_state = TitleState(self.game)
                        game_logger.debug("Transitioning to TitleState", "GameplayState")
                    except ImportError as e:
                        game_logger.error(f"Failed to import TitleState: {e}", "GameplayState")
                        self.next_state = None  # Fallback - trigger exit from gameplay
                        
                    return True
                
            # Priority 4: Let the player handle movement and any other events
            if self.player and hasattr(self.player, 'handle_event'):
                if self.player.handle_event(event):
                    return True
                    
            return False
            
        except Exception as e:
            game_logger.error(f"Error in gameplay event handling: {e}", "GameplayState", exc_info=True)
            return False
        
    def update(self, dt):
        """Update game logic.
        
        Args:
            dt: Time delta in seconds
        """
        try:
            # Update HUD (if shop is not open)
            if not (self.shop and self.shop.visible):
                # Update HUD and pass current selection
                if self.player and hasattr(self.player, 'selected_food_type'):
                    self.hud.update(dt, self.player.selected_food_type)
            if self.shop and self.shop.visible:
                self.shop.update(dt)
                # When shop is open, we still update particles but not gameplay
                if hasattr(self.game, 'particles'):
                    self.game.particles.update(dt)
                return
            
            # Priority 2: Process any pending upgrades
            self._process_pending_upgrades()
                
            # Priority 3: Update HUD and synchronize with game state
            if hasattr(self, 'hud') and self.hud:
                # Sync HUD with current game state if needed
                if hasattr(self.game, 'selected_food') and self.game.selected_food:
                    self.hud.set_selection(self.game.selected_food)
            
            # Priority 4: Update player and synchronize food selection
            if self.player:
                if hasattr(self.player, 'update'):
                    self.player.update(dt)
                # Make sure selected food is synchronized
                if hasattr(self.player, 'selected_food_type') and \
                   hasattr(self.game, 'selected_food') and \
                   self.player.selected_food_type != self.game.selected_food:
                    self.player.selected_food_type = self.game.selected_food
            
            # Priority 5: Update customer spawn timer
            self._update_customer_spawn(dt)
            
            # Priority 6: Update sprite groups
            self._update_sprites(dt)
            
            # Priority 7: Update particle effects if present
            if hasattr(self.game, 'particles'):
                self.game.particles.update(dt)
            
            # Priority 8: Check for object interactions
            self._check_interactions()
            
            # Priority 9: Update economy if available
            if hasattr(self.game, 'economy'):
                self.game.economy.update(dt)
                
        except Exception as e:
            game_logger.error(f"Error in GameplayState.update: {e}", "GameplayState", exc_info=True)
            
    def _process_pending_upgrades(self):
        """Process any pending upgrades from the shop."""
        try:
            if hasattr(self.game, 'purchased_upgrades'):
                for purchased_upgrade in self.game.purchased_upgrades:
                    if 'speed' in purchased_upgrade and self.player and hasattr(self.player, 'speed'):
                        self.player.speed += 20  # Increase player speed
                        game_logger.debug(f"Player speed increased to {self.player.speed}", "GameplayState")
                    elif 'inventory' in purchased_upgrade and self.player and hasattr(self.player, 'food_inventory'):
                        self.player.food_inventory += 10  # Increase inventory
                        game_logger.debug(f"Player inventory increased to {self.player.food_inventory}", "GameplayState")
                # Clear processed upgrades
                self.game.purchased_upgrades = []
        except Exception as e:
            game_logger.error(f"Error processing upgrades: {e}", "GameplayState")
            
    def _update_customer_spawn(self, dt):
        """Handle customer spawning based on timer."""
        try:
            self.customer_spawn_timer += dt
            if self.customer_spawn_timer >= self.customer_spawn_interval:
                self.customer_spawn_timer = 0
                game_logger.debug("Spawning new customer", "GameplayState")
                self.game.spawn_customer()
        except Exception as e:
            game_logger.error(f"Error spawning customer: {e}", "GameplayState")
            
    def _update_sprites(self, dt):
        """Update all sprite groups with the current time delta."""
        try:
            # Update customers
            for customer in self.customers:
                if hasattr(customer, 'update'):
                    customer.update(dt)
                    
            # Update foods
            for food in self.foods:
                if hasattr(food, 'update'):
                    food.update(dt)
        except Exception as e:
            game_logger.error(f"Error updating sprites: {e}", "GameplayState")
            
    def draw(self, screen):
        """Draw the gameplay state.
        
        Args:
            screen: The surface to draw on
        """
        try:
            # Layer 1: Background and Map
            self._draw_background_layer(screen)
            
            # Layer 2: Game Objects (NPCs, items, food)
            self._draw_game_objects_layer(screen)
            
            # Layer 3: Player Character
            self._draw_player_layer(screen)
            
            # Layer 4: Particle Effects
            self._draw_particle_layer(screen)
            
            # Layer 5: HUD (always visible during gameplay)
            self._draw_hud_layer(screen)
            
            # Layer 6: Shop UI (modal, highest priority when visible)
            self._draw_shop_layer(screen)
                
        except Exception as e:
            game_logger.error(f"Error in GameplayState.draw: {e}", "GameplayState", exc_info=True)
            
    def _draw_background_layer(self, screen):
        """Draw background and map elements."""
        try:
            # Fill background with solid color as fallback
            screen.fill(BLACK)
            
            # Draw game map if available
            if self.game_map and hasattr(self.game_map, 'draw'):
                self.game_map.draw(screen)
                game_logger.debug("Drew game map", "GameplayState")
        except Exception as e:
            game_logger.error(f"Error drawing background layer: {e}", "GameplayState")
            
    def _draw_game_objects_layer(self, screen):
        """Draw game objects like customers and food items."""
        try:
            # Draw customers
            for customer in self.customers:
                if hasattr(customer, 'draw'):
                    customer.draw(screen)
                # Fallback to standard pygame drawing
                elif hasattr(customer, 'image') and hasattr(customer, 'rect'):
                    screen.blit(customer.image, customer.rect)
            
            # Draw food items
            for food in self.foods:
                if hasattr(food, 'draw'):
                    food.draw(screen)
                # Fallback to standard pygame drawing
                elif hasattr(food, 'image') and hasattr(food, 'rect'):
                    screen.blit(food.image, food.rect)
        except Exception as e:
            game_logger.error(f"Error drawing game objects layer: {e}", "GameplayState")
            
    def _draw_player_layer(self, screen):
        """Draw the player character."""
        try:
            if self.player:
                if hasattr(self.player, 'draw'):
                    self.player.draw(screen)
                # Fallback to standard pygame drawing
                elif hasattr(self.player, 'image') and hasattr(self.player, 'rect'):
                    screen.blit(self.player.image, self.player.rect)
        except Exception as e:
            game_logger.error(f"Error drawing player layer: {e}", "GameplayState")
            
    def _draw_particle_layer(self, screen):
        """Draw particle effects and animations."""
        try:
            if hasattr(self.game, 'particles'):
                self.game.particles.draw(screen)
                game_logger.debug("Drew particle effects", "GameplayState")
        except Exception as e:
            game_logger.error(f"Error drawing particle layer: {e}", "GameplayState")
            
    def _draw_hud_layer(self, screen):
        """Draw HUD elements including food selection, money, etc."""
        try:
            # Draw general UI elements (money, hints)
            self._draw_ui(screen)
            
            # Draw main HUD with food selection
            if hasattr(self, 'hud') and self.hud:
                self.hud.draw(screen)
                if hasattr(self.player, 'selected_food_type'):
                    # Ensure HUD reflects current selection
                    self.hud.set_selection(self.player.selected_food_type)
        except Exception as e:
            game_logger.error(f"Error drawing HUD layer: {e}", "GameplayState")
            
    def _draw_shop_layer(self, screen):
        """Draw the shop UI when visible."""
        try:
            if self.shop and self.shop.visible:
                self.shop.draw(screen)
                game_logger.debug("Drew shop UI", "GameplayState")
        except Exception as e:
            game_logger.error(f"Error drawing shop layer: {e}", "GameplayState")
            
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
        
        # Always refresh shop reference (in case it was initialized elsewhere)
        self.shop = getattr(self.game, 'shop', None)
        if not self.shop and hasattr(self.game, 'initialize_shop'):
            game_logger.info("Creating shop instance during state enter", "GameplayState")
            self.game.initialize_shop()
            self.shop = self.game.shop
        
        # Ensure HUD is properly synced with player's food selection
        if not hasattr(self, 'hud') or not self.hud:
            self.hud = HUD(WIDTH, HEIGHT)
            
        # Initialize player's selected food and sync with HUD if needed
        if self.player:
            if not hasattr(self.player, 'selected_food_type') or not self.player.selected_food_type:
                self.player.selected_food_type = 'burger'  # Default food
            self.hud.set_selection(self.player.selected_food_type)
        
        # Set game state to playing
        self.game.game_state = PLAYING
        
        # Reset player position
        if self.player:
            if hasattr(self.player, 'reset_position'):
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
        """Draw UI elements like money and game info."""
        try:
            # Draw money in top-left corner
            money_text = self.font.render(f'${self.game.money}', True, WHITE)
            screen.blit(money_text, (20, 20))
            
            # Draw selected food indicator below money (if HUD not shown or shop is open)
            if self.shop and self.shop.visible and hasattr(self.player, 'selected_food_type'):
                selected_text = self.font.render(f'Selected: {self.player.selected_food_type}', True, WHITE)
                screen.blit(selected_text, (20, 50))
                
            # Only show key hints if shop is NOT open
            if not (self.shop and self.shop.visible):
                # Draw shop hint
                shop_text = self.font.render('Press B to open shop', True, (200, 200, 200))
                screen.blit(shop_text, (10, HEIGHT - 30))
                
                # Draw food selection hint
                food_text = self.font.render('1-5: Select Food', True, (200, 200, 200))
                screen.blit(food_text, (WIDTH // 2 - 70, HEIGHT - 30))
                
                # Draw key commands
                help_text = self.font.render('ESC: Menu | SPACE: Throw', True, (200, 200, 200))
                screen.blit(help_text, (WIDTH - 250, HEIGHT - 30))
            else:
                # Show exit hint when shop is open
                exit_text = self.font.render('B or ESC: Close Shop', True, GREEN)
                screen.blit(exit_text, (WIDTH // 2 - 80, HEIGHT - 30))
            
        except Exception as e:
            game_logger.error(f"Error drawing UI: {e}", "GameplayState", exc_info=True)
