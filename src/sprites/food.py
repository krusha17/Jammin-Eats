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
            'pizza': 'tropical_pizza',
            'smoothie': 'ska_smoothie',
            'icecream': 'island_ice_cream',
            'pudding': 'rasta_rice_pudding'
        }
        
        # Try to load the food sprite
        try:
            base_name = food_base_names.get(food_type, 'food')
            self.image = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'food', f'{base_name}.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))  # Scale to appropriate size
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
