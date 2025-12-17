"""
Data drift detection utilities.

We implement:
- PSI (Population Stability Index) for numeric columns
- KS statistic (Kolmogorov–Smirnov) for numeric columns (uses scipy if available)

This is intentionally lightweight and tutorial-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd


def psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10, eps: float = 1e-6) -> float:
    """
    Population Stability Index.

    PSI compares the distribution shift between expected (reference) and actual (current).
    Common interpretation (rough):
    - < 0.1: no significant drift
    - 0.1–0.25: moderate drift
    - > 0.25: significant drift
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    expected = expected[np.isfinite(expected)]
    actual = actual[np.isfinite(actual)]
    if expected.size == 0 or actual.size == 0:
        return float("nan")

    # Use quantile bins derived from expected distribution
    quantiles = np.linspace(0, 1, buckets + 1)
    cuts = np.quantile(expected, quantiles)
    cuts = np.unique(cuts)
    if cuts.size < 3:
        return 0.0

    exp_counts, _ = np.histogram(expected, bins=cuts)
    act_counts, _ = np.histogram(actual, bins=cuts)

    exp_perc = exp_counts / max(exp_counts.sum(), 1)
    act_perc = act_counts / max(act_counts.sum(), 1)

    exp_perc = np.clip(exp_perc, eps, 1)
    act_perc = np.clip(act_perc, eps, 1)

    return float(np.sum((act_perc - exp_perc) * np.log(act_perc / exp_perc)))


def ks_statistic(expected: np.ndarray, actual: np.ndarray) -> float:
    """
    KS statistic between two samples.

    Returns NaN if scipy is not available.
    """
    try:
        from scipy.stats import ks_2samp  # type: ignore
    except Exception:
        return float("nan")

    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    expected = expected[np.isfinite(expected)]
    actual = actual[np.isfinite(actual)]
    if expected.size == 0 or actual.size == 0:
        return float("nan")

    return float(ks_2samp(expected, actual).statistic)


def drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    numeric_cols: List[str],
    buckets: int = 10,
) -> pd.DataFrame:
    """
    Compute drift metrics per numeric column.

    Output columns:
    - feature
    - psi
    - ks
    - ref_n
    - cur_n
    """
    rows = []
    for col in numeric_cols:
        if col not in reference.columns or col not in current.columns:
            continue
        ref = reference[col].to_numpy()
        cur = current[col].to_numpy()
        rows.append(
            {
                "feature": col,
                "psi": psi(ref, cur, buckets=buckets),
                "ks": ks_statistic(ref, cur),
                "ref_n": int(np.isfinite(ref).sum()),
                "cur_n": int(np.isfinite(cur).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)


