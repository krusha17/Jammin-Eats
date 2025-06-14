import pyodbc
import os

# Get the absolute path to the SQL file
script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, "JamminEats-Schema.sql")

# Connect to the already-created JamminEats database
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=JamminEats;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()
conn.autocommit = True  # Important for some DDL statements

# Read the SQL script from the .sql file
with open(sql_file_path, "r") as file:
    sql_script = file.read()

# Split by GO and execute batches
sql_batches = sql_script.split("GO")
for batch in sql_batches:
    if batch.strip():
        try:
            cursor.execute(batch)
        except Exception as e:
            print(f"⚠️ Error executing:\n{batch.strip()}\n{e}\n")

cursor.close()
conn.close()
print("✅ JamminEats database has been fully set up!")
