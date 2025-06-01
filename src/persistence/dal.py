"""
Jammin' Eats Data Access Layer (DAL)

This module provides a clean interface for accessing the game's SQLite database,
handling all database operations through reusable functions.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
import time

# Import logger
try:
    from src.debug.logger import log, log_error
except ImportError:
    def log(message): print(f"[LOG] {message}")
    def log_error(message): print(f"[ERROR] {message}")

# Path to the database file
DB_PATH = Path(__file__).parent.parent.parent / "data" / "jammin.db"

# Cache for frequently accessed data
_cache = {
    'player_settings': None,
    'starting_stock': None,
    'owned_upgrades': None,
    'cache_time': 0
}

# Cache TTL in seconds
CACHE_TTL = 60


@contextmanager
def get_conn():
    """
    Context manager for database connections.
    
    Usage:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
    """
    if not DB_PATH.exists():
        log_error(f"Database file not found: {DB_PATH}")
        # Return a memory database as fallback
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
        return
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        log_error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def _clear_cache(key=None):
    """Clear the cache for a specific key or all keys."""
    global _cache
    if key:
        if key in _cache:
            _cache[key] = None
    else:
        for k in _cache:
            if k != 'cache_time':
                _cache[k] = None
    _cache['cache_time'] = time.time()


def _is_cache_valid(key):
    """Check if the cache for a key is valid."""
    if key not in _cache or _cache[key] is None:
        return False
    if time.time() - _cache['cache_time'] > CACHE_TTL:
        return False
    return True


# ---------- Player Profile Functions ----------

def get_player_profile(player_id=1):
    """Get the player's profile data."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM player_profile WHERE player_id = ?", 
                (player_id,)
            )
            profile = cursor.fetchone()
            if profile:
                return dict(profile)
            else:
                # Create default profile if it doesn't exist
                cursor.execute(
                    "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (?, ?, ?)",
                    (player_id, "Player", 0)
                )
                conn.commit()
                return {"player_id": player_id, "display_name": "Player", "high_score": 0}
    except sqlite3.Error as e:
        log_error(f"Failed to get player profile: {e}")
        # Return default profile as fallback
        return {"player_id": player_id, "display_name": "Player", "high_score": 0}


def update_high_score(player_id, score):
    """Update player's high score if the new score is higher."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE player_profile SET high_score = ? WHERE player_id = ? AND high_score < ?", 
                (score, player_id, score)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        log_error(f"Failed to update high score: {e}")
        return False


# ---------- Game Settings Functions ----------

def fetch_player_settings():
    """Fetch player settings from the database."""
    if _is_cache_valid('player_settings'):
        return _cache['player_settings']
    
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_settings WHERE id = 1")
            settings = cursor.fetchone()
            
            if settings:
                result = dict(settings)
                _cache['player_settings'] = result
                return result
            else:
                # Create default settings if they don't exist
                default_settings = {
                    "id": 1, 
                    "starting_money": 0,
                    "max_stock": 10,
                    "tutorial_mode": True
                }
                cursor.execute(
                    """
                    INSERT INTO player_settings 
                    (id, starting_money, max_stock, tutorial_mode) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (default_settings["id"], default_settings["starting_money"],
                     default_settings["max_stock"], default_settings["tutorial_mode"])
                )
                conn.commit()
                _cache['player_settings'] = default_settings
                return default_settings
    except sqlite3.Error as e:
        log_error(f"Failed to fetch player settings: {e}")
        # Return default settings as fallback
        default_settings = {
            "id": 1, 
            "starting_money": 0,
            "max_stock": 10,
            "tutorial_mode": True
        }
        _cache['player_settings'] = default_settings
        return default_settings


# ---------- Inventory Functions ----------

def fetch_starting_stock():
    """Fetch the starting stock configuration."""
    if _is_cache_valid('starting_stock'):
        return _cache['starting_stock']
    
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT food, qty FROM starting_stock")
            rows = cursor.fetchall()
            
            if rows:
                stock = {row["food"]: row["qty"] for row in rows}
                _cache['starting_stock'] = stock
                return stock
            else:
                # Return default stock if none found in DB
                default_stock = {
                    "Tropical Pizza": 5,
                    "Ska Smoothie": 5,
                    "Island Ice Cream": 5
                }
                # Insert default stock
                for food, qty in default_stock.items():
                    cursor.execute(
                        "INSERT INTO starting_stock (food, qty) VALUES (?, ?)",
                        (food, qty)
                    )
                conn.commit()
                _cache['starting_stock'] = default_stock
                return default_stock
    except sqlite3.Error as e:
        log_error(f"Failed to fetch starting stock: {e}")
        # Return default stock as fallback
        default_stock = {
            "Tropical Pizza": 5,
            "Ska Smoothie": 5,
            "Island Ice Cream": 5
        }
        _cache['starting_stock'] = default_stock
        return default_stock


