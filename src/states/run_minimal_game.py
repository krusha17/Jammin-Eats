"""
Minimal launcher script for Jammin' Eats with focused error reporting
"""

import os
import sys
import traceback

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Disable pygame welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


def main():
    """Run a minimal version of the game focusing on state transitions."""
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Jammin' Eats - Minimal Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    print("\n=== JAMMIN' EATS MINIMAL LAUNCHER ===")
    print("Testing core functionality with state transitions")

    # 1. Check database setup
    print("\n-- Database Check --")
    try:
        from src.persistence.db_init import DB_PATH

        print(f"Database path: {DB_PATH}")

        if os.path.exists(DB_PATH):
            print("✓ Database file exists")

            # Check for player_profile table
            import sqlite3

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='player_profile'"
            )
            if cursor.fetchone():
                print("✓ player_profile table exists")

                # Check for necessary columns
                cursor.execute("PRAGMA table_info(player_profile)")
                columns = [col[1] for col in cursor.fetchall()]
                print(f"Columns: {columns}")

                if "id" in columns and "tutorial_complete" in columns:
                    print("✓ Schema looks correct")
                else:
                    print("✗ Schema missing expected columns")

                # Check for player record
                cursor.execute(
                    "SELECT id, tutorial_complete FROM player_profile WHERE id=1"
                )
                result = cursor.fetchone()
                if result:
                    print(f"Player 1 tutorial status: {bool(result[1])}")
                else:
                    print("Creating default player record...")
                    cursor.execute(
                        "INSERT INTO player_profile (id, name, tutorial_complete) VALUES (1, 'Player', 0)"
                    )
                    conn.commit()
                    print("✓ Created player record")
            else:
                print("✗ player_profile table missing")

            conn.close()
        else:
            print(f"✗ Database file missing: {DB_PATH}")
            data_dir = os.path.dirname(DB_PATH)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"✓ Created data directory: {data_dir}")

            # Initialize the database
            from src.persistence.db_init import initialize_database

            result = initialize_database()
            print(f"Database initialization: {result}")
    except Exception as e:
        print(f"Database error: {e}")
        traceback.print_exc()

    # 2. Create Game instance
    print("\n-- Game Instance --")
    try:
        from src.core.game import Game

        game = Game()
        print("✓ Game instance created successfully")

        # Check if critical methods exist
        methods = ["run", "draw_current_state", "update", "handle_events"]
        for method in methods:
            if hasattr(game, method) and callable(getattr(game, method)):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing or not callable")

    except Exception as e:
        print(f"Game creation error: {e}")
        traceback.print_exc()
        return

    # 3. Run a simplified game loop
    print("\n-- Running Game --")

    # Configure game for testing
    game.use_simplified_gameplay = True
    game.tutorial_mode = True
    print("Game configured for tutorial mode with simplified gameplay")

    print("\nControls:")
    print("  SPACE: Add $10 and a delivery")
    print("  T: Toggle tutorial mode")
    print("  R: Reset tutorial")
    print("  ESC: Quit")

    print("\nStarting game loop...")

    # Show a debug overlay
    def draw_debug_overlay():
        # Create a semi-transparent surface
        overlay = pygame.Surface((400, 200))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (10, 10))

        # Show debug info
        lines = [
            f"Current state: {type(game.game_state).__name__ if hasattr(game, 'game_state') else 'Unknown'}",
            f"Tutorial mode: {getattr(game, 'tutorial_mode', False)}",
            f"Tutorial completed: {getattr(game, 'tutorial_completed', False)}",
            f"Money: ${getattr(game, 'money', 0)}",
            f"Deliveries: {getattr(game, 'successful_deliveries', 0)}",
            "Press SPACE to add $10 and delivery",
            "Press ESC to quit",
        ]

        y = 20
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, y))
            y += 30

    # Run a basic game loop
    running = True
    try:
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Add money and delivery for testing tutorial completion
                        if hasattr(game, "money"):
                            game.money += 10
                        if hasattr(game, "successful_deliveries"):
                            game.successful_deliveries += 1
                        print(
                            f"Money: ${getattr(game, 'money', 0)}, Deliveries: {getattr(game, 'successful_deliveries', 0)}"
                        )
                    elif event.key == pygame.K_t:
                        # Toggle tutorial mode
                        game.tutorial_mode = not getattr(game, "tutorial_mode", False)
                        print(f"Tutorial mode: {game.tutorial_mode}")
                    elif event.key == pygame.K_r:
                        # Reset tutorial
                        try:
                            from src.persistence.dal import mark_tutorial_complete

                            # First mark it complete to test both functions
                            mark_tutorial_complete(1)
                            # Then reset tutorial completion
                            import sqlite3

                            conn = sqlite3.connect(DB_PATH)
                            conn.execute(
                                "UPDATE player_profile SET tutorial_complete = 0 WHERE id = 1"
                            )
                            conn.commit()
                            conn.close()
                            print("Tutorial status reset")
                        except Exception as e:
                            print(f"Error resetting tutorial: {e}")

                # Pass event to game
                if hasattr(game, "handle_events"):
                    game.handle_events(event)

            # Update game (call game.update if it exists)
            dt = clock.tick(60) / 1000.0  # Convert to seconds
            if hasattr(game, "update"):
                game.update(dt)

            # Clear screen
            screen.fill((0, 0, 0))

            # Draw game (call game.draw_current_state if it exists)
            if hasattr(game, "draw_current_state"):
                try:
                    game.draw_current_state(screen)
                except Exception as e:
                    text = font.render(f"Draw error: {str(e)}", True, (255, 0, 0))
                    screen.blit(text, (20, 20))
                    print(f"Error drawing game: {e}")
            else:
                text = font.render(
                    "draw_current_state method missing", True, (255, 0, 0)
                )
                screen.blit(text, (20, 20))

            # Draw debug overlay
            draw_debug_overlay()

            # Update display
            pygame.display.flip()

    except Exception as e:
        print(f"Game loop error: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()
        print("\nGame closed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
