import pygame
import sys
import random
import time
import math
import os
import pytmx
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Third-party imports
try:
    import pytmx
    from pytmx.util_pygame import load_pygame
    print("pytmx successfully imported")
except ImportError:
    print("pytmx not found! Please install it with: pip install pytmx")
    sys.exit(1)

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAP_DIR = os.path.join(ASSETS_DIR, "Maps", "level1")

# Set up the game window
WIDTH, HEIGHT = 768, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jammin' Eats")
clock = pygame.time.Clock()
FPS = 60

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Score system
score = 0
high_score = 0
font = pygame.font.Font(None, 36)

# Load sounds with error handling
try:
    pickup_sound = mixer.Sound(os.path.join(ASSETS_DIR, 'sounds', 'characters', 'food_throw.wav'))
    engine_sound = mixer.Sound(os.path.join(ASSETS_DIR, 'sounds', 'vehicles', 'engine_idle.wav'))
    button_sound = mixer.Sound(os.path.join(ASSETS_DIR, 'sounds', 'ui', 'button_click.wav'))
    # Try to create background music - fallback to looping a sound if needed
    try:
        mixer.music.load(os.path.join(ASSETS_DIR, 'sounds', 'characters', 'food_throw.wav'))  # Placeholder for background music
        mixer.music.set_volume(0.5)
        mixer.music.play(-1)  # Loop indefinitely
    except:
        print("No background music found, continuing without it")
except:
    print("Error loading sounds, continuing without audio")

