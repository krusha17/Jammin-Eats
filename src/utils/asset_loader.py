import os
import pygame
from pygame import mixer
from src.core.constants import BASE_DIR, ASSETS_DIR

# Define paths for different asset types based on the existing structure
def get_asset_path(asset_type, asset_name):
    """Get the correct path for various asset types based on the existing folder structure"""
    
    # Map the asset types to their correct directories in the existing structure
    if asset_type == 'player' or asset_type.startswith('sprites/characters/kai'):
        # Handle both old 'player' type and direct path requests
        base_dir = ASSETS_DIR
        
        # Extract actual filename - handle both formats
        filename = asset_name
        if asset_type.startswith('sprites/'):
            # If asset_type already includes part of the path
            dir_path = asset_type
            paths = [os.path.join(base_dir, dir_path, filename)]
        else:
            # Traditional 'player' type with different naming conventions
            if asset_name.startswith('down_') or asset_name == 'down.png':
                paths = [os.path.join(base_dir, 'sprites', 'characters', 'kai', 'kai_down.png')]
            elif asset_name.startswith('up_') or asset_name == 'up.png':
                paths = [os.path.join(base_dir, 'sprites', 'characters', 'kai', 'kai_up.png')]
            elif asset_name.startswith('left_') or asset_name == 'left.png':
                paths = [os.path.join(base_dir, 'sprites', 'characters', 'kai', 'kai_left.png')]
            elif asset_name.startswith('right_') or asset_name == 'right.png':
                paths = [os.path.join(base_dir, 'sprites', 'characters', 'kai', 'kai_right.png')]
            else:
                # Try all possible player sprite locations
                paths = [
                    os.path.join(base_dir, 'sprites', 'characters', 'kai', asset_name),
                    os.path.join(base_dir, 'sprites', 'characters', 'kai', f'kai_{asset_name}'),
                ]
    elif asset_type == 'food' or asset_type.startswith('food/'):
        # Handle food sprites with multiple potential structures
        base_dir = ASSETS_DIR
        
        # Extract food type from asset_name or asset_type
        food_name = asset_name
        food_type = None
        
        # If the asset_type already includes the food type (food/Type)
        if '/' in asset_type:
            parts = asset_type.split('/')
            if len(parts) > 1:
                food_type = parts[1]
        
        # Otherwise determine from asset name
        if not food_type:
            if 'pizza' in asset_name.lower():
                food_type = 'Tropical_Pizza_Slice'
            elif 'smoothie' in asset_name.lower():
                food_type = 'Ska_Smoothie'
            elif 'icecream' in asset_name.lower() or 'ice_cream' in asset_name.lower():
                food_type = 'Island_Ice_Cream'
            elif 'pudding' in asset_name.lower() or 'rice' in asset_name.lower():
                food_type = 'Rasta_Rice_Pudding'
            elif 'rasgulla' in asset_name.lower() or 'reggae' in asset_name.lower():
                food_type = 'Reggae_Rasgulla'
        
        # Try various possible paths, from most specific to most general
        paths = []
        
        # 1. Check direct paths first
        paths.append(os.path.join(base_dir, 'food', food_name))
        
        # 2. Check specific food type directories
        if food_type:
            paths.extend([
                # Check in food type subdirectory
                os.path.join(base_dir, 'Food', food_type, f"{food_type}.png"),
                os.path.join(base_dir, 'Food', food_type, food_name),
                # Check directly in Food directory
                os.path.join(base_dir, 'Food', f"{food_type}.png"),
                # Check in lowercase naming conventions
                os.path.join(base_dir, 'food', food_type.lower(), f"{food_type}.png"),
                os.path.join(base_dir, 'food', food_type.lower(), food_name),
            ])
        
        # 3. Finally, try searching all food directories
        for dir_name in ['Tropical_Pizza_Slice', 'Ska_Smoothie', 'Island_Ice_Cream', 'Rasta_Rice_Pudding', 'Reggae_Rasgulla']:
            paths.append(os.path.join(base_dir, 'Food', dir_name, f"{dir_name}.png"))
            paths.append(os.path.join(base_dir, 'Food', dir_name, food_name))
    elif asset_type == 'customer':
        # Handle customer sprites with special mapping
        # Convert from logical states to file naming
        
        # Parse the customer type (e.g., 'lady_1', 'man_3') from asset_name
        customer_type = None
        state = None
        
        if '_' in asset_name:
            parts = asset_name.split('_')
            gender = parts[0].lower()  # 'lady' or 'man'
            
            # Check for valid gender type
            if gender in ['lady', 'man'] and len(parts) >= 2:
                # Try to get the customer number
                try:
                    number = parts[1]
                    # If it's just a digit, add it to the gender
                    if number.isdigit():
                        customer_type = f"{gender}_{number}"
                    else:
                        # It might be 'idle', 'happy', 'angry', etc.
                        customer_type = f"{gender}_1"  # Default to 1
                        state = parts[1]
                except (IndexError, ValueError):
                    customer_type = f"{gender}_1"  # Default to first customer
            
            # If we have more parts, it might include the state (idle, happy, angry)
            if not state and len(parts) >= 3:
                state = parts[2]
        
        # Fallback if we couldn't determine type or state
        if not customer_type:
            customer_type = "man_1"  # Default
        
        if not state:
            state = "idle"  # Default
        
        # Convert customer type to proper filename format
        gender, number = customer_type.split('_')
        base_name = f"Customer_{gender.capitalize()}_{number}"
        
        # Map states to directions for the customer sprite images
        if state == 'idle' or 'idle' in asset_name.lower():
            direction = 'down'  # For idle, use the regular down-facing sprite
        elif state == 'happy' or 'happy' in asset_name.lower():
            direction = 'up'    # For happy, use the up-facing sprite (smiling)
        elif state == 'angry' or 'angry' in asset_name.lower():
            direction = 'left'  # For angry, use the left-facing sprite
        else:
            direction = 'down'  # Default direction
        
        # Form the complete filename
        customer_filename = f"{base_name}_{direction}.png"
        
        print(f"Looking for customer sprite: {customer_filename} (from {asset_name})")
        
        paths = [
            os.path.join(ASSETS_DIR, 'sprites', 'characters', 'Customers', customer_filename),
            # Try alternate direction if available
            os.path.join(ASSETS_DIR, 'sprites', 'characters', 'Customers', f"{base_name}_right.png"),
            # Try the original asset name as fallback
            os.path.join(ASSETS_DIR, 'sprites', 'characters', 'Customers', asset_name),
        ]
    elif asset_type == 'sound':
        # Check in sounds directory and its subdirectories
        paths = [
            os.path.join(ASSETS_DIR, 'sounds', asset_name),
            os.path.join(ASSETS_DIR, 'music', asset_name),
            os.path.join(BASE_DIR, 'sounds', asset_name),
        ]
    elif asset_type == 'map':
        # Check in Maps directory
        paths = [
            os.path.join(ASSETS_DIR, 'Maps', 'level1', asset_name),
            os.path.join(ASSETS_DIR, 'Maps', asset_name),
        ]
    elif asset_type == 'tileset':
        # Check in tilesets and tiles directories
        paths = [
            os.path.join(ASSETS_DIR, 'tilesets', asset_name),
            os.path.join(ASSETS_DIR, 'tiles', asset_name),
            os.path.join(BASE_DIR, asset_name),  # Also check root directory
        ]
    else:
        # Generic asset path
        paths = [
            os.path.join(ASSETS_DIR, asset_name),
            os.path.join(BASE_DIR, asset_name),
        ]
    
    # Try each path
    for path in paths:
        if os.path.exists(path):
            return path
    
    # If not found, return None
    return None

