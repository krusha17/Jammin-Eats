import pygame
import math
from src.core.constants import WIDTH, HEIGHT, WHITE
from src.sprites.food import Food
from src.utils.asset_loader import load_image


# Create a minimal player for fallback cases where normal loading fails
def create_fallback_player(x, y):
    """Create a simplified player object that doesn't require external assets"""
    # Create a new player instance
    player = Player(x, y)

    # Override with very basic animation frames that require no assets
    for direction in ["up", "down", "left", "right", "idle"]:
        fallback = pygame.Surface((32, 32), pygame.SRCALPHA)

        # Draw the player avatar (a circle with a direction indicator)
        pygame.draw.circle(fallback, (0, 0, 255), (16, 16), 15)  # Blue circle

        # Draw direction indicator (white triangle)
        if direction == "up":
            pygame.draw.polygon(
                fallback, (255, 255, 255), [(16, 5), (20, 15), (12, 15)]
            )
        elif direction == "down":
            pygame.draw.polygon(
                fallback, (255, 255, 255), [(16, 27), (20, 17), (12, 17)]
            )
        elif direction == "left":
            pygame.draw.polygon(
                fallback, (255, 255, 255), [(5, 16), (15, 20), (15, 12)]
            )
        elif direction == "right":
            pygame.draw.polygon(
                fallback, (255, 255, 255), [(27, 16), (17, 20), (17, 12)]
            )

        # Set the fallback animation
        player.animations[direction] = [fallback]

    # Ensure we have a valid current frame
    player.image = player.animations["down"][0]
    player.direction = "down"
    player.frame_index = 0

    return player


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Initialize animation dictionaries with default empty lists
        self.animations = {"up": [], "down": [], "left": [], "right": [], "idle": []}

        # Debug print
        print("Initializing Player at position:", x, y)

        # Create simplified player sprites directly as fallbacks
        # This ensures we always have valid sprites even if loading fails

        # Import the constants here to avoid circular imports
        from src.core.constants import BLUE, WHITE

        # Create fallback sprites first to ensure we always have something
        for direction in ["up", "down", "left", "right", "idle"]:
            fallback = pygame.Surface((32, 32), pygame.SRCALPHA)

            # Draw the player avatar (a circle with a direction indicator)
            pygame.draw.circle(fallback, BLUE, (16, 16), 15)

            # Add direction indicator
            if direction == "up":
                pygame.draw.polygon(fallback, WHITE, [(16, 5), (20, 15), (12, 15)])
            elif direction == "down":
                pygame.draw.polygon(fallback, WHITE, [(16, 27), (20, 17), (12, 17)])
            elif direction == "left":
                pygame.draw.polygon(fallback, WHITE, [(5, 16), (15, 20), (15, 12)])
            elif direction == "right":
                pygame.draw.polygon(fallback, WHITE, [(27, 16), (17, 20), (17, 12)])

            # Add at least one fallback sprite to each direction list
            self.animations[direction] = [fallback]

        # Now try to load the actual sprites
        try:
            # Try to load the actual sprite files
            # Updated to match the actual file paths shown in the error logs
            img_down = load_image("sprites/characters/kai", "kai_down.png")
            if img_down:
                self.animations["down"] = [img_down] * 4

            img_up = load_image("sprites/characters/kai", "kai_up.png")
            if img_up:
                self.animations["up"] = [img_up] * 4

            img_left = load_image("sprites/characters/kai", "kai_left.png")
            if img_left:
                self.animations["left"] = [img_left] * 4

            img_right = load_image("sprites/characters/kai", "kai_right.png")
            if img_right:
                self.animations["right"] = [img_right] * 4

            # Always use first frame of down as idle
            self.animations["idle"] = [self.animations["down"][0]]

            print("Successfully loaded player sprites from assets")
        except Exception as e:
            print(f"Using fallback player sprites due to error: {str(e)}")

        # Initialize animation variables
        self.direction = "down"  # Starting direction
        self.frame_index = 0  # Current animation frame
        self.animation_timer = 0
        self.animation_speed = 0.2  # Seconds per frame

        # Set up player rectangle and initial image
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

        # Player stats
        self.speed = 200  # pixels per second
        self.deliveries = 0
        self.missed_deliveries = 0
        self.food_inventory = 99  # Unlimited for now

        # Food throwing cooldown
        self.throw_cooldown = 0.2  # seconds
        self.last_throw_time = 0

    def update(self, dt, customers=None, foods=None, game_map=None):
        # Add safety checks for None arguments
        if customers is None:
            customers = pygame.sprite.Group()
        if foods is None:
            foods = pygame.sprite.Group()

        try:
            # Handle player movement
            self.handle_movement(dt, game_map)

            # Update animation
            self.update_animation(dt)

            # Check for spacebar to throw food (like in the original main.py)
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds

            # Check throw cooldown
            if current_time - self.last_throw_time >= self.throw_cooldown:
                # Use spacebar to throw food in the current facing direction
                if keys[pygame.K_SPACE]:
                    # Throw in the direction the player is facing
                    # Ensure we have a reference to the game object
                    game_obj = getattr(self, "game", None)
                    if game_obj is None:
                        print(
                            "[WARNING] Player has no reference to game object! Food selection and inventory won't work."
                        )
                    result = self.throw_food(foods, self.direction, game_obj)
                    if result:
                        print("[DEBUG] Food was thrown successfully")
                    else:
                        print(
                            "[DEBUG] Food throw failed - possibly out of stock or inventory issues"
                        )
        except Exception as e:
            print(
                f"[ERROR] Player.update error: {str(e)}"
            )  # Log errors instead of crashing

    def handle_movement(self, dt, game_map=None):
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0

        # Calculate movement direction
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -1
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = 1
            self.direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y = -1
            self.direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y = 1
            self.direction = "down"

        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            # Pythagorean theorem to normalize movement speed on diagonals
            move_x /= math.sqrt(2)
            move_y /= math.sqrt(2)

        # Apply movement speed
        dx = move_x * self.speed * dt
        dy = move_y * self.speed * dt

        # Boundary checking
        new_x = self.rect.centerx + dx
        new_y = self.rect.centery + dy

        # Check map boundaries and collisions
        if 0 <= new_x <= WIDTH and 0 <= new_y <= HEIGHT:
            # Check walkability if map exists
            if game_map:
                # Try moving on X axis
                if game_map.is_walkable(new_x, self.rect.centery):
                    self.rect.centerx = new_x

                # Try moving on Y axis
                if game_map.is_walkable(self.rect.centerx, new_y):
                    self.rect.centery = new_y
            else:
                # No map, just move within screen bounds
                self.rect.centerx = new_x
                self.rect.centery = new_y

    def update_animation(self, dt):
        # If not moving, use idle animation
        keys = pygame.key.get_pressed()
        is_moving = (
            keys[pygame.K_LEFT]
            or keys[pygame.K_RIGHT]
            or keys[pygame.K_UP]
            or keys[pygame.K_DOWN]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
            or keys[pygame.K_w]
            or keys[pygame.K_s]
        )

        if not is_moving:
            current_direction = "idle"
        else:
            current_direction = self.direction

        # Safety check - make sure the animation list exists and is not empty
        if not self.animations[current_direction]:
            # If no animations for current direction, default to 'down' or first available
            for key in ["down", "up", "left", "right", "idle"]:
                if self.animations[key]:
                    current_direction = key
                    break

        # Another safety check - if still no animations available, don't proceed
        if not self.animations[current_direction]:
            return

        # Update animation frame
        if is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                # Ensure frame_index stays within bounds
                self.frame_index = (self.frame_index + 1) % len(
                    self.animations[current_direction]
                )

        # Ensure frame_index is in bounds before accessing
        if self.frame_index >= len(self.animations[current_direction]):
            self.frame_index = 0

        # Update image
        self.image = self.animations[current_direction][self.frame_index]

    def throw_food(self, foods, direction=None, game=None):
        # If no direction specified, use player's current direction
        if direction is None:
            direction = self.direction

        # Set velocity based on direction
        if direction == "up":
            dx, dy = 0, -7
        elif direction == "down":
            dx, dy = 0, 7
        elif direction == "left":
            dx, dy = -7, 0
        elif direction == "right":
            dx, dy = 7, 0
        else:
            return  # Invalid direction

        # Get selected food from inventory if available
        food_type = "pizza"  # Default fallback

        # Try to get game reference from self if not provided
        if game is None and hasattr(self, "game"):
            game = self.game

        if (
            game
            and hasattr(game, "inventory")
            and game.inventory is not None
            and hasattr(game, "selected_food")
        ):
            selected_food = game.selected_food

            # Get equivalent short name for the food type
            food_name_mapping = {
                "Tropical Pizza Slice": "pizza",
                "Ska Smoothie": "smoothie",
                "Island Ice Cream": "icecream",
                "Rasta Rice Pudding": "pudding",
            }

            # Check if the selected food is in stock
            if game.inventory.in_stock(selected_food):
                # Consume one unit from inventory
                consumed = game.inventory.consume(selected_food)
                if consumed:
                    food_type = food_name_mapping.get(selected_food, "pizza")

                    # Create the food object
                    food = Food(self.rect.centerx, self.rect.centery, dx, dy, food_type)
                    foods.add(food)

                    # Update throw cooldown
                    self.last_throw_time = pygame.time.get_ticks() / 1000.0

                    # Log the transaction in database if available
                    if (
                        hasattr(game, "game_database")
                        and game.game_database is not None
                    ):
                        # Use the appropriate price if available in constants
                        from src.core.constants import FOOD_PRICES

                        if selected_food in FOOD_PRICES:
                            estimated_price = FOOD_PRICES[selected_food]["buy_price"]
                            game.log_purchase_transaction(
                                selected_food, estimated_price
                            )

                    return True
            else:
                # Play error sound if no stock available
                if "error_sound" in game.sounds and game.sounds["error_sound"]:
                    game.sounds["error_sound"].play()

                # Debug feedback
                if hasattr(game, "debug_mode") and game.debug_mode:
                    print(f"[INVENTORY] Out of stock: {selected_food}")
        else:
            # Only use fallback if truly necessary - the inventory system is not available
            if not game or not hasattr(game, "inventory") or game.inventory is None:
                # Legacy fallback behavior if inventory system isn't active
                food_choices = ["pizza", "smoothie", "icecream", "pudding"]
                food_type = food_choices[pygame.time.get_ticks() % len(food_choices)]

                food = Food(self.rect.centerx, self.rect.centery, dx, dy, food_type)
                foods.add(food)

                # Update throw cooldown
                self.last_throw_time = pygame.time.get_ticks() / 1000.0
                return True
            else:
                # Inventory system exists but we don't have selected food or it's out of stock
                return False

        return False

    def draw_stats(self, surface):
        # Draw player stats (deliveries, missed)
        font = pygame.font.Font(None, 24)
        deliveries_text = font.render(f"Deliveries: {self.deliveries}", True, WHITE)
        surface.blit(deliveries_text, (10, 10))

        missed_text = font.render(f"Missed: {self.missed_deliveries}/10", True, WHITE)
        surface.blit(missed_text, (10, 40))

        # Draw a simple health/warning bar based on missed deliveries
        warning_width = 150 * (self.missed_deliveries / 10.0)
        pygame.draw.rect(surface, (100, 100, 100), (10, 70, 150, 15))
        pygame.draw.rect(surface, (255, 50, 50), (10, 70, warning_width, 15))

    def draw(self, surface, offset_x=0, offset_y=0):
        # Calculate the adjusted position with offset
        draw_x = self.rect.x + offset_x
        draw_y = self.rect.y + offset_y

        # Draw at the adjusted position
        surface.blit(self.image, (draw_x, draw_y))

    def reset_position(self):
        """Reset the player to the center of the screen or a safe spawn position."""
        from src.core.constants import WIDTH, HEIGHT

        # Store initial spawn position (center of screen by default)
        self.initial_x = getattr(self, "initial_x", WIDTH // 2)
        self.initial_y = getattr(self, "initial_y", HEIGHT // 2)

        # Reset to initial position
        self.rect.x = self.initial_x - self.rect.width // 2
        self.rect.y = self.initial_y - self.rect.height // 2

        # Reset movement state
        self.direction = "down"
        self.frame_index = 0
        self.current_speed = getattr(self, "base_speed", 3)

        # Update the current image
        if self.animations["down"] and len(self.animations["down"]) > 0:
            self.image = self.animations["down"][0]

        # Reset any movement flags or momentum
        if hasattr(self, "moving"):
            self.moving = False
