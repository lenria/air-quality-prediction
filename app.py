# ===============================
# AIRWARE STREAMLIT DASHBOARD
# ===============================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AirWare Dashboard", layout="wide")

st.title("🌍 AirWare - Smart AQI Monitoring System")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("city_day.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['AQI'])
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

df = load_data()

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("Filter Options")

stations = df["City"].unique()
selected_station = st.sidebar.selectbox("Select Station", stations)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min(), df["Date"].max()]
)

# Filter data
filtered_df = df[
    (df["City"] == selected_station) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# ===============================
# LOAD MODEL
# ===============================
model = joblib.load("air_quality_model.pkl")

features = ['PM2.5','PM10','NO','NO2','NOx','NH3','CO','SO2','O3']

# ===============================
# AQI PREDICTION
# ===============================
if not filtered_df.empty:
    latest_data = filtered_df.iloc[-1]
    input_data = latest_data[features].values.reshape(1, -1)
    predicted_aqi = model.predict(input_data)[0]
else:
    predicted_aqi = 0

# ===============================
# AQI GAUGE
# ===============================
st.subheader("📊 Current AQI Status")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=predicted_aqi,
    title={'text': "Predicted AQI"},
    gauge={
        'axis': {'range': [0, 500]},
        'steps': [
            {'range': [0, 50], 'color': "green"},
            {'range': [50, 100], 'color': "yellow"},
            {'range': [100, 200], 'color': "orange"},
            {'range': [200, 300], 'color': "red"},
            {'range': [300, 500], 'color': "purple"},
        ],
    }
))

st.plotly_chart(fig, use_container_width=True)

# ===============================
# ALERT SYSTEM
# ===============================
if predicted_aqi <= 50:
    st.success("Air Quality is Good 😊")
elif predicted_aqi <= 100:
    st.warning("Moderate Air Quality ⚠️")
elif predicted_aqi <= 200:
    st.warning("Unhealthy for Sensitive Groups 😷")
else:
    st.error("Hazardous Air Quality 🚨 Stay Indoors!")

# ===============================
# LINE PLOTS
# ===============================
st.subheader("📈 AQI Trend")

st.line_chart(filtered_df.set_index("Date")["AQI"])

st.subheader("📈 Pollution Parameters Trend")
st.line_chart(filtered_df.set_index("Date")[features])

# ===============================
# ADMIN PANEL
# ===============================
st.sidebar.header("⚙️ Admin Panel")

admin_password = st.sidebar.text_input("Enter Admin Password", type="password")

if admin_password == "admin123":

    st.sidebar.success("Admin Access Granted")

    uploaded_file = st.sidebar.file_uploader("Upload New Dataset")

    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        new_df['Date'] = pd.to_datetime(new_df['Date'], errors='coerce')
        new_df = new_df.dropna(subset=['AQI'])
        new_df = new_df.fillna(method='ffill').fillna(method='bfill')

        X = new_df[features]
        y = new_df['AQI']

        model_choice = st.sidebar.selectbox("Select Model", ["Random Forest", "XGBoost"])

        if st.sidebar.button("Retrain Model"):

            if model_choice == "Random Forest":
                new_model = RandomForestRegressor(n_estimators=200, random_state=42)
            else:
                new_model = XGBRegressor(n_estimators=300, learning_rate=0.05)

            new_model.fit(X, y)
            joblib.dump(new_model, "air_quality_model.pkl")

            st.sidebar.success("Model Retrained & Saved Successfully!")

else:
    st.sidebar.info("Admin access required for retraining.")