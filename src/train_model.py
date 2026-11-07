import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

# -------------------------------
# Load Cleaned Dataset
# -------------------------------
df = pd.read_csv("output/cleaned_dataset.csv")

# -------------------------------
# Input Features
# -------------------------------
X = df[
    [
        "Global_reactive_power",
        "Voltage",
        "Global_intensity",
        "Sub_metering_1",
        "Sub_metering_2",
        "Sub_metering_3",
        "Hour",
        "Day",
        "Month",
        "Year",
    ]
]

# -------------------------------
# Target
# -------------------------------
y = df["Global_active_power"]

# -------------------------------
# Train Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -------------------------------
# Final Optimized Random Forest Model
# (Best Parameters from Grid Search)
# -------------------------------
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

print("Training Final Model...")

model.fit(X_train, y_train)

print("Training Completed!")

# -------------------------------
# Prediction
# -------------------------------
y_pred = model.predict(X_test)

# -------------------------------
# Evaluation
# -------------------------------
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print("\n========== MODEL PERFORMANCE ==========")
print(f"R² Score : {r2:.6f}")
print(f"MAE      : {mae:.6f}")
print(f"RMSE     : {rmse:.6f}")

# -------------------------------
# Save Model
# -------------------------------
joblib.dump(model, "models/random_forest_model.pkl")

print("\nModel Saved Successfully!")