# Create menu background programmatically
menu_background = pygame.Surface((WIDTH, HEIGHT))
# Create a gradient background
for y in range(HEIGHT):
    color_value = int(255 * (1 - y / HEIGHT))
    color = (0, color_value // 2, color_value)
    pygame.draw.line(menu_background, color, (0, y), (WIDTH, y))

# Add some decorative elements
for _ in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    pygame.draw.circle(menu_background, (255, 255, 255), (x, y), size)

# Create game over background
game_over_background = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    color_value = int(200 * (1 - y / HEIGHT))
    color = (color_value + 55, 0, 0)
    pygame.draw.line(game_over_background, color, (0, y), (WIDTH, y))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Resource loader to handle tileset images
class ResourceLoader:
    def __init__(self, base_path):
        self.base_path = base_path

    def load(self, filename, **_):
        # Handle the specific path pattern we're seeing in the error
        if '../../tilesets' in filename:
            # Extract just the filename part
            tileset_name = os.path.basename(filename)
            # Try to find it in various locations
            candidates = [
                os.path.join(ASSETS_DIR, "tilesets", tileset_name),
                os.path.join(ASSETS_DIR, "tiles", tileset_name),
                os.path.join(BASE_DIR, "TileSet_1.png"),  # Check root directory
                filename  # Try the original path as a fallback
            ]
        else:
            # For other resources, use the original search paths
            candidates = [
                os.path.join(self.base_path, filename),
                os.path.join(ASSETS_DIR, "tiles", filename),
                filename
            ]
            
        # Try each path
        for path in candidates:
            if os.path.exists(path):
                print(f"Found resource at: {path}")
                return pygame.image.load(path).convert_alpha()
                
        print(f"WARNING: missing resource {filename}")
        print(f"Tried looking in: {candidates}")
        
        # Create a placeholder texture with the filename text
        # This is better than just a magenta square
        size = (64, 64)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 180))  # Semi-transparent magenta
        
        # Add a border
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, size[0], size[1]), 2)
        
        # Add text showing what's missing
        try:
            font = pygame.font.Font(None, 14)
            short_name = os.path.basename(filename)[:10]
            text = font.render(short_name, True, (255, 255, 255))
            surf.blit(text, (size[0]//2 - text.get_width()//2, size[1]//2 - text.get_height()//2))
        except:
            pass  # If text rendering fails, just use the colored square
        return surf


# TiledMap class for handling the TMX map
class TiledMap:
    def __init__(self, tmx_path):
        loader = ResourceLoader(os.path.dirname(tmx_path))
        self.tmx_data = load_pygame(tmx_path, image_loader=loader.load)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Collision and interactable objects
        self.collision_rects = []
        self.interactable_objects = []
        
        # Render the layers
        self._render_layers()
        
        # Extract collision and interactable objects
        self._extract_objects()
        
        print(f"Map dimensions: {self.width}x{self.height}")
        print(f"Extracted {len(self.collision_rects)} collision rects")
        print(f"Extracted {len(self.interactable_objects)} interactable objects")
    
        # Create a walkability cache grid
        self.walkable_cache = {}
        self.cache_walkable_areas()

    def cache_walkable_areas(self):
        """Pre-compute walkable areas for better performance"""
        print("Caching walkable areas...")
        grid_size = 32  # Cache in 32x32 pixel blocks
    
        for x in range(0, self.width, grid_size):
            for y in range(0, self.height, grid_size):
                # Cache the center point of each grid cell
                center_x = x + grid_size // 2
                center_y = y + grid_size // 2
            
                # Skip if out of bounds
                if center_x >= self.width or center_y >= self.height:
                    continue
                
                # Compute walkability without using the cache
                self.walkable_cache[(center_x, center_y)] = self._compute_walkable(center_x, center_y)
    
        print(f"Walkable cache created with {len(self.walkable_cache)} entries")

    def _compute_walkable(self, x, y):
        """Raw walkability check without using cache"""
        # This contains the original walkability logic
        check_rect = pygame.Rect(x - 8, y - 8, 16, 16)
    
        # Check if the position is within map bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
    
        # Check for collision with any collision rect
        for rect in self.collision_rects:
            if check_rect.colliderect(rect):
                return False
    
        # Check tile-based walkability
        tile_x = int(x // self.tmx_data.tilewidth)
        tile_y = int(y // self.tmx_data.tileheight)
    
        # Check ocean and water tiles
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'name') and layer.name.lower() in ["ocean", "water"]:
                if isinstance(layer, pytmx.TiledTileLayer):
                    if layer.data[tile_y][tile_x]:
                        return False
    
        return True

    def is_walkable(self, x, y):
        """Check if a position is walkable, using cache when possible"""
        # Convert to grid coordinates
        grid_size = 32
        grid_x = (x // grid_size) * grid_size + grid_size // 2
        grid_y = (y // grid_size) * grid_size + grid_size // 2
    
        # Check cache first
        if (grid_x, grid_y) in self.walkable_cache:
            return self.walkable_cache[(grid_x, grid_y)]
    
        # Fall back to computing directly
        return self._compute_walkable(x, y)

    def _render_layers(self):
        from pytmx import TiledTileLayer
        # Define the correct layer draw order
        layer_order = ["sky", "clouds", "ocean", "grass", "sand", "sidewalk", "road", "interactables"]
        
        # Print available layers for debugging
        available_layers = []
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'name'):
                available_layers.append(layer.name.lower())
        print(f"Available layers: {available_layers}")
        
        # Render each layer in the specified order
        for layer_name in layer_order:
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, 'name') and layer.name.lower() == layer_name:
                    if isinstance(layer, TiledTileLayer):
                        print(f"Rendering layer: {layer.name}")
                        for x, y, gid in layer:
                            if gid:
                                tile = self.tmx_data.get_tile_image_by_gid(gid)
                                if tile:
                                    px = x * self.tmx_data.tilewidth
                                    py = y * self.tmx_data.tileheight
                                    self.surface.blit(tile, (px, py))
                    break
    
    def _extract_objects(self):
        """Extracts collision and interactable objects from the TMX file"""
        # Clear existing objects
        self.collision_rects = []
        self.interactable_objects = []
        
        # Check for object layers
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                print(f"Found object layer: {layer.name}")
                for obj in layer:
                    if obj.type == "collision" or layer.name.lower() == "collision":
                        self.collision_rects.append(pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        ))
                    elif obj.type == "interactable" or layer.name.lower() == "interactables":
                        self.interactable_objects.append({
                            'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                            'properties': obj.properties if hasattr(obj, 'properties') else {}
                        })
        
        # For now, also handle tile-based collision
        self._extract_tile_collisions()
    
    def _extract_tile_collisions(self):
        """Extracts collision information from specific tile layers"""
        # Use Ocean and Interactables layers for collisions
        collision_layers = ["ocean", "interactables"]
        
        for layer_name in collision_layers:
            for layer in self.tmx_data.layers:
                if hasattr(layer, 'name') and layer.name.lower() == layer_name:
                    if isinstance(layer, pytmx.TiledTileLayer):
                        print(f"Processing collision tiles from layer: {layer.name}")
                        for x, y, gid in layer:
                            if gid != 0:  # Non-empty tile
                                rect = pygame.Rect(
                                    x * self.tmx_data.tilewidth,
                                    y * self.tmx_data.tileheight,
                                    self.tmx_data.tilewidth,
                                    self.tmx_data.tileheight
                                )
                                self.collision_rects.append(rect)
    
def is_walkable(self, x, y):
    """
    Checks if the specified position is walkable using collision detection.
    Returns False if the position is:
    - Out of map bounds
    - Colliding with any collision rectangle
    - On an unwalkable tile type (ocean, etc.)
    """
    # Create a small rect at the position (smaller than player for better precision)
    check_rect = pygame.Rect(x - 8, y - 8, 16, 16)
    
    # Check if the position is within map bounds
    if x < 0 or x >= self.width or y < 0 or y >= self.height:
        return False
    
    # Check for collision with any collision rect
    for rect in self.collision_rects:
        if check_rect.colliderect(rect):
            return False
    
    # Check tile-based walkability for specific layers
    # Convert to tile coordinates
    tile_x = int(x // self.tmx_data.tilewidth)
    tile_y = int(y // self.tmx_data.tileheight)
    
    # Check ocean and water tiles
    for layer in self.tmx_data.visible_layers:
        if hasattr(layer, 'name') and layer.name.lower() in ["ocean", "water"]:
            if isinstance(layer, pytmx.TiledTileLayer):
                # If there's a tile here in the ocean/water layer, it's not walkable
                if layer.data[tile_y][tile_x]:
                    return False
    
    return True
    
def get_spawn_positions(self, object_name="CustomerSpawn"):
    """Gets spawn positions for customers based on an object name"""
    spawn_points = []
    
    # Try to find spawn points from the map objects
    for layer in self.tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            # First look for specifically named CustomerSpawns layer
            if hasattr(layer, 'name') and layer.name == "CustomerSpawns":
                print(f"Found dedicated CustomerSpawns layer with {len(layer)} objects")
                for obj in layer:
                    # Add all points from this layer regardless of name/type
                    spawn_points.append((obj.x, obj.y))
            # Then look for any object with matching name or type
            else:
                for obj in layer:
                    if obj.name == object_name or obj.type == "spawn":
                        spawn_points.append((obj.x, obj.y))
    
    # Filter to ensure all spawn points are walkable
    valid_spawn_points = []
    for x, y in spawn_points:
        if self.is_walkable(x + 16, y + 16):  # Check the center position
            valid_spawn_points.append((x, y))
        else:
            print(f"Warning: Spawn point at ({x}, {y}) is not walkable")
    
    # If no valid spawn points found, generate some along the edges - but check walkability
    if not valid_spawn_points:
        print(f"No walkable {object_name} objects found in map, generating default spawn points")
        edge_margin = 100
        step = 50
        
        # Generate and check points along all four edges
        for x in range(edge_margin, self.width - edge_margin, step):
            if self.is_walkable(x, edge_margin):
                valid_spawn_points.append((x, edge_margin))
            
            if self.is_walkable(x, self.height - edge_margin):
                valid_spawn_points.append((x, self.height - edge_margin))
        
        for y in range(edge_margin, self.height - edge_margin, step):
            if self.is_walkable(edge_margin, y):
                valid_spawn_points.append((edge_margin, y))
            
            if self.is_walkable(self.width - edge_margin, y):
                valid_spawn_points.append((self.width - edge_margin, y))
        
        # If still no walkable spawn points, search more of the map
        if not valid_spawn_points:
            print("No walkable edge points found, searching the whole map area")
            grid_size = 80
            for x in range(grid_size, self.width - grid_size, grid_size):
                for y in range(grid_size, self.height - grid_size, grid_size):
                    if self.is_walkable(x, y):
                        valid_spawn_points.append((x, y))
                        # Just find a few good points
                        if len(valid_spawn_points) >= 10:
                            return valid_spawn_points
    
    if not valid_spawn_points:
        print("WARNING: Could not find ANY valid walkable spawn points")
    else:
        print(f"Found {len(valid_spawn_points)} valid walkable spawn points")
    
    return valid_spawn_points
    
    def draw(self, surface):
        """Draws the map to the specified surface"""
        surface.blit(self.surface, (0, 0))


    def draw_debug_spawn_points(self, surface):
        """
        Draw visual indicators for spawn points to help with debugging
        """
        spawn_points = self.get_spawn_positions()
    
    # Draw all spawn points
    for x, y in spawn_points:
        # Draw a circle at each spawn point
        pygame.draw.circle(surface, (0, 255, 0), (int(x), int(y)), 10, 2)
        
        # Draw an X in the middle
        pygame.draw.line(surface, (0, 255, 0), (x-5, y-5), (x+5, y+5), 2)
        pygame.draw.line(surface, (0, 255, 0), (x-5, y+5), (x+5, y-5), 2)




# A more detailed Player class with animations
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load directional sprites with error handling
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'idle': []
        }

        # Try loading the sprites from the specific file paths
        try:
            # Load character sprites for different directions
            self.image_up = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'characters', 'kai', 'kai_up.png')).convert_alpha()
            self.image_down = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'characters', 'kai', 'kai_down.png')).convert_alpha()
            self.image_left = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'characters', 'kai', 'kai_left.png')).convert_alpha()
            self.image_right = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'characters', 'kai', 'kai_right.png')).convert_alpha()

            # Use these images for our animations (single frame each direction)
            self.animations['up'] = [self.image_up]
            self.animations['down'] = [self.image_down]
            self.animations['left'] = [self.image_left]
            self.animations['right'] = [self.image_right]
            self.animations['idle'] = [self.image_down]  # Use down image for idle

            print("Successfully loaded character sprites")
        except pygame.error as e:
            print(f"Error loading character sprites: {e}")
            # Create a fallback sprite
            fallback = pygame.Surface((32, 32))
            fallback.fill((255, 0, 0))  # Red square as fallback
            pygame.draw.rect(fallback, (255, 255, 255), (8, 8, 16, 16))  # White inner square

            for direction in self.animations:
                self.animations[direction] = [fallback]

        # Animation variables 
        self.direction = 'down'
        self.animation_index = 0
        self.animation_speed = 0.2  # seconds per frame
        self.animation_timer = 0

        # Set initial image
        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect(center=(x, y))

        # Movement variables
        self.speed = 200  # Speed in pixels per second
        self.velocity = [0, 0]  # x, y velocity
        self.moving = False

        # Player stats
        self.deliveries = 0
        self.missed_deliveries = 0
        self.delivery_cooldown = 0
        self.delivery_cooldown_max = 0.5  # seconds

        # Food truck is not available yet, so we'll skip it for now
        self.has_truck = False
        print("Food truck disabled - will be added later")

    def update(self, dt, customers, foods, game_map=None):
        # Previous position for collision resolution
        prev_x, prev_y = self.rect.x, self.rect.y

        # Handle input and movement
        self.handle_movement(dt, game_map)

        # Update animation
        self.update_animation(dt)

        # Update delivery cooldown
        if self.delivery_cooldown > 0:
            self.delivery_cooldown -= dt

        # Check for customer interactions
        for customer in customers:
            if pygame.sprite.collide_rect(self, customer) and not customer.fed:
                customer.greet()

        # Update missed delivery count from expired customers
        for customer in customers:
            if customer.expired and not customer.counted:
                self.missed_deliveries += 1
                customer.counted = True

    def handle_movement(self, dt, game_map=None):
        keys = pygame.key.get_pressed()
        self.velocity = [0, 0]
        self.moving = False

        # Check key inputs and update velocity
        if keys[pygame.K_LEFT]:
            self.velocity[0] = -self.speed
            self.direction = 'left'
            self.moving = True
        elif keys[pygame.K_RIGHT]:
            self.velocity[0] = self.speed
            self.direction = 'right'
            self.moving = True

        if keys[pygame.K_UP]:
            self.velocity[1] = -self.speed
            self.direction = 'up'
            self.moving = True
        elif keys[pygame.K_DOWN]:
            self.velocity[1] = self.speed
            self.direction = 'down'
            self.moving = True

        # Diagonal movement should not be faster
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            self.velocity[0] *= 0.7071  # 1/sqrt(2)
            self.velocity[1] *= 0.7071

        # Save current position for collision detection
        old_x, old_y = self.rect.x, self.rect.y
        
        # Update position
        new_x = old_x + int(self.velocity[0] * dt)
        new_y = old_y + int(self.velocity[1] * dt)
        
        # Check for collisions with the map (if it exists)
        if game_map:
            # Check x-axis movement
            if game_map.is_walkable(new_x + self.rect.width // 2, old_y + self.rect.height // 2):
                self.rect.x = new_x
            
            # Check y-axis movement
            if game_map.is_walkable(self.rect.x + self.rect.width // 2, new_y + self.rect.height // 2):
                self.rect.y = new_y
        else:
            # Fallback to the old behavior if no map is available
            self.rect.x = new_x
            self.rect.y = new_y
            
            # Boundary checks
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT

    def update_animation(self, dt):
        # If not moving, use idle animation
        if not self.moving:
            if 'idle' in self.animations and self.animations['idle']:
                self.image = self.animations['idle'][0]
            else:
                self.image = self.animations[self.direction][0]
            self.animation_index = 0
            self.animation_timer = 0
            return

        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animations[self.direction])

        # Update image
        self.image = self.animations[self.direction][self.animation_index]

    def throw_food(self, foods):
        # Check if cooldown has passed
        if self.delivery_cooldown <= 0:
            # Create new food item in the direction player is facing
            direction_vectors = {
                'up': (0, -1),
                'down': (0, 1),
                'left': (-1, 0),
                'right': (1, 0)
            }

            dx, dy = direction_vectors[self.direction]

            # Randomly select a food type
            food_types = ['pizza', 'smoothie', 'icecream', 'pudding']
            food_type = random.choice(food_types)

            food = Food(self.rect.centerx, self.rect.centery, dx, dy, food_type)
            foods.add(food)

            # Play throw sound
            try:
                pickup_sound.play()
            except:
                pass

            # Reset cooldown
            self.delivery_cooldown = self.delivery_cooldown_max

    def draw_stats(self, surface):
        # Delivery stats
        delivery_text = font.render(f"Deliveries: {self.deliveries}", True, WHITE)
        surface.blit(delivery_text, (20, 20))

        missed_text = font.render(f"Missed: {self.missed_deliveries}", True, WHITE)
        surface.blit(missed_text, (20, 60))

        # Cooldown indicator
        if self.delivery_cooldown > 0:
            cooldown_width = int((self.delivery_cooldown / self.delivery_cooldown_max) * 100)
            pygame.draw.rect(surface, RED, (20, 100, 100, 10))
            pygame.draw.rect(surface, GREEN, (20, 100, 100 - cooldown_width, 10))
            pygame.draw.rect(surface, WHITE, (20, 100, 100, 10), 2)

    def draw(self, surface):
        # Draw player
        surface.blit(self.image, self.rect)


# Customer class
class Customer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Customer types for random selection
        customer_types = [
            {
                'type': 'lady_1',
                'sprites': {
                    'up': 'Customer_Lady_1_up.png',
                    'down': 'Customer_Lady_1_down.png',
                    'left': 'Customer_Lady_1_left.png',
                    'right': 'Customer_Lady_1_right.png'
                }
            },
            {
                'type': 'lady_2',
                'sprites': {
                    'up': 'Customer_Lady_2_up.png',
                    'down': 'Customer_Lady_2_down.png',
                    'left': 'Customer_Lady_2_left.png',
                    'right': 'Customer_Lady_2_right.png'
                }
            },
            {
                'type': 'lady_3',
                'sprites': {
                    'up': 'Customer_Lady_3_up.png',
                    'down': 'Customer_Lady_3_down.png',
                    'left': 'Customer_Lady_3_left.png',
                    'right': 'Customer_Lady_3_up.png'  # Note: Using up as fallback
                }
            },
            {
                'type': 'lady_4',
                'sprites': {
                    'up': 'Customer_Lady_4_up.png',
                    'down': 'Customer_Lady_4_down.png',
                    'left': 'Customer_Lady_4_left.png',
                    'right': 'Customer_Lady_4_right.png'
                }
            },
            {
                'type': 'man_1',
                'sprites': {
                    'up': 'Customer_Man_1_up.png',
                    'down': 'Customer_Man_1_down.png',
                    'left': 'Customer_Man_1_left.png',
                    'right': 'Customer_Man_1_right.png'
                }
            },
            {
                'type': 'man_2',
                'sprites': {
                    'up': 'Customer_Man_2_up.png',
                    'down': 'Customer_Man_2_down.png',
                    'left': 'Customer_Man_2_left.png',
                    'right': 'Customer_Man_2_up.png'  # Note: Using up as fallback
                }
            },
            {
                'type': 'man_3',
                'sprites': {
                    'up': 'Customer_Man_3_up.png',
                    'down': 'Customer_Man_3_down.png',
                    'left': 'Customer_Man_3_left.png',
                    'right': 'Customer_Man_3_right.png'
                }
            },
            {
                'type': 'man_4',
                'sprites': {
                    'up': 'Customer_Man_4_up.png',
                    'down': 'Customer_Man_4_down.png',
                    'left': 'Customer_Man_4_left.png',
                    'right': 'Customer_Man_4_right.png'
                }
            }
        ]
        
        # Randomly select a customer type
        self.customer_type = random.choice(customer_types)
        self.type = self.customer_type['type']
        
        # Load customer sprites
        self.sprites = {}
        try:
            for direction, filename in self.customer_type['sprites'].items():
                sprite_path = os.path.join(ASSETS_DIR, 'sprites', 'characters', 'customers', filename)
                if os.path.exists(sprite_path):
                    self.sprites[direction] = pygame.image.load(sprite_path).convert_alpha()
                else:
                    print(f"Warning: Customer sprite {sprite_path} not found")
                    
            # Set initial direction and image
            self.direction = 'down'
            self.image = self.sprites[self.direction]
            print(f"Successfully loaded customer sprites for {self.type}")
        except Exception as e:
            print(f"Error loading customer sprites: {e}")
            # Create a fallback sprite if loading fails
            fallback = pygame.Surface((32, 32))
            fallback.fill((0, 0, 255))  # Blue square as fallback
            pygame.draw.circle(fallback, (255, 255, 255), (16, 16), 10)  # White circle
            self.sprites = {'up': fallback, 'down': fallback, 'left': fallback, 'right': fallback}
            self.image = fallback
            
        self.rect = self.image.get_rect(center=(x, y))

        # Customer variables
        self.patience = random.uniform(10, 20)  # seconds before leaving
        self.timer = 0
        self.fed = False
        self.expired = False
        self.counted = False
        self.greeting = False
        self.greeting_timer = 0

        # Dialog bubble for greeting
        self.bubble = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.bubble, (255, 255, 255), (0, 0, 80, 40))
        self.bubble_rect = self.bubble.get_rect(center=(self.rect.centerx, self.rect.top - 30))

        # Food preference
        self.food_preference = random.choice(['pizza', 'smoothie', 'icecream', 'pudding'])

        # Draw food icon in bubble
        if self.food_preference == 'pizza':
            pygame.draw.polygon(self.bubble, YELLOW, [(40, 10), (60, 30), (20, 30)])
        elif self.food_preference == 'smoothie':
            pygame.draw.rect(self.bubble, (150, 0, 255), (30, 10, 20, 25))
            pygame.draw.ellipse(self.bubble, (200, 0, 255), (25, 5, 30, 10))
        elif self.food_preference == 'icecream':
            pygame.draw.polygon(self.bubble, (200, 200, 150), [(40, 30), (30, 10), (50, 10)])
            pygame.draw.circle(self.bubble, (255, 100, 100), (40, 10), 10)
        else:  # pudding
            pygame.draw.rect(self.bubble, (160, 120, 60), (30, 10, 20, 20))
            pygame.draw.ellipse(self.bubble, (180, 140, 70), (25, 5, 30, 10))

    def update(self, dt):
        # Update patience timer
        if not self.fed and not self.expired:
            self.timer += dt
            if self.timer >= self.patience:
                self.expired = True

        # Update greeting timer
        if self.greeting:
            self.greeting_timer += dt
            if self.greeting_timer >= 2.0:  # Show greeting for 2 seconds
                self.greeting = False
                self.greeting_timer = 0

        # Update bubble position to follow customer
        self.bubble_rect.center = (self.rect.centerx, self.rect.top - 30)

    def greet(self):
        self.greeting = True
        self.greeting_timer = 0

    def feed(self, food_type):
        if not self.fed and not self.expired:
            if food_type == self.food_preference:
                self.fed = True
                return 100  # Bonus points for matching preference
            else:
                self.fed = True
                return 50  # Base points for any food
        return 0

    def draw(self, surface):
        # Draw customer
        surface.blit(self.image, self.rect)

        # Draw speech bubble if greeting or not fed
        if self.greeting or (not self.fed and not self.expired):
            surface.blit(self.bubble, self.bubble_rect)

        # Draw patience meter
        if not self.fed and not self.expired:
            patience_width = int((1 - self.timer / self.patience) * 40)
            pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, 40, 5))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, patience_width, 5))

        # Visual indicator for fed status
        if self.fed:
            happy_face = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(happy_face, GREEN, (0, 0, 40, 20))
            surface.blit(happy_face, (self.rect.x, self.rect.top - 20))


