# ===============================
# AIRWARE DATABASE SETUP (SQLite)
# ===============================

import sqlite3
import pandas as pd

# ===============================
# CONNECT TO DATABASE
# ===============================
conn = sqlite3.connect("airware.db")
cursor = conn.cursor()

print("Database Connected Successfully!")

# ===============================
# CREATE TABLE: AIR QUALITY DATA
# ===============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS air_quality_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    date TEXT,
    pm25 REAL,
    pm10 REAL,
    no REAL,
    no2 REAL,
    nox REAL,
    nh3 REAL,
    co REAL,
    so2 REAL,
    o3 REAL,
    aqi REAL
)
""")

print("Table air_quality_data created!")

# ===============================
# CREATE TABLE: MODEL PERFORMANCE
# ===============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    r2 REAL,
    mae REAL,
    rmse REAL,
    trained_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("Table model_performance created!")

# ===============================
# LOAD CSV INTO DATABASE
# ===============================

# Change file name if needed
csv_file = "city_day.csv"

try:
    df = pd.read_csv(csv_file)

    # Rename columns to match database
    df = df.rename(columns={
        "City": "city",
        "Date": "date",
        "PM2.5": "pm25",
        "PM10": "pm10",
        "NO": "no",
        "NO2": "no2",
        "NOx": "nox",
        "NH3": "nh3",
        "CO": "co",
        "SO2": "so2",
        "O3": "o3",
        "AQI": "aqi"
    })

    # Keep only needed columns
    df = df[[
        "city", "date", "pm25", "pm10", "no", "no2",
        "nox", "nh3", "co", "so2", "o3", "aqi"
    ]]

    # Insert into database
    df.to_sql("air_quality_data", conn, if_exists="replace", index=False)

    print("CSV data inserted successfully!")

except Exception as e:
    print("Error loading CSV:", e)

# ===============================
# SAVE MODEL PERFORMANCE EXAMPLE
# ===============================
cursor.execute("""
INSERT INTO model_performance (model_name, r2, mae, rmse)
VALUES (?, ?, ?, ?)
""", ("XGBoost", 0.92, 12.4, 18.6))

conn.commit()
conn.close()

print("Database setup completed successfully!")