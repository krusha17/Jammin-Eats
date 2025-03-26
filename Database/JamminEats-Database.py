import pyodbc

# Connect to the default 'master' database first
connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=master;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

try:
    cursor.execute("CREATE DATABASE JamminEats;")
    conn.commit()
    print("✅ JamminEats database created successfully.")
except Exception as e:
    print("⚠️ Error creating database:", e)
finally:
    cursor.close()
    conn.close()
