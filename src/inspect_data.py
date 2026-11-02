
import duckdb

# Connect to our football database
con = duckdb.connect(
    "dataset/transfermarkt-datasets.duckdb",
    read_only=True
)

# Display all available tables
tables = con.execute("SHOW TABLES").fetchall()

print("\n===== FOOTBALL DATABASE TABLES =====")

for table in tables:
    print(table[0])

con.close()
