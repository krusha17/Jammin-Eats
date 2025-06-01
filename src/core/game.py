import pygame
import sys
import random
import os
import time
import math
import traceback
from pygame import mixer

# Import modules from our refactored structure
from src.core.constants import *
from src.sprites.player import Player
from src.sprites.customer import Customer
from src.sprites.food import Food
from src.sprites.particle import Particle
from src.map.tilemap import TiledMap
from src.ui.button import Button
from src.ui.text import draw_text
from src.utils.sounds import load_sounds
from src.debug.debug_tools import toggle_debug_mode
from src.debug.logger import log, log_error, log_asset_load
from src.ui.shop import ShopOverlay

# Import new economy, inventory and database systems
from src.core.economy import Economy, EconomyPhase
from src.core.inventory import Inventory

# Import the new persistence layer
from src.persistence.game_persistence import GamePersistence


class Game:
    def __init__(self, screen_width=WIDTH, screen_height=HEIGHT):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create the screen
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Jammin' Eats")
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Game state variables
        self.game_state = MENU  # Start at menu
        self.score = 0
        self.high_score = 0
        self.game_time = 0
        self.customer_spawn_timer = 0
        
        # Track player stats
        self.deliveries = 0
        self.missed_deliveries = 0
        self.missed = 0  # Counter for wrong food penalties
        
        # Map and frame tracking for economy/database integration
        self.current_map_id = 1
        self.current_frame = 1
        
        # Auto-save functionality
        self.last_save_time = pygame.time.get_ticks() / 1000.0
        self.auto_save_interval = 60  # Auto-save every 60 seconds
        
        # Debug mode
        self.debug_mode = False
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.customers = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()
        
        # Initialize upgrade system
        from src.core.upgrade_manager import UpgradeManager
        self.upgrades = UpgradeManager()
        
        # Initialize upgrade-affected attributes
        import src.core.constants as game_constants  # Direct import for easier access
        self.player_speed_mul = 1.0
        self.max_stock = MAX_STOCK
        self.food_lifespan_bonus = 0.0
        self.patience_multiplier = 1.0
        self.particles = pygame.sprite.Group()
        
        # UI elements
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start", GREEN, (100, 255, 100))
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))
        self.restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Restart", GREEN, (100, 255, 100))
        
        # Load game sounds
        self.sounds = load_sounds()
        
        # Initialize game state
        self.game_state = MENU  # Start in MENU state first
        
        # Initialize map
        self.game_map = None
        
        # Initialize player
        self.player = None
        
        # Initialize persistence layer
        self.persistence = GamePersistence(player_id=1)
        self.high_score = self.persistence.get_high_score()
        
        # Load persistent upgrades
        owned_upgrades = self.persistence.get_owned_upgrades()
        for upg_id in owned_upgrades:
            self.upgrades.own_upgrade(upg_id)
        
        # Initialize economy system
        log("Initializing economy system...")
        try:
            self.economy = Economy()
            log("Economy system initialized")
        except Exception as e:
            log_error("Failed to initialize economy", e)
            self.economy = None
        
        # Initialize inventory system
        log("Initializing inventory system...")
        try:
            self.inventory = Inventory(STARTING_STOCK)
            self.selected_food = "Tropical Pizza Slice"  # default selection
            log("Inventory system initialized")
        except Exception as e:
            log_error("Failed to initialize inventory", e)
            self.inventory = None
            self.selected_food = None
        
        # Initialize upgrade shop overlay
        self.shop = ShopOverlay(self)
        
        # Database initialization is now handled by the persistence layer
        # self.persistence is initialized above
        
        # Track current map and frame for database and economy tracking
        self.current_map_id = 1  # Default to first map
        self.current_frame = 1   # Default to first frame
        
        # Auto-save timer is already initialized in __init__
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create backgrounds
        self.menu_background = self._create_menu_background()
        self.game_over_background = self._create_game_over_background()
    
    def _create_menu_background(self):
        # Create menu background programmatically
        background = pygame.Surface((WIDTH, HEIGHT))
        
        # Create a gradient background
        for y in range(HEIGHT):
            color_value = int(255 * (1 - y / HEIGHT))
            color = (0, color_value // 2, color_value)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
        
        # Add some decorative elements
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            pygame.draw.circle(background, (255, 255, 255), (x, y), size)
            
        return background
    
    def _create_game_over_background(self):
        # Create game over background
        background = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color_value = int(200 * (1 - y / HEIGHT))
            color = (color_value + 55, 0, 0)
            pygame.draw.line(background, color, (0, y), (WIDTH, y))
            
        return background
    
    def reset_state(self):
        """Reset all game state variables but keep the same Game instance"""
        log("Resetting game state variables")
        
        # Reset all core gameplay variables
        self.score = 0
        self.missed = 0  # Reset wrong food penalty counter
        self.deliveries = 0
        self.missed_deliveries = 0
        self.game_time = 0
        self.customer_spawn_timer = 0
        
        # Do not reset upgrades - these persist between game sessions
        # But do re-apply their effects
        if hasattr(self, 'upgrades'):
            self.apply_upgrade_effects()
        
        # Reset economy if available
        if self.economy is not None:
            money, _ = self.persistence.get_starting_values()
            self.economy.money = money
            # Reset to tutorial phase
            self.economy.update_phase(1, 1)
        
        # Reset inventory to starting stock from DB
        from src.core.inventory import Inventory
        _, stock = self.persistence.get_starting_values()
        self.inventory = Inventory(stock)
        
        # Reset player's stats if player exists
        if self.player:
            self.player.deliveries = 0
            self.player.missed_deliveries = 0
        
        # Clear all active game entities
        self.customers.empty()
        self.foods.empty()
        self.particles.empty()
        
        # Switch back to active play
        self.game_state = PLAYING
        
        log("Game state reset complete")

    def reset_game(self):
        """Reset the game to its initial state"""
        log("Resetting game to initial state")
        
        # Clear sprite groups
        self.all_sprites.empty()
        self.customers.empty()
        self.foods.empty()
        self.particles.empty()
        
        # Reset game variables
        self.score = 0
        self.game_time = 0
        self.customer_spawn_timer = 0
        
        # Try loading saved progress first
        progress_loaded = self.load_player_progress()
        
        # If no progress was loaded, reset economy to defaults
        if not progress_loaded and self.economy is not None:
            log("No saved progress found, resetting economy to tutorial phase")
            # Update our map and frame tracking
            self.current_map_id = 1
            self.current_frame = 1
            # Reset economy to tutorial phase
            self.economy.update_phase(self.current_map_id, self.current_frame)
        elif progress_loaded:
            log(f"Loaded saved progress: Map {self.current_map_id}, Frame {self.current_frame}")
        
        # Reset auto-save timer
        self.last_save_time = pygame.time.get_ticks() / 1000.0
        
        # Initialize map
        log("Loading game map...")
        try:
            # Try to load the map from multiple possible locations
            map_name = "Level_1_Frame_1.tmx"
            map_paths = [
                os.path.join(MAP_DIR, map_name),
                os.path.join(ASSETS_DIR, "Maps", "level1", map_name),
                os.path.join(ASSETS_DIR, "Maps", map_name)
            ]
            
            # Log the map paths we're trying
            log(f"Trying to load map from {len(map_paths)} locations")
            for i, path in enumerate(map_paths):
                exists = os.path.exists(path)
                log(f"  {i+1}. {path} (Exists: {exists})")
            
            # Try each path until one works
            map_loaded = False
            for path in map_paths:
                if os.path.exists(path):
                    try:
                        log(f"Attempting to load map from: {path}")
                        self.game_map = TiledMap(path)
                        log("Map loaded successfully")
                        map_loaded = True
                        break
                    except Exception as e:
                        log_error(f"Error loading map from {path}", e)
            
            # If no map was loaded, create a fallback
            if not map_loaded:
                log_error("Could not load map from any location, using fallback")
                self.game_map = TiledMap("fallback")
        
        except Exception as e:
            log_error("Critical error loading map", e)
            self.game_map = None
        
        # Create player
        log("Creating player...")
        try:
            self.player = Player(WIDTH // 2, HEIGHT // 2)
            # Set reference to game object so player can access inventory
            self.player.game = self
            self.all_sprites.add(self.player)
            log("Player created successfully")
        except Exception as e:
            log_error("Error creating player", e)
            # Create a simplified player object if regular creation fails
            from src.sprites.player import create_fallback_player
            self.player = create_fallback_player(WIDTH // 2, HEIGHT // 2)
            self.player.game = self  # Even fallback player needs game reference
            log("Created fallback player")
            self.all_sprites.add(self.player)
        
        # Initialize shop overlay
        log("Shop overlay initialized")
        
        # Change game state to playing
        self.game_state = PLAYING
        log("Game reset complete, state changed to PLAYING")
    
    def apply_upgrade_effects(self):
        """Apply effects from all owned upgrades to the game"""
        if not hasattr(self, 'upgrades'):
            log("[ERROR] No upgrade manager found")
            return
            
        # Reset to base values first
        self.player_speed_mul = 1.0
        self.max_stock = MAX_STOCK
        self.food_lifespan_bonus = 0.0
        self.patience_multiplier = 1.0
        
        # Have the upgrade manager apply all effects
        mods = self.upgrades.apply_upgrades(self)
        
        # Apply to player if it exists
        if hasattr(self, 'player') and self.player:
            self.player.speed_multiplier = self.player_speed_mul
            log(f"Applied speed multiplier of {self.player_speed_mul}x to player")
        
    def buy_upgrade(self, upgrade_id):
        """Attempt to purchase an upgrade"""
        if self.shop and not self.shop.can_purchase(upgrade_id):
            return False
        
        upgrade = self.upgrades.get_upgrade(upgrade_id)
        if not upgrade:
            return False
        
        # Check money
        if self.economy.money < upgrade['cost']:
            return False
        
        # Deduct money and own the upgrade
        self.economy.money -= upgrade['cost']
        owned = self.upgrades.own_upgrade(upgrade_id)
        if owned:
            # Save upgrade purchase to DB
            self.persistence.save_upgrade_purchase(upgrade_id)
            self.apply_upgrade_effects()
            if self.shop:
                self.shop.refresh()
            return True
        return False

    def save_player_progress(self):
        """Save player progress to database using the persistence layer"""
        try:
            # Save current upgrades and money (if needed, expand as required)
            # This method can be expanded for more granular progress saving
            return True
        except Exception as e:
            log_error(f"Failed to save player progress: {e}")
            return False

    def load_player_progress(self):
        """Load player progress from database using the persistence layer"""
        try:
            self.high_score = self.persistence.get_high_score()
            owned_upgrades = self.persistence.get_owned_upgrades()
            for upg_id in owned_upgrades:
                self.upgrades.own_upgrade(upg_id)
            self.apply_upgrade_effects()
            money, stock = self.persistence.get_starting_values()
            if self.economy:
                self.economy.money = money
            if hasattr(self, 'inventory'):
                self.inventory = Inventory(stock)
            return True
        except Exception as e:
            log_error(f"Failed to load player progress: {e}")
            return None
            
    def spawn_customer(self):
        """Spawn a new customer at a random edge position"""
        # Retrieve spawn positions from Tiled map
        spawn_positions = []
        if self.game_map:
            spawn_positions = self.game_map.get_spawn_positions("CustomerSpawn")
        print(f"[DEBUG] Spawn positions from map: {spawn_positions}")
        
        if spawn_positions:
            x, y = random.choice(spawn_positions)
            print(f"[DEBUG] Selected map spawn position: ({x}, {y})")
        else:
            print("[DEBUG] No map spawn positions found, falling back to edge spawning")
            # Define map boundaries
            from src.core.constants import WIDTH, HEIGHT  # Import locally to avoid circular imports
            
            print("[DEBUG] Attempting to spawn customer...")
            
            # Choose edge placement (0=top, 1=right, 2=bottom, 3=left)
            edge = random.randint(0, 3)
            
            if edge == 0:  # Top edge
                x = random.randint(50, WIDTH - 50)
                y = 50
            elif edge == 1:  # Right edge
                x = WIDTH - 50
                y = random.randint(50, HEIGHT - 50)
            elif edge == 2:  # Bottom edge
                x = random.randint(50, WIDTH - 50)
                y = HEIGHT - 50
            else:  # Left edge
                x = 50
                y = random.randint(50, HEIGHT - 50)
            print(f"[DEBUG] Fallback spawn position: ({x}, {y})")
        
        # Create customer with food preferences
        customer = Customer(x, y)
        
        # Randomly assign food preference
        food_types = ["pizza", "smoothie", "icecream", "pudding"]
        customer.food_preference = random.choice(food_types)
        print(f"[DEBUG] Customer food preference assigned: {customer.food_preference}")
        
        # Redraw speech bubble icon for new preference
        customer._draw_fallback_food_icon()
        
        # Set up customer patience based on difficulty and upgrades
        base_patience = 10.0  # seconds
        customer.patience = base_patience * self.patience_multiplier
        customer.patience_timer = 0  # reset timer so they don't immediately leave
        
        print(f"[DEBUG] Customer patience: {customer.patience} seconds")
        
        # Add to sprite groups
        self.customers.add(customer)
        self.all_sprites.add(customer)
        
        print(f"[DEBUG] Customer added to sprite groups. Total customers: {len(self.customers)}")
        
        # Play spawn sound if available
        if 'customer_appear' in self.sounds and self.sounds['customer_appear']:
            self.sounds['customer_appear'].play()
        
        print("[DEBUG] Customer spawning complete")



    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                # Let shop overlay handle events first
                if hasattr(self, 'shop') and self.shop.handle_event(event):
                    continue
                # Toggle shop on B key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    self.shop.toggle()
                    continue
                if event.type == pygame.QUIT:
                    running = False
                if self.game_state == MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.start_button.is_clicked(event):
                            print("[DEBUG] Start button clicked")
                            if self.player is None:
                                print("[DEBUG] Resetting game (new game)")
                                self.reset_game()
                            else:
                                print("[DEBUG] Resetting state (continuing game)")
                                self.reset_state()
                            print(f"[DEBUG] Changing game state from {self.game_state} to PLAYING ({PLAYING})")
                            self.game_state = PLAYING
                            print(f"[DEBUG] Game state is now: {self.game_state}")
                        if self.exit_button.is_clicked(event):
                            running = False
                elif self.game_state == PLAYING:
                    # Handle food selection keys
                    if event.type == pygame.KEYDOWN:
                        # Debug key to manually spawn a customer with T key
                        if event.key == pygame.K_t:
                            print("[DEBUG] Manually spawning test customer")
                            self.spawn_customer()
                            
                        food_keys = {
                            pygame.K_1: "Tropical Pizza Slice",
                            pygame.K_2: "Ska Smoothie",
                            pygame.K_3: "Island Ice Cream",
                            pygame.K_4: "Rasta Rice Pudding"
                        }
                        if event.key in food_keys:
                            self.selected_food = food_keys[event.key]
                            if 'select_sound' in self.sounds and self.sounds['select_sound']:
                                self.sounds['select_sound'].play()
            # --- PLAYING state logic ---
            if self.game_state == PLAYING:
                # Make sure customer_spawn_timer is initialized
                if not hasattr(self, 'customer_spawn_timer'):
                    print("[DEBUG] Initializing missing customer_spawn_timer")
                    self.customer_spawn_timer = 0
                
                # Spawn customers at regular intervals
                self.customer_spawn_timer += dt
                print(f"[DEBUG] customer_spawn_timer: {self.customer_spawn_timer:.2f}/{CUSTOMER_SPAWN_RATE}")
                
                if self.customer_spawn_timer >= CUSTOMER_SPAWN_RATE:
                    print("[DEBUG] Time to spawn a customer!")
                    self.spawn_customer()
                    self.customer_spawn_timer = 0
            # Update game state, sprites, etc.
            if self.player:
                self.player.update(dt, self.customers, self.foods, self.game_map)
            self.customers.update(dt)
            self.foods.update(dt)
            # Food-customer collision detection
            for food in list(self.foods):
                for customer in list(self.customers):
                    if food.collides_with(customer):
                        food_match = food.food_type == customer.food_preference
                        print(f"[DEBUG] Food {food.food_type} collided with {customer.type} who wants {customer.food_preference} - MATCH: {food_match}")
                        
                        # Save the 'fed' state before feeding to detect changes
                        was_fed_before = getattr(customer, 'fed', False)
                        
                        # Feed the customer and remove the food
                        customer.feed(food.food_type)
                        food.kill()
                        
                        # Economy update: Only add money if customer was fed the correct food
                        if hasattr(customer, 'fed') and customer.fed and not was_fed_before:
                            payment = self.economy.calculate_delivery_payment(food.food_type, "perfect_delivery")
                            self.economy.add_money(payment, reason=f"Delivery to {customer.type}")
                            print(f"[DEBUG][ECONOMY] Added ${payment:.2f} for delivery of {food.food_type} to {customer.type}")
                            print(f"[DEBUG] Customer is now {customer.state} and leaving: {customer.leaving}")
            self.particles.update(dt) if hasattr(self, 'particles') else None
            # Render everything
            self._render(mouse_pos)
            pygame.display.flip()

    def _render(self, mouse_pos):
        """Render the game frame based on current game state"""
        self.screen.fill((BLACK))  # Or your preferred fallback color
        
        # PLAYING state - draw the game
        if self.game_state == PLAYING:
            # Initialize offset variables for centering
            blit_x, blit_y = 0, 0
            
            # Draw the map if available
            if self.game_map:
                # Get window and map sizes
                win_width, win_height = self.screen.get_size()
                map_width, map_height = self.game_map.map_surface.get_size()

                # Calculate top-left position to center the map
                blit_x = (win_width - map_width) // 2
                blit_y = (win_height - map_height) // 2

                # Draw the map centered
                self.screen.blit(self.game_map.map_surface, (blit_x, blit_y))
                
                # Draw debug information if debug mode is enabled
                if self.debug_mode:
                    self.game_map.draw_debug_spawn_points(self.screen, blit_x, blit_y)
                    self.game_map.draw_debug_walkable(self.screen, blit_x, blit_y)
                
                # Draw game entities with offset
                # Draw customers with offset
                for customer in self.customers:
                    customer.draw(self.screen, blit_x, blit_y)
                
                # Draw player with offset
                self.player.draw(self.screen, blit_x, blit_y)
                
                # Draw foods with offset (individual draws instead of group draw)
                for food in self.foods:
                    food.draw(self.screen, blit_x, blit_y)
                
                # Draw particles with offset
                for particle in self.particles:
                    particle.draw(self.screen, blit_x, blit_y)
            else:
                # Fallback without offsets if map failed to load
                self.screen.fill((0, 0, 0))
                draw_text(self.screen, "Map failed to load!", 48, WIDTH // 2, HEIGHT // 2, RED)
      
                for customer in self.customers:
                    customer.draw(self.screen)
                self.player.draw(self.screen)
                self.foods.draw(self.screen)
                self.particles.draw(self.screen)
            
            # Draw game time
            minutes = int(self.game_time) // 60
            seconds = int(self.game_time) % 60
            time_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            self.screen.blit(time_text, (WIDTH - 150, 60))
            
            # Draw economy information if available
            if self.economy is not None:
                # Display money
                money_text = self.font.render(f"Money: ${self.economy.money:.2f}", True, GREEN)
                self.screen.blit(money_text, (20, 20))
                
                # Display current phase
                # Fix: use self.economy.phase (and .name if it's an enum)
                phase_name = self.economy.phase.name if hasattr(self.economy.phase, 'name') else str(self.economy.phase)
                phase_text = self.font.render(f"Phase: {phase_name}", True, YELLOW)
                self.screen.blit(phase_text, (20, 60))
                
                # Display missed deliveries counter (penalty system)
                if not TUTORIAL_MODE:
                    color = YELLOW if self.missed < MAX_MISSED_DELIVERIES-1 else RED
                    missed_text = self.font.render(f"Wrong Food: {self.missed}/{MAX_MISSED_DELIVERIES}", True, color)
                    self.screen.blit(missed_text, (WIDTH - 250, 20))
                else:
                    # Show tutorial mode indicator
                    tutorial_text = self.font.render("TUTORIAL MODE", True, GREEN)
                    self.screen.blit(tutorial_text, (WIDTH - 250, 20))
            
            # Inventory information is now only displayed at the bottom of the screen
            if self.inventory is not None and hasattr(self, 'selected_food') and self.selected_food:
                # Show full inventory status at the bottom of the screen
                y_position = HEIGHT - 120
                self.screen.blit(self.font.render("INVENTORY:", True, WHITE), (20, y_position))
                
                # Map number keys to food types for display
                key_map = {
                    "1": "Tropical Pizza Slice",
                    "2": "Ska Smoothie",
                    "3": "Island Ice Cream",
                    "4": "Rasta Rice Pudding"
                }
                
                # Show each food type with its key binding and current stock
                for i, (key, food) in enumerate(key_map.items()):
                    color = GREEN if food == self.selected_food else WHITE
                    if self.inventory.qty(food) == 0:
                        color = RED  # Show in red if out of stock
                        
                    item_text = self.font.render(
                        f"[{key}] {food}: {self.inventory.qty(food)}", 
                        True, color)
                    self.screen.blit(item_text, (20, y_position + 30 + i * 25))
            
            # Draw debug mode indicator if active
            if self.debug_mode:
                debug_text = self.font.render("DEBUG MODE", True, YELLOW)
                self.screen.blit(debug_text, (WIDTH - 150, 100))
                
                # Draw additional economy debug info if available
                if self.economy is not None:
                    debug_econ_text = self.font.render(
                        f"Phase Mult: {self.economy.current_phase.price_multiplier:.2f}x", 
                        True, YELLOW)
                    self.screen.blit(debug_econ_text, (20, 100))
        
        # MENU state - draw the menu
        elif self.game_state == MENU:
            # Get current window size
            w, h = self.screen.get_size()
            
            # Create dynamic menu background based on current window size
            menu_bg = pygame.Surface((w, h))
            
            # Create a gradient background
            for y in range(h):
                color_value = int(255 * (1 - y / h))
                color = (0, color_value // 2, color_value)
                pygame.draw.line(menu_bg, color, (0, y), (w, y))
            
            # Add some decorative elements
            for _ in range(50):
                x = random.randint(0, w)
                y = random.randint(0, h)
                size = random.randint(1, 3)
                pygame.draw.circle(menu_bg, (255, 255, 255), (x, y), size)
                
            # Draw the dynamically created background
            self.screen.blit(menu_bg, (0, 0))
            
            # Center UI elements based on current window size
            draw_text(self.screen, "JAMMIN' EATS", 72, w // 2, h // 4, YELLOW)
            draw_text(self.screen, "Deliver tasty food to hungry customers!", 36, w // 2, h // 3, WHITE)
            
            # Reposition buttons
            self.start_button.rect.center = (w // 2, h // 2)
            self.exit_button.rect.center = (w // 2, h // 2 + 70)
            
            # Update and draw buttons
            self.start_button.update(mouse_pos)
            self.exit_button.update(mouse_pos)
            self.start_button.draw(self.screen)
            self.exit_button.draw(self.screen)
            
            # (High score display removed for now)
        
        # GAME_OVER state - draw the game over screen
        elif self.game_state == GAME_OVER:
            # Draw game over screen
            self.screen.blit(self.game_over_background, (0, 0))
            draw_text(self.screen, "GAME OVER", 72, WIDTH // 2, HEIGHT // 4, RED)
            draw_text(self.screen, f"Score: {self.score}", 48, WIDTH // 2, HEIGHT // 3, WHITE)
            draw_text(self.screen, f"High Score: {self.high_score}", 36, WIDTH // 2, HEIGHT // 3 + 50, WHITE)
            
            # Show stats
            minutes = int(self.game_time) // 60
            seconds = int(self.game_time) % 60
            draw_text(self.screen, f"Time Survived: {minutes:02d}:{seconds:02d}", 36, WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text(self.screen, f"Deliveries Made: {self.player.deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 40, WHITE)
            draw_text(self.screen, f"Customers Missed: {self.player.missed_deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 80, WHITE)
            
            # Update and draw restart button
            self.restart_button.update(mouse_pos)
            self.restart_button.draw(self.screen)
            
        # Draw shop overlay if it's open (on top of everything else)
        if hasattr(self, 'shop') and self.shop.is_open:
            self.shop.draw(self.screen)
