import pygame
import os
import pytmx
import traceback
from pytmx.util_pygame import load_pygame
from src.core.constants import *
from src.debug.logger import log, log_error, log_asset_load

# Resource loader class to handle tile resources
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
        # Create a fallback tile
        fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Create a checkerboard pattern to indicate missing texture
        colors = [(255, 0, 255), (0, 0, 0)]  # Magenta and black
        tile_size = 8
        for y in range(0, 32, tile_size):
            for x in range(0, 32, tile_size):
                color_idx = ((x // tile_size) + (y // tile_size)) % 2
                pygame.draw.rect(fallback, colors[color_idx], (x, y, tile_size, tile_size))
        return fallback


class TiledMap:
    def __init__(self, tmx_path):
        # Set up the resource loader to handle tileset images
        loader = ResourceLoader(os.path.dirname(tmx_path))
        
        try:
            # Load the TMX file using pytmx
            self.tmx_data = load_pygame(tmx_path, image_loader=loader.load)
            self.width = self.tmx_data.width * self.tmx_data.tilewidth
            self.height = self.tmx_data.height * self.tmx_data.tileheight
            
            # Properties for collision detection
            self.collision_rects = []
            self.unwalkable_tiles = []
            
            # Properties for spawn points
            self.spawn_points = {}
            
            # Extract collision objects and other game objects
            self._extract_objects()
            self._extract_tile_collisions()
            
            # Set up walkability caching
            self.walkable_cache = {}
            self.cache_enabled = True
            self.use_cache = True
            self.cache_walkable_areas()
            
            # Render the tilemap to a surface for better performance
            self.map_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self._render_layers()
        except Exception as e:
            print(f"Error loading map: {e}")
            self._create_fallback_map()
        
    def _find_and_load_tmx(self, tmx_path):
        """Attempt to find and load the TMX file using the same approach as original main.py"""
        # Check if the TMX file exists before trying to load it
        if os.path.exists(tmx_path):
            try:
                # Create a resource loader exactly as in the original main.py
                # This loader handles the relative paths in TMX files
                self.loader = ResourceLoader(os.path.dirname(tmx_path))
                
                # Load the TMX file
                self.tmx_data = load_pygame(tmx_path, image_loader=self.loader.load)
                self.width = self.tmx_data.width * self.tmx_data.tilewidth
                self.height = self.tmx_data.height * self.tmx_data.tileheight
                
                # Initialize map properties
                self._initialize_map_properties()
                log_asset_load("map", os.path.basename(tmx_path), tmx_path, True)
                return True
            except Exception as e:
                log_error(f"Error loading TMX file: {e}")
        else:
            # Try alternative paths
            map_name = os.path.basename(tmx_path)
            alt_paths = [
                os.path.join(ASSETS_DIR, 'Maps', 'level1', map_name),
                os.path.join(ASSETS_DIR, 'Maps', map_name)
            ]
            
            # Try each alternative path
            for path in alt_paths:
                if os.path.exists(path):
                    try:
                        self.loader = ResourceLoader(os.path.dirname(path))
                        self.tmx_data = load_pygame(path, image_loader=self.loader.load)
                        self.width = self.tmx_data.width * self.tmx_data.tilewidth
                        self.height = self.tmx_data.height * self.tmx_data.tileheight
                        self._initialize_map_properties()
                        log_asset_load("map", map_name, path, True)
                        return True
                    except Exception as e:
                        log_error(f"Error loading alternative TMX file from {path}: {e}")
        
        # If we get here, we need to create a fallback map
        log_error(f"TMX file not found or failed to load: {tmx_path}")
        return False
        
        # Pre-compute the walkable areas
        if self.cache_enabled:
            self.cache_walkable_areas()
    
    def cache_walkable_areas(self):
        """Pre-compute walkable areas for better performance"""
        # This can be expensive for large maps, so you might want to optimize further
        print("Caching walkable areas...")
        tile_size = self.tmx_data.tilewidth
        
        # We'll check every Nth pixel to reduce computation
        step = 8
        
        for x in range(0, self.width, step):
            for y in range(0, self.height, step):
                # Check if the position is walkable and cache the result
                self.walkable_cache[(x, y)] = self._compute_walkable(x, y)
        
        print(f"Walkability cache built with {len(self.walkable_cache)} entries")
    
    def _initialize_map_properties(self):
        """Initialize common map properties after loading a TMX file"""
        # Properties for walkable area caching
        self.walkable_cache = {}
        self.cache_enabled = True
        self.use_cache = True
        
        # Properties for collision detection
        self.collision_rects = []
        self.unwalkable_tiles = []
        
        # Properties for spawn points
        self.spawn_points = {}
        
        # Pre-render the entire tilemap to a surface for better performance
        self.map_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._render_layers()
        
        # Extract objects and collision info
        self._extract_objects()
        self._extract_tile_collisions()
        
        # Pre-compute the walkable areas
        if self.cache_enabled:
            self.cache_walkable_areas()
            
    def _create_fallback_map(self):
        """Create a simple fallback map when TMX loading fails"""
        print("Creating fallback map...")
        
        # Create a basic grid map
        width, height = 20, 15  # cells (20x15 grid)
        cell_size = 32  # pixels per cell
        
        self.width = width * cell_size
        self.height = height * cell_size
        
        # Initialize a fake TMX data object to avoid attribute errors
        class FakeTmxData:
            def __init__(self):
                self.width = width
                self.height = height
                self.tilewidth = cell_size
                self.tileheight = cell_size
                self.layers = []
                self.visible_layers = []  # Add missing attribute
                self.objectgroups = []
                
                # Add additional missing attributes that might be accessed
                self.layernames = {}
                self.properties = {}
                
            def get_layer_by_name(self, name):
                return None
                
            def get_tile_properties_by_gid(self, gid):
                return None
        
        self.tmx_data = FakeTmxData()
        
        # Initialize basic properties
        self.walkable_cache = {}
        self.cache_enabled = True
        self.use_cache = True
        self.collision_rects = []
        self.unwalkable_tiles = []
        self.spawn_points = {}
        
        # Create a map surface
        self.map_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw a grid
        for x in range(width):
            for y in range(height):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                # Make the edges of the map unwalkable
                if x == 0 or y == 0 or x == width-1 or y == height-1:
                    pygame.draw.rect(self.map_surface, (100, 100, 100), rect)
                    self.collision_rects.append(rect)
                else:
                    # Alternate colors for tiles
                    if (x + y) % 2 == 0:
                        color = (200, 230, 200)  # Light green
                    else:
                        color = (180, 210, 180)  # Slightly darker green
                    pygame.draw.rect(self.map_surface, color, rect)
                    
                # Draw grid lines
                pygame.draw.rect(self.map_surface, (150, 150, 150), rect, 1)
        
        # Add spawn points around the center
        center_x, center_y = self.width // 2, self.height // 2
        self.spawn_points['CustomerSpawn'] = [
            (center_x - 100, center_y - 100),
            (center_x + 100, center_y - 100),
            (center_x - 100, center_y + 100),
            (center_x + 100, center_y + 100)
        ]
        print("Fallback map created successfully")    
            
    def _compute_walkable(self, x, y):
        """Raw walkability check without using cache"""
        # Check if position is out of map bounds
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        
        # Check collision with collision rectangles
        for rect in self.collision_rects:
            if rect.collidepoint(x, y):
                return False
        
        # Convert pixel position to tile indices
        tile_x = x // self.tmx_data.tilewidth
        tile_y = y // self.tmx_data.tileheight
        
        # Check if the tile is in the unwalkable list
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                try:
                    if (tile_x, tile_y) in self.unwalkable_tiles:
                        return False
                except IndexError:
                    # Tile is out of bounds
                    continue
        
        # If we got here, position is walkable
        return True
    
    def is_walkable(self, x, y):
        """Check if a position is walkable, using cache when possible"""
        # Round to nearest cached point if cache is enabled
        if self.use_cache and self.cache_enabled:
            # Find the nearest cached point
            step = 8
            cache_x = round(x / step) * step
            cache_y = round(y / step) * step
            
            if (cache_x, cache_y) in self.walkable_cache:
                return self.walkable_cache[(cache_x, cache_y)]
        
        # Fall back to computing walkability directly
        return self._check_walkability(x, y)
    
    def _render_layers(self):
        """Render all tile layers to a single surface"""
        # Loop through all visible tile layers and render them
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                # This is a tile layer
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        # Calculate the position to draw the tile
                        pos_x = x * self.tmx_data.tilewidth
                        pos_y = y * self.tmx_data.tileheight
                        self.map_surface.blit(tile, (pos_x, pos_y))
    
    def _extract_objects(self):
        """Extracts collision and interactable objects from the TMX file"""
        # Process object layers to find collision rectangles and spawn points
        for obj_group in self.tmx_data.objectgroups:
            for obj in obj_group:
                if obj.type == 'collision' or obj_group.name.lower() == 'collision':
                    # This is a collision object
                    self.collision_rects.append(pygame.Rect(
                        obj.x, obj.y, obj.width, obj.height
                    ))
                elif 'spawn' in obj.name.lower() or 'spawn' in obj_group.name.lower():
                    # This is a spawn point, categorize by name
                    spawn_type = obj.name if obj.name else obj_group.name
                    if spawn_type not in self.spawn_points:
                        self.spawn_points[spawn_type] = []
                    
                    self.spawn_points[spawn_type].append((obj.x, obj.y))
    
    def _extract_tile_collisions(self):
        """Extracts collision information from specific tile layers"""
        # Example: looking for layer named 'collision' or 'unwalkable'
        unwalkable_layer_names = ['collision', 'unwalkable', 'ocean']
        
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data') and layer.name.lower() in unwalkable_layer_names:
                for x, y, gid in layer:
                    if gid:  # If there's a tile here (non-zero gid)
                        self.unwalkable_tiles.append((x, y))
    
    def _check_walkability(self, x, y):
        """Helper method to check if a position is walkable"""
        # Check if position is out of map bounds
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        
        # Check collision with collision rectangles
        for rect in self.collision_rects:
            if rect.collidepoint(x, y):
                return False
        
        # Convert pixel position to tile indices
        tile_x = int(x // self.tmx_data.tilewidth)
        tile_y = int(y // self.tmx_data.tileheight)
        
        # Check if the tile is in the unwalkable list
        if (tile_x, tile_y) in self.unwalkable_tiles:
            return False
        
        # If we got here, position is walkable
        return True
    
    def get_spawn_positions(self, object_name="CustomerSpawn"):
        """Gets spawn positions for customers based on an object name"""
        spawn_points = []
        
        # Try to find spawn points from the map objects
        if object_name in self.spawn_points:
            # Found spawn points in the cached object list
            potential_spawns = self.spawn_points[object_name]
            
            # Filter to only include walkable spawn points
            for pos in potential_spawns:
                if self.is_walkable(pos[0], pos[1]):
                    spawn_points.append(pos)
                elif self.debug_mode:
                    print(f"Spawn point at ({pos[0]}, {pos[1]}) is not walkable")
        
        # If no spawn points were found in the object layer, try looking for objects directly
        if not spawn_points:
            for obj_group in self.tmx_data.objectgroups:
                for obj in obj_group:
                    if object_name.lower() in obj.name.lower() or object_name.lower() in obj_group.name.lower():
                        # This is a spawn object
                        pos = (obj.x, obj.y)
                        
                        # Check if the spawn point is walkable
                        if self.is_walkable(pos[0], pos[1]):
                            spawn_points.append(pos)
                        elif self.debug_mode:
                            print(f"Spawn point at ({pos[0]}, {pos[1]}) is not walkable")
        
        # If still no spawn points, generate some algorithmically
        if not spawn_points:
            # Generate spawn points at the edges of the map
            margin = 100  # Pixel margin from the edge
            step = 50    # Spacing between spawn points
            
            # Top edge
            for x in range(margin, self.width - margin, step):
                if self.is_walkable(x, margin):
                    spawn_points.append((x, margin))
            
            # Bottom edge
            for x in range(margin, self.width - margin, step):
                if self.is_walkable(x, self.height - margin):
                    spawn_points.append((x, self.height - margin))
            
            # Left edge
            for y in range(margin, self.height - margin, step):
                if self.is_walkable(margin, y):
                    spawn_points.append((margin, y))
            
            # Right edge
            for y in range(margin, self.height - margin, step):
                if self.is_walkable(self.width - margin, y):
                    spawn_points.append((self.width - margin, y))
        
        return spawn_points
    
    def draw(self, surface):
        """Draws the map to the specified surface"""
        surface.blit(self.map_surface, (0, 0))
    
    def draw_debug_spawn_points(self, surface):
        """Draw visual indicators for spawn points to help with debugging"""
        # Loop through all spawn point categories
        for spawn_type, positions in self.spawn_points.items():
            # Use different colors for different spawn types
            if 'customer' in spawn_type.lower():
                color = (0, 255, 0)  # Green for customer spawns
            elif 'player' in spawn_type.lower():
                color = (0, 0, 255)  # Blue for player spawns
            else:
                color = (255, 255, 0)  # Yellow for other spawns
            
            # Draw each spawn point
            for pos in positions:
                pygame.draw.circle(surface, color, pos, 10, 2)  # Outline
                pygame.draw.circle(surface, color, pos, 2)      # Center dot
                
                # Optionally, add a label (disabled by default as it can clutter the screen)
                # font = pygame.font.Font(None, 16)
                # label = font.render(spawn_type, True, color)
                # surface.blit(label, (pos[0] + 12, pos[1] - 8))
    
    def draw_debug_walkable(self, surface):
        """Draw walkable/unwalkable areas for debugging"""
        # Use a grid approach instead of checking every pixel
        grid_size = 20  # Check every 20 pixels
        rect_size = 5   # Size of the indicator squares
        
        for x in range(0, self.width, grid_size):
            for y in range(0, self.height, grid_size):
                if self.is_walkable(x, y):
                    # Draw green dot for walkable area
                    pygame.draw.rect(surface, (0, 255, 0, 128), 
                                    (x - rect_size//2, y - rect_size//2, rect_size, rect_size))
                else:
                    # Draw red X for unwalkable area
                    pygame.draw.line(surface, (255, 0, 0, 192), 
                                    (x - rect_size//2, y - rect_size//2), 
                                    (x + rect_size//2, y + rect_size//2), 2)
                    pygame.draw.line(surface, (255, 0, 0, 192), 
                                    (x + rect_size//2, y - rect_size//2), 
                                    (x - rect_size//2, y + rect_size//2), 2)
