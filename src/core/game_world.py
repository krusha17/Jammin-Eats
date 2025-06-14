"""Game world management component for Jammin' Eats.

This module handles the game world objects, entity spawning, and world state management.
It is responsible for maintaining the game's entities like customers, foods, and environment.

Classes:
    GameWorld: Manages game world objects and entity spawning.
"""

import pygame
import random

# Import from either direct or src-prefixed paths
try:
    # Try direct imports first
    from debug.logger import game_logger
except ImportError:
    # Fall back to src-prefixed imports
    from src.debug.logger import game_logger


class GameWorld:
    """Handles game world objects and entity management."""

    def __init__(self, game):
        """Initialize the world manager with a reference to the main game object.

        Args:
            game: Reference to the main Game instance
        """
        self.game = game
        self._import_prefix = ""

        # Determine import prefix by trying imports
        try:
            from sprites.customer import Customer  # noqa: F401

            self._import_prefix = ""
        except ImportError:
            try:
                from src.sprites.customer import Customer  # noqa: F401

                self._import_prefix = "src."
            except ImportError:
                game_logger.error(
                    "Could not import Customer class with any prefix", "GameWorld"
                )

    def spawn_customer(self):
        """Spawn a new customer at a valid spawn point."""
        try:
            # Import using the correct prefix
            if self._import_prefix == "":
                from sprites.customer import Customer  # noqa: F401
            else:
                from src.sprites.customer import Customer  # noqa: F401

            # Get valid spawn points from the map or use predefined positions
            spawn_points = getattr(
                self.game.game_map,
                "customer_spawn_points",
                [(100, 100), (200, 100), (300, 100)],
            )

            if spawn_points:
                x, y = random.choice(spawn_points)
                customer = Customer(x, y)
                self.game.customers.add(customer)
                game_logger.debug(f"Customer spawned at {x},{y}", "GameWorld")
            else:
                game_logger.warning(
                    "No valid spawn points found for customer", "GameWorld"
                )
        except ImportError as e:
            game_logger.error(f"Failed to import Customer class: {e}", "GameWorld")
        except Exception as e:
            game_logger.error(
                f"Error spawning customer: {e}", "GameWorld", exc_info=True
            )

    def setup_tutorial_objects(self):
        """Initialize objects needed for the tutorial."""
        game_logger.info("Setting up tutorial objects", "GameWorld")

        try:
            # Import using the correct prefix to avoid import errors
            if self._import_prefix == "":
                from sprites.player import Player
                from map.game_map import GameMap
                from economy.economy import Economy
                from ui.hud import HUD
            else:
                from src.sprites.player import Player
                from src.map.game_map import GameMap
                from src.economy.economy import Economy
                from src.ui.hud import HUD

            # Initialize basic objects needed for tutorial
            game_logger.debug("Initializing Player for tutorial", "GameWorld")
            self.game.player = Player(
                self.game.screen_width // 2, self.game.screen_height // 2
            )

            game_logger.debug("Initializing GameMap for tutorial", "GameWorld")
            self.game.game_map = GameMap()

            game_logger.debug("Initializing Economy for tutorial", "GameWorld")
            self.game.economy = Economy(self.game)

            # Initialize HUD for tutorial if needed
            if not hasattr(self.game, "hud"):
                game_logger.debug("Initializing HUD for tutorial", "GameWorld")
                self.game.hud = HUD(self.game.screen_width, self.game.screen_height)

            # Preload some customers for tutorial
            self.spawn_customer()
            game_logger.info("Tutorial objects setup complete", "GameWorld")

        except ImportError as e:
            game_logger.error(
                f"Failed to initialize tutorial objects: {e}",
                "GameWorld",
                exc_info=True,
            )
            # Provide fallback minimal initialization
            if not hasattr(self.game, "player") or self.game.player is None:
                # Create a minimal player if import fails
                from pygame.sprite import Sprite

                minimal_player = type(
                    "MinimalPlayer",
                    (Sprite,),
                    {
                        "rect": pygame.Rect(
                            self.game.screen_width // 2,
                            self.game.screen_height // 2,
                            32,
                            32,
                        ),
                        "reset_position": lambda: None,
                        "draw": lambda surf: pygame.draw.rect(
                            surf,
                            (255, 0, 0),
                            pygame.Rect(
                                self.game.screen_width // 2,
                                self.game.screen_height // 2,
                                32,
                                32,
                            ),
                        ),
                    },
                )()
                self.game.player = minimal_player
                game_logger.warning(
                    "Created minimal player fallback for tutorial", "GameWorld"
                )
        except Exception as e:
            game_logger.critical(
                f"Unexpected error in tutorial setup: {e}", "GameWorld", exc_info=True
            )

    def reset_game(self):
        """Reset the game to initial state."""
        game_logger.info("Resetting game", "GameWorld")

        try:
            # Import using the correct prefix
            if self._import_prefix == "":
                from sprites.player import Player
                import pygame.sprite
            else:
                from src.sprites.player import Player
                import pygame.sprite

            # Create sprite groups if they don't exist
            if not hasattr(self.game, "all_sprites"):
                self.game.all_sprites = pygame.sprite.Group()
            else:
                self.game.all_sprites.empty()

            if not hasattr(self.game, "customers"):
                self.game.customers = pygame.sprite.Group()
            else:
                self.game.customers.empty()

            if not hasattr(self.game, "foods"):
                self.game.foods = pygame.sprite.Group()
            else:
                self.game.foods.empty()

            # Create player if it doesn't exist
            if not hasattr(self.game, "player") or self.game.player is None:
                self.game.player = Player(
                    self.game.screen_width // 2, self.game.screen_height // 2
                )
            else:
                # Reset player position
                self.game.player.reset_position()

            # Reset other attributes
            self.setup_tutorial_objects()

            game_logger.info("Game reset completed", "GameWorld")
        except Exception as e:
            game_logger.error(f"Error resetting game: {e}", "GameWorld", exc_info=True)

    def reset_state(self):
        """Reset the game state without recreating objects."""
        game_logger.info("Resetting game state", "GameWorld")

        try:
            # Empty sprite groups if they exist
            if hasattr(self.game, "customers"):
                self.game.customers.empty()
                game_logger.debug("Cleared customer sprites", "GameWorld")

            if hasattr(self.game, "foods"):
                self.game.foods.empty()
                game_logger.debug("Cleared food sprites", "GameWorld")

            # Reset player position if player exists
            if hasattr(self.game, "player") and self.game.player:
                self.game.player.reset_position()
                game_logger.debug("Reset player position", "GameWorld")

            game_logger.info("Game state reset completed", "GameWorld")
        except Exception as e:
            game_logger.error(
                f"Error resetting game state: {e}", "GameWorld", exc_info=True
            )
