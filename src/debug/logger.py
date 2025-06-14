import logging
import sys
from datetime import datetime
from pathlib import Path


class GameLogger:
    """Centralized logging system for Jammin' Eats"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Set up file and console logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"jammin_{timestamp}.log"

        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger("JamminEats")
        self._initialized = True

        # Log startup
        self.logger.info("=" * 60)
        self.logger.info("Jammin' Eats Game Logger Initialized")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 60)

    def debug(self, message, module="General"):
        """Log debug message"""
        self.logger.debug(f"[{module}] {message}")

    def info(self, message, module="General"):
        """Log info message"""
        self.logger.info(f"[{module}] {message}")

    def warning(self, message, module="General"):
        """Log warning message"""
        self.logger.warning(f"[{module}] {message}")

    def error(self, message, module="General", exc_info=False):
        """Log error message"""
        self.logger.error(f"[{module}] {message}", exc_info=exc_info)

    def critical(self, message, module="General", exc_info=True):
        """Log critical error"""
        self.logger.critical(f"[{module}] {message}", exc_info=exc_info)


# Global instance
game_logger = GameLogger()


# Maintain backward compatibility with original functions
def log(msg):
    """Legacy log function"""
    game_logger.info(msg)
    print(f"[LOG] {msg}")


def log_error(msg):
    """Legacy error function"""
    game_logger.error(msg)
    print(f"[ERROR] {msg}")


def log_asset_load(msg):
    """Legacy asset load function"""
    game_logger.debug(msg, "Asset")
    print(f"[ASSET] {msg}")
