import os
import pygame
import sys

# Initialize pygame
pygame.init()
pygame.display.set_mode((100, 100))

# Set up base paths exactly like original main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Test for directory existence
print(f"BASE_DIR: {BASE_DIR} (exists: {os.path.exists(BASE_DIR)})")
print(f"ASSETS_DIR: {ASSETS_DIR} (exists: {os.path.exists(ASSETS_DIR)})")

# Check specific subdirectories
food_dir = os.path.join(ASSETS_DIR, "Food")
print(f"Food directory: {food_dir} (exists: {os.path.exists(food_dir)})")

# List all subdirectories in assets
if os.path.exists(ASSETS_DIR):
    print("\nContents of assets directory:")
    for item in os.listdir(ASSETS_DIR):
        full_path = os.path.join(ASSETS_DIR, item)
        if os.path.isdir(full_path):
            print(f"  {item}/ (directory)")
            # List contents if it's the Food directory
            if item == "Food":
                try:
                    food_items = os.listdir(full_path)
                    print(f"    Contents ({len(food_items)} items):")
                    for food_item in food_items:
                        print(f"      {food_item}")
                except Exception as e:
                    print(f"    Error listing food items: {e}")
        else:
            print(f"  {item} (file)")

# Check for specific food assets
food_types = ["Tropical_Pizza_Slice", "Ska_Smoothie", "Island_Ice_Cream", "Rasta_Rice_Pudding", "Reggae_Rasgulla"]
for food in food_types:
    # Try different potential paths
    paths_to_check = [
        os.path.join(ASSETS_DIR, "Food", food, f"{food}.png"),
        os.path.join(ASSETS_DIR, "Food", f"{food}.png"),
        os.path.join(ASSETS_DIR, "food", food, f"{food}.png"),
        os.path.join(ASSETS_DIR, "food", f"{food}.png")
    ]
    
    print(f"\nChecking paths for {food}:")
    for path in paths_to_check:
        exists = os.path.exists(path)
        print(f"  {path} (exists: {exists})")
        if exists:
            try:
                # Try to load it
                img = pygame.image.load(path)
                print(f"    Successfully loaded image: {img.get_size()}")
            except Exception as e:
                print(f"    Error loading image: {e}")
