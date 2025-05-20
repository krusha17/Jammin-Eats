import pygame
import sys
import time
import os

# Add the project root to the Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import our game modules
from src.core.game import Game
from src.debug.debug_tools import toggle_debug_mode, install_exception_handler, log_performance

# Install the global exception handler for better error reporting
install_exception_handler()

# Initialize performance monitoring
start_time = time.time()
log_performance("Module imports completed", start_time)

def main():
    """Main entry point for the game"""
    try:
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create and run the game
        game = Game()
        
        # Performance output
        init_time = time.time() - start_time
        print(f"Game initialized in {init_time:.2f} seconds")
        
        # Start the game loop
        game.run()
        
    except Exception as e:
        # Print detailed error information for debugging
        import traceback
        print("\n==== ERROR DETAILS ====")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTraceback (most recent call last):")
        traceback.print_exc()
        print("==== END ERROR DETAILS ====")

# Run the game if this script is executed directly
if __name__ == '__main__':
    main()
