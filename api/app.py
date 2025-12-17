from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Allow running inside/outside repo root
REPO_ROOT = Path(__file__).resolve().parents[1]

try:
    # Ensure src imports work when running `uvicorn api.app:app`
    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
except Exception:
    pass

from src.data.loaders import load_sales_data
from src.models.baseline import naive_forecast, moving_average_forecast, simple_exponential_smoothing_forecast


class ForecastRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier, e.g. SKU001")
    horizon: int = Field(14, ge=1, le=365, description="Forecast horizon (days)")
    method: Literal["naive", "moving_average", "ses"] = Field("moving_average")
    ma_window: int = Field(7, ge=1, le=365)
    ses_alpha: float = Field(0.3, gt=0.0, le=1.0)
    cutoff_date: Optional[str] = Field(
        None, description="Optional cutoff date YYYY-MM-DD. Defaults to latest date in data."
    )


class ForecastResponse(BaseModel):
    sku_id: str
    horizon: int
    method: str
    cutoff_date: str
    forecast_dates: list[str]
    forecast: list[float]


def _load_dataset() -> pd.DataFrame:
    """
    Load sales data from a path configured by env var.

    Env:
    - FORECAST_DATA_PATH (default: data/raw/sample_sales.csv)
    """
    data_path = os.getenv("FORECAST_DATA_PATH", "data/raw/sample_sales.csv")
    # Resolve relative to repo root
    p = Path(data_path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.exists():
        raise FileNotFoundError(f"Forecast data not found at: {p}")
    return load_sales_data(p)


def _forecast_series(y_train: pd.Series, req: ForecastRequest) -> list[float]:
    if req.method == "naive":
        return naive_forecast(y_train, req.horizon).y_pred.tolist()
    if req.method == "moving_average":
        return moving_average_forecast(y_train, req.horizon, window=req.ma_window).y_pred.tolist()
    return simple_exponential_smoothing_forecast(y_train, req.horizon, alpha=req.ses_alpha).y_pred.tolist()


app = FastAPI(
    title="E-commerce Forecasting API",
    version="0.1.0",
    description="Forecast demand for a SKU using baseline models (tutorial deployment).",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    try:
        df = _load_dataset()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if "sku_id" not in df.columns or "date" not in df.columns or "units_sold" not in df.columns:
        raise HTTPException(status_code=500, detail="Dataset missing required columns: date, sku_id, units_sold")

    df_sku = df[df["sku_id"] == req.sku_id].copy()
    if df_sku.empty:
        raise HTTPException(status_code=404, detail=f"SKU not found: {req.sku_id}")

    df_sku = df_sku.sort_values("date")
    cutoff = pd.to_datetime(req.cutoff_date) if req.cutoff_date else df_sku["date"].max()

    train = df_sku[df_sku["date"] <= cutoff]
    if train.empty:
        raise HTTPException(status_code=400, detail="Cutoff date is before first available date for this SKU")

    y_train = train["units_sold"].astype(float)
    y_pred = _forecast_series(y_train, req)

    future_dates = pd.date_range(start=cutoff + pd.Timedelta(days=1), periods=req.horizon, freq="D")

    return ForecastResponse(
        sku_id=req.sku_id,
        horizon=req.horizon,
        method=req.method,
        cutoff_date=str(pd.to_datetime(cutoff).date()),
        forecast_dates=[str(d.date()) for d in future_dates],
        forecast=[float(x) for x in y_pred],
    )


