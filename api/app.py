from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Header
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
from src.explanations import ExplanationContext, explain_forecast


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


class ExplainRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier, e.g. SKU001")
    horizon: int = Field(14, ge=1, le=365, description="Forecast horizon (days)")
    method: Literal["naive", "moving_average", "ses"] = Field("moving_average")
    ma_window: int = Field(7, ge=1, le=365)
    ses_alpha: float = Field(0.3, gt=0.0, le=1.0)
    cutoff_date: Optional[str] = Field(None, description="Optional cutoff date YYYY-MM-DD.")


class ExplainResponse(BaseModel):
    sku_id: str
    cutoff_date: str
    horizon: int
    method: str
    explanation_mode: str
    explanation: str
    bullets: list[str]


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


class _DatasetCache:
    """
    Simple in-memory dataset cache with file mtime tracking.

    Env:
    - FORECAST_DATA_PATH: path to CSV (default: data/raw/sample_sales.csv)
    - FORECAST_CACHE_TTL_SECONDS: optional TTL; 0/empty disables TTL checks (mtime-only)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._df: Optional[pd.DataFrame] = None
        self._path: Optional[Path] = None
        self._mtime: Optional[float] = None
        self._loaded_at: Optional[float] = None

    def _resolve_path(self) -> Path:
        data_path = os.getenv("FORECAST_DATA_PATH", "data/raw/sample_sales.csv")
        p = Path(data_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p

    def _ttl_seconds(self) -> int:
        raw = os.getenv("FORECAST_CACHE_TTL_SECONDS", "").strip()
        if not raw:
            return 0
        try:
            return max(0, int(raw))
        except ValueError:
            return 0

    def get(self) -> pd.DataFrame:
        p = self._resolve_path()
        if not p.exists():
            raise FileNotFoundError(f"Forecast data not found at: {p}")

        ttl = self._ttl_seconds()
        now = time.time()
        mtime = p.stat().st_mtime

        with self._lock:
            needs_load = self._df is None or self._path != p or self._mtime != mtime
            if not needs_load and ttl > 0 and self._loaded_at is not None:
                if now - self._loaded_at > ttl:
                    needs_load = True

            if needs_load:
                df = load_sales_data(p)
                self._df = df
                self._path = p
                self._mtime = mtime
                self._loaded_at = now

            # Return cached df (callers must treat as read-only)
            return self._df

    def reload(self) -> pd.DataFrame:
        p = self._resolve_path()
        if not p.exists():
            raise FileNotFoundError(f"Forecast data not found at: {p}")
        with self._lock:
            df = load_sales_data(p)
            self._df = df
            self._path = p
            self._mtime = p.stat().st_mtime
            self._loaded_at = time.time()
            return df


DATASET_CACHE = _DatasetCache()


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


@app.post("/admin/reload")
def admin_reload(x_admin_token: Optional[str] = Header(default=None)):
    """
    Force reload the dataset into memory.

    Guarded by env var:
    - FORECAST_ADMIN_TOKEN

    Call with header:
    - X-Admin-Token: <token>
    """
    required = os.getenv("FORECAST_ADMIN_TOKEN")
    if required:
        if not x_admin_token or x_admin_token != required:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        df = DATASET_CACHE.reload()
        return {"status": "reloaded", "rows": int(len(df))}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    try:
        df = DATASET_CACHE.get()
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


@app.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest):
    """
    Generate a forecast + explanation for a SKU.

    Uses:
    - Template explanations by default
    - LLM explanations if LLM_API_KEY is configured (see src/explanations/llm_client.py)
    """
    try:
        df = DATASET_CACHE.get()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    df_sku = df[df["sku_id"] == req.sku_id].copy()
    if df_sku.empty:
        raise HTTPException(status_code=404, detail=f"SKU not found: {req.sku_id}")

    df_sku = df_sku.sort_values("date")
    cutoff = pd.to_datetime(req.cutoff_date) if req.cutoff_date else df_sku["date"].max()
    train = df_sku[df_sku["date"] <= cutoff]
    if train.empty:
        raise HTTPException(status_code=400, detail="Cutoff date is before first available date for this SKU")

    # Build forecast
    fr = ForecastRequest(
        sku_id=req.sku_id,
        horizon=req.horizon,
        method=req.method,
        ma_window=req.ma_window,
        ses_alpha=req.ses_alpha,
        cutoff_date=req.cutoff_date,
    )
    y_train = train["units_sold"].astype(float)
    y_pred = _forecast_series(y_train, fr)
    future_dates = pd.date_range(start=cutoff + pd.Timedelta(days=1), periods=req.horizon, freq="D")

    ctx = ExplanationContext(
        sku_id=req.sku_id,
        cutoff_date=pd.to_datetime(cutoff),
        horizon=req.horizon,
        forecast=[float(x) for x in y_pred],
        forecast_dates=list(future_dates),
        method=req.method,
        top_drivers=None,
    )
    result = explain_forecast(ctx, history=train[["date", "units_sold"] + ([c for c in ["promotion_flag", "price"] if c in train.columns])])

    return ExplainResponse(
        sku_id=req.sku_id,
        cutoff_date=str(pd.to_datetime(cutoff).date()),
        horizon=req.horizon,
        method=req.method,
        explanation_mode=result.mode,
        explanation=result.explanation,
        bullets=result.bullets,
    )


