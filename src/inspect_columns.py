
import duckdb

# Connect to the football database
con = duckdb.connect(
    "dataset/transfermarkt-datasets.duckdb",
    read_only=True
)

tables = [
    "players",
    "player_valuations",
    "appearances",
    "transfers"
]

for table in tables:
    print("\n" + "=" * 50)
    print(f"TABLE: {table.upper()}")
    print("=" * 50)

    columns = con.execute(
        f"DESCRIBE {table}"
    ).fetchall()

    for column in columns:
        print(f"{column[0]} : {column[1]}")

con.close()
