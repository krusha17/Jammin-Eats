import pygame
import math
import os
from pygame import mixer
from src.core.constants import *
from src.sprites.food import Food

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load directional sprites with error handling
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'idle': []
        }
        
        try:
            # Try to load player sprites from the assets directory
            for i in range(1, 5):  # Assuming 4 frames per direction
                # Down animation
                img_down = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'player', f'down_{i}.png')).convert_alpha()
                self.animations['down'].append(img_down)
                
                # Up animation
                img_up = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'player', f'up_{i}.png')).convert_alpha()
                self.animations['up'].append(img_up)
                
                # Left animation
                img_left = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'player', f'left_{i}.png')).convert_alpha()
                self.animations['left'].append(img_left)
                
                # Right animation
                img_right = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'player', f'right_{i}.png')).convert_alpha()
                self.animations['right'].append(img_right)
            
            # Add idle animation
            self.animations['idle'] = [self.animations['down'][0]]  # Just use first frame of down as idle
        except Exception as e:
            # If sprite loading fails, create simple geometric fallback
            print(f"Error loading player sprites: {e}")
            print("Using fallback player sprite")
            
            # Create a simple geometric player sprite
            for direction in ['up', 'down', 'left', 'right', 'idle']:
                fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
                
                # Draw the player avatar (a circle with a direction indicator)
                pygame.draw.circle(fallback, BLUE, (16, 16), 15)
                
                # Add direction indicator
                if direction == 'up':
                    pygame.draw.polygon(fallback, WHITE, [(16, 5), (20, 15), (12, 15)])
                elif direction == 'down':
                    pygame.draw.polygon(fallback, WHITE, [(16, 27), (20, 17), (12, 17)])
                elif direction == 'left':
                    pygame.draw.polygon(fallback, WHITE, [(5, 16), (15, 20), (15, 12)])
                elif direction == 'right':
                    pygame.draw.polygon(fallback, WHITE, [(27, 16), (17, 20), (17, 12)])
                
                # Add the fallback sprite to the animations
                self.animations[direction].append(fallback)
        
        # Initialize animation variables
        self.direction = 'down'  # Starting direction
        self.frame_index = 0
        self.animation_speed = 0.2  # seconds per frame
        self.animation_timer = 0
        
        # Set up player rectangle and initial image
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
        # Player stats
        self.speed = 200  # pixels per second
        self.deliveries = 0
        self.missed_deliveries = 0
        self.food_inventory = 99  # Unlimited for now
        
        # Food throwing cooldown
        self.throw_cooldown = 0.2  # seconds
        self.last_throw_time = 0
    
    def update(self, dt, customers, foods, game_map=None):
        # Handle player movement
        self.handle_movement(dt, game_map)
        
        # Update animation
        self.update_animation(dt)
        
        # Check for key presses to throw food
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Check throw cooldown
        if current_time - self.last_throw_time >= self.throw_cooldown:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.throw_food(foods, 'up')
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.throw_food(foods, 'down')
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.throw_food(foods, 'left')
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.throw_food(foods, 'right')
    
    def handle_movement(self, dt, game_map=None):
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        
        # Calculate movement direction
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -1
            self.direction = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = 1
            self.direction = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y = -1
            self.direction = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y = 1
            self.direction = 'down'
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            # Pythagorean theorem to normalize movement speed on diagonals
            move_x /= math.sqrt(2)
            move_y /= math.sqrt(2)
        
        # Apply movement speed
        dx = move_x * self.speed * dt
        dy = move_y * self.speed * dt
        
        # Boundary checking
        new_x = self.rect.centerx + dx
        new_y = self.rect.centery + dy
        
        # Check map boundaries and collisions
        if 0 <= new_x <= WIDTH and 0 <= new_y <= HEIGHT:
            # Check walkability if map exists
            if game_map:
                # Try moving on X axis
                if game_map.is_walkable(new_x, self.rect.centery):
                    self.rect.centerx = new_x
                
                # Try moving on Y axis
                if game_map.is_walkable(self.rect.centerx, new_y):
                    self.rect.centery = new_y
            else:
                # No map, just move within screen bounds
                self.rect.centerx = new_x
                self.rect.centery = new_y
    
    def update_animation(self, dt):
        # If not moving, use idle animation
        keys = pygame.key.get_pressed()
        is_moving = (
            keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or 
            keys[pygame.K_UP] or keys[pygame.K_DOWN] or
            keys[pygame.K_a] or keys[pygame.K_d] or 
            keys[pygame.K_w] or keys[pygame.K_s]
        )
        
        if not is_moving:
            current_direction = 'idle'
        else:
            current_direction = self.direction
        
        # Update animation frame
        if is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[current_direction])
        
        # Update image
        self.image = self.animations[current_direction][self.frame_index]
    
    def throw_food(self, foods, direction=None):
        # If no direction specified, use player's current direction
        if direction is None:
            direction = self.direction
        
        # Set velocity based on direction
        if direction == 'up':
            dx, dy = 0, -7
        elif direction == 'down':
            dx, dy = 0, 7
        elif direction == 'left':
            dx, dy = -7, 0
        elif direction == 'right':
            dx, dy = 7, 0
        else:
            return  # Invalid direction
        
        # Randomly choose a food type (for variety)
        food_choices = ['pizza', 'smoothie', 'icecream', 'pudding']
        food_type = food_choices[pygame.time.get_ticks() % len(food_choices)]
        
        # Create the food object
        food = Food(self.rect.centerx, self.rect.centery, dx, dy, food_type)
        foods.add(food)
        
        # Update throw cooldown
        self.last_throw_time = pygame.time.get_ticks() / 1000.0
    
    def draw_stats(self, surface):
        # Draw player stats (deliveries, missed)
        font = pygame.font.Font(None, 24)
        deliveries_text = font.render(f"Deliveries: {self.deliveries}", True, WHITE)
        surface.blit(deliveries_text, (10, 10))
        
        missed_text = font.render(f"Missed: {self.missed_deliveries}/10", True, WHITE)
        surface.blit(missed_text, (10, 40))
        
        # Draw a simple health/warning bar based on missed deliveries
        warning_width = 150 * (self.missed_deliveries / 10.0)
        pygame.draw.rect(surface, (100, 100, 100), (10, 70, 150, 15))
        pygame.draw.rect(surface, (255, 50, 50), (10, 70, warning_width, 15))
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
