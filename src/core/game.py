import pygame
import traceback
from src.core.constants import WIDTH, HEIGHT, FPS, MENU, PLAYING, CUSTOMER_SPAWN_RATE
from src.persistence.dal import is_tutorial_complete
from src.persistence.game_persistence import GamePersistence
from src.states import TitleState, TutorialState
from src.states.gameplay_state import GameplayState
from src.debug.logger import game_logger

class Game:
    def __init__(self, screen_width=WIDTH, screen_height=HEIGHT):
        game_logger.info("Initializing Game class", "Game")
        
        # Initialize pygame
        try:
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Jammin' Eats")
            self.clock = pygame.time.Clock()
            game_logger.debug("Pygame display initialized successfully", "Game")
        except Exception as e:
            game_logger.critical(f"Failed to initialize pygame display: {e}", "Game", exc_info=True)
            raise  # Re-raise as this is critical
        
        # Game state
        self.game_state = MENU
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize persistence
        try:
            self.persistence = GamePersistence()
            game_logger.debug("Game persistence initialized", "Game")
        except Exception as e:
            game_logger.error(f"Failed to initialize persistence: {e}", "Game", exc_info=True)
            self.persistence = None  # Set to None as fallback
        
        # Create sprite groups - critical for gameplay
        try:
            self.customers = pygame.sprite.Group()
            self.foods = pygame.sprite.Group()
            game_logger.debug("Sprite groups initialized", "Game")
        except Exception as e:
            game_logger.critical(f"Failed to create sprite groups: {e}", "Game", exc_info=True)
            raise  # Re-raise as sprite groups are critical
        
        # Other game objects will be created in reset_game()
        self.player = None
        self.game_map = None
        
        # Economy variables
        self.money = 0
        self.successful_deliveries = 0
        self.selected_food = None
        
        # Tutorial mode
        self.tutorial_mode = False
        
        # Check tutorial completion status if available
        try:
            # First check if persistence is available
            if self.persistence is None:
                game_logger.warning("Cannot check tutorial status: persistence unavailable", "Game")
                self.tutorial_mode = True  # Default to tutorial mode
            else:
                tutorial_completed = is_tutorial_complete(self.persistence.player_id)
                if not tutorial_completed:
                    self.tutorial_mode = True
                    game_logger.info("Tutorial not completed, enabling tutorial mode", "Game")
                else:
                    game_logger.info("Tutorial already completed", "Game")
        except Exception as e:
            game_logger.error(f"Error checking tutorial completion: {e}", "Game", exc_info=True)
            # Default to completed to avoid blocking player
            self.tutorial_mode = False  # Skip tutorial by default on error

    def run(self):
        """Main loop: tutorial, title, then gameplay using state pattern."""
        game_logger.info("Starting main game loop", "Game")
        
        current_state = None
        running = True
        
        # Tutorial Phase - only if tutorial hasn't been completed
        if self.tutorial_mode:
            game_logger.info("Starting tutorial phase", "Game")
            # Create tutorial state on demand
            from src.states.tutorial_state import TutorialState
            tutorial_state = TutorialState(self)
            current_state = tutorial_state
            current_state.enter()
        else:
            # Skip directly to title if tutorial already completed
            game_logger.info("Tutorial already completed, skipping to title", "Game")
            current_state = TitleState(self)
            current_state.enter()
            
        # Track current state type and time for debugging state transitions
        last_state_type = type(current_state).__name__
        last_state_change = pygame.time.get_ticks()
        
        # Main state machine loop
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # Let the current state handle the event
                try:
                    if current_state.handle_event(event):
                        continue  # Event was handled by state
                except Exception as e:
                    game_logger.error(f"Error in state event handling: {e}", "Game", exc_info=True)
            
            # Check for state transitions after event handling
            current_time = pygame.time.get_ticks()
            current_state_type = type(current_state).__name__
            
            # Log if we're in a different state type now
            if current_state_type != last_state_type:
                game_logger.info(f"State changed from {last_state_type} to {current_state_type}", "Game")
                last_state_type = current_state_type
                last_state_change = current_time
            
            # Check if we need to transition to gameplay based on game_state flag
            if self.game_state == PLAYING and not isinstance(current_state, GameplayState):
                game_logger.info(f"Explicit transition to GameplayState triggered by game_state={self.game_state}", "Game")
                try:
                    # First exit current state properly
                    game_logger.debug(f"Exiting current state: {type(current_state).__name__}", "Game")
                    current_state.exit()
                    
                    # Create and enter gameplay state
                    game_logger.debug("Creating new GameplayState instance", "Game")
                    current_state = GameplayState(self)
                    game_logger.debug("Entering GameplayState", "Game")
                    current_state.enter()
                    game_logger.info("Successfully transitioned to GameplayState", "Game")
                    
                    # Update tracking
                    last_state_change = current_time
                    last_state_type = "GameplayState"
                except Exception as e:
                    game_logger.critical(f"Failed to transition to GameplayState: {e}", "Game", exc_info=True)
                    # Try to recover by returning to title
                    try:
                        current_state = TitleState(self)
                        current_state.enter()
                        self.game_state = MENU
                    except Exception as recover_error:
                        game_logger.critical(f"Could not recover from transition error: {recover_error}", "Game", exc_info=True)
                    continue
                    
            # Update current state
            if current_state:
                dt = self.clock.tick(FPS) / 1000.0
                current_state.update(dt)
                current_state.draw(self.screen)
                pygame.display.flip()
                
        game_logger.info("Game loop terminated", "Game")

    def run_gameplay(self):
        """Legacy gameplay loop - now handled by GameplayState.
        This method is kept for backward compatibility but is no longer used.
        The main game loop now uses the state machine pattern."""
        game_logger.warning("run_gameplay() called directly - this method is deprecated", "Game")
        
        # Create and run a GameplayState directly
        gameplay_state = GameplayState(self)
        gameplay_state.enter()
        
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                    
                if gameplay_state.handle_event(event):
                    if gameplay_state.next_state:
                        gameplay_state.exit()
                        running = False
                        break
                    continue
                    
            gameplay_state.update(dt)
            gameplay_state.draw(self.screen)
            # Updates
            if self.player:
                self.player.update(dt, self.customers, self.foods, self.game_map)
            self.customers.update(dt)
            self.foods.update(dt)

            # Collision and economy
            for food in list(self.foods):
                for customer in list(self.customers):
                    if food.collides_with(customer):
                        was_fed_before = getattr(customer, 'fed', False)
                        customer.feed(food.food_type)
                        food.kill()
                        if getattr(customer, 'fed', False) and not was_fed_before:
                            payment = self.economy.calculate_delivery_payment(food.food_type, "perfect_delivery")
                            self.economy.add_money(payment, reason=f"Delivery to {customer.type}")

            # Render
            if hasattr(self, 'particles'):
                self.particles.update(dt)
            self._render(mouse_pos)
            pygame.display.flip()

    def draw_current_state(self, screen):
        """Draw the current game state - used by tutorial and other states."""
        game_logger.debug("Drawing current game state", "Game")
        try:
            # Clear the screen
            screen.fill((0, 0, 0))  # Black background
            
            # Draw map if available
            if self.game_map:
                self.game_map.draw(screen)
            else:
                game_logger.warning("No game map available for drawing", "Game")
                
            # Draw game objects
            if self.player:
                self.player.draw(screen)
            else:
                game_logger.warning("No player available for drawing", "Game")
                
            # Draw sprite groups only if they exist
            if hasattr(self, 'customers') and self.customers:
                self.customers.draw(screen)
            else:
                game_logger.warning("No customers available for drawing", "Game")
                
            if hasattr(self, 'foods') and self.foods:
                self.foods.draw(screen)
            else:
                game_logger.warning("No foods available for drawing", "Game")
                
            # Draw UI elements
            # Add basic UI rendering for score, money, etc.
            font = pygame.font.SysFont(None, 24)
            if hasattr(self, 'money'):
                money_text = font.render(f'${self.money}', True, (255, 255, 255))
                screen.blit(money_text, (10, 10))
        except Exception as e:
            game_logger.error(f"Error drawing game state: {e}", "Game", exc_info=True)
    
    def _render(self, mouse_pos):
        """Render the game screen."""
        # First draw the base game state
        self.draw_current_state(self.screen)
        
        # Then add gameplay UI elements
        font = pygame.font.SysFont(None, 24)
        money_text = font.render(f'${self.money}', True, (255, 255, 255))
        self.screen.blit(money_text, (10, 10))
        
        # Draw selected food indicator if applicable
        if self.selected_food:
            selected_text = font.render(f'Selected: {self.selected_food}', True, (255, 255, 255))
            self.screen.blit(selected_text, (10, 40))
        
        # Draw shop button indicator
        shop_text = font.render('Press B to open shop', True, (255, 255, 255))
        self.screen.blit(shop_text, (10, self.screen_height - 30))
    
    def reset_game(self):
        """Reset the game to initial state."""
        game_logger.info("Resetting entire game state", "Game")
        
        try:
            # Initialize or reset game objects
            # This is a simplified implementation
            from src.sprites.player import Player  # Import here to avoid circular imports
            from src.map.game_map import GameMap
            
            game_logger.debug("Initializing Player", "Game")
            self.player = Player(self.screen_width // 2, self.screen_height // 2)
            
            game_logger.debug("Initializing GameMap", "Game")
            self.game_map = GameMap()
            
            self.customers.empty()
            self.foods.empty()
            game_logger.debug("Cleared sprite groups", "Game")
        except Exception as e:
            game_logger.critical(f"Failed to reset game objects: {e}", "Game", exc_info=True)
            # Try to recover by setting to None
            self.player = None
            self.game_map = None
        
        # Reset economy
        self.money = 0
        self.successful_deliveries = 0
        self.selected_food = None
        
        # Initialize shop if not already done
        if not hasattr(self, 'shop'):
            from src.ui.shop import Shop  # Import here to avoid circular imports
            self.shop = Shop(self)
        
        # Initialize economy if not already done
        if not hasattr(self, 'economy'):
            from src.economy.economy import Economy  # Import here to avoid circular imports
            self.economy = Economy(self)
        
        # Initialize particles if not already done
        if not hasattr(self, 'particles'):
            from src.effects.particles import ParticleSystem  # Import here to avoid circular imports
            self.particles = ParticleSystem()
    
    def reset_state(self):
        """Reset the game state without recreating objects."""
        game_logger.info("Resetting game state (keeping objects)", "Game")
        
        try:
            self.money = 0
            self.successful_deliveries = 0
            self.selected_food = None
            self.customers.empty()
            self.foods.empty()
            
            # Reset player position if exists
            if self.player:
                game_logger.debug("Resetting player position", "Game")
                self.player.reset_position()
            else:
                game_logger.warning("Cannot reset player position: player is None", "Game")
                # Try to create player if missing
                self.reset_game()
                
            game_logger.info("Game state reset completed", "Game")
            # Set proper game state - this triggers state transition in the main loop
            self.game_state = PLAYING
            game_logger.info(f"Game state set to: {self.game_state}", "Game")
        except Exception as e:
            game_logger.error(f"Error resetting game state: {e}", "Game", exc_info=True)
    
    def spawn_customer(self):
        """Spawn a new customer at a valid spawn point."""
        from src.sprites.customer import Customer  # Import here to avoid circular imports
        import random
        
        # Get valid spawn points from the map or use predefined positions
        spawn_points = getattr(self.game_map, 'customer_spawn_points', [(100, 100), (200, 100), (300, 100)])
        
        if spawn_points:
            x, y = random.choice(spawn_points)
            customer = Customer(x, y)
            self.customers.add(customer)
            
    def setup_tutorial_objects(self):
        """Initialize objects needed for the tutorial."""
        game_logger.info("Setting up tutorial objects", "Game")
        
        try:
            # Import here to avoid circular imports
            from src.sprites.player import Player
            from src.map.game_map import GameMap
            from src.economy.economy import Economy
            
            # Initialize basic objects needed for tutorial
            game_logger.debug("Initializing Player for tutorial", "Game")
            self.player = Player(self.screen_width // 2, self.screen_height // 2)
            
            game_logger.debug("Initializing GameMap for tutorial", "Game")
            self.game_map = GameMap()
            
            game_logger.debug("Initializing Economy for tutorial", "Game")
            self.economy = Economy(self)
            
            # Preload some customers for tutorial
            self.spawn_customer()
            game_logger.info("Tutorial objects setup complete", "Game")
            
        except ImportError as e:
            game_logger.error(f"Failed to initialize tutorial objects: {e}", "Game", exc_info=True)
            # Provide fallback minimal initialization
            pass
        except Exception as e:
            game_logger.critical(f"Unexpected error in tutorial setup: {e}", "Game", exc_info=True)
