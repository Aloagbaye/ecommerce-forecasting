"""
Baseline forecasting models.

These models are intentionally simple and are used to establish benchmark performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastResult:
    """Container for forecast output."""

    y_pred: np.ndarray


def _to_1d_array(y: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(y), dtype=float)
    if arr.ndim != 1:
        raise ValueError("y must be a 1D iterable of numbers")
    if len(arr) == 0:
        raise ValueError("y must not be empty")
    return arr


def naive_forecast(y_train: Iterable[float], horizon: int) -> ForecastResult:
    """
    Naive forecast: repeats the last observed value for the entire horizon.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")
    y = _to_1d_array(y_train)
    last = y[-1]
    return ForecastResult(y_pred=np.full(horizon, last, dtype=float))


def moving_average_forecast(
    y_train: Iterable[float],
    horizon: int,
    window: int = 7,
) -> ForecastResult:
    """
    Moving average forecast: uses the average of the last `window` observations.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")
    if window <= 0:
        raise ValueError("window must be > 0")
    y = _to_1d_array(y_train)
    w = min(window, len(y))
    avg = float(np.mean(y[-w:]))
    return ForecastResult(y_pred=np.full(horizon, avg, dtype=float))


def simple_exponential_smoothing_forecast(
    y_train: Iterable[float],
    horizon: int,
    alpha: float = 0.3,
) -> ForecastResult:
    """
    Simple Exponential Smoothing (SES) forecast.

    Uses a one-parameter smoothing for level; forecast is a flat line at the final level.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")
    if not (0 < alpha <= 1):
        raise ValueError("alpha must be in (0, 1]")
    y = _to_1d_array(y_train)

    level = y[0]
    for t in range(1, len(y)):
        level = alpha * y[t] + (1 - alpha) * level

    return ForecastResult(y_pred=np.full(horizon, float(level), dtype=float))


def forecast_by_sku(
    df: pd.DataFrame,
    sku_col: str,
    date_col: str,
    target_col: str,
    horizon: int,
    method: str = "naive",
    ma_window: int = 7,
    ses_alpha: float = 0.3,
    cutoff_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Convenience helper: produce per-SKU forecasts at a given cutoff date.

    Returns a dataframe with columns: sku_col, date_col, y_pred, method.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")
    if method not in {"naive", "moving_average", "ses"}:
        raise ValueError("method must be one of: naive, moving_average, ses")

    data = df[[sku_col, date_col, target_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col])
    data = data.sort_values([sku_col, date_col]).reset_index(drop=True)

    if cutoff_date is None:
        cutoff_date = data[date_col].max()
    cutoff_date = pd.to_datetime(cutoff_date)

    forecast_rows = []

    for sku, g in data.groupby(sku_col, sort=False):
        train = g[g[date_col] <= cutoff_date]
        if len(train) == 0:
            continue
        y_train = train[target_col].to_numpy(dtype=float)

        if method == "naive":
            fr = naive_forecast(y_train, horizon=horizon)
        elif method == "moving_average":
            fr = moving_average_forecast(y_train, horizon=horizon, window=ma_window)
        else:
            fr = simple_exponential_smoothing_forecast(y_train, horizon=horizon, alpha=ses_alpha)

        future_dates = pd.date_range(start=cutoff_date + pd.Timedelta(days=1), periods=horizon, freq="D")
        forecast_rows.extend(
            {
                sku_col: sku,
                date_col: d,
                "y_pred": float(p),
                "method": method,
            }
            for d, p in zip(future_dates, fr.y_pred)
        )

    return pd.DataFrame(forecast_rows)


