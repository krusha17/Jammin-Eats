import pyodbc

# Connect to the default 'master' database first
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;Database=JamminEats;T"
    "rusted_Connection=yes;"
)

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

try:
    # Set autocommit mode to True to avoid transaction for DDL statements
    conn.autocommit = True

    cursor.execute("CREATE DATABASE JamminEats;")
    print("✅ JamminEats database created successfully.")
except Exception as e:
    print("⚠️ Error creating database:", e)
finally:
    cursor.close()
    conn.close()
