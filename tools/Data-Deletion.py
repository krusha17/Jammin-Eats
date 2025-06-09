import pyodbc


def connect_to_database():
    """Connect to the SQL Server database with error handling."""
    try:
        # Modify these connection details to match your SQL Server setup
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"  # Change to your server name
            "DATABASE=JamminEats;"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str, autocommit=False)
        print("Connected to database successfully.")
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def delete_initial_data(conn):
    """Delete the initial data from tables without dropping the tables."""
    cursor = conn.cursor()
    try:
        print("Beginning deletion of initial data...")

        # Disable constraints
        disable_constraints = [
            "ALTER TABLE Deliveries NOCHECK CONSTRAINT ALL;",
            "ALTER TABLE PlayerAchievements NOCHECK CONSTRAINT ALL;",
            "ALTER TABLE LevelFoodTypes NOCHECK CONSTRAINT ALL;",
            "ALTER TABLE CustomerPreferences NOCHECK CONSTRAINT ALL;",
            "ALTER TABLE GameSessions NOCHECK CONSTRAINT ALL;"
        ]

        for stmt in disable_constraints:
            cursor.execute(stmt)
        print("Foreign key constraints disabled.")

        # Delete achievements data
        cursor.execute("""
            DELETE FROM PlayerAchievements WHERE achievement_id IN 
                (SELECT achievement_id FROM Achievements WHERE achievement_name IN 
                ('First Delivery', 'Speed Demon', 'Food Maestro', 'No Customer Left Behind'));
        """)
        print(f"Deleted {cursor.rowcount} rows from PlayerAchievements.")

        cursor.execute("""
            DELETE FROM Achievements WHERE achievement_name IN 
                ('First Delivery', 'Speed Demon', 'Food Maestro', 'No Customer Left Behind');
        """)
        print(f"Deleted {cursor.rowcount} rows from Achievements.")

        # Delete sounds data
        cursor.execute("""
            DELETE FROM Sounds WHERE sound_name IN 
                ('pickup_sound', 'engine_sound', 'button_sound', 'background_music');
        """)
        print(f"Deleted {cursor.rowcount} rows from Sounds.")

        # Delete game settings
        cursor.execute("""
            DELETE FROM GameSettings WHERE setting_name IN 
                ('FPS', 'SCREEN_WIDTH', 'SCREEN_HEIGHT');
        """)
        print(f"Deleted {cursor.rowcount} rows from GameSettings.")

        # Delete customer type data
        cursor.execute("""
            DELETE FROM CustomerPreferences WHERE customer_type_id IN 
                (SELECT customer_type_id FROM CustomerTypes WHERE type_name = 'Regular');
        """)
        print(f"Deleted {cursor.rowcount} rows from CustomerPreferences related to 'Regular' type.")

        cursor.execute("DELETE FROM CustomerTypes WHERE type_name = 'Regular';")
        print(f"Deleted {cursor.rowcount} rows from CustomerTypes.")

        # Delete game level data
        cursor.execute("""
            DELETE FROM LevelFoodTypes WHERE level_id IN 
                (SELECT level_id FROM GameLevels WHERE level_name = 'Kitchen Chaos');
        """)
        print(f"Deleted {cursor.rowcount} rows from LevelFoodTypes related to 'Kitchen Chaos'.")

        cursor.execute("""
            DELETE FROM CustomerSpawnLocations WHERE level_id IN 
                (SELECT level_id FROM GameLevels WHERE level_name = 'Kitchen Chaos');
        """)
        print(f"Deleted {cursor.rowcount} rows from CustomerSpawnLocations related to 'Kitchen Chaos'.")

        cursor.execute("DELETE FROM GameLevels WHERE level_name = 'Kitchen Chaos';")
        print(f"Deleted {cursor.rowcount} rows from GameLevels.")

        # Delete food types data
        cursor.execute("""
            DELETE FROM CustomerPreferences WHERE food_id IN 
                (SELECT food_id FROM FoodTypes WHERE food_name IN ('pizza', 'smoothie', 'icecream', 'pudding'));
        """)
        print(f"Deleted {cursor.rowcount} rows from CustomerPreferences related to food types.")

        cursor.execute("""
            DELETE FROM LevelFoodTypes WHERE food_id IN 
                (SELECT food_id FROM FoodTypes WHERE food_name IN ('pizza', 'smoothie', 'icecream', 'pudding'));
        """)
        print(f"Deleted {cursor.rowcount} rows from LevelFoodTypes related to food types.")

        cursor.execute("""
            DELETE FROM Deliveries WHERE food_id IN 
                (SELECT food_id FROM FoodTypes WHERE food_name IN ('pizza', 'smoothie', 'icecream', 'pudding'));
        """)
        print(f"Deleted {cursor.rowcount} rows from Deliveries related to food types.")

        cursor.execute("DELETE FROM FoodTypes WHERE food_name IN ('pizza', 'smoothie', 'icecream', 'pudding');")
        print(f"Deleted {cursor.rowcount} rows from FoodTypes.")

        # Re-enable constraints
        enable_constraints = [
            "ALTER TABLE Deliveries CHECK CONSTRAINT ALL;",
            "ALTER TABLE PlayerAchievements CHECK CONSTRAINT ALL;",
            "ALTER TABLE LevelFoodTypes CHECK CONSTRAINT ALL;",
            "ALTER TABLE CustomerPreferences CHECK CONSTRAINT ALL;",
            "ALTER TABLE GameSessions CHECK CONSTRAINT ALL;"
        ]

        for stmt in enable_constraints:
            cursor.execute(stmt)
        print("Foreign key constraints re-enabled.")

        # Commit the transaction
        conn.commit()
        print("Initial data deletion completed successfully.")

    except pyodbc.Error as e:
        conn.rollback()
        print(f"Error during deletion: {e}")
        return False

    finally:
        cursor.close()

    return True


def main():
    # Connect to database
    conn = connect_to_database()
    if not conn:
        print("Exiting due to database connection failure.")
        return

    try:
        # Delete initial data
        print("\n=== DELETING INITIAL DATA ===")
        delete_success = delete_initial_data(conn)
        if not delete_success:
            print("Initial data deletion failed. Exiting.")
            return

        print("\n=== DATA DELETION COMPLETE ===")
        print("Initial data has been successfully deleted.")
        print("You can now run your SQL insertion script to add new data.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # Close the connection
        conn.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()