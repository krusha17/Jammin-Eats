import os
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We need to make sure we're using the existing assets in the main project directory
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAP_DIR = os.path.join(ASSETS_DIR, "Maps", "level1")

# Print paths for debugging
print(f"Base directory: {BASE_DIR}")
print(f"Assets directory: {ASSETS_DIR}")
print(f"Map directory: {MAP_DIR}")
print(f"Assets directory exists: {os.path.exists(ASSETS_DIR)}")
if os.path.exists(ASSETS_DIR):
    print(f"Assets contents: {os.listdir(ASSETS_DIR)}")
else:
    print("Warning: Assets directory not found! Using fallbacks.")

# Set up the game window
WIDTH, HEIGHT = 768, 768
FPS = 60

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game variables
CUSTOMER_SPAWN_RATE = 5  # seconds
