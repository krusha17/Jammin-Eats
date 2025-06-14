import pygame
import random
import math


class Particle:
    """Individual particle object with position, velocity, color, and lifespan."""

    def __init__(
        self,
        x,
        y,
        color=(255, 255, 255),
        size=5,
        velocity=None,
        decay_rate=0.05,
        gravity=0.1,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.original_size = size  # Store original size for reference

        # Set random velocity if none provided
        if velocity is None:
            angle = random.uniform(0, 360) * (3.14159 / 180)  # Convert to radians
            speed = random.uniform(1, 3)
            self.velocity = {"x": speed * math.cos(angle), "y": speed * math.sin(angle)}
        else:
            self.velocity = velocity

        self.decay_rate = decay_rate  # How quickly particle shrinks
        self.gravity = gravity  # Downward acceleration
        self.alpha = 255  # Transparency (255=solid)

    def update(self, dt):
        """Update particle position and properties."""
        # Apply velocity
        self.x += self.velocity["x"] * dt * 60  # Scale by dt and target 60 FPS
        self.y += self.velocity["y"] * dt * 60

        # Apply gravity
        self.velocity["y"] += self.gravity * dt * 60

        # Shrink particle
        self.size -= self.decay_rate * dt * 60

        # Fade out
        self.alpha -= (self.decay_rate * 2) * 255 * dt * 60
        self.alpha = max(0, min(255, self.alpha))  # Clamp between 0-255

    def is_alive(self):
        """Check if particle is still visible."""
        return self.size > 0 and self.alpha > 0

    def draw(self, surface):
        """Draw particle on the given surface."""
        if not self.is_alive():
            return

        # Create a surface with per-pixel alpha
        particle_surface = pygame.Surface(
            (int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA
        )

        # Draw the particle with alpha
        color_with_alpha = (*self.color, int(self.alpha))
        pygame.draw.circle(
            particle_surface,
            color_with_alpha,
            (int(self.size), int(self.size)),
            int(self.size),
        )

        # Blit to main surface
        surface.blit(
            particle_surface, (int(self.x - self.size), int(self.y - self.size))
        )


class ParticleSystem:
    """Manages groups of particles for various effects."""

    def __init__(self):
        self.particle_groups = {}  # Dictionary of particle groups by ID
        self.next_group_id = 0

    def create_explosion(
        self, x, y, color=(255, 255, 0), num_particles=20, size=5, decay_rate=0.1
    ):
        """Create an explosion particle effect."""
        particles = []

        for _ in range(num_particles):
            # Random direction
            angle = random.uniform(0, 360) * (3.14159 / 180)
            speed = random.uniform(2, 5)
            velocity = {"x": speed * math.cos(angle), "y": speed * math.sin(angle)}

            # Random color variation
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))

            # Create particle
            particle = Particle(
                x,
                y,
                color=(r, g, b),
                size=random.uniform(size * 0.7, size * 1.3),
                velocity=velocity,
                decay_rate=decay_rate,
            )
            particles.append(particle)

        # Store and return group ID
        group_id = self.next_group_id
        self.particle_groups[group_id] = particles
        self.next_group_id += 1
        return group_id

    def create_trail(
        self, x, y, color=(100, 100, 255), num_particles=5, size=3, decay_rate=0.15
    ):
        """Create a trail particle effect (e.g., behind moving objects)."""
        particles = []

        for _ in range(num_particles):
            # Minimal random velocity
            velocity = {"x": random.uniform(-0.5, 0.5), "y": random.uniform(-0.5, 0.5)}

            # Random color variation
            r = min(255, max(0, color[0] + random.randint(-10, 10)))
            g = min(255, max(0, color[1] + random.randint(-10, 10)))
            b = min(255, max(0, color[2] + random.randint(-10, 10)))

            # Create particle with low gravity
            particle = Particle(
                x + random.uniform(-2, 2),
                y + random.uniform(-2, 2),
                color=(r, g, b),
                size=random.uniform(size * 0.8, size * 1.2),
                velocity=velocity,
                decay_rate=decay_rate,
                gravity=0.01,  # Very low gravity
            )
            particles.append(particle)

        # Store and return group ID
        group_id = self.next_group_id
        self.particle_groups[group_id] = particles
        self.next_group_id += 1
        return group_id

    def create_sparkle(
        self, x, y, color=(255, 255, 255), num_particles=10, size=2, decay_rate=0.08
    ):
        """Create a sparkle effect (e.g., for powerups, achievements)."""
        particles = []

        for _ in range(num_particles):
            # Outward velocity
            angle = random.uniform(0, 360) * (3.14159 / 180)
            speed = random.uniform(1, 2)
            velocity = {"x": speed * math.cos(angle), "y": speed * math.sin(angle)}

            # Random color variation - more towards white for sparkle
            r = min(255, max(0, color[0] + random.randint(0, 30)))
            g = min(255, max(0, color[1] + random.randint(0, 30)))
            b = min(255, max(0, color[2] + random.randint(0, 30)))

            # Create particle with no gravity
            particle = Particle(
                x,
                y,
                color=(r, g, b),
                size=random.uniform(size * 0.8, size * 1.2),
                velocity=velocity,
                decay_rate=decay_rate,
                gravity=0,  # No gravity for sparkles
            )
            particles.append(particle)

        # Store and return group ID
        group_id = self.next_group_id
        self.particle_groups[group_id] = particles
        self.next_group_id += 1
        return group_id

    def update(self, dt):
        """Update all particle groups."""
        groups_to_remove = []

        for group_id, particles in self.particle_groups.items():
            # Update particles
            for particle in particles[:]:  # Copy the list to avoid modification issues
                particle.update(dt)
                if not particle.is_alive():
                    particles.remove(particle)

            # If group is empty, mark for removal
            if not particles:
                groups_to_remove.append(group_id)

        # Remove empty groups
        for group_id in groups_to_remove:
            del self.particle_groups[group_id]

    def draw(self, surface):
        """Draw all particles to the given surface."""
        for particles in self.particle_groups.values():
            for particle in particles:
                particle.draw(surface)

    def clear(self):
        """Clear all particle groups."""
        self.particle_groups.clear()
