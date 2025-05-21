import pygame
import os
import random
from src.core.constants import *

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, food_type='pizza'):
        super().__init__()
        self.food_type = food_type
        
        # Food types and their corresponding image base names
        food_base_names = {
            'pizza': 'Tropical_Pizza_Slice',
            'smoothie': 'Ska_Smoothie',
            'icecream': 'Island_Ice_Cream',
            'pudding': 'Rasta_Rice_Pudding',
            'rasgulla': 'Reggae_Rasgulla'
        }
        
        # Maintain a class-level counter for cycling through food sprites
        if not hasattr(Food, 'cycle_counter'):
            Food.cycle_counter = {}
            
        # Try to load the food sprite with cycling through variants
        try:
            base_name = food_base_names.get(food_type, 'food')
            print(f"Loading food sprite for type: {food_type}, base name: {base_name}")
            
            # Initialize the cycle counter for this food type if it doesn't exist
            if food_type not in Food.cycle_counter:
                Food.cycle_counter[food_type] = 1
            else:
                # Cycle to the next number (1-5)
                Food.cycle_counter[food_type] = (Food.cycle_counter[food_type] % 5) + 1
            
            # Get the current cycle number for this food type
            cycle_num = Food.cycle_counter[food_type]
            
            # Try to load the corresponding numbered PNG
            self.image = None
            
            # Handle special cases with different naming patterns
            special_cases = {
                'Ska_Smoothie': 'Ska'  # For Ska_Smoothie, the files are just named Ska1.png, etc.
            }
            
            # Check if this food type has a special naming case
            file_prefix = special_cases.get(base_name, base_name)
            
            # First try with the special case name if applicable
            preferred_path = os.path.join(ASSETS_DIR, 'Food', base_name, f"{file_prefix}{cycle_num}.png")
            print(f"Trying to load cycle {cycle_num}: {preferred_path}")
            
            if os.path.exists(preferred_path):
                self.image = pygame.image.load(preferred_path).convert_alpha()
                print(f"Loaded food image: {file_prefix}{cycle_num}.png")
            else:
                # Fallback to other numbers and naming patterns if this one doesn't exist
                food_dir = os.path.join(ASSETS_DIR, 'Food', base_name)
                if os.path.isdir(food_dir):
                    # First try with special case naming
                    for i in range(1, 6):
                        alt_path = os.path.join(food_dir, f"{file_prefix}{i}.png")
                        if os.path.exists(alt_path):
                            self.image = pygame.image.load(alt_path).convert_alpha()
                            print(f"Loaded alternate food image: {file_prefix}{i}.png")
                            break
                        
                    # If still not found, try standard naming as a last resort
                    if not self.image and file_prefix != base_name:
                        alt_path = os.path.join(food_dir, f"{base_name}{cycle_num}.png")
                        if os.path.exists(alt_path):
                            self.image = pygame.image.load(alt_path).convert_alpha()
                            print(f"Loaded with standard name: {base_name}{cycle_num}.png")
            
            # If image was found, scale it to the appropriate size
            if self.image:
                self.image = pygame.transform.scale(self.image, (32, 32))  # Scale to appropriate size
            else:
                # If no image was found, raise an exception to trigger the fallback
                raise FileNotFoundError(f"Could not find food image for {food_type}")
        except Exception as e:
            print(f"Error loading food sprite: {e}")
            print("Using fallback food sprite")
            
            # Create a fallback food sprite (colored circle)
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            
            # Different colors for different food types
            if food_type == 'pizza':
                color = (255, 200, 0)  # Yellow
                pygame.draw.circle(self.image, color, (16, 16), 16)
                pygame.draw.polygon(self.image, (200, 0, 0), [(8, 8), (24, 8), (16, 24)])
            elif food_type == 'smoothie':
                color = (200, 0, 200)  # Purple
                pygame.draw.rect(self.image, color, (8, 4, 16, 24))
                pygame.draw.circle(self.image, (255, 255, 255), (16, 6), 6)
            elif food_type == 'icecream':
                color = (200, 255, 255)  # Light blue
                pygame.draw.polygon(self.image, (240, 220, 180), [(8, 28), (24, 28), (16, 10)])
                pygame.draw.circle(self.image, color, (16, 8), 8)
            elif food_type == 'pudding':
                color = (240, 220, 180)  # Tan
                pygame.draw.ellipse(self.image, color, (4, 8, 24, 16))
                pygame.draw.circle(self.image, (150, 50, 0), (16, 16), 4)
            else:
                color = (255, 0, 0)  # Default red
                pygame.draw.circle(self.image, color, (16, 16), 16)
        
        # Set up the food rectangle
        self.rect = self.image.get_rect(center=(x, y))
        
        # Velocity components (in pixels per frame)
        self.direction = pygame.math.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        
        # Speed multiplier
        self.speed = 300  # pixels per second
        
        # Lifespan (despawn after a few seconds)
        self.lifespan = 2.0  # seconds
        self.timer = 0
    
    def update(self, dt):
        # Move the food
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        
        # Update timer and check lifespan
        self.timer += dt
        if self.timer >= self.lifespan:
            self.kill()
        
        # Despawn if out of screen bounds
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()
    
    @staticmethod
    def reset_counters():
        """Reset the cycling counters - useful when starting a new game"""
        Food.cycle_counter = {}
