"""
Forecast evaluation metrics.

We include business-friendly metrics like WAPE and sMAPE to handle zeros better than MAPE.
"""

from __future__ import annotations

import numpy as np


def _to_1d(a) -> np.ndarray:
    arr = np.asarray(a, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("Input array must not be empty")
    return arr


def mae(y_true, y_pred) -> float:
    """Mean Absolute Error."""
    yt = _to_1d(y_true)
    yp = _to_1d(y_pred)
    if yt.size != yp.size:
        raise ValueError("y_true and y_pred must have the same length")
    return float(np.mean(np.abs(yt - yp)))


def rmse(y_true, y_pred) -> float:
    """Root Mean Squared Error."""
    yt = _to_1d(y_true)
    yp = _to_1d(y_pred)
    if yt.size != yp.size:
        raise ValueError("y_true and y_pred must have the same length")
    return float(np.sqrt(np.mean((yt - yp) ** 2)))


def wape(y_true, y_pred, eps: float = 1e-9) -> float:
    """
    Weighted Absolute Percentage Error.

    WAPE = sum(|y - yhat|) / (sum(|y|) + eps)
    """
    yt = _to_1d(y_true)
    yp = _to_1d(y_pred)
    if yt.size != yp.size:
        raise ValueError("y_true and y_pred must have the same length")
    denom = float(np.sum(np.abs(yt)) + eps)
    return float(np.sum(np.abs(yt - yp)) / denom)


def smape(y_true, y_pred, eps: float = 1e-9) -> float:
    """
    Symmetric Mean Absolute Percentage Error (sMAPE).

    sMAPE = mean( 2*|y - yhat| / (|y| + |yhat| + eps) )
    """
    yt = _to_1d(y_true)
    yp = _to_1d(y_pred)
    if yt.size != yp.size:
        raise ValueError("y_true and y_pred must have the same length")
    denom = np.abs(yt) + np.abs(yp) + eps
    return float(np.mean(2 * np.abs(yt - yp) / denom))