# Food class
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, food_type='pizza'):
        super().__init__()
        self.food_type = food_type

        # Food types and their corresponding image base names
        food_base_names = {
            'pizza': 'Tropical_Pizza_Slice',
            'smoothie': 'Ska',
            'icecream': 'Island_Ice_Cream',
            'pudding': 'Rasta_Rice_Pudding'
        }
        
        # Food folders
        food_folders = {
            'pizza': os.path.join(ASSETS_DIR, 'Food', 'Tropical_Pizza_Slice'),
            'smoothie': os.path.join(ASSETS_DIR, 'Food', 'Ska_Smoothie'),
            'icecream': os.path.join(ASSETS_DIR, 'Food', 'Island_Ice_Cream'),
            'pudding': os.path.join(ASSETS_DIR, 'Food', 'Rasta_Rice_Pudding')
        }
        
        # Food names for score display
        self.food_names = {
            'pizza': "Tropical Pizza Slice",
            'smoothie': "Ska Smoothie",
            'icecream': "Island Ice Cream Jam",
            'pudding': "Rasta Rice Pudding"
        }
        
        # Set the food name
        self.name = self.food_names[food_type]
        
        # Load animation frames
        self.animation_frames = []
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # 100ms per frame
        
        # Try to load the food animation frames
        try:
            folder_path = food_folders[food_type]
            base_name = food_base_names[food_type]
            
            for i in range(1, 6):  # Load frames 1 through 5
                frame_name = f"{base_name}{i}.png"
                image_path = os.path.join(folder_path, frame_name)
                
                if os.path.exists(image_path):
                    frame = pygame.image.load(image_path).convert_alpha()
                    # Scale the image if needed
                    current_size = frame.get_size()
                    if current_size[0] > 40 or current_size[1] > 40:
                        frame = pygame.transform.scale(frame, (30, 30))
                    self.animation_frames.append(frame)
                else:
                    print(f"Warning: Food frame not found at {image_path}")
            
            if self.animation_frames:
                print(f"Successfully loaded {len(self.animation_frames)} frames for {food_type}")
                self.image = self.animation_frames[0]
            else:
                print(f"No frames loaded for {food_type}")
                # Create a fallback sprite if loading fails
                self.image = pygame.Surface((20, 20))
                if food_type == 'pizza':
                    self.image.fill(YELLOW)
                elif food_type == 'smoothie':
                    self.image.fill((150, 0, 255))
                elif food_type == 'icecream':
                    self.image.fill((255, 100, 100))
                else:  # pudding
                    self.image.fill((160, 120, 60))
                self.animation_frames = [self.image]
                
        except Exception as e:
            print(f"Error loading food images: {e}")
            # Create a simple surface for error handling
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 255, 255))  # White as fallback
            self.animation_frames = [self.image]

        self.rect = self.image.get_rect(center=(x, y))

        # Movement variables
        self.speed = 300
        self.direction = pygame.math.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction.normalize_ip()

        # Lifespan (despawn after a few seconds)
        self.lifespan = 2.0  # seconds
        self.timer = 0
    
    def update(self, dt):
        # Move food
        self.rect.x += int(self.direction.x * self.speed * dt)
        self.rect.y += int(self.direction.y * self.speed * dt)

        # Update timer
        self.timer += dt
        if self.timer >= self.lifespan:
            self.kill()
            
        # Update animation
        if len(self.animation_frames) > 1:  # Only animate if we have multiple frames
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
                self.image = self.animation_frames[self.animation_index]

        # Check if out of bounds
        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()