def fetch_starting_defaults():
    """Fetch starting money and stock configuration."""
    settings = fetch_player_settings()
    stock = fetch_starting_stock()
    return settings["starting_money"], stock


# ---------- Upgrade Functions ----------

def load_owned_upgrades(player_id=1):
    """Load all upgrades owned by the player."""
    if _is_cache_valid('owned_upgrades'):
        return _cache['owned_upgrades']
    
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT upg_id FROM upgrades_owned WHERE player_id = ?",
                (player_id,)
            )
            rows = cursor.fetchall()
            
            if rows:
                owned_upgrades = [row["upg_id"] for row in rows]
                _cache['owned_upgrades'] = owned_upgrades
                return owned_upgrades
            else:
                _cache['owned_upgrades'] = []
                return []
    except sqlite3.Error as e:
        log_error(f"Failed to load owned upgrades: {e}")
        return []


def own_upgrade(player_id, upgrade_id):
    """Record that a player now owns a specific upgrade."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO upgrades_owned (player_id, upg_id, acquired_at) 
                    VALUES (?, ?, ?)
                    """,
                    (player_id, upgrade_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                _clear_cache('owned_upgrades')
                return True
            except sqlite3.IntegrityError:
                # Already owns this upgrade
                return False
    except sqlite3.Error as e:
        log_error(f"Failed to own upgrade: {e}")
        return False


# ---------- Game Run History Functions ----------

def save_run_history(player_id, score, money_earned, missed, duration_sec):
    """Save the history of a game run."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO run_history 
                (player_id, score, money_earned, missed, duration_sec, run_date) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (player_id, score, money_earned, missed, duration_sec, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            
            # Check if this is a new high score
            update_high_score(player_id, score)
            
            return cursor.lastrowid
    except sqlite3.Error as e:
        log_error(f"Failed to save run history: {e}")
        return None


def get_high_scores(limit=10):
    """Get the top high scores from the run history."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT rh.*, pp.display_name 
                FROM run_history rh
                JOIN player_profile pp ON rh.player_id = pp.player_id
                ORDER BY rh.score DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        log_error(f"Failed to get high scores: {e}")
        return []


def get_recent_runs(player_id=1, limit=5):
    """Get the most recent runs for a player."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM run_history 
                WHERE player_id = ? 
                ORDER BY run_date DESC 
                LIMIT ?
                """,
                (player_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        log_error(f"Failed to get recent runs: {e}")
        return []


# ---------- Database Backup Functions ----------

def create_backup():
    """Create a backup of the database."""
    if not DB_PATH.exists():
        log_error("Cannot backup: database file not found")
        return False
    
    try:
        # Create backup directory
        backup_dir = DB_PATH.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"jammin_{timestamp}.db"
        
        # Copy database to backup location
        import shutil
        shutil.copy2(DB_PATH, backup_file)
        
        log(f"Database backed up to {backup_file}")
        return True
    except Exception as e:
        log_error(f"Backup failed: {e}")
        return False


# ---------- Health Check Functions ----------

def check_database_health():
    """Check the health of the database."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            tables = [
                "player_profile", 
                "player_settings", 
                "starting_stock", 
                "upgrades_owned",
                "run_history"
            ]
            
            missing_tables = []
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                log_error(f"Missing tables: {', '.join(missing_tables)}")
                return False, missing_tables
            
            return True, None
    except sqlite3.Error as e:
        log_error(f"Database health check failed: {e}")
        return False, str(e)


# ---------- Tutorial Completion Functions ----------

def is_tutorial_complete(player_id=1):
    """Check if the player has completed the tutorial."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tutorial_complete FROM player_profile WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            return bool(row["tutorial_complete"]) if row else False
    except sqlite3.Error as e:
        log_error(f"Failed to check tutorial completion: {e}")
        return False

def mark_tutorial_complete(player_id=1):
    """Mark the tutorial as complete for a player."""
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE player_profile SET tutorial_complete = 1 WHERE player_id = ?",
                (player_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        log_error(f"Failed to mark tutorial complete: {e}")
        return False
