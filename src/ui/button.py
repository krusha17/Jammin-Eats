import pygame
from src.core.constants import WHITE


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = WHITE
        self.font = pygame.font.Font(None, 36)
        self.hovered = False

    def draw(self, surface):
        # Draw the button box
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # White border

        # Render and draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        # Check if the mouse is hovering over the button
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.hovered = True
        else:
            self.current_color = self.color
            self.hovered = False

    def is_clicked(self, event):
        # Check if the mouse clicked on the button
        return self.rect.collidepoint(event.pos)
