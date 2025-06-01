import pygame
import os
import random
from src.core.constants import *

class Customer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        print(f"Initializing Customer at position: {x}, {y}")
        
        # Initialize customer state variables
        self.fed = False
        self.leaving = False
        self.patience_timer = 0
        self.leave_timer = 0
        self.patience = random.uniform(20, 30)  # Seconds before customer leaves
        self.state = 'idle'
        
        # Customer types for random selection
        customer_types = [
            # Ladies
            {
                'type': 'lady_1',
                'sprites': {
                    'idle': ['lady_1_idle.png'],
                    'happy': ['lady_1_happy.png'],
                    'angry': ['lady_1_angry.png']
                }
            },
            {
                'type': 'lady_2',
                'sprites': {
                    'idle': ['lady_2_idle.png'],
                    'happy': ['lady_2_happy.png'],
                    'angry': ['lady_2_angry.png']
                }
            },
            {
                'type': 'lady_3',
                'sprites': {
                    'idle': ['lady_3_idle.png'],
                    'happy': ['lady_3_happy.png'],
                    'angry': ['lady_3_angry.png']
                }
            },
            {
                'type': 'lady_4',
                'sprites': {
                    'idle': ['lady_4_idle.png'],
                    'happy': ['lady_4_happy.png'],
                    'angry': ['lady_4_angry.png']
                }
            },
            # Men
            {
                'type': 'man_1',
                'sprites': {
                    'idle': ['man_1_idle.png'],
                    'happy': ['man_1_happy.png'],
                    'angry': ['man_1_angry.png']
                }
            },
            {
                'type': 'man_2',
                'sprites': {
                    'idle': ['man_2_idle.png'],
                    'happy': ['man_2_happy.png'],
                    'angry': ['man_2_angry.png']
                }
            },
            {
                'type': 'man_3',
                'sprites': {
                    'idle': ['man_3_idle.png'],
                    'happy': ['man_3_happy.png'],
                    'angry': ['man_3_angry.png']
                }
            },
            {
                'type': 'man_4',
                'sprites': {
                    'idle': ['man_4_idle.png'],
                    'happy': ['man_4_happy.png'],
                    'angry': ['man_4_angry.png']
                }
            }
        ]
        
        # Safely select a customer type (with fallback)
        if customer_types:
            self.customer_info = random.choice(customer_types)
            self.type = self.customer_info['type']
        else:
            # Fallback if list is empty
            print("WARNING: No customer types defined, using fallback")
            self.customer_info = {
                'type': 'default',
                'sprites': {
                    'idle': ['default_idle.png'],
                    'happy': ['default_happy.png'],
                    'angry': ['default_angry.png']
                }
            }
            self.type = 'default'
        
        # Create sprites dictionary
        self.sprites = {'idle': None, 'happy': None, 'angry': None}
        
        # Create fallback sprites for each state
        for state in ['idle', 'happy', 'angry']:
            fallback = pygame.Surface((48, 64), pygame.SRCALPHA)
            
            # Base customer shape with different colors for different states
            if state == 'idle':
                color = (0, 150, 200)  # Blue for idle
            elif state == 'happy':
                color = (0, 200, 0)    # Green for happy
            elif state == 'angry':
                color = (200, 0, 0)    # Red for angry
            
            # Draw a simple humanoid figure
            pygame.draw.ellipse(fallback, color, (12, 12, 24, 24))  # Head
            pygame.draw.rect(fallback, color, (16, 36, 16, 20))      # Body
            
            # Draw limbs
            pygame.draw.line(fallback, color, (16, 40), (8, 55), 3)   # Left arm
            pygame.draw.line(fallback, color, (32, 40), (40, 55), 3)  # Right arm
            pygame.draw.line(fallback, color, (20, 56), (12, 64), 3)  # Left leg
            pygame.draw.line(fallback, color, (28, 56), (36, 64), 3)  # Right leg
            
            # Store the fallback sprite
            self.sprites[state] = fallback
        
        # Now try to load the actual sprites
        try:
            # Import the asset loader here to avoid circular imports
            from src.utils.asset_loader import load_image
            
            # Load customer sprites using our asset loader
            for state, filenames in self.customer_info['sprites'].items():
                if filenames and isinstance(filenames, list) and len(filenames) > 0:
                    img = load_image('customer', filenames[0])
                    if img:  # Only replace fallback if successful
                        self.sprites[state] = img
            
            print(f"Successfully loaded customer sprites for {self.type}")
        except Exception as e:
            print(f"Keeping fallback customer sprites due to error: {e}")
        
        # Set up the initial sprite and position
        self.image = self.sprites[self.state]
        self.rect = self.image.get_rect(center=(x, y))
        self.collision_radius = 25  # For collision detection with food
        
        # Choose food preference and build bubble
        food_types = ['pizza', 'smoothie', 'icecream', 'pudding', 'rasgulla']
        self.food_preference = random.choice(food_types)
        print(f"[DEBUG] Customer {self.type} wants {self.food_preference}")

        # Speech bubble creation
        self.bubble = pygame.Surface((80, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(self.bubble, (255, 255, 255), (0, 0, 80, 50))
        pygame.draw.polygon(self.bubble, (255, 255, 255), [(10, 50), (30, 50), (20, 60)])

        # Load the food icon for the bubble
        try:
            from src.utils.asset_loader import load_image
            # Map preference to asset folder name
            food_map = {
                'pizza': 'Tropical_Pizza_Slice',
                'smoothie': 'Ska_Smoothie',
                'icecream': 'Island_Ice_Cream',
                'pudding': 'Rasta_Rice_Pudding',
                'rasgulla': 'Reggae_Rasgulla'
            }
            base_name = food_map.get(self.food_preference, self.food_preference)
            # Attempt specific then generic
            self.food_image = load_image(f'food/{base_name}', f'{base_name}1.png') or load_image('food', f'{base_name}1.png')
            if self.food_image:
                self.food_image = pygame.transform.scale(self.food_image, (32, 32))
                self.bubble.blit(self.food_image, (24, 8))
                print(f"[DEBUG] Loaded food icon for {self.food_preference}")
            else:
                print(f"[DEBUG] Icon missing, using fallback for {self.food_preference}")
                self._draw_fallback_food_icon()
        except Exception as e:
            print(f"[DEBUG] Error loading food icon: {e}")
            self._draw_fallback_food_icon()
        self.leave_timer = 0
    
    def greet(self):
        # Optional: Play a greeting sound or animation
        pass
    
    def feed(self, food_type):
        # Check if this is the food they want
        if food_type == self.food_preference:
            print(f"[DEBUG] Customer {self.type} received correct food {food_type}!")
            self.fed = True
            self.state = 'happy'
            self.image = self.sprites[self.state]
            # Start leaving after being fed, but with a small delay
            # We'll set a timer and use it in the update method
            self.satisfaction_timer = 0  # Will count up to show satisfaction before leaving
            self.satisfaction_delay = 1.0  # 1 second of visible happiness before leaving
        else:
            # Wrong food, get angry but don't leave yet
            print(f"[DEBUG] Customer {self.type} received wrong food! Wanted {self.food_preference}, got {food_type}")
            self.state = 'angry'
            self.image = self.sprites[self.state]
    
    def _draw_fallback_food_icon(self):
        """Draw a simple shape-based food icon when the sprite can't be loaded"""
        if self.food_preference == 'pizza':
            pygame.draw.polygon(self.bubble, (255, 200, 0), [(40, 10), (60, 30), (20, 30)])
        elif self.food_preference == 'smoothie':
            pygame.draw.rect(self.bubble, (200, 0, 200), (30, 10, 20, 30))
            pygame.draw.circle(self.bubble, (255, 255, 255), (40, 15), 8)
        elif self.food_preference == 'icecream':
            pygame.draw.polygon(self.bubble, (240, 220, 180), [(30, 35), (50, 35), (40, 15)])
            pygame.draw.circle(self.bubble, (200, 255, 255), (40, 15), 10)
        elif self.food_preference == 'pudding':
            pygame.draw.ellipse(self.bubble, (240, 220, 180), (25, 15, 30, 20))
            pygame.draw.circle(self.bubble, (150, 50, 0), (40, 25), 5)
        else:
            # Generic food icon for unknown types
            pygame.draw.circle(self.bubble, (150, 150, 150), (40, 25), 15)
    
    def update(self, dt):
        # Update patience timer if not fed
        if not self.fed and not self.leaving:
            self.patience_timer += dt
            # Change to angry state when patience is running low
            if self.patience_timer > self.patience * 0.7 and self.state != 'angry':
                self.state = 'angry'
                self.image = self.sprites[self.state]
            
            # Leave if patience runs out
            if self.patience_timer >= self.patience:
                self.leaving = True
        
        # If fed but not yet leaving, update satisfaction timer
        if self.fed and not self.leaving and hasattr(self, 'satisfaction_timer'):
            self.satisfaction_timer += dt
            if self.satisfaction_timer >= self.satisfaction_delay:
                print(f"[DEBUG] Customer {self.type} is now leaving after showing satisfaction")
                self.leaving = True
        
        # If leaving, update leave timer
        if self.leaving:
            self.leave_timer += dt
            # Fade out effect (shrink and disappear)
            scale_factor = max(0, 1 - self.leave_timer/1.0)  # 1 second to disappear
            if scale_factor > 0:
                original = self.sprites[self.state]
                new_width = int(original.get_width() * scale_factor)
                new_height = int(original.get_height() * scale_factor)
                if new_width > 0 and new_height > 0:  # Prevent scaling to zero
                    self.image = pygame.transform.scale(original, (new_width, new_height))
                    # Re-center the rect after scaling
                    center = self.rect.center
                    self.rect = self.image.get_rect(center=center)
            else:
                # Remove from all groups when fully faded
                self.kill()

    def draw(self, surface, offset_x=0, offset_y=0):
        # Draw the customer sprite
        if not self.leaving or self.leave_timer < 1.0:  # Only draw if still visible
            # Calculate adjusted position with offset
            draw_x = self.rect.x + offset_x
            draw_y = self.rect.y + offset_y
            
            # Draw at the adjusted position
            surface.blit(self.image, (draw_x, draw_y))
            
            # Draw speech bubble if not fed
            if not self.fed and not self.leaving:
                # Adjust bubble position above the customer's head (with offset)
                bubble_x = self.rect.centerx - 40 + offset_x
                bubble_y = self.rect.top - 70 + offset_y
                
                # Draw patience indicator (change bubble color based on patience)
                patience_ratio = self.patience_timer / self.patience
                if patience_ratio < 0.7:
                    opacity = 255
                else:
                    # Pulse/flash effect when patience is running low
                    flash_speed = 10  # Higher = faster flashing
                    pulse_value = (pygame.time.get_ticks() * flash_speed) % 1000 / 1000.0
                    # Oscillate between 128 and 255 opacity for pulse effect
                    opacity = int(128 + 127 * pulse_value)
                
                # Apply opacity to bubble
                self.bubble.set_alpha(opacity)
                surface.blit(self.bubble, (bubble_x, bubble_y))
