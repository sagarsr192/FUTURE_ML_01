from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


app = FastAPI(title="Sales Forecast Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "processed" / "featured_sales_data.csv"
FEATURES = ["Year", "Month", "Day", "DayOfWeek"]


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Dataset not found")
    frame = pd.read_csv(DATA_PATH)
    frame["Order Date"] = pd.to_datetime(frame["Order Date"])
    return frame


def create_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    feature_frame = frame.copy()
    feature_frame["Year"] = feature_frame["Order Date"].dt.year
    feature_frame["Month"] = feature_frame["Order Date"].dt.month
    feature_frame["Day"] = feature_frame["Order Date"].dt.day
    feature_frame["DayOfWeek"] = feature_frame["Order Date"].dt.dayofweek
    return feature_frame


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/historical")
def historical() -> dict:
    frame = load_data()
    daily_sales = (
        frame.groupby("Order Date")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Order Date")
    )
    payload = [
        {"date": item["Order Date"].strftime("%Y-%m-%d"), "sales": float(item["Sales"])}
        for _, item in daily_sales.iterrows()
    ]
    return {"items": payload}


@app.get("/model-info")
def model_info() -> dict:
    frame = load_data()
    model_frame = create_feature_frame(frame)

    x_values = model_frame[FEATURES]
    y_values = model_frame["Sales"]

    model = LinearRegression()
    model.fit(x_values, y_values)
    predictions = model.predict(x_values)

    mae = mean_absolute_error(y_values, predictions)
    rmse = np.sqrt(mean_squared_error(y_values, predictions))

    return {
        "algorithm": "Linear Regression",
        "features": FEATURES,
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
        },
    }


@app.get("/forecast")
def forecast(days: int = Query(default=30, ge=7, le=90)) -> dict:
    frame = load_data()
    model_frame = create_feature_frame(frame)

    x_values = model_frame[FEATURES]
    y_values = model_frame["Sales"]

    model = LinearRegression()
    model.fit(x_values, y_values)

    last_date = model_frame["Order Date"].max()
    future_dates = [last_date + timedelta(days=index) for index in range(1, days + 1)]
    future_frame = pd.DataFrame({"Order Date": future_dates})

    future_frame["Year"] = future_frame["Order Date"].dt.year
    future_frame["Month"] = future_frame["Order Date"].dt.month
    future_frame["Day"] = future_frame["Order Date"].dt.day
    future_frame["DayOfWeek"] = future_frame["Order Date"].dt.dayofweek

    future_predictions = model.predict(future_frame[FEATURES])
    future_frame["Predicted Sales"] = future_predictions

    payload = [
        {
            "date": item["Order Date"].strftime("%Y-%m-%d"),
            "predicted_sales": float(item["Predicted Sales"]),
        }
        for _, item in future_frame.iterrows()
    ]
    return {"days": days, "items": payload}
