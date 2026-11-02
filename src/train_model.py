
import pandas as pd
import numpy as np
import joblib
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("Loading football training dataset...")

df = pd.read_csv("dataset/training_data.csv")

# Convert dates
df["valuation_date"] = pd.to_datetime(df["valuation_date"])

# Add valuation year
df["valuation_year"] = df["valuation_date"].dt.year

# Remove invalid target values
df = df[df["market_value_eur"] > 0].copy()

# Features used for prediction
numeric_features = [
    "age",
    "height_in_cm",
    "goals_last_365_days",
    "assists_last_365_days",
    "minutes_last_365_days",
    "yellow_cards_last_365_days",
    "red_cards_last_365_days",
    "valuation_year"
]

categorical_features = [
    "position",
    "sub_position",
    "foot"
]

features = numeric_features + categorical_features

X = df[features]
y = np.log1p(df["market_value_eur"])

print("Total records:", len(df))

# Chronological train/test split
cutoff_date = pd.Timestamp("2025-01-01")

train_mask = df["valuation_date"] < cutoff_date

# Use a chronological fallback if necessary
if train_mask.sum() == 0 or train_mask.sum() == len(df):
    cutoff_date = df["valuation_date"].quantile(0.80)
    train_mask = df["valuation_date"] < cutoff_date

X_train = X.loc[train_mask]
X_test = X.loc[~train_mask]

y_train = y.loc[train_mask]
y_test = y.loc[~train_mask]

actual_values = df.loc[~train_mask, "market_value_eur"]

print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Test begins:", df.loc[~train_mask, "valuation_date"].min())

# Preprocessing
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(
        handle_unknown="ignore",
        min_frequency=20
    ))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])

# Models
models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=18,
        min_samples_leaf=3,
        n_jobs=-1,
        random_state=42
    ),

    "Gradient Boosting": HistGradientBoostingRegressor(
        max_iter=150,
        max_leaf_nodes=31,
        learning_rate=0.1,
        l2_regularization=1.0,
        random_state=42
    )
}

results = []
best_model = None
best_mae = float("inf")
best_name = ""

os.makedirs("models", exist_ok=True)

for name, algorithm in models.items():

    print(f"\nTraining {name}...")

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", algorithm)
    ])

    # HistGradientBoosting requires dense input.
    if name == "Gradient Boosting":
        pipeline.named_steps["preprocessor"].set_params(
            categorical__encoder__sparse_output=False
        )

    pipeline.fit(X_train, y_train)

    predictions_log = pipeline.predict(X_test)

    predictions = np.maximum(
        np.expm1(predictions_log), 0
    )

    mae = mean_absolute_error(
        actual_values, predictions
    )

    rmse = np.sqrt(
        mean_squared_error(actual_values, predictions)
    )

    r2 = r2_score(actual_values, predictions)

    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))
    print("R2:", round(r2, 4))

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    if mae < best_mae:
        best_mae = mae
        best_model = pipeline
        best_name = name

# Save best model
joblib.dump(best_model, "models/best_model.pkl")

print("\n===== MODEL COMPARISON =====")
print(pd.DataFrame(results).to_string(index=False))

print("\nBest model:", best_name)
print("Saved to models/best_model.pkl")
