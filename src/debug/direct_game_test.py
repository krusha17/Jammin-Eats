"""
Simple, direct test of game state transitions without complex logging
"""
import os
import sys
import pygame
from pygame.locals import *

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Jammin' Eats - State Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    print("\n=== LOADING GAME ===")
    
    # Import game
    try:
        from src.core.game import Game
        print("✓ Game module imported")
    except Exception as e:
        print(f"✗ Failed to import Game: {e}")
        return
    
    # Import database functions
    try:
        from src.persistence.dal import is_tutorial_complete, mark_tutorial_complete
        print("✓ Database functions imported")
        
        # Reset tutorial
        print("Resetting tutorial completion...")
        from src.persistence.db_init import initialize_database
        try:
            with open("C:/Users/jerom/Jammin-Eats/data/jammin.db", "r+") as f:
                pass  # Just checking we can access it
            print("✓ Database is accessible")
        except Exception as e:
            print(f"✗ Database access error: {e}")
            
        # Check tutorial status
        status = is_tutorial_complete(1)
        print(f"Tutorial complete status: {status}")
        
    except Exception as e:
        print(f"✗ Database setup error: {e}")
    
    # Create game instance with error handling
    game = None
    try:
        print("\nCreating Game instance...")
        game = Game()
        print(f"✓ Game created with state: {type(game.game_state).__name__ if hasattr(game, 'game_state') else None}")
    except Exception as e:
        print(f"✗ Failed to create game: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check if needed methods exist
    methods_to_check = [
        'draw_current_state',
        'update',
        'handle_events',
        'run',
        'change_state'
    ]
    
    print("\nChecking for required methods:")
    for method in methods_to_check:
        if hasattr(game, method):
            print(f"✓ Method exists: {method}")
        else:
            print(f"✗ Missing method: {method}")
    
    # Try to run the game with black screen state
    print("\nStarting game with simplified state...")
    try:
        game.use_simplified_gameplay = True  # Use black screen gameplay
        game.tutorial_mode = True  # Start with tutorial
        
        # Main game loop with manual implementation for testing
        running = True
        debug_active = True
        print("\nGame loop starting. Press ESC to quit, T to toggle tutorial mode")
        
        # Debug info display function
        def show_debug_info():
            lines = [
                f"FPS: {clock.get_fps():.1f}",
                f"Game State: {type(game.game_state).__name__ if hasattr(game, 'game_state') else 'None'}",
                f"Tutorial Mode: {getattr(game, 'tutorial_mode', False)}",
                f"Tutorial Completed: {getattr(game, 'tutorial_completed', False)}",
                f"Money: ${getattr(game, 'money', 0)}",
                f"Deliveries: {getattr(game, 'successful_deliveries', 0)}"
            ]
            
            # Draw black background for debug text
            debug_surf = pygame.Surface((300, len(lines) * 25 + 10))
            debug_surf.fill((0, 0, 0))
            debug_surf.set_alpha(200)
            screen.blit(debug_surf, (10, 10))
            
            # Draw debug text
            for i, line in enumerate(lines):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (20, 20 + i * 25))
            
            # Draw keyboard controls
            controls = [
                "ESC: Quit",
                "T: Toggle Tutorial",
                "C: Mark Tutorial Complete",
                "R: Reset Tutorial",
                "SPACE: Add $10 / Delivery",
                "D: Debug Info"
            ]
            
            # Draw background for controls
            ctrl_surf = pygame.Surface((250, len(controls) * 25 + 10))
            ctrl_surf.fill((0, 0, 0))
            ctrl_surf.set_alpha(200)
            screen.blit(ctrl_surf, (500, 10))
            
            # Draw control text
            for i, line in enumerate(controls):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (510, 20 + i * 25))
        
        # Main loop
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                        
                    elif event.key == K_t:
                        # Toggle tutorial mode
                        if hasattr(game, 'tutorial_mode'):
                            game.tutorial_mode = not game.tutorial_mode
                            print(f"Tutorial mode: {game.tutorial_mode}")
                        
                    elif event.key == K_c:
                        # Mark tutorial complete
                        print("Marking tutorial complete...")
                        try:
                            result = mark_tutorial_complete(1)
                            status = is_tutorial_complete(1)
                            print(f"Tutorial marked complete: {result}, Status: {status}")
                            if hasattr(game, 'tutorial_completed'):
                                game.tutorial_completed = True
                        except Exception as e:
                            print(f"Error marking tutorial complete: {e}")
                    
                    elif event.key == K_r:
                        # Reset tutorial
                        print("Resetting tutorial...")
                        try:
                            # Manual DB update to reset
                            import sqlite3
                            conn = sqlite3.connect("data/jammin.db")
                            conn.execute("UPDATE player_profile SET tutorial_complete = 0 WHERE id = 1")
                            conn.commit()
                            conn.close()
                            status = is_tutorial_complete(1)
                            print(f"Tutorial reset, Status: {status}")
                            if hasattr(game, 'tutorial_completed'):
                                game.tutorial_completed = False
                        except Exception as e:
                            print(f"Error resetting tutorial: {e}")
                    
                    elif event.key == K_SPACE:
                        # Add money and deliveries for testing
                        if hasattr(game, 'money'):
                            game.money += 10
                            print(f"Money increased to ${game.money}")
                        
                        if hasattr(game, 'successful_deliveries'):
                            game.successful_deliveries += 1
                            print(f"Deliveries increased to {game.successful_deliveries}")
                    
                    elif event.key == K_d:
                        # Toggle debug info
                        debug_active = not debug_active
                        print(f"Debug info: {debug_active}")
                    
                # Handle game's event handling if available
                if hasattr(game, 'handle_events'):
                    game.handle_events(event)
            
            # Update game logic
            dt = clock.tick(60) / 1000.0  # Convert to seconds
            if hasattr(game, 'update'):
                game.update(dt)
            
            # Draw the game
            screen.fill((0, 0, 0))  # Black background
            
            # Use game's drawing if available
            if hasattr(game, 'draw_current_state'):
                game.draw_current_state(screen)
            else:
                # Fallback drawing
                text = font.render("Game State Test", True, (255, 255, 255))
                screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 
                                   screen.get_height() // 2 - text.get_height() // 2))
            
            # Draw debug info if enabled
            if debug_active:
                show_debug_info()
            
            # Update display
            pygame.display.flip()
        
    except Exception as e:
        print(f"Error during game execution: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    pygame.quit()
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    print("\nJAMMIN' EATS - DIRECT GAME TEST")
    print("===============================")
    try:
        run_test()
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
