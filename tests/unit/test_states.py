"""Test script for Jammin' Eats game state transitions.

This script provides a controlled environment to test state transitions and
debug the tutorial completion logic. It initializes the game in a simplified
mode and provides debugging commands.
"""

import os
import sys
import time
import traceback

# Add the root directory to the Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
    from src.core.game import Game
    from src.debug.logger import game_logger, setup_logging
    
    # Configure simplified gameplay for testing
    TEST_MODE = True
    USE_BLACK_SCREEN = True
    RESET_TUTORIAL = True
    
    def reset_tutorial_state():
        """Reset the tutorial completion state in the database."""
        try:
            from src.persistence.reset_tutorial import reset_tutorial_completion
            result = reset_tutorial_completion()
            print(f"Tutorial state reset: {result}")
            return result
        except Exception as e:
            print(f"Error resetting tutorial state: {e}")
            traceback.print_exc()
            return False
    
    def init_game(use_black_screen=True, tutorial_mode=False):
        """Initialize the game with testing parameters.
        
        Args:
            use_black_screen: Whether to use the simplified black screen state
            tutorial_mode: Whether to start in tutorial mode
        
        Returns:
            Game instance
        """
        # Initialize pygame
        pygame.init()
        
        # Setup logging first
        setup_logging()
        game_logger.info("=== STATE TRANSITION TEST STARTED ===", "test_states")
        
        try:
            # Create game instance
            game = Game()
            game_logger.info("Game instance created", "test_states")
            
            # Configure game for testing
            game.use_simplified_gameplay = use_black_screen
            game.tutorial_mode = tutorial_mode
            game.money = 0
            game.successful_deliveries = 0
            
            # Log configuration
            game_logger.info(f"Test configuration: simplified={use_black_screen}, tutorial_mode={tutorial_mode}", "test_states")
            
            return game
        except Exception as e:
            game_logger.error(f"Error initializing game: {e}", "test_states", exc_info=True)
            raise
    
    def print_keyboard_commands():
        """Print available keyboard commands for testing."""
        print("\nKEYBOARD COMMANDS:")
        print("------------------")
        print("Arrow keys / WASD:  Move player")
        print("1-4:               Select different foods")
        print("SPACE:             Simulate successful food delivery (+$10)")
        print("ENTER:             Confirm/proceed (when in tutorial complete screen)")
        print("ESC:               Quit the game")
        print("H:                 Show/hide debug info")
        print("\nTUTORIAL COMPLETION:")
        print("Press SPACE repeatedly to simulate 5 deliveries or earn $50 to complete the tutorial.")
        print("------------------\n")
    
    # Main execution
    if __name__ == "__main__":
        # Print header
        print("\n" + "=" * 60)
        print("JAMMIN' EATS - STATE TRANSITION TEST")
        print("=" * 60)
        
        # Reset tutorial if requested
        if RESET_TUTORIAL:
            print("\nResetting tutorial completion state...")
            reset_tutorial_state()
            print("Tutorial reset complete!")
        
        # Print test mode info
        print(f"\nTest Mode: {'ON' if TEST_MODE else 'OFF'}")
        print(f"Black Screen Mode: {'ON' if USE_BLACK_SCREEN else 'OFF'}")
        print(f"Tutorial Mode: {'ON' if RESET_TUTORIAL else 'OFF'}")
        
        # Print keyboard commands
        print_keyboard_commands()
        
        print("\nInitializing game...")
        game = init_game(use_black_screen=USE_BLACK_SCREEN, tutorial_mode=RESET_TUTORIAL)
        
        print("\nStarting game loop...")
        print("Watch the console for logging information.")
        print("\nPress ESC to quit anytime.\n")
        
        # Start the game
        try:
            game.run()
        except Exception as e:
            game_logger.critical(f"Game crashed: {e}", "test_states", exc_info=True)
            print(f"\nGAME CRASHED: {e}")
            traceback.print_exc()
        finally:
            pygame.quit()
            print("\nTest complete. Check logs for details.")
    
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
