import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import altair as alt

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Sales Demand Forecasting Dashboard",
    layout="wide"
)

# -------------------------------------------------
# Load Dataset (Cloud Compatible Path)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "data", "processed", "featured_sales_data.csv")

if not os.path.exists(data_path):
    st.error("Dataset not found. Please check file path.")
    st.stop()

df = pd.read_csv(data_path)

# Ensure correct date format
df["Order Date"] = pd.to_datetime(df["Order Date"])

# -------------------------------------------------
# Title Section
# -------------------------------------------------
st.title("📊 Sales Demand Forecasting Dashboard")
st.markdown("### Machine Learning Based Time-Series Prediction")
st.divider()

# -------------------------------------------------
# Historical Sales Trend
# -------------------------------------------------
st.subheader("📈 Historical Sales Trend")

daily_sales = df.groupby("Order Date")["Sales"].sum().reset_index()

history_chart = alt.Chart(daily_sales).mark_line().encode(
    x="Order Date:T",
    y="Sales:Q",
    tooltip=["Order Date", "Sales"]
).properties(height=400)

st.altair_chart(history_chart, use_container_width=True)
st.divider()

# -------------------------------------------------
# Feature Engineering
# -------------------------------------------------
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month
df["Day"] = df["Order Date"].dt.day
df["DayOfWeek"] = df["Order Date"].dt.dayofweek

X = df[["Year", "Month", "Day", "DayOfWeek"]]
y = df["Sales"]

# -------------------------------------------------
# Train Model Inside App
# -------------------------------------------------
model = LinearRegression()
model.fit(X, y)

predictions = model.predict(X)

# -------------------------------------------------
# Model Performance
# -------------------------------------------------
st.subheader("📊 Model Performance")

mae = mean_absolute_error(y, predictions)
rmse = np.sqrt(mean_squared_error(y, predictions))

col1, col2 = st.columns(2)

col1.metric("Mean Absolute Error (MAE)", f"{mae:,.2f}")
col2.metric("Root Mean Squared Error (RMSE)", f"{rmse:,.2f}")

st.divider()

# -------------------------------------------------
# Forecast Future Sales
# -------------------------------------------------
st.subheader("🔮 Future Sales Prediction")

days = st.slider("Select number of days to forecast", 7, 90, 30)

last_date = df["Order Date"].max()
future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]

future_df = pd.DataFrame({"Order Date": future_dates})

future_df["Year"] = future_df["Order Date"].dt.year
future_df["Month"] = future_df["Order Date"].dt.month
future_df["Day"] = future_df["Order Date"].dt.day
future_df["DayOfWeek"] = future_df["Order Date"].dt.dayofweek

future_X = future_df[["Year", "Month", "Day", "DayOfWeek"]]

future_predictions = model.predict(future_X)

future_df["Predicted Sales"] = future_predictions

forecast_chart = alt.Chart(future_df).mark_line(color="orange").encode(
    x="Order Date:T",
    y="Predicted Sales:Q",
    tooltip=["Order Date", "Predicted Sales"]
).properties(height=400)

st.altair_chart(forecast_chart, use_container_width=True)

st.success("✅ App running successfully!")