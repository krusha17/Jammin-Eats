import pygame
from src.core.constants import WHITE

def draw_text(surface, text, size, x, y, color=WHITE):
    """Draw text on a surface with the specified parameters"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    return text_rect  # Return the rect in case it's needed
