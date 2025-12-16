"""
Classical time series forecasting models (single-series).

These models are typically fit per-SKU (local models) and do not scale well to thousands of SKUs
without careful orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class ClassicalForecast:
    y_pred: np.ndarray
    model_name: str


def _to_1d(y) -> np.ndarray:
    arr = np.asarray(y, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("y must not be empty")
    return arr


def ets_holt_winters_forecast(
    y_train,
    horizon: int,
    seasonal_periods: Optional[int] = 7,
    trend: Optional[str] = "add",
    seasonal: Optional[str] = "add",
) -> ClassicalForecast:
    """
    Exponential Smoothing (ETS / Holt-Winters) forecast via statsmodels.

    Parameters
    ----------
    y_train : array-like
    horizon : int
    seasonal_periods : int or None
        7 for weekly seasonality on daily data. Use None to disable seasonality.
    trend : {'add','mul',None}
    seasonal : {'add','mul',None}
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")

    y = _to_1d(y_train)

    # Lazy import: statsmodels is heavier and not always needed.
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    model = ExponentialSmoothing(
        y,
        trend=trend,
        seasonal=seasonal if seasonal_periods else None,
        seasonal_periods=seasonal_periods if seasonal_periods else None,
        initialization_method="estimated",
    )
    fit = model.fit(optimized=True)
    y_pred = np.asarray(fit.forecast(horizon), dtype=float)
    return ClassicalForecast(y_pred=y_pred, model_name="ets_holt_winters")


def sarimax_forecast(
    y_train,
    horizon: int,
    order: Tuple[int, int, int] = (1, 1, 1),
    seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 7),
    enforce_stationarity: bool = False,
    enforce_invertibility: bool = False,
) -> ClassicalForecast:
    """
    SARIMAX forecast via statsmodels.

    Parameters
    ----------
    y_train : array-like
    horizon : int
    order : (p,d,q)
    seasonal_order : (P,D,Q,s)
        Use s=7 for weekly seasonality on daily data. Set to (0,0,0,0) to disable.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")

    y = _to_1d(y_train)

    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(
        y,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=enforce_stationarity,
        enforce_invertibility=enforce_invertibility,
    )
    fit = model.fit(disp=False)
    y_pred = np.asarray(fit.forecast(horizon), dtype=float)
    return ClassicalForecast(y_pred=y_pred, model_name="sarimax")


def sarimax_fit_residuals(
    y_train,
    order: Tuple[int, int, int] = (1, 1, 1),
    seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 7),
):
    """
    Fit SARIMAX and return residuals for diagnostics in notebooks.
    """
    y = _to_1d(y_train)
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(y, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    fit = model.fit(disp=False)
    resid = np.asarray(fit.resid, dtype=float)
    return fit, resid


