"""
Game Persistence Layer

This module provides integration between the Game class and the persistence layer.
It handles loading and saving game state, upgrades, and run history.
"""

from src.persistence.dal import (
    fetch_starting_defaults, load_owned_upgrades, own_upgrade,
    save_run_history, get_high_scores, update_high_score,
    get_player_profile, create_backup
)
from src.debug.logger import log, log_error

class GamePersistence:
    """
    Handles persistence operations for the Game class.
    
    This class is responsible for loading initial game state from the database,
    saving game history when a run ends, and managing persistent upgrades.
    """
    
    def __init__(self, player_id=1):
        """Initialize the game persistence manager."""
        self.player_id = player_id
        self._load_player_profile()
    
    def _load_player_profile(self):
        """Load the player profile from the database."""
        try:
            self.player_profile = get_player_profile(self.player_id)
            log(f"Loaded player profile: {self.player_profile.get('display_name')} (High Score: {self.player_profile.get('high_score')})")
        except Exception as e:
            log_error(f"Failed to load player profile: {e}")
            self.player_profile = {"player_id": self.player_id, "display_name": "Player", "high_score": 0}
    
    def get_high_score(self):
        """Get the player's high score from their profile."""
        return self.player_profile.get("high_score", 0)
    
    def get_starting_values(self):
        """
        Get starting values for a new game from the database.
        
        Returns:
            tuple: (starting_money, starting_stock)
        """
        try:
            money, stock = fetch_starting_defaults()
            log(f"Loaded starting values: ${money}, stock items: {len(stock)}")
            return money, stock
        except Exception as e:
            log_error(f"Failed to get starting values: {e}")
            # Return fallback defaults
            from src.core.constants import STARTING_MONEY, STARTING_STOCK
            return STARTING_MONEY, STARTING_STOCK
    
    def get_owned_upgrades(self):
        """
        Get list of upgrades owned by the player.
        
        Returns:
            list: List of upgrade IDs owned by the player
        """
        try:
            upgrades = load_owned_upgrades(self.player_id)
            log(f"Loaded {len(upgrades)} owned upgrades")
            return upgrades
        except Exception as e:
            log_error(f"Failed to load owned upgrades: {e}")
            return []
    
    def save_upgrade_purchase(self, upgrade_id):
        """
        Save a newly purchased upgrade to the database.
        
        Args:
            upgrade_id: ID of the upgrade purchased
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            success = own_upgrade(self.player_id, upgrade_id)
            if success:
                log(f"Saved upgrade purchase: {upgrade_id}")
            return success
        except Exception as e:
            log_error(f"Failed to save upgrade purchase: {e}")
            return False
    
    def save_game_results(self, score, money_earned, missed, duration_sec):
        """
        Save game run results to the database.
        
        Args:
            score: Final score for the game run
            money_earned: Money earned during the run
            missed: Number of missed deliveries
            duration_sec: Duration of the run in seconds
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            run_id = save_run_history(
                self.player_id, score, money_earned, missed, duration_sec
            )
            if run_id:
                log(f"Saved game results: Score {score}, Run ID {run_id}")
                
                # Check if this is a new high score and update player profile
                if score > self.player_profile.get("high_score", 0):
                    update_high_score(self.player_id, score)
                    self.player_profile["high_score"] = score
                    log(f"New high score set: {score}")
                return True
            return False
        except Exception as e:
            log_error(f"Failed to save game results: {e}")
            return False
    
    def get_leaderboard(self, limit=10):
        """
        Get the high score leaderboard.
        
        Args:
            limit: Maximum number of high scores to retrieve
            
        Returns:
            list: List of high score entries
        """
        try:
            scores = get_high_scores(limit)
            return scores
        except Exception as e:
            log_error(f"Failed to get leaderboard: {e}")
            return []
    
    def create_db_backup(self):
        """Create a backup of the database."""
        try:
            success = create_backup()
            if success:
                log("Database backup created successfully")
            else:
                log_error("Failed to create database backup")
            return success
        except Exception as e:
            log_error(f"Error creating database backup: {e}")
            return False
