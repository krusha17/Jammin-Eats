import pygame
import sys
import random
import math
from pygame import mixer
import os

# Initialize Pygame
pygame.init()
mixer.init()

# Set up the game window
WIDTH, HEIGHT = 768, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jammin' Eats")
clock = pygame.time.Clock()
FPS = 60

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Score system
score = 0
high_score = 0
font = pygame.font.Font(None, 36)

# Load sounds with error handling
try:
    pickup_sound = mixer.Sound('assets/sounds/characters/food_throw.wav')
    engine_sound = mixer.Sound('assets/sounds/vehicles/engine_idle.wav')
    button_sound = mixer.Sound('assets/sounds/ui/button_click.wav')
    # Try to create background music - fallback to looping a sound if needed
    try:
        mixer.music.load('assets/sounds/characters/food_throw.wav')  # Placeholder for background music
        mixer.music.set_volume(0.5)
        mixer.music.play(-1)  # Loop indefinitely
    except:
        print("No background music found, continuing without it")
except:
    print("Error loading sounds, continuing without audio")

# Load the background image with error handling
try:
    background = pygame.image.load('assets/backgrounds/level1/level1.png').convert()
    print("Successfully loaded background image")
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background = pygame.Surface((WIDTH, HEIGHT))
    # Create a colorful background that matches the game's tropical theme
    for y in range(HEIGHT):
        color_value = int(255 * (1 - y / HEIGHT))
        # Create a gradient from cyan to deep blue
        color = (0, 150 + color_value // 3, 200 + color_value // 4)
        pygame.draw.line(background, color, (0, y), (WIDTH, y))

    # Add some decorative elements (palm trees and buildings as rectangles)
    for _ in range(5):
        # Draw simple palm trees
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT // 2)
        pygame.draw.rect(background, (60, 30, 10), (x, y, 10, 30))  # Trunk
        pygame.draw.circle(background, (0, 180, 0), (x + 5, y - 10), 20)  # Leaves

    # Draw a simple road
    pygame.draw.rect(background, (80, 80, 80), (0, HEIGHT // 2, WIDTH, 100))
    # Add road lines
    for x in range(0, WIDTH, 40):
        pygame.draw.rect(background, (255, 255, 255), (x, HEIGHT // 2 + 50, 20, 5))

# Create menu background programmatically
menu_background = pygame.Surface((WIDTH, HEIGHT))
# Create a gradient background
for y in range(HEIGHT):
    color_value = int(255 * (1 - y / HEIGHT))
    color = (0, color_value // 2, color_value)
    pygame.draw.line(menu_background, color, (0, y), (WIDTH, y))

# Add some decorative elements
for _ in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    pygame.draw.circle(menu_background, (255, 255, 255), (x, y), size)

# Create game over background
game_over_background = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    color_value = int(200 * (1 - y / HEIGHT))
    color = (color_value + 55, 0, 0)
    pygame.draw.line(game_over_background, color, (0, y), (WIDTH, y))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# A more detailed Player class with animations
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load directional sprites with error handling
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'idle': []
        }

        # Try loading the sprites from the specific file paths
        try:
            # Load character sprites for different directions
            self.image_up = pygame.image.load('assets/sprites/characters/kai/kai_up.png').convert_alpha()
            self.image_down = pygame.image.load('assets/sprites/characters/kai/kai_down.png').convert_alpha()
            self.image_left = pygame.image.load('assets/sprites/characters/kai/kai_left.png').convert_alpha()
            self.image_right = pygame.image.load('assets/sprites/characters/kai/kai_right.png').convert_alpha()

            # Use these images for our animations (single frame each direction)
            self.animations['up'] = [self.image_up]
            self.animations['down'] = [self.image_down]
            self.animations['left'] = [self.image_left]
            self.animations['right'] = [self.image_right]
            self.animations['idle'] = [self.image_down]  # Use down image for idle

            print("Successfully loaded character sprites")
        except pygame.error as e:
            print(f"Error loading character sprites: {e}")
            # Create fallback surfaces
            fallback = pygame.Surface((50, 50))
            fallback.fill(WHITE)
            pygame.draw.circle(fallback, (0, 100, 200), (25, 25), 20)  # Blue circle for player
            pygame.draw.rect(fallback, (200, 150, 0), (15, 15, 20, 20))  # Yellow face

            for direction in self.animations:
                self.animations[direction] = [fallback]

        # Animation variables
        self.direction = 'down'
        self.animation_index = 0
        self.animation_speed = 0.2  # seconds per frame
        self.animation_timer = 0

        # Set initial image
        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect(center=(x, y))

        # Movement variables
        self.speed = 200  # Speed in pixels per second
        self.velocity = [0, 0]  # x, y velocity
        self.moving = False

        # Player stats
        self.deliveries = 0
        self.missed_deliveries = 0
        self.delivery_cooldown = 0
        self.delivery_cooldown_max = 0.5  # seconds

        # Food truck is not available yet, so we'll skip it for now
        self.has_truck = False
        print("Food truck disabled - will be added later")

    def update(self, dt, customers, foods):
        # Previous position for collision resolution
        prev_x, prev_y = self.rect.x, self.rect.y

        # Handle input and movement
        self.handle_movement(dt)

        # Update animation
        self.update_animation(dt)

        # Update delivery cooldown
        if self.delivery_cooldown > 0:
            self.delivery_cooldown -= dt

        # Check for customer interactions
        for customer in customers:
            if pygame.sprite.collide_rect(self, customer) and not customer.fed:
                customer.greet()

        # Update missed delivery count from expired customers
        for customer in customers:
            if customer.expired and not customer.counted:
                self.missed_deliveries += 1
                customer.counted = True

    def handle_movement(self, dt):
        keys = pygame.key.get_pressed()
        self.velocity = [0, 0]
        self.moving = False

        # Check key inputs and update velocity
        if keys[pygame.K_LEFT]:
            self.velocity[0] = -self.speed
            self.direction = 'left'
            self.moving = True
        elif keys[pygame.K_RIGHT]:
            self.velocity[0] = self.speed
            self.direction = 'right'
            self.moving = True

        if keys[pygame.K_UP]:
            self.velocity[1] = -self.speed
            self.direction = 'up'
            self.moving = True
        elif keys[pygame.K_DOWN]:
            self.velocity[1] = self.speed
            self.direction = 'down'
            self.moving = True

        # Diagonal movement should not be faster
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            self.velocity[0] *= 0.7071  # 1/sqrt(2)
            self.velocity[1] *= 0.7071

        # Update position
        self.rect.x += int(self.velocity[0] * dt)
        self.rect.y += int(self.velocity[1] * dt)

        # Boundary checks
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update_animation(self, dt):
        # If not moving, use idle animation
        if not self.moving:
            if 'idle' in self.animations and self.animations['idle']:
                self.image = self.animations['idle'][0]
            else:
                self.image = self.animations[self.direction][0]
            self.animation_index = 0
            self.animation_timer = 0
            return

        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animations[self.direction])

        # Update image
        self.image = self.animations[self.direction][self.animation_index]

    def throw_food(self, foods):
        # Check if cooldown has passed
        if self.delivery_cooldown <= 0:
            # Create new food item in the direction player is facing
            direction_vectors = {
                'up': (0, -1),
                'down': (0, 1),
                'left': (-1, 0),
                'right': (1, 0)
            }

            dx, dy = direction_vectors[self.direction]

            # Randomly select a food type
            food_types = ['pizza', 'smoothie', 'icecream', 'pudding']
            food_type = random.choice(food_types)

            food = Food(self.rect.centerx, self.rect.centery, dx, dy, food_type)
            foods.add(food)

            # Play throw sound
            try:
                pickup_sound.play()
            except:
                pass

            # Reset cooldown
            self.delivery_cooldown = self.delivery_cooldown_max

    def draw_stats(self, surface):
        # Delivery stats
        delivery_text = font.render(f"Deliveries: {self.deliveries}", True, WHITE)
        surface.blit(delivery_text, (20, 20))

        missed_text = font.render(f"Missed: {self.missed_deliveries}", True, WHITE)
        surface.blit(missed_text, (20, 60))

        # Cooldown indicator
        if self.delivery_cooldown > 0:
            cooldown_width = int((self.delivery_cooldown / self.delivery_cooldown_max) * 100)
            pygame.draw.rect(surface, RED, (20, 100, 100, 10))
            pygame.draw.rect(surface, GREEN, (20, 100, 100 - cooldown_width, 10))
            pygame.draw.rect(surface, WHITE, (20, 100, 100, 10), 2)

    def draw(self, surface):
        # Draw player
        surface.blit(self.image, self.rect)

        # We'll add the food truck drawing later when the sprite is available


# Customer class
class Customer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Create a simple customer sprite
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

        # Draw a simple person
        pygame.draw.ellipse(self.image, self.color, (10, 10, 20, 20))  # Head
        pygame.draw.rect(self.image, self.color, (10, 30, 20, 30))  # Body

        self.rect = self.image.get_rect(center=(x, y))

        # Customer variables
        self.patience = random.uniform(10, 20)  # seconds before leaving
        self.timer = 0
        self.fed = False
        self.expired = False
        self.counted = False
        self.greeting = False
        self.greeting_timer = 0

        # Dialog bubble for greeting
        self.bubble = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.bubble, (255, 255, 255), (0, 0, 80, 40))
        self.bubble_rect = self.bubble.get_rect(center=(self.rect.centerx, self.rect.top - 30))

        # Food preference
        self.food_preference = random.choice(['pizza', 'smoothie', 'icecream', 'pudding'])

        # Draw food icon in bubble
        if self.food_preference == 'pizza':
            pygame.draw.polygon(self.bubble, YELLOW, [(40, 10), (60, 30), (20, 30)])
        elif self.food_preference == 'smoothie':
            pygame.draw.rect(self.bubble, (150, 0, 255), (30, 10, 20, 25))
            pygame.draw.ellipse(self.bubble, (200, 0, 255), (25, 5, 30, 10))
        elif self.food_preference == 'icecream':
            pygame.draw.polygon(self.bubble, (200, 200, 150), [(40, 30), (30, 10), (50, 10)])
            pygame.draw.circle(self.bubble, (255, 100, 100), (40, 10), 10)
        else:  # pudding
            pygame.draw.rect(self.bubble, (160, 120, 60), (30, 10, 20, 20))
            pygame.draw.ellipse(self.bubble, (180, 140, 70), (25, 5, 30, 10))

    def update(self, dt):
        # Update patience timer
        if not self.fed and not self.expired:
            self.timer += dt
            if self.timer >= self.patience:
                self.expired = True

        # Update greeting timer
        if self.greeting:
            self.greeting_timer += dt
            if self.greeting_timer >= 2.0:  # Show greeting for 2 seconds
                self.greeting = False
                self.greeting_timer = 0

        # Update bubble position to follow customer
        self.bubble_rect.center = (self.rect.centerx, self.rect.top - 30)

    def greet(self):
        self.greeting = True
        self.greeting_timer = 0

    def feed(self, food_type):
        if not self.fed and not self.expired:
            if food_type == self.food_preference:
                self.fed = True
                return 100  # Bonus points for matching preference
            else:
                self.fed = True
                return 50  # Base points for any food
        return 0

    def draw(self, surface):
        # Draw customer
        surface.blit(self.image, self.rect)

        # Draw speech bubble if greeting or not fed
        if self.greeting or (not self.fed and not self.expired):
            surface.blit(self.bubble, self.bubble_rect)

        # Draw patience meter
        if not self.fed and not self.expired:
            patience_width = int((1 - self.timer / self.patience) * 40)
            pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 10, 40, 5))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, patience_width, 5))

        # Visual indicator for fed status
        if self.fed:
            happy_face = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(happy_face, GREEN, (0, 0, 40, 20))
            surface.blit(happy_face, (self.rect.x, self.rect.top - 20))


