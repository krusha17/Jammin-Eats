"""Core game engine for Jammin' Eats.

Handles game initialization, main game loop, state management, and core gameplay functionality.
Serves as the central controller connecting all game components and systems.
Manages resource loading, persistence, and transitions between different game states.

This module has been refactored for improved maintainability by separating:
- Core game loop and state management (this file)
- Rendering logic (game_renderer.py)
- World object management (game_world.py)
"""


import pygame

# Fix imports to work with the way main.py sets up the Python path
try:
    # Try direct imports first (when src is in path)
    from core.constants import FPS, HEIGHT, MENU, PLAYING, WIDTH
    from core.game_renderer import GameRenderer
    from core.game_world import GameWorld
    from debug.logger import game_logger
    from persistence.dal import is_tutorial_complete
    from persistence.game_persistence import GamePersistence
    from states import TitleState
    from states.gameplay_state import GameplayState
    
    print("Direct imports succeeded")
    IMPORT_PREFIX = ""
    
except ImportError as e:
    # Fall back to src-prefixed imports
    print(f"Direct imports failed: {e}, trying with src prefix")
    from src.core.constants import FPS, HEIGHT, MENU, PLAYING, WIDTH
    from src.core.game_renderer import GameRenderer
    from src.core.game_world import GameWorld
    from src.debug.logger import game_logger
    from src.persistence.dal import is_tutorial_complete
    from src.persistence.game_persistence import GamePersistence
    from src.states import TitleState
    from src.states.gameplay_state import GameplayState
    
    IMPORT_PREFIX = "src."