# Particle effect class
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size=5, speed=2, lifetime=1):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))

        # Particle properties
        self.velocity = [random.uniform(-speed, speed), random.uniform(-speed, speed)]
        self.lifetime = lifetime
        self.timer = 0
        self.alpha = 255
        self.fade_rate = 255 / lifetime

    def update(self, dt):
        # Update position
        self.rect.x += int(self.velocity[0])
        self.rect.y += int(self.velocity[1])

        # Update lifetime and transparency
        self.timer += dt
        self.alpha = max(0, 255 - int(self.timer * self.fade_rate))
        self.image.set_alpha(self.alpha)

        # Kill particle if lifetime exceeded
        if self.timer >= self.lifetime:
            self.kill()


# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = WHITE
        self.font = pygame.font.Font(None, 36)
        self.hovered = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.hovered = True
        else:
            self.current_color = self.color
            self.hovered = False

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hovered
        return False


# Create sprite groups
all_sprites = pygame.sprite.Group()
customers = pygame.sprite.Group()
foods = pygame.sprite.Group()
particles = pygame.sprite.Group()

# Create UI buttons
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start Game", GREEN, (100, 255, 100))
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))
restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Restart", GREEN, (100, 255, 100))

# Game variables
game_time = 0
customer_spawn_rate = 5  # seconds
customer_spawn_timer = 0
debug_mode = False  # Set to True to enable debug mode


