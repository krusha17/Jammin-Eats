import pygame
import random


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size=5, speed=2, lifetime=1):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))

        # Random velocity in all directions
        self.velocity = [random.uniform(-speed, speed), random.uniform(-speed, speed)]
        self.lifetime = lifetime  # seconds
        self.timer = 0
        self.alpha = 255
        self.fade_rate = 255 / lifetime

    def update(self, dt):
        # Move particle
        self.rect.x += self.velocity[0] * dt * 60  # Scale by dt for consistent speed
        self.rect.y += self.velocity[1] * dt * 60

        # Update lifetime timer
        self.timer += dt

        # Fade out effect
        self.alpha = max(0, 255 - (self.timer / self.lifetime) * 255)
        self.image.set_alpha(int(self.alpha))

        # Remove when lifetime expires
        if self.timer >= self.lifetime:
            self.kill()

    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw the particle with the specified offset"""
        # Calculate adjusted position with offset
        draw_x = self.rect.x + offset_x
        draw_y = self.rect.y + offset_y

        # Draw at the adjusted position
        surface.blit(self.image, (draw_x, draw_y))