# Food class
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, food_type='pizza'):
        super().__init__()
        self.food_type = food_type

        # Create different food types with shapes and colors
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)

        if food_type == 'pizza':
            # Pizza slice
            pygame.draw.polygon(self.image, YELLOW, [(10, 0), (20, 20), (0, 20)])
            pygame.draw.circle(self.image, RED, (10, 15), 3)  # Pepperoni
            self.name = "Tropical Pizza Slice"
        elif food_type == 'smoothie':
            # Smoothie
            pygame.draw.rect(self.image, (150, 0, 255), (5, 0, 10, 15))
            pygame.draw.ellipse(self.image, (200, 0, 255), (0, 0, 20, 5))
            pygame.draw.line(self.image, WHITE, (10, 0), (10, -5), 2)  # Straw
            self.name = "Ska Smoothie"
        elif food_type == 'icecream':
            # Ice cream
            pygame.draw.polygon(self.image, (200, 200, 150), [(10, 20), (0, 0), (20, 0)])  # Cone
            pygame.draw.circle(self.image, (255, 100, 100), (10, 0), 8)  # Scoop
            self.name = "Island Ice Cream Jam"
        else:  # pudding
            # Rice pudding
            pygame.draw.rect(self.image, (160, 120, 60), (2, 2, 16, 16))
            pygame.draw.ellipse(self.image, (180, 140, 70), (0, 0, 20, 5))
            self.name = "Rasta Rice Pudding"

        self.rect = self.image.get_rect(center=(x, y))

        # Movement variables
        self.speed = 300
        self.direction = pygame.math.Vector2(dx, dy)
        if self.direction.length() > 0:
            self.direction.normalize_ip()

        # Lifespan (despawn after a few seconds)
        self.lifespan = 2.0  # seconds
        self.timer = 0

    def update(self, dt):
        # Move food
        self.rect.x += int(self.direction.x * self.speed * dt)
        self.rect.y += int(self.direction.y * self.speed * dt)

        # Update timer
        self.timer += dt
        if self.timer >= self.lifespan:
            self.kill()

        # Check if out of bounds
        if (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()


# Particle effect class
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size=5, speed=2, lifetime=1):
        super().__init__()
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))

        # Particle properties
        self.velocity = [random.uniform(-speed, speed), random.uniform(-speed, speed)]
        self.lifetime = lifetime
        self.timer = 0
        self.alpha = 255
        self.fade_rate = 255 / lifetime

    def update(self, dt):
        # Update position
        self.rect.x += int(self.velocity[0])
        self.rect.y += int(self.velocity[1])

        # Update lifetime and transparency
        self.timer += dt
        self.alpha = max(0, 255 - int(self.timer * self.fade_rate))
        self.image.set_alpha(self.alpha)

        # Kill particle if lifetime exceeded
        if self.timer >= self.lifetime:
            self.kill()


