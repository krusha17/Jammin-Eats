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

# Import new economy and database systems
from src.core.economy import Economy, EconomyPhase

# Handle potential database module import errors
DATABASE_AVAILABLE = False
try:
    from src.core.database import GameDatabase
    DATABASE_AVAILABLE = True
except ImportError as e:
    # Only log the error message, not the exception object
    log_error(f"Database module import error: {str(e)}")
    print("[INFO] Database functionality will be disabled")
    
    # Create a stub GameDatabase class for fallback
    class GameDatabase:
        def __init__(self, *args, **kwargs):
            log_error("Using stub GameDatabase - database features unavailable")
            
        def save_player_progress(self, *args, **kwargs):
            return False
            
        def load_player_progress(self, *args, **kwargs):
            return None
            
        def log_transaction(self, *args, **kwargs):
            return False


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
        self.particles = pygame.sprite.Group()
        
        # UI elements
        self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start", GREEN, (100, 255, 100))
        self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))
        self.restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Restart", GREEN, (100, 255, 100))
        
        # Load game sounds
        self.sounds = load_sounds()
        
        # Initialize map
        self.game_map = None
        
        # Initialize player
        self.player = None
        
        # Initialize economy system
        log("Initializing economy system...")
        try:
            self.economy = Economy()
            log("Economy system initialized")
        except Exception as e:
            log_error("Failed to initialize economy", e)
            self.economy = None
        
        # Initialize database connection if available
        self.game_database = None
        if DATABASE_AVAILABLE:
            log("Initializing database connection...")
            try:
                self.game_database = GameDatabase()
                log("Database system initialized")
            except Exception as e:
                log_error(f"Failed to initialize database: {str(e)}")
                self.game_database = None
        
        # Track current map and frame for database and economy tracking
        self.current_map_id = 1  # Default to first map
        self.current_frame = 1   # Default to first frame
        
        # Auto-save timer is already initialized in __init__
        
        # Load font
        self.font = pygame.font.Font(None, 36)
        
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
        progress_loaded = False
        if self.game_database is not None:
            log("Attempting to load saved progress")
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
            self.all_sprites.add(self.player)
            log("Player created successfully")
        except Exception as e:
            log_error("Error creating player", e)
            # Create a simplified player object if regular creation fails
            # This is a minimal implementation to prevent crashes
            from src.sprites.player import create_fallback_player
            self.player = create_fallback_player(WIDTH // 2, HEIGHT // 2)
            log("Created fallback player")
            self.all_sprites.add(self.player)
        
        # Change game state to playing
        self.game_state = PLAYING
        log("Game reset complete, state changed to PLAYING")
    
    def log_purchase_transaction(self, food_type, amount):
        """Log a food purchase transaction to the database"""
        # Skip if database is not available
        if self.game_database is None:
            return False
            
        try:
            # Log the purchase transaction
            self.game_database.log_transaction(
                player_id=1,  # Default player ID for now
                transaction_type="food_purchase",
                amount=-amount,  # Negative amount for purchases
                description=f"Purchase of {food_type}",
                map_id=self.current_map_id,
                frame=self.current_frame
            )
            
            if self.debug_mode:
                print(f"[DATABASE] Logged purchase transaction for {food_type} (${amount:.2f})")
            return True
        except Exception as e:
            # Soft fail for database errors
            if self.debug_mode:
                print(f"[DATABASE] Error logging purchase transaction: {str(e)}")
            return False
    
    def save_player_progress(self):
        """Save player progress to database if available"""
        # Skip if database is not available
        if self.game_database is None:
            if self.debug_mode:
                print("[DATABASE] Save skipped - database not available")
            return False
        
        try:
            # Prepare economy data for saving
            economy_data = {
                'money': self.economy.money if self.economy else 0,
                'current_phase': self.economy.current_phase if self.economy else 1,
                'map_id': self.current_map_id,
                'frame': self.current_frame
            }
            
            # Prepare inventory data (placeholder for now)
            inventory_data = {
                'pizza': 10,
                'smoothie': 10,
                'icecream': 10,
                'pudding': 10
            }
            
            # Save to database
            result = self.game_database.save_player_progress(
                player_id=1,  # Default player ID for now
                economy_data=economy_data,
                inventory_data=inventory_data
            )
            
            if self.debug_mode:
                print(f"[DATABASE] Player progress saved successfully")
            return True
            
        except Exception as e:
            # Log error but don't crash the game
            if self.debug_mode:
                print(f"[DATABASE] Error saving progress: {str(e)}")
            return False
    
    def load_player_progress(self):
        """Load player progress from database if available"""
        # Skip if database is not available
        if self.game_database is None:
            if self.debug_mode:
                print("[DATABASE] Load skipped - database not available")
            return False
        
        try:
            # Load from database
            progress_data = self.game_database.load_player_progress(player_id=1)
            
            if not progress_data:
                if self.debug_mode:
                    print("[DATABASE] No saved progress found")
                return False
            
            # Update economy with saved data
            if self.economy and 'economy' in progress_data:
                econ_data = progress_data['economy']
                
                # Set money
                if 'money' in econ_data:
                    self.economy.money = econ_data['money']
                
                # Update map and frame tracking
                if 'map_id' in econ_data and 'frame' in econ_data:
                    self.current_map_id = econ_data['map_id']
                    self.current_frame = econ_data['frame']
                    
                    # Update economy phase based on map and frame
                    self.economy.update_phase(self.current_map_id, self.current_frame)
            
            # Update inventory with saved data (placeholder for now)
            # Will be implemented in inventory phase
            
            if self.debug_mode:
                print(f"[DATABASE] Player progress loaded successfully")
            return True
            
        except Exception as e:
            # Log error but don't crash the game
            if self.debug_mode:
                print(f"[DATABASE] Error loading progress: {str(e)}")
            return False
    
    def spawn_customer(self):
        """Spawn a customer at a valid position"""
        spawn_time = time.time()  # Start timing for performance monitoring
        
        if self.game_map:
            # Try to get spawn points from the map
            spawn_positions = self.game_map.get_spawn_positions("CustomerSpawn")
            
            if spawn_positions and len(spawn_positions) > 0:
                # Choose a random spawn point from the map
                pos = random.choice(spawn_positions)
                
                # Create the customer at the spawn position
                customer = Customer(pos[0], pos[1])
                self.customers.add(customer)
                self.all_sprites.add(customer)
                
                # Create spawn particles
                self._create_spawn_particles(pos[0], pos[1])
                
                if self.debug_mode:
                    print(f"Customer spawned at map position: {pos}")
                    spawn_time_elapsed = time.time() - spawn_time
                    print(f"Spawn time: {spawn_time_elapsed:.4f} seconds")
                return
        
        # Fallback: Find a random walkable position if map-based spawning failed
        for attempt in range(20):  # Try up to 20 random positions
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            
            # Check if the position is walkable
            if not self.game_map or self.game_map.is_walkable(x, y):
                customer = Customer(x, y)
                self.customers.add(customer)
                self.all_sprites.add(customer)
                
                # Create spawn particles
                self._create_spawn_particles(x, y)
                
                if self.debug_mode:
                    print(f"Customer spawned at random position: ({x}, {y})")
                    if 'spawn_time' in locals():
                        spawn_time_elapsed = time.time() - spawn_time
                        print(f"Spawn time: {spawn_time_elapsed:.4f} seconds")
                return
        
        if self.debug_mode:
            print("Failed to spawn customer: No valid spawn positions found")
    
    def _create_spawn_particles(self, x, y):
        """Helper function to create particle effects at spawn point"""
        for _ in range(10):
            particle = Particle(x, y, (255, 255, 255), size=random.randint(2, 5), speed=1.5, lifetime=0.5)
            self.particles.add(particle)
            self.all_sprites.add(particle)
    
    def validate_customer_positions(self):
        """Checks all customers to ensure they're in valid positions"""
        for customer in self.customers:
            if self.game_map and not self.game_map.is_walkable(customer.rect.centerx, customer.rect.centery):
                # Try to find a valid position nearby
                for attempt in range(10):
                    offset_x = random.randint(-50, 50)
                    offset_y = random.randint(-50, 50)
                    new_x = customer.rect.centerx + offset_x
                    new_y = customer.rect.centery + offset_y
                    
                    if self.game_map.is_walkable(new_x, new_y):
                        customer.rect.centerx = new_x
                        customer.rect.centery = new_y
                        if self.debug_mode:
                            print(f"Relocated customer to valid position: ({new_x}, {new_y})")
                        break
    
    def run(self):
        """Main game loop"""
        running = True
        
        # Initialize game elements
        if self.game_state == MENU:
            # Create UI buttons (re-create them to ensure they're at the right position)
            self.start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start", GREEN, (100, 255, 100))
            self.exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))
        
        while running:
            # Calculate delta time for frame-rate independent physics
            dt = self.clock.tick(FPS) / 1000.0
            
            # Process events
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    # Update the screen surface to the new size
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    # Optionally, store new width/height if you use them elsewhere:
                   # WIDTH, HEIGHT = event.size


                if event.type == pygame.KEYDOWN:
                    # Toggle debug mode with F12 or D key
                    if event.key == pygame.K_F12 or event.key == pygame.K_d:
                        self.debug_mode = toggle_debug_mode(self.debug_mode, self.sounds)
                
                # Handle button clicks
                if self.game_state == MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.start_button.is_clicked(event):
                            if 'button_sound' in self.sounds and self.sounds['button_sound']:
                                self.sounds['button_sound'].play()
                            self.reset_game()
                        
                        if self.exit_button.is_clicked(event):
                            if 'button_sound' in self.sounds and self.sounds['button_sound']:
                                self.sounds['button_sound'].play()
                            running = False
                
                elif self.game_state == GAME_OVER:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.restart_button.is_clicked(event):
                            if 'button_sound' in self.sounds and self.sounds['button_sound']:
                                self.sounds['button_sound'].play()
                            self.reset_game()
            
            # Update game state
            if self.game_state == PLAYING:
                # Update game time
                self.game_time += dt
                
                # Check if it's time to auto-save progress
                current_time = pygame.time.get_ticks() / 1000.0
                if current_time - self.last_save_time >= self.auto_save_interval:
                    self.save_player_progress()
                    self.last_save_time = current_time
                
                # Spawn customers at regular intervals
                self.customer_spawn_timer += dt
                if self.customer_spawn_timer >= CUSTOMER_SPAWN_RATE:
                    self.spawn_customer()
                    self.customer_spawn_timer = 0
                
                # Update game elements
                self.player.update(dt, self.customers, self.foods, self.game_map)
                self.customers.update(dt)
                self.foods.update(dt)
                
                # Check for food-customer collisions
                for food in list(self.foods):
                    for customer in self.customers:
                        if food.rect.colliderect(customer.rect):
                            # Check if customer likes this type of food
                            if customer.food_preference == food.food_type:
                                # Determine delivery quality based on customer patience
                                patience_percent = customer.patience_timer / customer.patience
                                if patience_percent < 0.3:
                                    delivery_quality = "perfect_delivery"
                                else:
                                    delivery_quality = "standard_delivery"
                                
                                # Calculate payment through economy system if available
                                if self.economy is not None:
                                    # Calculate payment based on food type and delivery quality
                                    payment = self.economy.calculate_delivery_payment(
                                        food.food_type, delivery_quality)
                                    self.economy.add_money(
                                        payment, f"Delivery of {food.food_type} ({delivery_quality})")
                                    
                                    # Log transaction in database if available
                                    if self.game_database is not None:
                                        try:
                                            # Log transaction with current map and frame info
                                            self.game_database.log_transaction(
                                                player_id=1,  # Default player ID for now
                                                transaction_type="delivery_payment",
                                                amount=payment,
                                                description=f"Delivery of {food.food_type} ({delivery_quality})",
                                                map_id=self.current_map_id,
                                                frame=self.current_frame
                                            )
                                        except Exception as e:
                                            # Soft fail for database errors - log but continue gameplay
                                            if self.debug_mode:
                                                print(f"[DATABASE] Error logging transaction: {str(e)}")
                                    
                                    # Log in debug mode
                                    if self.debug_mode:
                                        print(f"[ECONOMY] Earned ${payment:.2f} for {food.food_type} delivery")
                                
                                # Traditional scoring still in place during transition
                                self.score += 100
                                if 'pickup_sound' in self.sounds and self.sounds['pickup_sound']:
                                    self.sounds['pickup_sound'].play()
                                
                                # Customer leaves
                                customer.feed(food.food_type)
                                self.player.deliveries += 1
                                
                                # Create happy particles
                                for _ in range(15):
                                    particle = Particle(
                                        customer.rect.centerx,
                                        customer.rect.centery,
                                        GREEN,
                                        size=random.randint(3, 6),
                                        speed=2,
                                        lifetime=0.8
                                    )
                                    self.particles.add(particle)
                                    self.all_sprites.add(particle)
                            
                            # Remove the food
                            food.kill()
                
                # Update particles
                self.particles.update(dt)
                
                # Update high score
                self.high_score = max(self.high_score, self.score)
                
                # Check game over condition (optional)
                if self.player.missed_deliveries >= 10:
                    self.game_state = GAME_OVER
            
            # Render frame
            self._render(mouse_pos)
            
            # Update the display
            pygame.display.flip()
        
        # Update game state
        if self.game_state == PLAYING:
            # Update game time
            self.game_time += dt
            
            # Spawn customers at regular intervals
            self.customer_spawn_timer += dt
            if self.customer_spawn_timer >= CUSTOMER_SPAWN_RATE:
                self.spawn_customer()
                self.customer_spawn_timer = 0
            
            # Update game elements
            self.player.update(dt, self.customers, self.foods, self.game_map)
            self.customers.update(dt)
            self.foods.update(dt)
            
            # Check for food-customer collisions
            for food in list(self.foods):
                for customer in self.customers:
                    if food.rect.colliderect(customer.rect):
                        # Check if customer likes this type of food
                        if customer.food_preference == food.food_type:
                            # Correct food delivered
                            self.score += 100
                            if 'pickup_sound' in self.sounds and self.sounds['pickup_sound']:
                                self.sounds['pickup_sound'].play()
                            
                            # Customer leaves
                            customer.feed(food.food_type)
                            self.player.deliveries += 1
                            
                            # Create happy particles
                            for _ in range(15):
                                particle = Particle(
                                    customer.rect.centerx,
                                    customer.rect.centery,
                                    GREEN,
                                    size=random.randint(3, 6),
                                    speed=2,
                                    lifetime=0.8
                                )
                                self.particles.add(particle)
                                self.all_sprites.add(particle)
                        
                        # Remove the food
                        food.kill()
            
            # Update particles
            self.particles.update(dt)
            
            # Update high score
            self.high_score = max(self.high_score, self.score)
            
            # Check game over condition (optional)
            if self.player.missed_deliveries >= 10:
                self.game_state = GAME_OVER
        
        # Render frame
        self._render(mouse_pos)
        
        # Update the display
        pygame.display.flip()
    
        # Check if we should exit
        if not running:
            # Clean up
            pygame.quit()
            sys.exit()

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
