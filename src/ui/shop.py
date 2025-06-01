import pygame
import os
from src.core.constants import WHITE, BLACK, GREEN, YELLOW, RED, BLUE, UPGRADE_DATA
from src.debug.logger import log

class ShopButton:
    def __init__(self, x, y, width, height, upgrade_id, game):
        self.rect = pygame.Rect(x, y, width, height)
        self.upgrade_id = upgrade_id
        self.game = game
        
        # Get upgrade details
        self.details = UPGRADE_DATA[upgrade_id]
        self.name = self.details["name"]
        self.desc = self.details["desc"]
        self.cost = self.details["cost"]
        self.requires = self.details.get("requires", [])
        
        # Status colors
        self.owned_color = GREEN
        self.available_color = WHITE
        self.expensive_color = YELLOW
        self.locked_color = (100, 100, 100)  # Gray
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
    def is_owned(self):
        return self.game.upgrades.has(self.upgrade_id)
    
    def is_available(self):
        # Check if all prerequisites are met
        for req in self.requires:
            if not self.game.upgrades.has(req):
                return False
        return True
    
    def is_affordable(self):
        # If no economy, can't afford anything
        if not hasattr(self.game, 'economy'):
            return False
        return self.game.economy.money >= self.cost
    
    def get_status_color(self):
        if self.is_owned():
            return self.owned_color
        elif not self.is_available():
            return self.locked_color
        elif not self.is_affordable():
            return self.expensive_color
        else:
            return self.available_color
    
    def get_status_text(self):
        if self.is_owned():
            return "Owned"
        elif not self.is_available():
            # Get the names of prerequisites
            req_names = [UPGRADE_DATA[req]["name"] for req in self.requires]
            return f"Requires: {', '.join(req_names)}"
        elif not self.is_affordable():
            return f"Cost: ${self.cost} (Need ${self.cost - self.game.economy.money} more)"
        else:
            return f"Cost: ${self.cost}"
    
    def draw(self, surface):
        color = self.get_status_color()
        
        # Draw button background
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        # Draw name
        name_text = self.font.render(self.name, True, color)
        surface.blit(name_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw description
        desc_text = self.small_font.render(self.desc, True, color)
        surface.blit(desc_text, (self.rect.x + 10, self.rect.y + 40))
        
        # Draw status
        status_text = self.small_font.render(self.get_status_text(), True, color)
        surface.blit(status_text, (self.rect.x + 10, self.rect.y + 65))
        
    def is_clicked(self, event):
        return self.rect.collidepoint(event.pos)

class ShopOverlay:
    def __init__(self, game):
        self.game = game
        self.is_open = False
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create surface for dimming background
        self.screen_size = game.screen.get_size()
        self.dim_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Create shop buttons
        self.update_shop_buttons()
        
        # Close button
        self.close_rect = pygame.Rect(self.screen_size[0] - 150, self.screen_size[1] - 70, 100, 40)
    
    def update_shop_buttons(self):
        # Calculate grid layout
        self.buttons = []
        button_width = 300
        button_height = 90
        margin = 20
        start_x = (self.screen_size[0] - (button_width * 2 + margin)) // 2
        start_y = 100
        
        # Create buttons for each upgrade
        upgrade_ids = list(UPGRADE_DATA.keys())
        for i, upgrade_id in enumerate(upgrade_ids):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)
            button = ShopButton(x, y, button_width, button_height, upgrade_id, self.game)
            self.buttons.append(button)
    
    def toggle(self):
        # Toggle shop visibility
        self.is_open = not self.is_open
        if self.is_open:
            # Update screen size in case of resize
            self.screen_size = self.game.screen.get_size()
            self.dim_surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            self.dim_surface.fill((0, 0, 0, 180))
            self.update_shop_buttons()
            # Update close button position
            self.close_rect = pygame.Rect(self.screen_size[0] - 150, self.screen_size[1] - 70, 100, 40)
            log("Shop opened")
        else:
            log("Shop closed")
    
    def handle_event(self, event):
        if not self.is_open:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if close button was clicked
            if self.close_rect.collidepoint(event.pos):
                self.toggle()
                return True
                
            # Check if any upgrade buttons were clicked
            for button in self.buttons:
                if button.is_clicked(event):
                    # Try to purchase the upgrade
                    if not button.is_owned() and button.is_available() and button.is_affordable():
                        success = self.game.buy_upgrade(button.upgrade_id)
                        if success:
                            log(f"Purchased upgrade: {button.name}")
                            # Play purchase sound if available
                            if hasattr(self.game, 'sounds') and 'purchase_sound' in self.game.sounds and self.game.sounds['purchase_sound']:
                                self.game.sounds['purchase_sound'].play()
                        return True
        
        # B key to close shop
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            self.toggle()
            return True
            
        # Escape key to close shop
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle()
            return True
            
        return True  # Event was handled
    
    def draw(self, surface):
        if not self.is_open:
            return
            
        # Dim the background
        surface.blit(self.dim_surface, (0, 0))
        
        # Draw title
        title_text = self.font.render("Upgrade Shop", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_size[0] // 2, 50))
        surface.blit(title_text, title_rect)
        
        # Draw available money if economy exists
        if hasattr(self.game, 'economy'):
            money_text = self.small_font.render(f"Available Money: ${self.game.economy.money}", True, GREEN)
            money_rect = money_text.get_rect(topleft=(50, 50))
            surface.blit(money_text, money_rect)
        
        # Draw all upgrade buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw close button
        pygame.draw.rect(surface, RED, self.close_rect)
        close_text = self.small_font.render("Close", True, WHITE)
        close_rect = close_text.get_rect(center=self.close_rect.center)
        surface.blit(close_text, close_rect)