def load_image(asset_type, asset_name, fallback_color=(255, 0, 255)):
    """Load an image with proper error handling and fallbacks"""
    path = get_asset_path(asset_type, asset_name)
    
    # Debugging information to help track asset loading
    if path:
        try:
            print(f"Loading image from: {path}")
            image = pygame.image.load(path).convert_alpha()
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
    else:
        # Try one more direct attempt by combining asset_type and asset_name
        # This is useful when asset_type contains part of the path
        if '/' in asset_type:
            direct_path = os.path.join(ASSETS_DIR, asset_type, asset_name)
            if os.path.exists(direct_path):
                try:
                    print(f"Loading image from direct path: {direct_path}")
                    return pygame.image.load(direct_path).convert_alpha()
                except pygame.error as e:
                    print(f"Error loading image from direct path {direct_path}: {e}")
        
        print(f"Image not found: {asset_type}/{asset_name}")
    
    # Create a fallback image
    size = (32, 32)
    fallback = pygame.Surface(size, pygame.SRCALPHA)
    
    # Simple colored rectangle with a letter indicating the asset type
    fallback.fill(fallback_color)
    font = pygame.font.Font(None, 24)
    
    # Get a short identifier for the asset_type
    identifier = asset_type.split('/')[-1][0].upper() if '/' in asset_type else asset_type[0].upper()
    text = font.render(identifier, True, (255, 255, 255))
    text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
    fallback.blit(text, text_rect)
    
    return fallback

def load_sound(sound_name):
    """Load a sound with proper error handling"""
    path = get_asset_path('sound', sound_name)
    
    if path and os.path.exists(path):
        try:
            return mixer.Sound(path)
        except pygame.error as e:
            print(f"Error loading sound {path}: {e}")
    
    # Return None if sound can't be loaded
    return None
