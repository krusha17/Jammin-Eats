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
        print(f"[ResourceLoader] Attempting to load resource: {filename}")
        print(f"[ResourceLoader] Current working directory: {os.getcwd()}")
        # Handle the specific path pattern we're seeing in the error
        if '../../tilesets' in filename or 'TileSet_1.png' in filename:
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
            print(f"[ResourceLoader] Checking path: {path}")
            if os.path.exists(path):
                print(f"[ResourceLoader] Successfully loaded: {path}")
                return pygame.image.load(path).convert_alpha()
                
        print(f"[ResourceLoader] WARNING: missing resource {filename}")
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
        print(f"[TiledMap] Loading TMX map from: {tmx_path}")
        print(f"[TiledMap] Current working directory: {os.getcwd()}")
        self.debug_mode = False  # Set this to True for additional debug info
        
        # Initialize some base properties
        self.width = WIDTH  # Default to screen width
        self.height = HEIGHT  # Default to screen height
        self.walkable_cache = {}
        self.cache_enabled = True
        self.use_cache = True
        self.collision_rects = []
        self.unwalkable_tiles = []
        self.spawn_points = {}
        self.map_surface = None
        
        # If this is a 'fallback' request, skip trying to load the real map
        if tmx_path == "fallback":
            self._create_fallback_map()
            return
            
        # Try to load the actual map
        try:
            loader = ResourceLoader(os.path.dirname(tmx_path))
            self.tmx_data = load_pygame(tmx_path, image_loader=loader.load)
            print(f"[TiledMap] Successfully loaded TMX: {tmx_path}")
            self.width = self.tmx_data.width * self.tmx_data.tilewidth
            self.height = self.tmx_data.height * self.tmx_data.tileheight
            self._initialize_map_properties()
        except Exception as e:
            print(f"[TiledMap] Error loading map: {e}")
            traceback.print_exc()  # Print the full stack trace for debugging
            self._create_fallback_map()

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
        
        # Extract objects and collision info
        self._extract_objects()
        self._extract_tile_collisions()
        self._render_layers()
        
        # Pre-compute the walkable areas
        if self.cache_enabled:
            self.cache_walkable_areas()
    
    def _create_fallback_map(self):
        """Create a simple fallback map when TMX loading fails"""
        width = WIDTH // 32
        height = HEIGHT // 32
        cell_size = 32
        self.width = WIDTH
        self.height = HEIGHT
        print(f"[TiledMap] Creating fallback map of size {width}x{height} cells")
        
        # Create map surface
        self.map_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Set width and height properly
        self.width = WIDTH
        self.height = HEIGHT
        
        # Create a checkered pattern for the fallback map
        for y in range(0, self.height, cell_size):
            for x in range(0, self.width, cell_size):
                color = (200, 200, 200) if (x // cell_size + y // cell_size) % 2 == 0 else (150, 150, 150)
                pygame.draw.rect(self.map_surface, color, (x, y, cell_size, cell_size))
                
        # Add a border around the map
        pygame.draw.rect(self.map_surface, (100, 100, 100), (0, 0, self.width, self.height), 5)
        
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
    
    def _extract_tile_collisions(self):
        """Extracts collision information from tiles based on their 'collides' property
        
        This method will check each tile for a 'collides' property set to True in Tiled,
        and mark those tiles as unwalkable. It also maintains backward compatibility
        with the layer-based collision detection system.
        """
        # Clear existing unwalkable tiles
        self.unwalkable_tiles = []
        
        # For backward compatibility: layer names that are considered unwalkable
        unwalkable_layer_names = ['collision', 'unwalkable', 'ocean']
        
        # Debug logging
        log("Extracting tile collisions...")
        collision_count = 0
        
        # Iterate through all visible tile layers
        for layer in self.tmx_data.visible_layers:
            # Check if it's a tile layer
            if hasattr(layer, 'data'):
                # Check if entire layer is unwalkable (for backward compatibility)
                layer_is_unwalkable = (hasattr(layer, 'name') and 
                                     layer.name is not None and 
                                     layer.name.lower() in unwalkable_layer_names)
                
                # Check each tile in the layer
                for x, y, gid in layer:
                    if gid == 0:  # Skip empty tiles
                        continue
                        
                    # Check if this tile has the 'collides' property
                    properties = self.tmx_data.get_tile_properties_by_gid(gid)
                    
                    # Add tile to unwalkable list if:
                    # 1. The tile has 'collides' property set to True, OR
                    # 2. The layer is entirely unwalkable (for backward compatibility)
                    if ((properties and properties.get('collides', False)) or 
                        layer_is_unwalkable):
                        self.unwalkable_tiles.append((x, y))
                        collision_count += 1
        
        # Log the result for debugging
        log(f"Extracted {collision_count} unwalkable tiles")
        
    def _extract_objects(self):
        """Extracts collision and interactable objects from the TMX file"""
        # Process object layers to find collision rectangles and spawn points
        for obj_group in self.tmx_data.objectgroups:
            # Safely get the group name, using empty string if None
            group_name = obj_group.name.lower() if obj_group.name else ''
            
            for obj in obj_group:
                # Safely get the object name, using empty string if None
                obj_name = obj.name.lower() if obj.name else ''
                obj_type = obj.type if hasattr(obj, 'type') else ''
                
                # Check collision objects
                if obj_type == 'collision' or 'collision' in group_name:
                    # This is a collision object
                    self.collision_rects.append(pygame.Rect(
                        obj.x, obj.y, obj.width, obj.height
                    ))
                # Check spawn points
                elif 'spawn' in obj_name or 'spawn' in group_name:
                    # This is a spawn point, categorize by name
                    spawn_type = obj.name if obj.name else obj_group.name
                    if spawn_type not in self.spawn_points:
                        self.spawn_points[spawn_type] = []
                    
                    self.spawn_points[spawn_type].append((obj.x, obj.y))

    def _render_layers(self):
        """Render all tile layers to a single surface"""
        # First, fill the entire map surface with a solid color
        # This ensures no transparency shows through if there are any gaps in the tiles
        # Choose a color that matches your game's theme (typically blue for sky/water, or green for grass)
        fill_color = (0, 200, 255)  # Light blue background as a fallback
        self.map_surface.fill(fill_color)
        
        # Log the rendering process
        log("Rendering map layers...")
        
        # Loop through all visible tile layers and render them in order (bottom to top)
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
        
        # Log completion
        log("Map rendering complete")
    
    def cache_walkable_areas(self):
        """Pre-compute walkable areas for better performance"""
        # This can be expensive for large maps, so you might want to optimize further
        log("Caching walkable areas...")
        
        # We'll check every Nth pixel to reduce computation
        step = 8
        
        for x in range(0, self.width, step):
            for y in range(0, self.height, step):
                # Check if the position is walkable and cache the result
                self.walkable_cache[(x, y)] = self._check_walkability(x, y)
        
        log(f"Walkability cache built with {len(self.walkable_cache)} entries")
    
    def _check_walkability(self, x, y):
        """Helper method to check if a position is walkable
        
        A position is unwalkable if:  
        1. It's outside the map bounds
        2. It collides with a collision rectangle object
        3. It's on a tile marked as unwalkable (has collides=True property or is in an unwalkable layer)
        """
        try:
            # Check if position is out of map bounds
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return False
            
            # If we don't have a valid TMX data object, use a simplified check
            if not hasattr(self, 'tmx_data') or self.tmx_data is None:
                # Create a margin for walkability (make edge non-walkable)
                margin = 50
                return margin < x < self.width - margin and margin < y < self.height - margin
            
            # Check collision with collision rectangles
            for rect in self.collision_rects:
                if rect.collidepoint(x, y):
                    return False
            
            # Convert pixel position to tile indices
            tile_x = int(x // self.tmx_data.tilewidth)
            tile_y = int(y // self.tmx_data.tileheight)
            
            # Check if the tile is in the unwalkable list
            # This list is populated with tiles that either:
            # 1. Have collides=True property in Tiled, or
            # 2. Are in a layer marked as unwalkable
            if (tile_x, tile_y) in self.unwalkable_tiles:
                return False
                
            # If we got here, position is walkable
            return True
        except Exception as e:
            print(f"[ERROR] TiledMap._check_walkability error: {str(e)}")
            # If there's an error, default to allowing movement
            return True
    
    def is_walkable(self, x, y):
        """Check if a position is walkable, using cache when possible"""
        try:
            # First, check if position is outside of map bounds
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return False
                
            # Use the cache if enabled for better performance
            if self.use_cache:
                # Round to nearest cached point if cache is enabled
                step = 8
                cache_x = round(x / step) * step
                cache_y = round(y / step) * step
                
                if (cache_x, cache_y) in self.walkable_cache:
                    return self.walkable_cache[(cache_x, cache_y)]
            
            # Otherwise, perform the actual check
            result = self._check_walkability(x, y)
            
            # Cache the result if caching is enabled
            if self.use_cache:
                step = 8
                cache_x = round(x / step) * step
                cache_y = round(y / step) * step
                self.walkable_cache[(cache_x, cache_y)] = result
                
            return result
        except Exception as e:
            print(f"[ERROR] TiledMap.is_walkable error: {str(e)}")
            # If there's an error, default to allowing movement (less frustrating for players)
            return True
            
    def get_spawn_positions(self, object_name="CustomerSpawn"):
        """Gets spawn positions for customers based on an object name"""
        # Match map-defined spawn points case-insensitively by spawn type
        spawn_points = []
        key_lower = object_name.lower()
        for spawn_type, positions in self.spawn_points.items():
            if key_lower in str(spawn_type).lower():
                print(f"[TiledMap] Found spawn type '{spawn_type}' with positions {positions}")
                for pos in positions:
                    if self.is_walkable(pos[0], pos[1]):
                        spawn_points.append(pos)
                    elif self.debug_mode:
                        print(f"[TiledMap] Spawn point at ({pos[0]}, {pos[1]}) not walkable")
                return spawn_points
        # Fallback to direct object scanning if none matched
        for obj_group in self.tmx_data.objectgroups:
            for obj in obj_group:
                name_lower = (obj.name or '').lower()
                group_lower = (obj_group.name or '').lower()
                if key_lower in name_lower or key_lower in group_lower:
                    pos = (obj.x, obj.y)
                    if self.is_walkable(pos[0], pos[1]):
                        spawn_points.append(pos)
                    elif self.debug_mode:
                        print(f"[TiledMap] Object spawn point at ({pos[0]}, {pos[1]}) not walkable")
        if spawn_points:
            return spawn_points
        # Final fallback: generate edge-based spawn points
        margin, step = 100, 50
        for x in range(margin, self.width - margin, step):
            if self.is_walkable(x, margin): spawn_points.append((x, margin))
            if self.is_walkable(x, self.height - margin): spawn_points.append((x, self.height - margin))
        for y in range(margin, self.height - margin, step):
            if self.is_walkable(margin, y): spawn_points.append((margin, y))
            if self.is_walkable(self.width - margin, y): spawn_points.append((self.width - margin, y))
        return spawn_points
    
    def draw(self, surface):
        """Draws the map to the specified surface"""
        surface.blit(self.map_surface, (0, 0))
    
    def draw_debug_spawn_points(self, surface, offset_x=0, offset_y=0):
        """Draw visual indicators for spawn points to help with debugging"""
        # Loop through all spawn point categories
        for spawn_type, positions in self.spawn_points.items():
            # Make sure spawn_type is a string before calling lower()
            spawn_type_str = str(spawn_type).lower() if spawn_type is not None else ''
        
        # Use different colors for different spawn types
        if 'customer' in spawn_type_str:
            color = (0, 255, 0)  # Green for customer spawns
        elif 'player' in spawn_type_str:
            color = (0, 0, 255)  # Blue for player spawns
        else:
            color = (255, 255, 0)  # Yellow for other spawns
        
        # Draw each spawn point with offset
        for pos in positions:
            # Apply offset to position
            draw_pos = (pos[0] + offset_x, pos[1] + offset_y)
            pygame.draw.circle(surface, color, draw_pos, 10, 2)  # Outline
            pygame.draw.circle(surface, color, draw_pos, 2)      # Center dot

def draw_debug_walkable(self, surface, offset_x=0, offset_y=0):
    """Draw walkable/unwalkable areas for debugging"""
    # Use a grid approach instead of checking every pixel
    grid_size = 20  # Check every 20 pixels
    rect_size = 5   # Size of the indicator squares
    
    for x in range(0, self.width, grid_size):
        for y in range(0, self.height, grid_size):
            # Apply offset to coordinates
            draw_x = x + offset_x
            draw_y = y + offset_y
            
            if self.is_walkable(x, y):
                # Draw green dot for walkable area
                pygame.draw.rect(surface, (0, 255, 0, 128), 
                               (draw_x - rect_size//2, draw_y - rect_size//2, rect_size, rect_size))
            else:
                # Draw red X for unwalkable area
                pygame.draw.line(surface, (255, 0, 0, 192), 
                               (draw_x - rect_size//2, draw_y - rect_size//2), 
                               (draw_x + rect_size//2, draw_y + rect_size//2), 2)
                pygame.draw.line(surface, (255, 0, 0, 192), 
                               (draw_x + rect_size//2, draw_y - rect_size//2), 
                               (draw_x - rect_size//2, draw_y + rect_size//2), 2)
