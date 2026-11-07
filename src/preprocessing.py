import pandas as pd
import numpy as np

# Load Dataset
df = pd.read_excel("dataset/dataset_electricity.xlsx")

# Display first 5 rows
print(df.head())

# Dataset Shape
print("\nDataset Shape:")
print(df.shape)

# Dataset Information
print("\nDataset Information:")
print(df.info())

# Missing Values
print("\nMissing Values:")
print(df.isnull().sum())

# Statistical Summary
print("\nStatistical Summary:")
print(df.describe())

# Remove Missing Values
df = df.dropna()

print("\nDataset Shape After Removing Missing Values:")
print(df.shape)

# Create Date-Time Features
df["Hour"] = df["Time"].apply(lambda x: x.hour)
df["Day"] = df["Date"].dt.day
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year

print("\nNew Features Created Successfully!")
print(df[["Date", "Time", "Hour", "Day", "Month", "Year"]].head())

# Save Cleaned Dataset
df.to_csv("output/cleaned_dataset.csv", index=False)

print("\nCleaned Dataset Saved Successfully!")

print("\nNew Features Created:")
print(df[["Date", "Time", "Hour", "Day", "Month", "Year"]].head(10))

df["Hour"] = df["Time"].apply(lambda x: x.hour)
df["Day"] = df["Date"].dt.day
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year
df.to_csv("output/cleaned_dataset.csv", index=False)