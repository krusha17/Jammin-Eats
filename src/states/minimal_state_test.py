"""
Minimal test script for Jammin' Eats state transitions.
This script avoids complex logging and focuses on core functionality.
"""

import os
import sys
import traceback

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def check_imports():
    """Test importing critical modules."""
    print("\n=== IMPORT TEST ===")

    modules_to_test = [
        "pygame",
        "src.core.game",
        "src.states.title_state",
        "src.states.tutorial_state",
        "src.states.tutorial_complete_state",
        "src.persistence.dal",
        "src.persistence.db_init",
    ]

    success_count = 0
    for module in modules_to_test:
        try:
            print(f"Importing {module}...", end="")
            __import__(module)
            print(" SUCCESS")
            success_count += 1
        except Exception as e:
            print(f" FAILED: {e}")
            traceback.print_exc()

    print(f"\nSuccessfully imported {success_count}/{len(modules_to_test)} modules")


def check_database():
    """Test database connectivity."""
    print("\n=== DATABASE TEST ===")

    try:
        from src.persistence.db_init import DB_PATH

        print(f"Database path: {DB_PATH}")

        if os.path.exists(DB_PATH):
            print(f"✓ Database file exists ({os.path.getsize(DB_PATH)} bytes)")

            # Try to connect and check schema
            import sqlite3

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables in database: {[t[0] for t in tables]}")

            # Check player_profile schema
            cursor.execute("PRAGMA table_info(player_profile)")
            columns = cursor.fetchall()
            print(f"player_profile columns: {[col[1] for col in columns]}")

            # Check tutorial status
            cursor.execute(
                "SELECT id, tutorial_complete FROM player_profile WHERE id=1"
            )
            result = cursor.fetchone()
            if result:
                print(f"Player 1 tutorial status: {bool(result[1])}")
            else:
                print("No player with id=1 found")

            conn.close()
        else:
            print("✗ Database file does not exist")
    except Exception as e:
        print(f"Database test error: {e}")
        traceback.print_exc()


def check_game_initialization():
    """Test game initialization."""
    print("\n=== GAME INITIALIZATION TEST ===")

    try:
        import pygame

        pygame.init()

        from src.core.game import Game

        print("Creating Game instance...", end="")
        game = Game()
        print(" SUCCESS")

        print(f"Tutorial mode: {getattr(game, 'tutorial_mode', 'Not set')}")
        print(f"Game state: {getattr(game, 'game_state', 'Not set')}")

        # Test state creation
        try:
            from src.states.title_state import TitleState

            print("Creating TitleState...", end="")
            state = TitleState(game)
            print(" SUCCESS")

            # Check menu items
            print(f"Menu items: {len(getattr(state, 'menu_items', []))}")
            for i, item in enumerate(getattr(state, "menu_items", [])):
                enabled = item.get("enabled", False)
                print(
                    f"  {i+1}. {item.get('text', 'Unknown')} - {'Enabled' if enabled else 'Disabled'}"
                )

        except Exception as e:
            print(f" FAILED: {e}")
            traceback.print_exc()

        # Test black screen state
        try:
            print("Importing BlackScreenGameplayState...", end="")
            from src.states.black_screen_gameplay_state import BlackScreenGameplayState

            print(" SUCCESS")

            print("Creating BlackScreenGameplayState...", end="")
            _ = BlackScreenGameplayState(game)
            print(" SUCCESS")
        except Exception as e:
            print(f" FAILED: {e}")
            traceback.print_exc()

        pygame.quit()
    except Exception as e:
        print(f"Game initialization error: {e}")
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("JAMMIN' EATS - MINIMAL STATE TEST")
    print("=" * 60)

    check_imports()
    check_database()
    check_game_initialization()

    print("\n=== TEST COMPLETE ===\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nCritical error in main: {e}")
        traceback.print_exc()
