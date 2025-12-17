"""
Performance monitoring utilities.

We compute rolling error metrics comparing forecasts vs actuals.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from src.evaluation.metrics import wape


def wape_series(y_true: pd.Series, y_pred: pd.Series, eps: float = 1e-9) -> pd.Series:
    """
    Point-wise WAPE numerator/denominator is global; for rolling WAPE we compute over a window.
    This helper exists primarily for API symmetry; use rolling_error_report for windowed metrics.
    """
    yt = y_true.astype(float)
    yp = y_pred.astype(float)
    return (yt - yp).abs() / (yt.abs() + eps)


def rolling_error_report(
    df: pd.DataFrame,
    date_col: str,
    y_true_col: str,
    y_pred_col: str,
    window_days: int = 28,
) -> pd.DataFrame:
    """
    Compute rolling WAPE and MAE aggregated by date (across all SKUs).

    Expects df with at least:
    - date_col
    - y_true_col
    - y_pred_col
    """
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col])
    d = d.sort_values(date_col)

    d = d.assign(abs_err=(d[y_true_col].astype(float) - d[y_pred_col].astype(float)).abs())
    daily = d.groupby(date_col, as_index=False).agg(
        y_true_sum=(y_true_col, "sum"),
        abs_err_sum=("abs_err", "sum"),
        n=(y_true_col, "size"),
    )
    daily["mae"] = daily["abs_err_sum"] / daily["n"].clip(lower=1)

    # Rolling WAPE = rolling(sum abs error) / rolling(sum abs y)
    daily["rolling_wape"] = (
        daily["abs_err_sum"].rolling(window_days, min_periods=1).sum()
        / (daily["y_true_sum"].abs().rolling(window_days, min_periods=1).sum() + 1e-9)
    )

    return daily[[date_col, "mae", "rolling_wape"]]


