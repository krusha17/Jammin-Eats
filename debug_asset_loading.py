import os
import sys
import pygame

# Initialize pygame
pygame.init()
pygame.display.set_mode((100, 100))

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {BASE_DIR}")
sys.path.insert(0, BASE_DIR)

# Import from src directory
from src.core.constants import ASSETS_DIR, MAP_DIR

# Basic asset tests
def test_directory(path, name):
    print(f"\n--- Testing {name} directory ---")
    print(f"Path: {path}")
    print(f"Exists: {os.path.exists(path)}")
    if os.path.exists(path):
        print(f"Contents: {os.listdir(path)}")
    else:
        print("Directory not found!")

def test_asset_loading(asset_path, asset_type):
    print(f"\n--- Testing {asset_type} loading ---")
    print(f"Path: {asset_path}")
    print(f"Exists: {os.path.exists(asset_path)}")
    
    if os.path.exists(asset_path):
        if asset_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            try:
                image = pygame.image.load(asset_path).convert_alpha()
                print(f"Successfully loaded image. Size: {image.get_size()}")
            except Exception as e:
                print(f"Failed to load image: {e}")
        elif asset_path.lower().endswith(('.wav', '.mp3', '.ogg')):
            try:
                sound = pygame.mixer.Sound(asset_path)
                print(f"Successfully loaded sound.")
            except Exception as e:
                print(f"Failed to load sound: {e}")
        elif asset_path.lower().endswith('.tmx'):
            print("TMX file found, attempting to load with pytmx")
            try:
                import pytmx
                from pytmx.util_pygame import load_pygame
                
                # Create a simple ResourceLoader for testing
                class ResourceLoader:
                    def __init__(self, base_path):
                        self.base_path = base_path
                        
                    def load(self, filename, **_):
                        print(f"ResourceLoader attempting to load: {filename}")
                        candidates = [
                            os.path.join(self.base_path, filename),
                            os.path.join(ASSETS_DIR, "tilesets", os.path.basename(filename)),
                            os.path.join(ASSETS_DIR, "tiles", os.path.basename(filename)),
                            filename
                        ]
                        
                        for path in candidates:
                            print(f"Trying path: {path} (Exists: {os.path.exists(path)})")
                            if os.path.exists(path):
                                try:
                                    img = pygame.image.load(path).convert_alpha()
                                    print(f"Successfully loaded tileset from {path}")
                                    return img
                                except Exception as e:
                                    print(f"Error loading from {path}: {e}")
                        
                        print(f"Failed to load resource: {filename}")
                        fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
                        fallback.fill((255, 0, 255))
                        return fallback
                
                # Try to load the TMX
                loader = ResourceLoader(os.path.dirname(asset_path))
                tmx_data = load_pygame(asset_path, image_loader=loader.load)
                print(f"Successfully loaded TMX map: {tmx_data.width}x{tmx_data.height} tiles")
                print(f"Layers: {[l.name for l in tmx_data.visible_layers]}")
            except Exception as e:
                import traceback
                print(f"Failed to load TMX: {e}")
                traceback.print_exc()
    else:
        print("File does not exist!")

# Test basic directories
test_directory(BASE_DIR, "Base")
test_directory(ASSETS_DIR, "Assets")
test_directory(MAP_DIR, "Map")
test_directory(os.path.join(ASSETS_DIR, "tilesets"), "Tilesets")
test_directory(os.path.join(ASSETS_DIR, "sprites"), "Sprites")

# Test specific assets
map_file = os.path.join(MAP_DIR, "Level_1_Frame_1.tmx")
test_asset_loading(map_file, "Map")

# Test a tileset directly
tileset_file = os.path.join(ASSETS_DIR, "tilesets", "TileSet_1.png")
test_asset_loading(tileset_file, "Tileset")

# Test player sprite
player_sprite = os.path.join(ASSETS_DIR, "sprites", "characters", "kai", "kai_down.png")
test_asset_loading(player_sprite, "Player sprite")

print("\nAsset loading test completed.")