# Button class for menu
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
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.hovered = True
        else:
            self.current_color = self.color
            self.hovered = False

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.hovered
        return False


# Create sprite groups
all_sprites = pygame.sprite.Group()
customers = pygame.sprite.Group()
foods = pygame.sprite.Group()
particles = pygame.sprite.Group()

# Create player instance
player = Player(WIDTH // 2, HEIGHT // 2)
all_sprites.add(player)

# Create UI buttons
start_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Start Game", GREEN, (100, 255, 100))
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50, "Exit", RED, (255, 100, 100))
restart_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50, "Restart", GREEN, (100, 255, 100))

# Game variables
game_time = 0
customer_spawn_rate = 5  # seconds
customer_spawn_timer = 0


def spawn_customer():
    # Spawn customer at edge of screen
    side = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left

    if side == 0:
        x = random.randint(50, WIDTH - 50)
        y = 50
    elif side == 1:
        x = WIDTH - 50
        y = random.randint(50, HEIGHT - 50)
    elif side == 2:
        x = random.randint(50, WIDTH - 50)
        y = HEIGHT - 50
    else:
        x = 50
        y = random.randint(50, HEIGHT - 50)

    customer = Customer(x, y)
    customers.add(customer)
    all_sprites.add(customer)

    # Add spawn particle effect
    for _ in range(5):
        particle = Particle(x, y, (0, 255, 255), size=random.randint(3, 8), speed=1, lifetime=0.5)
        particles.add(particle)
        all_sprites.add(particle)


