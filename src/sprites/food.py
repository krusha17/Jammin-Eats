import pygame
import os
import random
import math
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
            
            # Only change the cycle counter every 5th time a food is created
            if not hasattr(Food, 'throw_counter'):
                Food.throw_counter = {}
            
            if food_type not in Food.throw_counter:
                Food.throw_counter[food_type] = 0
                
            # Increment throw counter
            Food.throw_counter[food_type] = (Food.throw_counter[food_type] + 1) % 5
            
            # Only cycle animation when throw counter hits 0
            if Food.throw_counter[food_type] == 0:
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
        
        # List to hold animation frames for this food instance
        self.frames = []
        # Track current animation frame index
        self.current_frame = 0
        # Track timer for determining animation progression
        self.frame_timer = 0.0
        
        # Attempt to load up to 5 numbered frames for smooth animation
        base_dir = os.path.join(ASSETS_DIR, 'Food', base_name)
        if os.path.isdir(base_dir):
            for i in range(1, 6):
                frame_path = os.path.join(base_dir, f"{file_prefix}{i}.png")
                if os.path.exists(frame_path):
                    frame_surf = pygame.image.load(frame_path).convert_alpha()
                    frame_surf = pygame.transform.scale(frame_surf, (32, 32))
                    self.frames.append(frame_surf)
        # If no specific frames found, fall back to repeating the primary image
        if not self.frames:
            self.frames = [self.image] * 5
        
        # Ensure current image matches first frame
        self.image = self.frames[0]
        
        # Set up the food rectangle
        self.rect = self.image.get_rect(center=(x, y))
        
        # Store starting position to gauge travel progress (for animation pacing)
        self.start_pos = pygame.math.Vector2(x, y)
        
        # Velocity components (in pixels per frame)
        self.direction = pygame.math.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        
        # Speed multiplier
        self.speed = 300  # pixels per second
        
        # Lifespan (despawn after a few seconds)
        self.lifespan = 2.0  # seconds
        self.timer = 0
        
        # Set up collision radius for more accurate hit detection
        self.collision_radius = 12  # Smaller than the sprite's visual size for tighter collisions
    
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
        
        # Determine animation frame based on progress towards lifespan
        if len(self.frames) > 1:
            progress_ratio = min(self.timer / self.lifespan, 1.0)
            target_index = int(progress_ratio * (len(self.frames) - 1))
            if target_index != self.current_frame:
                self.current_frame = target_index
                current_center = self.rect.center  # preserve position when image size differs
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(center=current_center)
    
    def collides_with(self, other_sprite):
        """Better collision detection using circular hitboxes instead of rectangles"""
        # Calculate distance between centers
        dx = self.rect.centerx - other_sprite.rect.centerx
        dy = self.rect.centery - other_sprite.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        # For the other sprite, use a reasonable collision radius if not defined
        other_radius = getattr(other_sprite, 'collision_radius', 20)  # Default to 20px if not defined
        
        # Return True if the distance is less than the sum of the two collision radii
        return distance < (self.collision_radius + other_radius)
    
    @staticmethod
    def reset_counters():
        """Reset the cycling counters - useful when starting a new game"""
        Food.cycle_counter = {}
    
    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw the food with the specified offset"""
        # Calculate adjusted position with offset
        draw_x = self.rect.x + offset_x
        draw_y = self.rect.y + offset_y
        
        # Draw at the adjusted position
        surface.blit(self.image, (draw_x, draw_y))
