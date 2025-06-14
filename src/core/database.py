"""
Database connection and operations for Jammin' Eats
Handles all database interactions for game data persistence
"""

import pyodbc
from typing import Optional, Dict

# Test comment to verify pre-commit hooks


class GameDatabase:
    """Manages database connections and game data operations"""

    def __init__(self):
        self.connection = None
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost\\SQLEXPRESS;"
            "Database=JamminEats;"
            "Trusted_Connection=yes;"
        )

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            print("[DATABASE] Connected successfully")
            return True
        except Exception as e:
            print(f"[DATABASE] Connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("[DATABASE] Disconnected")

    def save_player_progress(
        self, player_id: int, economy_data: Dict, inventory_data: Dict
    ) -> bool:
        """Save current game progress"""
        try:
            cursor = self.connection.cursor()

            # Update or insert player progression
            cursor.execute(
                """
                MERGE PlayerProgression AS target
                USING (SELECT ? AS player_id) AS source
                ON target.player_id = source.player_id
                WHEN MATCHED THEN
                    UPDATE SET 
                        current_money = ?,
                        lifetime_earnings = ?,
                        current_map = ?,
                        current_frame = ?,
                        last_played = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (player_id, current_money, lifetime_earnings, 
                           current_map, current_frame)
                    VALUES (?, ?, ?, ?, ?);
            """,
                (
                    player_id,
                    economy_data["money"],
                    economy_data["lifetime_earnings"],
                    economy_data["current_map"],
                    economy_data["current_frame"],
                    player_id,
                    economy_data["money"],
                    economy_data["lifetime_earnings"],
                    economy_data["current_map"],
                    economy_data["current_frame"],
                ),
            )

            # Update inventory
            for food_type, quantity in inventory_data.items():
                cursor.execute(
                    """
                    MERGE PlayerInventory AS target
                    USING (SELECT ? AS player_id, 
                          (SELECT food_id FROM FoodTypes WHERE food_name = ?) AS food_id) AS source
                    ON target.player_id = source.player_id AND target.food_id = source.food_id
                    WHEN MATCHED THEN
                        UPDATE SET quantity = ?, last_updated = GETDATE()
                    WHEN NOT MATCHED THEN
                        INSERT (player_id, food_id, quantity)
                        VALUES (?, (SELECT food_id FROM FoodTypes WHERE food_name = ?), ?);
                """,
                    (player_id, food_type, quantity, player_id, food_type, quantity),
                )

            self.connection.commit()
            print("[DATABASE] Progress saved successfully")
            return True

        except Exception as e:
            print(f"[DATABASE] Save failed: {e}")
            self.connection.rollback()
            return False

    def load_player_progress(self, player_id: int) -> Optional[Dict]:
        """Load player progress from database"""
        try:
            cursor = self.connection.cursor()

            # Load progression data
            cursor.execute(
                """
                SELECT current_money, lifetime_earnings, current_map, 
                       current_frame, tutorial_completed
                FROM PlayerProgression
                WHERE player_id = ?
            """,
                (player_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            progress_data = {
                "money": float(row[0]),
                "lifetime_earnings": float(row[1]),
                "current_map": row[2],
                "current_frame": row[3],
                "tutorial_completed": row[4],
            }

            # Load inventory
            cursor.execute(
                """
                SELECT f.food_name, i.quantity
                FROM PlayerInventory i
                JOIN FoodTypes f ON i.food_id = f.food_id
                WHERE i.player_id = ?
            """,
                (player_id,),
            )

            inventory = {}
            for row in cursor.fetchall():
                inventory[row[0]] = row[1]

            progress_data["inventory"] = inventory

            return progress_data

        except Exception as e:
            print(f"[DATABASE] Load failed: {e}")
            return None

    def log_transaction(
        self,
        player_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        map_id: int,
        frame: int,
    ):
        """Log a financial transaction for analytics"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO TransactionHistory 
                (player_id, transaction_type, amount, item_description, map_id, frame_number)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (player_id, transaction_type, amount, description, map_id, frame),
            )

            self.connection.commit()

        except Exception as e:
            print(f"[DATABASE] Transaction log failed: {e}")
