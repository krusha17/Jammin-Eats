"""Unit tests for the game economy in Jammin' Eats.

These tests validate monetary transactions, scoring, and reward systems.
"""

from src.economy.economy_manager import EconomyManager


class TestEconomyManager:
    """Tests for the economy system functionality."""

    def test_delivery_rewards(self):
        """Test that deliveries provide appropriate rewards."""
        # Create economy manager
        economy = EconomyManager()

        # Test basic delivery
        initial_money = economy.money
        reward = economy.process_delivery(difficulty=1)

        assert reward > 0, "Delivery should provide a positive reward"
        assert (
            economy.money == initial_money + reward
        ), "Money should increase by reward amount"
        assert economy.deliveries == 1, "Delivery count should increment"

    def test_difficulty_scaling(self):
        """Test that difficulty properly scales rewards."""
        economy = EconomyManager()

        # Compare rewards at different difficulties
        easy_reward = economy.calculate_reward(difficulty=1)
        medium_reward = economy.calculate_reward(difficulty=2)
        hard_reward = economy.calculate_reward(difficulty=3)

        assert (
            medium_reward > easy_reward
        ), "Higher difficulty should give better rewards"
        assert (
            hard_reward > medium_reward
        ), "Higher difficulty should give better rewards"

    def test_combo_multiplier(self):
        """Test that combos properly multiply rewards."""
        economy = EconomyManager()

        # Set up a combo
        base_reward = economy.calculate_reward(difficulty=1)

        # Process multiple deliveries quickly to build combo
        for _ in range(3):
            economy.process_delivery(difficulty=1)

        # Now combo should be active
        combo_reward = economy.calculate_reward(difficulty=1)

        assert combo_reward > base_reward, "Combo should increase rewards"
        assert economy.combo_multiplier > 1.0, "Combo multiplier should increase"

    def test_combo_decay(self):
        """Test that combos decay over time."""
        economy = EconomyManager()

        # Build up combo
        for _ in range(3):
            economy.process_delivery(difficulty=1)

        initial_multiplier = economy.combo_multiplier
        assert initial_multiplier > 1.0, "Combo multiplier should be active"

        # Simulate time passing
        economy.update(5.0)  # 5 seconds

        assert (
            economy.combo_multiplier < initial_multiplier
        ), "Combo should decay over time"

        # After more time, combo should reset
        economy.update(10.0)  # 10 more seconds
        assert economy.combo_multiplier == 1.0, "Combo should reset after long enough"
