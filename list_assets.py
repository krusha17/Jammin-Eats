import os
import sys

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def explore_directory(path, indent=0):
    """Recursively explore a directory and print its contents"""
    if not os.path.exists(path):
        print(f"{' ' * indent}Directory does not exist: {path}")
        return
        
    print(f"{' ' * indent}Exploring: {path}")
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print(f"{' ' * (indent+2)}📁 {item}/")
                # Recursively explore subdirectories, but limit depth
                if indent < 8:  # Limit recursion depth
                    explore_directory(item_path, indent + 4)
            else:
                print(f"{' ' * (indent+2)}📄 {item}")
    except Exception as e:
        print(f"{' ' * indent}Error exploring {path}: {e}")

# Check if assets directory exists
if not os.path.exists(ASSETS_DIR):
    print(f"Assets directory not found: {ASSETS_DIR}")
    sys.exit(1)

# Explore the assets directory structure
print(f"Base directory: {BASE_DIR}")
print(f"Assets directory: {ASSETS_DIR}")
print("\nAssets Directory Structure:")
explore_directory(ASSETS_DIR)

# Specifically explore the Food directory
food_dir = os.path.join(ASSETS_DIR, "Food")
print("\nFood Directory Structure (case-sensitive):")
explore_directory(food_dir)

# Also check for lowercase "food" directory
food_dir_lower = os.path.join(ASSETS_DIR, "food")
print("\nChecking for lowercase 'food' directory:")
if os.path.exists(food_dir_lower) and food_dir_lower != food_dir:
    print(f"Lowercase 'food' directory found at: {food_dir_lower}")
    explore_directory(food_dir_lower)
else:
    print(f"No separate lowercase 'food' directory found")
