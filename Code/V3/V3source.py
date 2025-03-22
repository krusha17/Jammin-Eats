import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 768, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jammin Eats")

clock = pygame.time.Clock()
FPS = 60

# Load the background image with error handling
try:
    background = pygame.image.load('D:\Jammin eats\assets\backgrounds\level1').convert()
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((0, 0, 0))

# A simple Player class with directional sprites
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load directional sprites with error handling
        try:
            self.image_up = pygame.image.load('D:\Jammin eats\assets\sprites\characters\kai\kai_up.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading up image: {e}")
            self.image_up = pygame.Surface((50, 50))
            self.image_up.fill((255, 255, 255))
            
        try:
            self.image_down = pygame.image.load('D:\Jammin eats\assets\sprites\characters\kai\kai_down.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading down image: {e}")
            self.image_down = pygame.Surface((50, 50))
            self.image_down.fill((255, 255, 255))
            
        try:
            self.image_left = pygame.image.load('D:\Jammin eats\assets\sprites\characters\kai\kai_left.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading left image: {e}")
            self.image_left = pygame.Surface((50, 50))
            self.image_left.fill((255, 255, 255))
            
        try:
            self.image_right = pygame.image.load('D:\Jammin eats\assets\sprites\characters\kai\kai_right.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading right image: {e}")
            self.image_right = pygame.Surface((50, 50))
            self.image_right.fill((255, 255, 255))
        
        # Set a default image (facing down)
        self.image = self.image_down
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 200  # Speed in pixels per second

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # Check key inputs and update position and sprite image accordingly
        if keys[pygame.K_LEFT]:
            self.rect.x -= int(self.speed * dt)
            self.image = self.image_left
        elif keys[pygame.K_RIGHT]:
            self.rect.x += int(self.speed * dt)
            self.image = self.image_right
        elif keys[pygame.K_UP]:
            self.rect.y -= int(self.speed * dt)
            self.image = self.image_up
        elif keys[pygame.K_DOWN]:
            self.rect.y += int(self.speed * dt)
            self.image = self.image_down
        
        # Boundary checks to keep the player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

# Create a player instance and add it to the sprite group
player = Player(WIDTH // 2, HEIGHT // 2)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

def main():
    running = True
    while running:
        # Calculate delta time (in seconds)
        dt = clock.tick(FPS) / 1000
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game logic with delta time
        all_sprites.update(dt)

        # Draw background and sprites
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
