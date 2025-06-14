"""
Unit tests for the Data Access Layer (DAL)
Uses in-memory SQLite database for testing
"""

import sys
from pathlib import Path

# Add the project root to the Python path for importing modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import sqlite3  # noqa: E402
import time  # noqa: E402
import unittest  # noqa: E402
from unittest.mock import patch  # noqa: E402

from src.persistence.dal import (  # noqa: E402
    get_player_profile,
    update_high_score,
    fetch_player_settings,
    fetch_starting_stock,
    fetch_starting_defaults,
    load_owned_upgrades,
    own_upgrade,
    save_run_history,
    get_high_scores,
    get_recent_runs,
    _cache,
)


class TestDAL(unittest.TestCase):
    """Test cases for the Data Access Layer"""

    def setUp(self):
        """Set up the test environment before each test method"""
        # Use an in-memory database for testing
        self.patcher = patch("src.persistence.dal.get_conn")
        self.mock_get_conn = self.patcher.start()
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.mock_get_conn.return_value.__enter__.return_value = self.conn

        # Create the necessary tables for testing
        self._create_test_tables()

        # Clear the cache
        for key in _cache:
            if key != "cache_time":
                _cache[key] = None
        _cache["cache_time"] = time.time()

    def tearDown(self):
        """Clean up the test environment after each test method"""
        self.conn.close()
        self.patcher.stop()

    def _create_test_tables(self):
        """Create test tables in the in-memory database"""
        self.conn.executescript(
            """
        -- Player Profile table
        CREATE TABLE player_profile (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT DEFAULT 'Player',
            high_score INTEGER DEFAULT 0
        );
        
        -- Player Settings table
        CREATE TABLE player_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            starting_money INTEGER DEFAULT 0,
            max_stock INTEGER DEFAULT 10,
            tutorial_mode BOOLEAN DEFAULT 1
        );
        
        -- Starting Stock table
        CREATE TABLE starting_stock (
            food TEXT PRIMARY KEY,
            qty INTEGER DEFAULT 5,
            CONSTRAINT positive_qty CHECK (qty >= 0)
        );
        
        -- Upgrades Owned table
        CREATE TABLE upgrades_owned (
            player_id INTEGER,
            upg_id TEXT,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (player_id, upg_id),
            FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
        );
        
        -- Run History table
        CREATE TABLE run_history (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            score INTEGER DEFAULT 0,
            money_earned INTEGER DEFAULT 0,
            missed INTEGER DEFAULT 0,
            duration_sec REAL DEFAULT 0.0,
            run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES player_profile(player_id)
        );
        """
        )
        self.conn.commit()

    def test_get_player_profile_existing(self):
        """Test getting an existing player profile"""
        # Create a test player profile
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (1, 'TestPlayer', 100)"
        )
        self.conn.commit()

        # Test retrieving the profile
        profile = get_player_profile(1)
        self.assertEqual(profile["player_id"], 1)
        self.assertEqual(profile["display_name"], "TestPlayer")
        self.assertEqual(profile["high_score"], 100)

    def test_get_player_profile_nonexistent(self):
        """Test getting a non-existent player profile creates default"""
        # Test retrieving a non-existent profile
        profile = get_player_profile(2)
        self.assertEqual(profile["player_id"], 2)
        self.assertEqual(profile["display_name"], "Player")
        self.assertEqual(profile["high_score"], 0)

        # Check that the profile was created in the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM player_profile WHERE player_id = 2")
        db_profile = cursor.fetchone()
        self.assertIsNotNone(db_profile)
        self.assertEqual(dict(db_profile)["display_name"], "Player")

    def test_update_high_score(self):
        """Test updating a player's high score"""
        # Create a test player profile
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (1, 'TestPlayer', 100)"
        )
        self.conn.commit()

        # Test updating with a higher score
        result = update_high_score(1, 150)
        self.assertTrue(result)

        # Check that the high score was updated
        cursor = self.conn.cursor()
        cursor.execute("SELECT high_score FROM player_profile WHERE player_id = 1")
        high_score = cursor.fetchone()[0]
        self.assertEqual(high_score, 150)

        # Test updating with a lower score (should not update)
        result = update_high_score(1, 120)
        self.assertFalse(result)

        # Check that the high score was not updated
        cursor.execute("SELECT high_score FROM player_profile WHERE player_id = 1")
        high_score = cursor.fetchone()[0]
        self.assertEqual(high_score, 150)

    def test_fetch_player_settings_existing(self):
        """Test fetching existing player settings"""
        # Create test settings
        self.conn.execute(
            "INSERT INTO player_settings (id, starting_money, max_stock, tutorial_mode) VALUES (1, 50, 15, 0)"
        )
        self.conn.commit()

        # Test retrieving the settings
        settings = fetch_player_settings()
        self.assertEqual(settings["id"], 1)
        self.assertEqual(settings["starting_money"], 50)
        self.assertEqual(settings["max_stock"], 15)
        self.assertEqual(settings["tutorial_mode"], 0)

    def test_fetch_player_settings_nonexistent(self):
        """Test fetching non-existent player settings creates default"""
        # Test retrieving settings when they don't exist
        settings = fetch_player_settings()
        self.assertEqual(settings["id"], 1)
        self.assertEqual(settings["starting_money"], 0)
        self.assertEqual(settings["max_stock"], 10)
        self.assertTrue(settings["tutorial_mode"])

        # Check that the settings were created in the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM player_settings WHERE id = 1")
        db_settings = cursor.fetchone()
        self.assertIsNotNone(db_settings)

    def test_fetch_starting_stock(self):
        """Test fetching starting stock"""
        # Create test stock
        self.conn.executemany(
            "INSERT INTO starting_stock (food, qty) VALUES (?, ?)",
            [("Tropical Pizza", 7), ("Ska Smoothie", 8), ("Island Ice Cream", 9)],
        )
        self.conn.commit()

        # Test retrieving the stock
        stock = fetch_starting_stock()
        self.assertEqual(len(stock), 3)
        self.assertEqual(stock["Tropical Pizza"], 7)
        self.assertEqual(stock["Ska Smoothie"], 8)
        self.assertEqual(stock["Island Ice Cream"], 9)

    def test_fetch_starting_defaults(self):
        """Test fetching starting defaults (money and stock)"""
        # Create test settings and stock
        self.conn.execute(
            "INSERT INTO player_settings (id, starting_money, max_stock) VALUES (1, 75, 15)"
        )
        self.conn.executemany(
            "INSERT INTO starting_stock (food, qty) VALUES (?, ?)",
            [("Tropical Pizza", 7), ("Ska Smoothie", 8)],
        )
        self.conn.commit()

        # Test retrieving the defaults
        money, stock = fetch_starting_defaults()
        self.assertEqual(money, 75)
        self.assertEqual(len(stock), 2)
        self.assertEqual(stock["Tropical Pizza"], 7)
        self.assertEqual(stock["Ska Smoothie"], 8)

    def test_load_owned_upgrades(self):
        """Test loading owned upgrades"""
        # Create test player and upgrades
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name) VALUES (1, 'TestPlayer')"
        )
        self.conn.executemany(
            "INSERT INTO upgrades_owned (player_id, upg_id) VALUES (?, ?)",
            [(1, "UP_SKATE"), (1, "UP_BAG")],
        )
        self.conn.commit()

        # Test retrieving owned upgrades
        upgrades = load_owned_upgrades(1)
        self.assertEqual(len(upgrades), 2)
        self.assertIn("UP_SKATE", upgrades)
        self.assertIn("UP_BAG", upgrades)

    def test_own_upgrade(self):
        """Test owning an upgrade"""
        # Create test player
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name) VALUES (1, 'TestPlayer')"
        )
        self.conn.commit()

        # Test owning a new upgrade
        result = own_upgrade(1, "UP_SKATE")
        self.assertTrue(result)

        # Check that the upgrade was added to the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT upg_id FROM upgrades_owned WHERE player_id = 1")
        upgrades = cursor.fetchall()
        self.assertEqual(len(upgrades), 1)
        self.assertEqual(upgrades[0][0], "UP_SKATE")

        # Test owning the same upgrade again (should fail due to primary key constraint)
        result = own_upgrade(1, "UP_SKATE")
        self.assertFalse(result)

        # Test owning a different upgrade
        result = own_upgrade(1, "UP_BAG")
        self.assertTrue(result)

        # Check that the upgrade was added
        cursor.execute("SELECT upg_id FROM upgrades_owned WHERE player_id = 1")
        upgrades = [row[0] for row in cursor.fetchall()]
        self.assertEqual(len(upgrades), 2)
        self.assertIn("UP_SKATE", upgrades)
        self.assertIn("UP_BAG", upgrades)

    def test_save_run_history(self):
        """Test saving run history"""
        # Create test player
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (1, 'TestPlayer', 100)"
        )
        self.conn.commit()

        # Test saving a run
        run_id = save_run_history(1, 150, 200, 5, 120.5)
        self.assertIsNotNone(run_id)

        # Check that the run was saved and high score updated
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM run_history WHERE run_id = ?", (run_id,))
        run = cursor.fetchone()
        self.assertIsNotNone(run)
        self.assertEqual(run["score"], 150)
        self.assertEqual(run["money_earned"], 200)
        self.assertEqual(run["missed"], 5)
        self.assertEqual(run["duration_sec"], 120.5)

        # Check high score was updated
        cursor.execute("SELECT high_score FROM player_profile WHERE player_id = 1")
        high_score = cursor.fetchone()[0]
        self.assertEqual(high_score, 150)

        # Test saving another run with lower score
        run_id2 = save_run_history(1, 80, 100, 10, 60.0)
        self.assertIsNotNone(run_id2)

        # Check high score was not updated
        cursor.execute("SELECT high_score FROM player_profile WHERE player_id = 1")
        high_score = cursor.fetchone()[0]
        self.assertEqual(high_score, 150)

    def test_get_high_scores(self):
        """Test getting high scores"""
        # Create test players and runs
        self.conn.executemany(
            "INSERT INTO player_profile (player_id, display_name, high_score) VALUES (?, ?, ?)",
            [(1, "Player1", 200), (2, "Player2", 300)],
        )
        self.conn.executemany(
            "INSERT INTO run_history (run_id, player_id, score) VALUES (?, ?, ?)",
            [(1, 1, 100), (2, 1, 200), (3, 2, 300), (4, 2, 150), (5, 1, 250)],
        )
        self.conn.commit()

        # Test getting high scores
        scores = get_high_scores(3)
        self.assertEqual(len(scores), 3)
        self.assertEqual(scores[0]["score"], 300)
        self.assertEqual(scores[0]["display_name"], "Player2")
        self.assertEqual(scores[1]["score"], 250)
        self.assertEqual(scores[2]["score"], 200)

    def test_get_recent_runs(self):
        """Test getting recent runs"""
        # Create test player and runs
        self.conn.execute(
            "INSERT INTO player_profile (player_id, display_name) VALUES (1, 'TestPlayer')"
        )
        self.conn.executemany(
            "INSERT INTO run_history (run_id, player_id, score, run_date) VALUES (?, ?, ?, ?)",
            [
                (1, 1, 100, "2025-05-30 10:00:00"),
                (2, 1, 200, "2025-05-31 10:00:00"),
                (3, 1, 150, "2025-06-01 10:00:00"),
                (4, 1, 300, "2025-06-01 11:00:00"),
            ],
        )
        self.conn.commit()

        # Test getting recent runs
        runs = get_recent_runs(1, 2)
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0]["run_id"], 4)
        self.assertEqual(runs[0]["score"], 300)
        self.assertEqual(runs[1]["run_id"], 3)
        self.assertEqual(runs[1]["score"], 150)


if __name__ == "__main__":
    unittest.main()
