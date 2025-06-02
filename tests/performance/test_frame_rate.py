"""Performance tests for frame rate and rendering in Jammin' Eats.

These tests ensure the game maintains acceptable performance
even as complexity increases.
"""

import pytest
import time
import pygame
from pytest_benchmark.fixture import BenchmarkFixture
from src.game import Game


@pytest.mark.benchmark(group="rendering")
def test_game_render_performance(benchmark: BenchmarkFixture):
    """Test rendering performance to ensure acceptable frame rates."""
    # Initialize pygame display for rendering
    screen = pygame.Surface((800, 600))
    
    # Create a game instance
    game = Game()
    game.initialize()
    
    # Define the operation to benchmark
    def render_frame():
        game.draw_current_state(screen)
    
    # Run the benchmark
    result = benchmark(render_frame)
    
    # Verify frame time is acceptable (aim for 60+ FPS)
    max_frame_time = 1.0 / 60.0  # 16.67ms for 60 FPS
    assert result.stats.stats.mean < max_frame_time, (
        f"Average frame time ({result.stats.stats.mean * 1000:.2f}ms) exceeds target "
        f"({max_frame_time * 1000:.2f}ms) for 60+ FPS"
    )


@pytest.mark.benchmark(group="update")
def test_game_update_performance(benchmark: BenchmarkFixture):
    """Test game update performance to ensure logic processing is efficient."""
    # Create a game instance
    game = Game()
    game.initialize()
    
    # Define the operation to benchmark
    def update_frame():
        game.update(1/60)  # Update with standard frame time
    
    # Run the benchmark
    result = benchmark(update_frame)
    
    # Verify update time is acceptable (should be a fraction of frame time)
    max_update_time = 1.0 / 120.0  # Half of render budget for 60 FPS
    assert result.stats.stats.mean < max_update_time, (
        f"Average update time ({result.stats.stats.mean * 1000:.2f}ms) exceeds target "
        f"({max_update_time * 1000:.2f}ms)"
    )