def reset_game():
    global score, game_state, game_time

    # Clear sprite groups
    all_sprites.empty()
    customers.empty()
    foods.empty()
    particles.empty()

    # Reset player
    player.__init__(WIDTH // 2, HEIGHT // 2)
    all_sprites.add(player)

    # Reset game variables
    score = 0
    game_time = 0

    # Reset game state
    game_state = PLAYING

    # Start background music again
    try:
        mixer.music.play(-1)
    except:
        pass


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def main():
    global game_state, score, high_score, game_time
    global customer_spawn_timer, customer_spawn_rate
    
    # Make sure the assets directory exists
    print(f"Current working directory: {os.getcwd()}")
    if not os.path.exists('assets'):
        print("Warning: 'assets' directory not found in current working directory.")

    # Set initial game state
    game_state = MENU

    running = True
    while running:
        # Calculate delta time (in seconds)
        dt = clock.tick(FPS) / 1000

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Space bar to throw food
            if game_state == PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.throw_food(foods)

            # Check button clicks in menus
            if game_state == MENU:
                if start_button.is_clicked(event):
                    game_state = PLAYING
                    try:
                        button_sound.play()
                    except:
                        pass
                if exit_button.is_clicked(event):
                    running = False

            if game_state == GAME_OVER:
                if restart_button.is_clicked(event):
                    reset_game()
                    try:
                        button_sound.play()
                    except:
                        pass

        # Get mouse position for button hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Update game based on state
        if game_state == PLAYING:
            # Update game time
            game_time += dt

            # Spawn customers
            customer_spawn_timer += dt
            if customer_spawn_timer >= customer_spawn_rate:
                customer_spawn_timer = 0
                spawn_customer()

            # Update player
            player.update(dt, customers, foods)

            # Update customers
            for customer in customers:
                customer.update(dt)

            # Update foods
            for food in foods:
                food.update(dt)

            # Check for food collisions with customers
            for food in foods:
                hit_customers = pygame.sprite.spritecollide(food, customers, False)
                for customer in hit_customers:
                    points = customer.feed(food.food_type)
                    if points > 0:
                        # Only count points and increment deliveries if the customer wasn't fed before
                        if not customer.fed:
                            score += points
                            player.deliveries += 1

                            # Create success particles
                            for _ in range(10):
                                particle = Particle(
                                    customer.rect.centerx,
                                    customer.rect.centery,
                                    GREEN,
                                    size=random.randint(3, 6),
                                    speed=2,
                                    lifetime=0.8
                                )
                                particles.add(particle)
                                all_sprites.add(particle)

                    # Remove the food
                    food.kill()

            # Update particles
            particles.update(dt)

            # Update high score
            high_score = max(high_score, score)

            # Check game over condition (optional)
            if player.missed_deliveries >= 10:
                game_state = GAME_OVER

            # Draw everything
            screen.blit(background, (0, 0))

            # Draw customers
            for customer in customers:
                customer.draw(screen)

            # Draw player
            player.draw(screen)

            # Draw foods and particles
            foods.draw(screen)
            particles.draw(screen)

            # Draw player stats
            player.draw_stats(screen)

            # Draw score
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (WIDTH - 150, 20))

            # Draw game time
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            time_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
            screen.blit(time_text, (WIDTH - 150, 60))

        elif game_state == MENU:
            # Draw menu
            screen.blit(menu_background, (0, 0))
            draw_text(screen, "JAMMIN' EATS", 72, WIDTH // 2, HEIGHT // 4, YELLOW)
            draw_text(screen, "Deliver tasty food to hungry customers!", 36, WIDTH // 2, HEIGHT // 3, WHITE)

            # Update and draw buttons
            start_button.update(mouse_pos)
            exit_button.update(mouse_pos)
            start_button.draw(screen)
            exit_button.draw(screen)

            # Draw high score
            draw_text(screen, f"High Score: {high_score}", 36, WIDTH // 2, HEIGHT - 100, WHITE)

        elif game_state == GAME_OVER:
            # Draw game over screen
            screen.blit(game_over_background, (0, 0))
            draw_text(screen, "GAME OVER", 72, WIDTH // 2, HEIGHT // 4, RED)
            draw_text(screen, f"Score: {score}", 48, WIDTH // 2, HEIGHT // 3, WHITE)
            draw_text(screen, f"High Score: {high_score}", 36, WIDTH // 2, HEIGHT // 3 + 50, WHITE)

            # Show stats
            minutes = int(game_time) // 60
            seconds = int(game_time) % 60
            draw_text(screen, f"Time Survived: {minutes:02d}:{seconds:02d}", 36, WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text(screen, f"Deliveries Made: {player.deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 40, WHITE)
            draw_text(screen, f"Customers Missed: {player.missed_deliveries}", 36, WIDTH // 2, HEIGHT // 2 + 80, WHITE)

            # Update and draw restart button
            restart_button.update(mouse_pos)
            restart_button.draw(screen)

        # Update the display
        pygame.display.flip()

    pygame.quit()
    sys.exit()


# Make sure to actually call the main function to start the game
if __name__ == '__main__':
    main()