def spawn_customer(game_map=None):
    """
    Spawns a customer at a valid position, prioritizing map-defined spawn points
    but falling back to algorithmic methods if needed.
    """
    # Get spawn positions from the map if available
    if game_map:
        # Try to use spawn points defined in the map
        spawn_points = game_map.get_spawn_positions("CustomerSpawn")
        
        if spawn_points:
            # Pick a random spawn point
            x, y = random.choice(spawn_points)
            customer = Customer(x, y)
            customers.add(customer)
            all_sprites.add(customer)
            
            # Add spawn particle effect
            create_spawn_particles(x, y)
            print(f"Spawned customer at map-defined point ({x}, {y})")
            return True
    
    # If we get here, either no game_map exists or no valid spawn points were found
    
    # Define edge spawn logic with walkability checks
    if game_map:
        # Try up to 10 times to find a valid spawn point along the edges
        for attempt in range(10):
            side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
            
            if side == 0:  # Top edge
                x = random.randint(50, WIDTH - 50)
                y = 50
            elif side == 1:  # Right edge
                x = WIDTH - 50
                y = random.randint(50, HEIGHT - 50)
            elif side == 2:  # Bottom edge
                x = random.randint(50, WIDTH - 50)
                y = HEIGHT - 50
            else:  # Left edge
                x = 50
                y = random.randint(50, HEIGHT - 50)
            
            # Check if this position is walkable
            if game_map.is_walkable(x, y):
                customer = Customer(x, y)
                customers.add(customer)
                all_sprites.add(customer)
                
                create_spawn_particles(x, y)
                print(f"Spawned customer at edge point ({x}, {y}) on attempt {attempt+1}")
                return True
    
    # Final fallback - just use the old method without walkability checks
    # This ensures customers still spawn even in worst-case scenarios
    side = random.randint(0, 3)
    
    if side == 0:
        x = random.randint(50, WIDTH - 50)
        y = 50
    elif side == 1:
        x = WIDTH - 50
        y = random.randint(50, HEIGHT - 50)
    elif side == 2:
        x = random.randint(50, WIDTH - 50)
        y = HEIGHT - 50
    else:
        x = 50
        y = random.randint(50, HEIGHT - 50)
    
    customer = Customer(x, y)
    customers.add(customer)
    all_sprites.add(customer)
    
    create_spawn_particles(x, y)
    print(f"WARNING: Spawned customer at fallback position ({x}, {y}) - could not find walkable spot")
    return True

