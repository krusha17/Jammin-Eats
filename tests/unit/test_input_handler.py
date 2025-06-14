"""Unit tests for the input handler in Jammin' Eats.

These tests validate input validation, rate limiting, and security features.
"""

import time
from src.input.input_validator import InputValidator


class TestInputValidator:
    """Tests for the input validation system."""

    def test_valid_key_validation(self):
        """Test that valid keys are accepted."""
        validator = InputValidator()
        current_time = time.time()

        # Test all valid keys
        for key in InputValidator.VALID_KEYS:
            assert validator.validate_key_input(key, current_time) is True

    def test_invalid_key_rejection(self):
        """Test that invalid keys are rejected."""
        validator = InputValidator()
        current_time = time.time()

        # Test some invalid keys
        invalid_keys = ["a", "z", "1", "invalid_key", "", None]
        for key in invalid_keys:
            if key is not None:  # Skip None which would cause an exception
                assert validator.validate_key_input(key, current_time) is False

    def test_input_rate_limiting(self):
        """Test that inputs are properly rate-limited."""
        validator = InputValidator()
        current_time = time.time()

        # First key press should be accepted
        assert validator.validate_key_input("space", current_time) is True

        # Immediate repeat should be rejected (rate limiting)
        assert validator.validate_key_input("space", current_time) is False

        # Different key should still be accepted
        assert validator.validate_key_input("enter", current_time) is True

        # After waiting, the key should be accepted again
        new_time = current_time + InputValidator.MAX_INPUT_RATE + 0.01
        assert validator.validate_key_input("space", new_time) is True

    def test_name_sanitization(self):
        """Test that player names are properly sanitized."""
        validator = InputValidator()

        # Valid names should be returned unchanged
        valid_names = ["Player1", "Test Name", "player-name"]
        for name in valid_names:
            assert validator.sanitize_player_name(name) == name

        # Names with invalid characters should be sanitized
        assert (
            validator.sanitize_player_name("Player;DROP TABLE scores;")
            == "PlayerDROP TABLE scores"
        )

        # Test name length limits
        assert (
            validator.sanitize_player_name("") is None
        ), "Empty name should be rejected"
        long_name = "A" * 30
        sanitized = validator.sanitize_player_name(long_name)
        assert sanitized is not None, "Long names should be truncated, not rejected"
        assert len(sanitized) <= 20, "Name should be within length limits"
