
import duckdb

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

    print("\n" + "=" * 60)
    print(f"TABLE: {table.upper()}")
    print("=" * 60)

    # Total number of records
    count = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"Total records: {count:,}")

    # Display five real records
    sample = con.execute(
        f"SELECT * FROM {table} LIMIT 5"
    ).df()

    print("\nSample records:")
    print(sample.to_string(index=False))

con.close()
