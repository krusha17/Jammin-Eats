"""
Debug version of the Jammin' Eats game launcher with enhanced logging.
This will run the game with detailed console output to diagnose state transitions.
"""

import os
import logging
import pygame

# Configure enhanced logging before importing game modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
)

# Now import the game
try:
    from src.core.game import Game
    from src.debug.logger import game_logger
except ImportError:
    # Try direct import as fallback
    from core.game import Game
    from debug.logger import game_logger

def main():
    """Enhanced debug entry point for Jammin' Eats."""
    game_logger.info("=== STARTING DEBUG GAME ===")
    game_logger.info("Pygame version: " + pygame.version.ver)
    
    # Create and run game with extra debug
    try:
        game = Game()
        game_logger.info("Game instance created successfully")
        
        # Enable all debug flags
        game.debug_mode = True
        if hasattr(game, 'persistence'):
            game_logger.debug(f"Game persistence initialized: {game.persistence}")
        else:
            game_logger.warning("Game persistence not available")
        
        # Print state of tutorial flag
        game_logger.info(f"Tutorial mode: {game.tutorial_mode}")
        
        # Run the game
        game_logger.info("Starting game...")
        game.run()
        game_logger.info("Game loop exited normally")
    except Exception as e:
        game_logger.critical(f"Game crashed: {e}", exc_info=True)
    finally:
        pygame.quit()
        game_logger.info("=== GAME EXITED ===")

if __name__ == "__main__":
    main()
