
import pandas as pd
import numpy as np
import joblib

print("Loading Football Transfer Value Predictor...")

model = joblib.load("models/best_model.pkl")

print("\n===== PLAYER DETAILS =====")

name = input("Enter player name: ")

age = float(input("Enter age: "))

height = float(input("Enter height in cm (0 if unknown): "))
if height <= 0:
    height = np.nan

position = input(
    "Enter position (Attack/Defender/Midfield/Goalkeeper): "
)

sub_position = input("Enter sub-position (or Unknown): ")

foot = input("Enter preferred foot (left/right/both/Unknown): ")

goals = float(input("Goals in last 365 days: "))

assists = float(input("Assists in last 365 days: "))

minutes = float(input("Minutes played in last 365 days: "))

yellow = float(input("Yellow cards in last 365 days: "))

red = float(input("Red cards in last 365 days: "))

year = 2026

if sub_position.strip().lower() == "unknown":
    sub_position = np.nan

if foot.strip().lower() == "unknown":
    foot = np.nan

player = pd.DataFrame([{
    "age": age,
    "height_in_cm": height,
    "goals_last_365_days": goals,
    "assists_last_365_days": assists,
    "minutes_last_365_days": minutes,
    "yellow_cards_last_365_days": yellow,
    "red_cards_last_365_days": red,
    "valuation_year": year,
    "position": position,
    "sub_position": sub_position,
    "foot": foot
}])

predicted_log_value = model.predict(player)[0]

predicted_value = max(0, np.expm1(predicted_log_value))

print("\n" + "=" * 45)
print("       TRANSFER VALUE PREDICTION")
print("=" * 45)

print("Player:", name)
print("Estimated market value: €{:,.0f}".format(predicted_value))

print("=" * 45)

print("Note: This is an ML estimate, not an actual transfer fee.")
