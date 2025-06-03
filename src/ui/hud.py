"""
HUD (Heads-Up-Display) module for Jammin' Eats.

This module provides the HUD class that displays game information to the player,
including food selection, money, and other relevant gameplay information.
"""

import pygame
import os

# Try both import styles to support different run configurations
try:
    from core.constants import WIDTH, HEIGHT, COLORS
    from debug.logger import game_logger
except ImportError:
    try:
        from src.core.constants import WIDTH, HEIGHT, COLORS
        from src.debug.logger import game_logger
    except ImportError:
        # Fallback default values if imports fail
        WIDTH, HEIGHT = 800, 600
        COLORS = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'GRAY': (128, 128, 128),
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'YELLOW': (255, 255, 0)
        }
        # Simple logger fallback
        import logging
        logging.basicConfig(level=logging.INFO)
        game_logger = logging.getLogger(__name__)
        game_logger.info = lambda msg, *args, **kwargs: print(f"[LOG] {msg}")
        game_logger.error = lambda msg, *args, **kwargs: print(f"[ERROR] {msg}")
        game_logger.debug = lambda msg, *args, **kwargs: print(f"[DEBUG] {msg}")


class HUD:
    """Head-Up Display for showing game information to the player"""
    
    def __init__(self, width, height):
        """Initialize the HUD with screen dimensions"""
        self.width = width
        self.height = height
        self.selected_food = "burger"  # Default food
        self.food_icons = {}
        self.load_food_icons()
        game_logger.debug("HUD initialized", "HUD")
    
    def load_food_icons(self):
        """Load food icons for the HUD"""
        try:
            # Try to find assets in either path structure
            base_dirs = [
                os.path.join('assets', 'foods'),
                os.path.join('assets', 'images', 'foods')
            ]
            
            food_types = ['burger', 'pizza', 'sushi', 'taco', 'hotdog']
            
            for food in food_types:
                found = False
                for base_dir in base_dirs:
                    for ext in ['.png', '.jpg']:
                        path = os.path.join(base_dir, f"{food}{ext}")
                        if os.path.exists(path):
                            try:
                                self.food_icons[food] = pygame.image.load(path).convert_alpha()
                                # Scale to a reasonable size for HUD
                                self.food_icons[food] = pygame.transform.scale(self.food_icons[food], (32, 32))
                                found = True
                                game_logger.debug(f"Loaded food icon: {food} from {path}", "HUD")
                                break
                            except Exception as e:
                                game_logger.error(f"Error loading food icon {food}: {e}", "HUD")
                    if found:
                        break
                
                if not found:
                    # Create a fallback colored rectangle
                    color_map = {
                        'burger': (139, 69, 19),   # Brown
                        'pizza': (255, 99, 71),    # Tomato
                        'sushi': (46, 139, 87),    # Sea Green
                        'taco': (255, 215, 0),     # Gold
                        'hotdog': (255, 105, 180)  # Hot Pink
                    }
                    
                    surf = pygame.Surface((32, 32))
                    surf.fill(color_map.get(food, (200, 200, 200)))
                    self.food_icons[food] = surf
                    game_logger.warning(f"Created fallback icon for {food}", "HUD")
            
        except Exception as e:
            game_logger.error(f"Failed to load food icons: {e}", "HUD")
    
    def set_selection(self, food_type):
        """Set the selected food type"""
        if food_type in self.food_icons:
            self.selected_food = food_type
            game_logger.debug(f"HUD selected food: {food_type}", "HUD")
            return True
        else:
            game_logger.warning(f"Unknown food type: {food_type}", "HUD")
            return False
    
    def update(self, dt, selected_food=None):
        """Update the HUD state
        
        Args:
            dt: Time delta in seconds
            selected_food: Currently selected food type (optional)
        """
        # Update selection if provided
        if selected_food and selected_food in self.food_icons:
            self.selected_food = selected_food
            
        # Any additional update logic can go here
        # For now, this is mostly used to sync selected food
    
    def draw(self, surface):
        """Draw the HUD on the given surface"""
        # Draw food selection panel at bottom
        self._draw_food_selection(surface)
        
        # Draw selected food indicator
        self._draw_selected_indicator(surface)
        
        # Draw key hints
        self._draw_key_hints(surface)
    
    def _draw_food_selection(self, surface):
        """Draw the food selection panel"""
        # Draw panel background
        panel_height = 60
        panel_rect = pygame.Rect(0, self.height - panel_height, self.width, panel_height)
        pygame.draw.rect(surface, COLORS.get('BLACK', (0, 0, 0)), panel_rect)
        pygame.draw.rect(surface, COLORS.get('GRAY', (128, 128, 128)), panel_rect, 2)
        
        # Draw food icons in a row
        start_x = 20
        y = self.height - panel_height + 10
        
        for i, (food_type, icon) in enumerate(self.food_icons.items()):
            x = start_x + i * 80
            # Draw icon
            surface.blit(icon, (x, y))
            
            # Draw food name
            font = pygame.font.SysFont(None, 20)
            text = font.render(food_type.capitalize(), True, COLORS.get('WHITE', (255, 255, 255)))
            surface.blit(text, (x, y + 35))
            
            # Draw key number
            key_font = pygame.font.SysFont(None, 24)
            key_text = key_font.render(f"{i+1}", True, COLORS.get('YELLOW', (255, 255, 0)))
            surface.blit(key_text, (x + 15, y - 20))
    
    def _draw_selected_indicator(self, surface):
        """Draw an indicator around the currently selected food"""
        # Find the selected food position
        food_types = list(self.food_icons.keys())
        try:
            idx = food_types.index(self.selected_food)
            x = 20 + idx * 80
            y = self.height - 60 + 10
            
            # Draw highlight rectangle
            highlight_rect = pygame.Rect(x - 5, y - 5, 42, 42)
            pygame.draw.rect(surface, COLORS.get('YELLOW', (255, 255, 0)), highlight_rect, 2)
            
            # Add a "SELECTED" indicator
            font = pygame.font.SysFont(None, 16)
            sel_text = font.render("SELECTED", True, COLORS.get('YELLOW', (255, 255, 0)))
            surface.blit(sel_text, (x - 5, y - 20))
        except ValueError:
            game_logger.warning(f"Selected food {self.selected_food} not found in icons", "HUD")
    
    def _draw_key_hints(self, surface):
        """Draw keyboard shortcut hints"""
        hint_font = pygame.font.SysFont(None, 20)
        hints = [
            "1-5: Select Food",
            "SPACE: Throw Food",
            "B: Shop Menu",
            "ESC: Exit"
        ]
        
        y = self.height - 100
        for hint in hints:
            text = hint_font.render(hint, True, COLORS.get('WHITE', (255, 255, 255)))
            surface.blit(text, (self.width - text.get_width() - 20, y))
            y += 20
