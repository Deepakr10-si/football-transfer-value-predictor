
import duckdb
import os

DB_PATH = "dataset/transfermarkt-datasets.duckdb"
OUTPUT_PATH = "dataset/training_data.csv"

print("Connecting to football database...")

con = duckdb.connect(DB_PATH, read_only=True)

print("Building historical player dataset...")

query = """
SELECT
    v.player_id,
    p.name AS player_name,

    -- Age on the valuation date
    DATE_DIFF(
        'day',
        CAST(p.date_of_birth AS DATE),
        v.date
    ) / 365.25 AS age,

    p.position,
    p.sub_position,
    p.foot,
    p.height_in_cm,

    v.date AS valuation_date,

    -- Performance in the 365 days before valuation
    COALESCE(SUM(a.goals), 0) AS goals_last_365_days,

    COALESCE(SUM(a.assists), 0) AS assists_last_365_days,

    COALESCE(SUM(a.minutes_played), 0) AS minutes_last_365_days,

    COALESCE(SUM(a.yellow_cards), 0) AS yellow_cards_last_365_days,

    COALESCE(SUM(a.red_cards), 0) AS red_cards_last_365_days,

    -- Prediction target
    v.market_value_in_eur AS market_value_eur

FROM player_valuations v

JOIN players p
    ON v.player_id = p.player_id

LEFT JOIN appearances a
    ON v.player_id = a.player_id
    AND a.date >= v.date - INTERVAL 365 DAY
    AND a.date < v.date

WHERE
    p.date_of_birth IS NOT NULL
    AND v.market_value_in_eur > 0
    AND v.date >= CAST(p.date_of_birth AS DATE)
    AND v.date <= DATE '2026-07-06'

GROUP BY
    v.player_id,
    p.name,
    p.date_of_birth,
    p.position,
    p.sub_position,
    p.foot,
    p.height_in_cm,
    v.date,
    v.market_value_in_eur

HAVING
    DATE_DIFF(
        'day',
        CAST(p.date_of_birth AS DATE),
        v.date
    ) / 365.25 BETWEEN 15 AND 45
"""

print("Executing SQL query...")

df = con.execute(query).df()

con.close()

print("Cleaning dataset...")

df = df.dropna(
    subset=["age", "position", "market_value_eur"]
)

df = df.drop_duplicates(
    subset=["player_id", "valuation_date"]
)

os.makedirs("dataset", exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)

print("\n===== DATASET CREATED =====")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Missing values:")
print(df.isnull().sum())

print("\nFirst five records:")
print(df.head().to_string(index=False))

print("\nSaved successfully to:", OUTPUT_PATH)
