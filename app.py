import streamlit as st
import pandas as pd
import os
import plotly.express as px
import base64
import mimetypes
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Sales Demand Forecasting Dashboard",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
background_candidates = [
    os.path.join(BASE_DIR, "visuals", "background.png"),
    os.path.join(BASE_DIR, "visuals", "background.jpg"),
    os.path.join(BASE_DIR, "visuals", "background.jpeg"),
    os.path.join(BASE_DIR, "visuals", "historical_sales.png"),
    os.path.join(BASE_DIR, "visuals", "actual_vs_predicted.png"),
]
background_image_path = next((path for path in background_candidates if os.path.exists(path)), None)

background_style = "background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);"
if background_image_path:
    with open(background_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    mime_type = mimetypes.guess_type(background_image_path)[0] or "image/png"
    background_style = (
        "background-image: linear-gradient(rgba(15, 23, 42, 0.38), rgba(15, 23, 42, 0.38)), "
        f"url('data:{mime_type};base64,{encoded_image}');"
        "background-size: cover;"
        "background-position: center;"
        "background-repeat: no-repeat;"
        "background-attachment: fixed;"
    )

st.markdown(
    """
    <style>
    .stApp {
    """
    + background_style
    + """
    }
    .hero-wrapper {
        min-height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .hero-title {
        font-size: clamp(2.1rem, 4vw, 4rem);
        font-weight: 700;
        letter-spacing: 0.04em;
        color: #0f172a;
        text-transform: uppercase;
    }
    .chart-title {
        font-size: clamp(1.4rem, 2.2vw, 2.2rem);
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.4rem;
    }
    .chart-subtitle {
        color: #475569;
        margin-bottom: 1rem;
    }
    .section-card {
        background: rgba(229, 231, 235, 0.9);
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin: 0.6rem 0 1rem 0;
        color: #0f172a;
    }
    div.stButton > button[kind="primary"] {
        position: fixed;
        right: 1.6rem;
        bottom: 1.2rem;
        border-radius: 999px;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        border: 1px solid #cbd5e1;
        background-color: #e5e7eb;
        color: #0f172a;
    }
    div.stButton > button[kind="primary"]:hover {
        border-color: #93c5fd;
        color: #1d4ed8;
    }
    [data-testid="stVegaLiteChart"] > div {
        background-color: #e5e7eb !important;
        border-radius: 10px;
        padding: 0.3rem;
    }
    [data-testid="stVegaLiteChart"],
    [data-testid="stVegaLiteChart"] canvas,
    [data-testid="stVegaLiteChart"] svg {
        background-color: #e5e7eb !important;
    }
    [data-testid="stMetric"] {
        background-color: #e5e7eb;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 0.6rem;
    }
    [data-testid="stSlider"] > div,
    [data-testid="stSlider"] label,
    [data-baseweb="slider"] {
        background-color: transparent;
        color: #ef4444 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Load Dataset (Cloud Compatible Path)
# -------------------------------------------------
data_path = os.path.join(BASE_DIR, "data", "processed", "featured_sales_data.csv")

if not os.path.exists(data_path):
    st.error("Dataset not found. Please check file path.")
    st.stop()

df = pd.read_csv(data_path)

PLOT_BG = "#e5e7eb"
PLOT_GRID = "#d1d5db"

# Ensure correct date format
df["Order Date"] = pd.to_datetime(df["Order Date"])

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-title">Sales Demand Forcasting Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("ENTER", type="primary"):
        st.session_state.page = "historical"
        st.rerun()

elif st.session_state.page == "historical":
    back_col, _ = st.columns([1, 11])
    with back_col:
        if st.button("BACK"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown("<div class='chart-title'>Historical Sales Trend</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='chart-subtitle'>Daily sales movement based on order date.</div>",
        unsafe_allow_html=True,
    )

    daily_sales = df.groupby("Order Date")["Sales"].sum().reset_index()

    history_chart = px.line(
        daily_sales,
        x="Order Date",
        y="Sales",
        title="",
    )
    history_chart.update_traces(line_color="#2563eb", line_width=3)
    history_chart.update_layout(
        height=500,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Date", gridcolor=PLOT_GRID, color="#374151"),
        yaxis=dict(title="Sales", gridcolor=PLOT_GRID, color="#374151"),
    )
    st.plotly_chart(history_chart, use_container_width=True)

    st.divider()
    st.markdown("<div class='chart-title'>Model Used</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-card'><b>Algorithm:</b> Linear Regression<br><b>Features:</b> Year, Month, Day, DayOfWeek</div>", unsafe_allow_html=True)

    model_df = df.copy()
    model_df["Year"] = model_df["Order Date"].dt.year
    model_df["Month"] = model_df["Order Date"].dt.month
    model_df["Day"] = model_df["Order Date"].dt.day
    model_df["DayOfWeek"] = model_df["Order Date"].dt.dayofweek

    features = ["Year", "Month", "Day", "DayOfWeek"]
    X = model_df[features]
    y = model_df["Sales"]

    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)

    st.markdown("<div class='chart-title'>Model Performance</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-card'>Performance is calculated on available historical data.</div>", unsafe_allow_html=True)
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Mean Absolute Error (MAE)", f"{mae:,.2f}")
    metric_col2.metric("Root Mean Squared Error (RMSE)", f"{rmse:,.2f}")

    st.divider()
    st.markdown("<div class='chart-title'>Future Sales Prediction</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='chart-subtitle'>Scroll down to explore forecasted demand for upcoming days.</div>",
        unsafe_allow_html=True,
    )

    days = st.slider("Select number of days to forecast", 7, 90, 30)

    last_date = model_df["Order Date"].max()
    future_dates = [last_date + timedelta(days=index) for index in range(1, days + 1)]
    future_df = pd.DataFrame({"Order Date": future_dates})

    future_df["Year"] = future_df["Order Date"].dt.year
    future_df["Month"] = future_df["Order Date"].dt.month
    future_df["Day"] = future_df["Order Date"].dt.day
    future_df["DayOfWeek"] = future_df["Order Date"].dt.dayofweek

    future_predictions = model.predict(future_df[features])
    future_df["Predicted Sales"] = future_predictions

    forecast_chart = px.line(
        future_df,
        x="Order Date",
        y="Predicted Sales",
        title="",
    )
    forecast_chart.update_traces(line_color="#f97316", line_width=3)
    forecast_chart.update_layout(
        height=460,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Date", gridcolor=PLOT_GRID, color="#374151"),
        yaxis=dict(title="Predicted Sales", gridcolor=PLOT_GRID, color="#374151"),
    )
    st.plotly_chart(forecast_chart, use_container_width=True)