class Game:
    """Main game class that controls the game loop and state management.
    
    This class is responsible for initializing the game, handling the main loop,
    managing game states, and coordinating between different components like
    the renderer, world manager, and persistence layer.
    """
    def __init__(self, screen_width=WIDTH, screen_height=HEIGHT):  # noqa: PLR0915
        """Initialize the game with the given screen dimensions.
        
        Args:
            screen_width: Width of the game window in pixels
            screen_height: Height of the game window in pixels
        """
        game_logger.info("Initializing Game class", "Game")
        
        # Initialize pygame
        try:
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Jammin' Eats")
            self.clock = pygame.time.Clock()
            game_logger.debug("Pygame display initialized successfully", "Game")
        except Exception as e:
            game_logger.critical(
                f"Failed to initialize pygame display: {e}", 
                "Game", 
                exc_info=True
            )
            raise  # Re-raise as this is critical
        
        # Game state
        self.game_state = MENU
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize renderer and world manager
        self.renderer = GameRenderer(self)
        self.world = GameWorld(self)
        
        # Initialize database and persistence
        try:
            # Initialize database first - use the right import path based on what worked
            db_init_module = f"{IMPORT_PREFIX}persistence.db_init"
            db_init = __import__(db_init_module, fromlist=["initialize_database", "check_database_integrity"])
            initialize_database = db_init.initialize_database
            check_database_integrity = db_init.check_database_integrity
                
            game_logger.info("Initializing game database", "Game")
            
            # Run database initialization
            db_init_success = initialize_database()
            if db_init_success:
                game_logger.info("Database initialized successfully", "Game")
                # Check database integrity
                integrity_result, missing_tables = check_database_integrity()
                if not integrity_result:
                    game_logger.warning(
                        f"Database integrity issues detected: {missing_tables}",
                        "Game"
                    )
            else:
                game_logger.error("Failed to initialize database", "Game")
            
            # Now initialize persistence
            self.persistence = GamePersistence()
            game_logger.debug("Game persistence initialized", "Game")
        except ImportError as ie:
            game_logger.error(f"Failed to import database modules: {ie}", "Game", exc_info=True)
            self.persistence = None  # Set to None as fallback
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

    def run(self):  # noqa: PLR0912, PLR0915
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
            
        # Track current state type for debugging state transitions
        last_state_type = type(current_state).__name__
        
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
                game_logger.debug(
                    f"State update: {current_state_type} at {current_time}",
                    "Game"
                )
                last_state_type = current_state_type
            
            # Check if we need to transition to gameplay based on game_state flag
            if self.game_state == PLAYING and not isinstance(current_state, GameplayState):
                game_logger.info(
                    f"Explicit transition to gameplay triggered by game_state={self.game_state}",
                    "Game"
                )
                try:
                    # First exit current state properly
                    game_logger.debug(f"Exiting current state: {type(current_state).__name__}", "Game")
                    current_state.exit()
                    
                    # Determine which gameplay state to use
                    use_simplified = getattr(self, 'use_simplified_gameplay', False)
                    
                    # Create and enter appropriate gameplay state
                    if use_simplified:
                        # Use the simplified black screen gameplay state
                        try:
                            # Dynamic import based on prefix
                            black_screen_module = f"{IMPORT_PREFIX}states.black_screen_gameplay_state"
                            black_screen_module = __import__(black_screen_module, fromlist=["BlackScreenGameplayState"])
                            game_logger.debug("Creating new BlackScreenGameplayState instance", "Game")
                            current_state = black_screen_module.BlackScreenGameplayState(self)
                            game_logger.info("Successfully created BlackScreenGameplayState", "Game")
                        except Exception as e:
                            game_logger.error(
                                f"Failed to create BlackScreenGameplayState: {e}",
                                "Game", 
                                exc_info=True
                            )
                            # Fall back to regular GameplayState
                            game_logger.warning("Falling back to regular GameplayState", "Game")
                            current_state = GameplayState(self)
                    else:
                        # Use the regular gameplay state
                        game_logger.debug("Creating new GameplayState instance", "Game")
                        current_state = GameplayState(self)
                    
                    # Enter the chosen state
                    game_logger.debug(f"Entering {type(current_state).__name__}", "Game")
                    current_state.enter()
                    game_logger.info(f"Successfully transitioned to {type(current_state).__name__}", "Game")
                    
                    # Update tracking
                    last_state_type = type(current_state).__name__
                except Exception as e:
                    game_logger.critical(
                        f"Failed to transition to GameplayState: {e}",
                        "Game", 
                        exc_info=True
                    )
                    # Try to recover by returning to title
                    try:
                        current_state = TitleState(self)
                        current_state.enter()
                        self.game_state = MENU
                    except Exception as recover_error:
                        game_logger.critical(f"Could not recover from transition error: {recover_error}", "Game", exc_info=True)
                    continue
                    
            # Check for next_state transition
            if hasattr(current_state, 'next_state') and current_state.next_state is not None:
                game_logger.info(
                    f"State transition detected: {type(current_state).__name__} -> "
                    f"{type(current_state.next_state).__name__}",
                    "Game"
                )
                
                try:
                    # Exit current state properly
                    if hasattr(current_state, 'exit'):
                        current_state.exit()
                    
                    # Switch to next state
                    next_state = current_state.next_state
                    current_state = next_state
                    current_state.next_state = None  # Clear next_state to prevent loops
                    
                    # Enter new state
                    if hasattr(current_state, 'enter'):
                        current_state.enter()
                    
                    # Update tracking
                    last_state_type = type(current_state).__name__
                    
                    game_logger.info(f"Successfully transitioned to {type(current_state).__name__}", "Game")
                except Exception as e:
                    game_logger.critical(
                        f"Error during state transition: {e}",
                        "Game", 
                        exc_info=True
                    )
                    # Try to recover
                    try:
                        current_state = TitleState(self)
                        current_state.enter()
                        self.game_state = MENU
                    except Exception as recover_error:
                        game_logger.critical(f"Could not recover from transition error: {recover_error}", "Game", exc_info=True)
            
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
        The main game loop now uses the state machine pattern.
        """
        game_logger.warning("run_gameplay() called directly - this method is deprecated", "Game")
        
        # Transition to gameplay state if called directly
        try:
            from states.gameplay_state import GameplayState
        except ImportError:
            from src.states.gameplay_state import GameplayState
            
        self.current_state = GameplayState(self)
        game_logger.info("Transition to GameplayState", "Game")



    def draw_current_state(self, screen):
        """Draw the current game state - used by tutorial and other states.
        
        Args:
            screen: The surface to draw on
        """
        try:
            # Delegate to the renderer for base rendering
            self.renderer.draw_current_state(screen)
            
            # Draw particle effects
            if hasattr(self, 'particles') and self.particles is not None:
                self.particles.draw(screen)
                game_logger.debug("Drew particle effects", "Game")
                
            # Draw HUD if available
            if hasattr(self, 'hud') and self.hud is not None:
                game_logger.debug("Drawing HUD", "Game")
                self.hud.draw(screen)
                game_logger.debug("Drew HUD successfully", "Game")
            else:
                game_logger.warning("No HUD available to draw", "Game")
                
            # Shop is drawn last (on top) if visible
            if hasattr(self, 'shop') and self.shop is not None and hasattr(self.shop, 'visible') and self.shop.visible:
                self.shop.draw(screen)
                game_logger.debug("Drew shop UI", "Game")
                
            game_logger.debug("Completed draw_current_state method successfully", "Game")
                
        except Exception as e:
            game_logger.error(f"Error in draw_current_state: {e}", "Game", exc_info=True)
            # Draw an emergency message
            try:
                font = pygame.font.SysFont(None, 24)
                error_text = font.render(f"Drawing error: {str(e)}", True, (255, 0, 0))
                screen.blit(error_text, (10, 10))
                game_logger.debug("Drew error message on screen", "Game")
            except Exception as font_error:
                game_logger.error(f"Could not draw error message: {font_error}", "Game")

def render(self):
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
        game_logger.info("Delegating reset_game to GameWorld", "Game")
        # Delegate to the world manager
        self.world.reset_game()
    
    def reset_state(self):
        """Reset the game state without recreating objects."""
        game_logger.info("Delegating reset_state to GameWorld", "Game")
        # Delegate to the world manager
        self.world.reset_state()
        
        # Set proper game state - this triggers state transition in the main loop
        self.game_state = PLAYING
        game_logger.info(f"Game state set to: {self.game_state}", "Game")
    
    def spawn_customer(self):
        """Spawn a new customer at a valid spawn point."""
        game_logger.info("Delegating spawn_customer to GameWorld", "Game")
        # Delegate to the world manager
        self.world.spawn_customer()
            
    def setup_tutorial_objects(self):
        """Initialize objects needed for the tutorial."""
        game_logger.info("Delegating setup_tutorial_objects to GameWorld", "Game")
        # Delegate to the world manager
        self.world.setup_tutorial_objects()
