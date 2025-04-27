import pygame
import sys
import random
import os
from pygame import mixer

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

# Initialize Pygame and audio
pygame.init()
mixer.init()

# Window setup
WIDTH, HEIGHT = 768, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jammin' Eats")
clock = pygame.time.Clock()
FPS = 60

# Font setup (requires pygame.init())
font = pygame.font.Font(None, 36)

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

# Class to load and render Tiled maps
class TiledMap:
    def __init__(self, tmx_path):
        loader = ResourceLoader(os.path.dirname(tmx_path))
        self.tmx_data = load_pygame(tmx_path, image_loader=loader.load)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._render_layers()

    def _render_layers(self):
        from pytmx import TiledTileLayer
        order = ["sky","clouds","ocean","grass","sand","sidewalk","road","interactables"]
        for name in order:
            for layer in self.tmx_data.visible_layers:
                if hasattr(layer, 'name') and layer.name.lower() == name:
                    if isinstance(layer, TiledTileLayer):
                        for x, y, gid in layer:
                            if gid:
                                tile = self.tmx_data.get_tile_image_by_gid(gid)
                                if tile:
                                    px = x * self.tmx_data.tilewidth
                                    py = y * self.tmx_data.tileheight
                                    self.surface.blit(tile, (px, py))
                    break

    def draw(self, target):
        target.blit(self.surface, (0, 0))

# --- Copy your Player, Customer, Food, Particle, Button classes here, unchanged ---
# Make sure any file loads use ASSETS_DIR and os.path.join
# e.g., pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'characters', 'kai', 'kai_up.png'))

# Main game loop
def main():
    # Create a fallback background
    fallback_background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(200 * (1 - y / HEIGHT))
        color = (0, color_value, color_value + 55)
        pygame.draw.line(fallback_background, color, (0, y), (WIDTH, y))
    
    # Load TMX map
    tmx_file = os.path.join(MAP_DIR, "Level_1_Frame_1.tmx")
    print(f"Looking for map at: {tmx_file}")
    
    # Also try looking in the root directory
    if not os.path.exists(tmx_file):
        alt_path = os.path.join(BASE_DIR, "Level_1_Frame_1.tmx")
        if os.path.exists(alt_path):
            tmx_file = alt_path
            print(f"Found map in root directory: {tmx_file}")
    
    game_map = None
    if os.path.exists(tmx_file):
        try:
            game_map = TiledMap(tmx_file)
            print(f"Map loaded from {tmx_file}")
        except Exception as e:
            print(f"Error loading map: {e}")
            game_map = None
    else:
        print(f"Map not found: {tmx_file}")
        game_map = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Draw the map or fallback background
        if game_map:
            game_map.draw(screen)
        else:
            screen.blit(fallback_background, (0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Map failed to load - using fallback", True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))
        
        # Draw any additional game elements here
        # (sprites, HUD, UI, etc.)
        
        # Update the display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
