#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jammin' Eats - A food truck game

This is the main entry point for the Jammin' Eats game. It imports and uses
the modular game components from the src directory.
"""

import os
import sys

# Ensure src is in sys.path for both normal and PyInstaller builds
if getattr(sys, "frozen", False):
    # If running as a bundled exe
    src_dir = os.path.join(sys._MEIPASS, "src")
else:
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from core.game import Game


def main():
    print("====== STARTING JAMMIN' EATS GAME ======")

    try:
        # Basic setup before logger is available
        print("Setting up Python path...")

        # Import logger
        print("Importing logger...")
        from src.debug.logger import game_logger

        game_logger.info("=== STARTING JAMMIN' EATS GAME ===")

        # Import critical pygame components
        print("Initializing pygame...")
        import pygame

        pygame.init()
        print(f"Pygame initialized: {pygame.get_init()}")

        # Initialize database
        print("Checking database...")
        from src.persistence.db_init import initialize_database

        db_status = initialize_database()
        print(f"Database initialization status: {db_status}")

        # Initialize game
        print("Creating Game instance...")
        game_logger.info("Creating Game instance")
        game = Game()
        print("Game instance created successfully")

        # Run game loop
        print("Starting game loop...")
        game_logger.info("Starting game loop")
        game.run()

        print("====== GAME EXITED NORMALLY ======")
        game_logger.info("=== GAME EXITED NORMALLY ===")
    except Exception as e:
        print("\n====== FATAL ERROR ======")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")

        try:
            from src.debug.logger import game_logger

            game_logger.critical(f"Fatal error in main: {e}", exc_info=True)
        except ImportError:
            pass  # Logger not available

        import traceback

        traceback.print_exc()
        print("========================")


# Run the game
if __name__ == "__main__":
    main()
