import pygame
import random
from src.core.constants import WIDTH, HEIGHT

class GameMap:
    """Represents the game world/level with tiles, obstacles, and spawn points.
    
    This class manages the game map including:
    - Background/terrain rendering
    - Collision detection with obstacles
    - Spawn points for customers and player
    - Path finding and navigation information
    """
    
    def __init__(self):
        # Basic initialization
        self.width = WIDTH
        self.height = HEIGHT
        
        # Define tile properties
        self.tile_size = 64  # Standard tile size in pixels
        self.cols = self.width // self.tile_size
        self.rows = self.height // self.tile_size
        
        # Create map grid (0 = empty/walkable, 1 = obstacle/wall)
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Add some random obstacles to the grid
        self._add_obstacles()
        
        # Define spawn points
        self._define_spawn_points()
        
        # Load textures
        self._load_textures()
    
    def _load_textures(self):
        """Load map textures (placeholder implementation)."""
        # In a full implementation, we would load actual textures
        # For now, we'll create simple colored surfaces
        self.floor_texture = pygame.Surface((self.tile_size, self.tile_size))
        self.floor_texture.fill((100, 100, 100))  # Dark gray floor
        
        self.wall_texture = pygame.Surface((self.tile_size, self.tile_size))
        self.wall_texture.fill((50, 50, 50))  # Darker gray wall
        
        self.spawn_texture = pygame.Surface((self.tile_size, self.tile_size))
        self.spawn_texture.fill((0, 100, 0))  # Green for spawn points
    
    def _add_obstacles(self):
        """Add obstacles to the map grid."""
        # Add border walls
        for x in range(self.cols):
            self.grid[0][x] = 1  # Top wall
            self.grid[self.rows-1][x] = 1  # Bottom wall
        
        for y in range(self.rows):
            self.grid[y][0] = 1  # Left wall
            self.grid[y][self.cols-1] = 1  # Right wall
        
        # Add some random obstacles (not too many in this basic version)
        num_obstacles = (self.cols * self.rows) // 20  # About 5% coverage
        
        for _ in range(num_obstacles):
            x = random.randint(2, self.cols-3)
            y = random.randint(2, self.rows-3)
            self.grid[y][x] = 1
    
    def _define_spawn_points(self):
        """Define customer and player spawn points."""
        # Find valid (non-obstacle) positions for spawning
        valid_positions = []
        
        # Check positions at least 2 tiles away from edges and obstacles
        for y in range(2, self.rows-2):
            for x in range(2, self.cols-2):
                if self.grid[y][x] == 0:  # If walkable
                    # Convert grid coordinates to pixel coordinates (center of tile)
                    px = x * self.tile_size + self.tile_size // 2
                    py = y * self.tile_size + self.tile_size // 2
                    valid_positions.append((px, py))
        
        # Ensure we have enough spawn points
        if len(valid_positions) < 5:
            # Fallback to predefined positions if not enough valid ones
            self.customer_spawn_points = [
                (100, 100), 
                (WIDTH - 100, 100),
                (WIDTH - 100, HEIGHT - 100),
                (100, HEIGHT - 100)
            ]
        else:
            # Use a subset of valid positions for customer spawns
            self.customer_spawn_points = random.sample(valid_positions, min(5, len(valid_positions)))
        
        # Player spawn point (center of map)
        self.player_spawn_point = (WIDTH // 2, HEIGHT // 2)
    
    def draw(self, screen):
        """Draw the map to the screen."""
        # Draw the map grid
        for y in range(self.rows):
            for x in range(self.cols):
                # Calculate pixel position
                px = x * self.tile_size
                py = y * self.tile_size
                
                # Draw the appropriate texture
                if self.grid[y][x] == 1:  # Wall/obstacle
                    screen.blit(self.wall_texture, (px, py))
                else:  # Floor/walkable
                    screen.blit(self.floor_texture, (px, py))
        
        # Optionally visualize spawn points (for debugging)
        for px, py in self.customer_spawn_points:
            # Draw a small indicator at spawn points
            pygame.draw.circle(screen, (0, 255, 0), (px, py), 5)
    
    def is_valid_position(self, x, y):
        """Check if a position is valid (within bounds and not an obstacle)."""
        # Convert pixel coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.cols or grid_y < 0 or grid_y >= self.rows:
            return False
        
        # Check for obstacles
        return self.grid[grid_y][grid_x] == 0
    
    def get_path(self, start_pos, end_pos):
        """Simple placeholder for pathfinding.
        In a full implementation, this would use A* or similar algorithm.
        """
        # This is a minimal implementation - in a real game, we'd implement proper pathfinding
        return [start_pos, end_pos]  # Direct path for now
