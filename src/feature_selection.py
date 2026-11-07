import pandas as pd
from sklearn.model_selection import train_test_split

# Load Cleaned Dataset
df = pd.read_csv("output/cleaned_dataset.csv")

print("Dataset Loaded Successfully!\n")

print(df.head())

# Input Features (X)
X = df[[
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
    "Hour",
    "Day",
    "Month",
    "Year"
]]

# Target Variable (y)
y = df["Global_active_power"]

print("\nInput Features Shape:", X.shape)
print("Target Shape:", y.shape)

# Split Dataset (80% Training, 20% Testing)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTrain-Test Split Completed!")

print("Training Data:", X_train.shape)
print("Testing Data :", X_test.shape)

print("Training Target:", y_train.shape)
print("Testing Target :", y_test.shape)