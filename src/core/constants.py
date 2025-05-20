import os
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAP_DIR = os.path.join(ASSETS_DIR, "Maps", "level1")

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
