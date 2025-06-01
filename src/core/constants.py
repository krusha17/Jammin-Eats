import os
import pygame

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Project directories - Match exactly how paths were calculated in the original main.py
# This is critical for asset loading to work consistently
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Gets to project root

# Use exactly the same relative paths as in the original main.py
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MAP_DIR = os.path.join(ASSETS_DIR, "Maps", "level1")

# Print basic path information, same as in original main.py
print(f"Assets directory: {ASSETS_DIR}")
print(f"Map directory: {MAP_DIR}")

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

# Inventory / stock (units in player's truck)
STARTING_STOCK = {
    "Tropical Pizza Slice": 5,
    "Ska Smoothie": 5,
    "Island Ice Cream": 5,
    "Rasta Rice Pudding": 5,
}
MAX_STOCK = 10  # for future upgrades

# Food prices for economy
FOOD_PRICES = {
    "Tropical Pizza Slice": {
        "buy_price": 2,
        "sell_price": 5
    },
    "Ska Smoothie": {
        "buy_price": 1,
        "sell_price": 3
    },
    "Island Ice Cream": {
        "buy_price": 1,
        "sell_price": 4
    },
    "Rasta Rice Pudding": {
        "buy_price": 2,
        "sell_price": 4
    }
}

# ---------------- Tutorial toggle & penalties ----------------
TUTORIAL_MODE = False          # Flip to True during onboarding
WRONG_FOOD_PENALTY_MONEY = 2   # Dollars lost per bad throw
WRONG_FOOD_PENALTY_SCORE = 5   # Points lost per bad throw
MAX_MISSED_DELIVERIES = 3      # Game-over after this many

# ---------------- Game economy defaults ----------------
STARTING_MONEY = 0             # Starting cash for each new game