def create_spawn_particles(x, y):
    """Helper function to create particle effects at spawn point"""
    for _ in range(5):
        particle = Particle(
            x, y, (0, 255, 255), size=random.randint(3, 8), speed=1, lifetime=0.5
        )
        particles.add(particle)
        all_sprites.add(particle)

def validate_customer_positions(customers_group, game_map):
    """
    Checks all customers to ensure they're in valid positions.
    Relocates any that are in invalid positions.
    """
    for customer in customers_group:
        if not game_map.is_walkable(customer.rect.centerx, customer.rect.centery):
            print(f"Found customer in invalid position at ({customer.rect.centerx}, {customer.rect.centery})")
            # Try to find a valid position
            spawn_points = game_map.get_spawn_positions()
            if spawn_points:
                x, y = random.choice(spawn_points)
                customer.rect.center = (x, y)
                print(f"Relocated customer to ({x}, {y})")
            else:
                # If all else fails, remove the customer
                customer.kill()
                print("Removed customer in invalid position")

def reset_game(game_map=None):
    global score, game_state, game_time

    # Clear sprite groups
    all_sprites.empty()
    customers.empty()
    foods.empty()
    particles.empty()

    # Create player instance
    player = Player(WIDTH // 2, HEIGHT // 2)
    all_sprites.add(player)

    # Reset game variables
    score = 0
    game_time = 0

    # Reset game state
    game_state = PLAYING

    # Start background music again
    try:
        mixer.music.play(-1)
    except:
        pass
    
    return player


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def main():
    global game_state, score, high_score, game_time
    global customer_spawn_timer, customer_spawn_rate

    # Set initial game state
    game_state = MENU
    
    # Initialize tilemap
    game_map = None
    try:
        # Look for the map in different possible locations
        map_candidates = [
            os.path.join(MAP_DIR, "Level_1_Frame_1.tmx"),  # Standard path
            os.path.join(BASE_DIR, "assets", "Maps", "level1", "Level_1_Frame_1.tmx"),  # Alternate path
            os.path.join(BASE_DIR, "Level_1_Frame_1.tmx")  # Root directory
        ]
        
        map_path = None
        for candidate in map_candidates:
            if os.path.exists(candidate):
                map_path = candidate
                break
        
        if map_path:
            print(f"Found map at: {map_path}")
            game_map = TiledMap(map_path)
            print("Map loaded successfully")
        else:
            print("Map file not found in any of the expected locations")
    except Exception as e:
        print(f"Error loading map: {e}")
    
    # Create player instance
    player = Player(WIDTH // 2, HEIGHT // 2)
    all_sprites.add(player)

    running = True
    while running:
        # Calculate delta time (in seconds)
        dt = clock.tick(FPS) / 1000

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Space bar to throw food
            if game_state == PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.throw_food(foods)

            # Toggle debug mode with F12
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                debug_mode = not debug_modeprint(f"Debug mode {'enabled' if debug_mode else 'disabled'}")


            # Check button clicks in menus
            if game_state == MENU:
                if start_button.is_clicked(event):
                    game_state = PLAYING
                    try:
                        button_sound.play()
                    except:
                        pass
                if exit_button.is_clicked(event):
                    running = False

            if game_state == GAME_OVER:
                if restart_button.is_clicked(event):
                    player = reset_game(game_map)
                    try:
                        button_sound.play()
                    except:
                        pass

        # Get mouse position for button hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Update game based on state
        if game_state == PLAYING:
            # Update game time
            game_time += dt

            # Spawn customers
            customer_spawn_timer += dt
            if customer_spawn_timer >= customer_spawn_rate:
                customer_spawn_timer = 0
                
                # Don't spawn too many customers
                if len(customers) < 15:  # Set a reasonable limit
                    # Measure spawn time for performance monitoring
                    start_time = time.time()
                    spawn_customer(game_map)
                    spawn_time = time.time() - start_time
            
            # Only log if spawning takes a long time
            if spawn_time > 0.01:
                print(f"Customer spawn took {spawn_time*1000:.1f}ms")

            # Update player (pass the game_map to the update method)
            player.update(dt, customers, foods, game_map)

            # Update customers
            for customer in customers:
                customer.update(dt)

            # Check for customers in invalid positions - run occasionally
            if game_time % 5 < 0.1:  # Run approximately every 5 seconds
                validate_customer_positions(customers, game_map)

            # Update foods
            for food in foods:
                food.update(dt)

            # Check for food collisions with customers
            for food in foods:
                hit_customers = pygame.sprite.spritecollide(food, customers, False)
                for customer in hit_customers:
                    points = customer.feed(food.food_type)
                    if points > 0:
                        # Only count points and increment deliveries if the customer wasn't fed before
                        if not customer.fed:
                            score += points
                            player.deliveries += 1

                            # Create success particles
                            for _ in range(10):
                                particle = Particle(
                                    customer.rect.centerx,
                                    customer.rect.centery,
                                    GREEN,
                                    size=random.randint(3, 6),
                                    speed=2,
                                    lifetime=0.8
                                )
                                particles.add(particle)
                                all_sprites.add(particle)

                    # Remove the food
                    food.kill()

            # Update particles
            particles.update(dt)

            # Update high score
            high_score = max(high_score, score)

            # Check game over condition (optional)
            if player.missed_deliveries >= 10:
                game_state = GAME_OVER

            # Draw everything
            if game_map:
                # Draw the tilemap
                game_map.draw(screen)
                
                # Draw debug spawn points if debug mode is enabled
                if debug_mode:
                    game_map.draw_debug_spawn_points(screen)
                
            else:
                # This should not happen with the refactored code
                screen.fill((0, 0, 0))
                draw_text(screen, "Map failed to load!", 48, WIDTH // 2, HEIGHT // 2, RED)

            # Draw customers
            for customer in customers:
                customer.draw(screen)

            # Draw player
            player.draw(screen)

            # Draw foods and particles
            foods.draw(screen)
            particles.draw(screen)

            # Draw player stats
            player.draw_stats(screen)

            # Draw score
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (WIDTH - 150, 20))

            # Draw game time
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            screen.blit(time_text, (WIDTH - 150, 60))

        elif game_state == MENU:
            # Draw menu
            screen.blit(menu_background, (0, 0))
            draw_text(screen, "JAMMIN' EATS", 72, WIDTH // 2, HEIGHT // 4, YELLOW)
            draw_text(screen, "Deliver tasty food to hungry customers!", 36, WIDTH // 2, HEIGHT // 3, WHITE)

            # Update and draw buttons
            start_button.update(mouse_pos)
            exit_button.update(mouse_pos)
            start_button.draw(screen)
            exit_button.draw(screen)

            # Draw high score
            draw_text(screen, f"High Score: {high_score}", 36, WIDTH // 2, HEIGHT - 100, WHITE)

        elif game_state == GAME_OVER:
            # Draw game over screen
            screen.blit(game_over_background, (0, 0))
            draw_text(screen, "GAME OVER", 72, WIDTH // 2, HEIGHT // 4, RED)
            draw_text(screen, f"Score: {score}", 48, WIDTH // 2, HEIGHT // 3, WHITE)
            draw_text(screen, f"High Score: {high_score}", 36, WIDTH // 2, HEIGHT // 3 + 50, WHITE)

            # Show stats
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            draw_text(screen, f"Time Survived: {minutes:02d}:{seconds:02d}", 36, WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text(screen, f"Deliveries Made: {player.deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 40, WHITE)
            draw_text(screen, f"Customers Missed: {player.missed_deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 80, WHITE)

            # Update and draw restart button
            restart_button.update(mouse_pos)
            restart_button.draw(screen)

        # Update the display
        pygame.display.flip()

    pygame.quit()
    sys.exit()


# Run the game
if __name__ == '__main__':
    main()