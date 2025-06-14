"""Performance tests for memory usage in Jammin' Eats.

These tests monitor memory consumption during gameplay
to prevent memory leaks and excessive resource usage.
"""

import gc
import psutil
import pygame
import time
from src.game import Game


def test_memory_stability():
    """Test that memory usage remains stable during extended gameplay."""
    # Get current process
    process = psutil.Process()

    # Force garbage collection to get accurate baseline
    gc.collect()

    # Record initial memory usage
    initial_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB

    # Initialize pygame display for rendering
    screen = pygame.Surface((800, 600))

    # Create a game instance
    game = Game()
    game.initialize()

    # Run game for multiple frames
    frame_count = 100
    for _ in range(frame_count):
        # Simulate game loop
        game.update(1 / 60)
        game.draw_current_state(screen)

        # Add slight delay to simulate real gameplay
        time.sleep(0.01)

    # Force garbage collection again
    gc.collect()

    # Measure memory after gameplay
    final_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB

    # Calculate memory growth
    memory_growth = final_memory - initial_memory

    # Assert memory growth is within acceptable limits
    # Allow 5MB of growth over 100 frames as a conservative limit
    max_allowed_growth = 5.0  # MB

    assert memory_growth < max_allowed_growth, (
        f"Memory growth ({memory_growth:.2f}MB) exceeds limit ({max_allowed_growth:.2f}MB) "
        f"after {frame_count} frames. Possible memory leak."
    )

    print(
        f"Memory usage: Initial={initial_memory:.2f}MB, Final={final_memory:.2f}MB, "
        f"Growth={memory_growth:.2f}MB over {frame_count} frames"
    )


def test_asset_loading_memory():
    """Test that asset loading doesn't cause excessive memory usage."""
    process = psutil.Process()

    # Force garbage collection
    gc.collect()

    # Record memory before asset loading
    before_memory = process.memory_info().rss / (1024 * 1024)  # MB

    # Create game instance (which should load assets)
    game = Game()
    game.initialize()

    # Force garbage collection again
    gc.collect()

    # Measure memory after asset loading
    after_memory = process.memory_info().rss / (1024 * 1024)  # MB

    # Calculate memory used for assets
    asset_memory = after_memory - before_memory

    # Print asset memory usage for reference
    print(f"Asset loading memory usage: {asset_memory:.2f}MB")

    # Assert memory usage is reasonable (adjust based on your asset sizes)
    max_asset_memory = 50.0  # MB - adjust based on expected asset size
    assert (
        asset_memory < max_asset_memory
    ), f"Asset loading uses {asset_memory:.2f}MB, which exceeds the limit of {max_asset_memory:.2f}MB"
