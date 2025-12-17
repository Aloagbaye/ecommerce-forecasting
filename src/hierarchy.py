"""
Hierarchical forecasting utilities.

This module supports common retail hierarchies like:
category -> subcategory -> sku

Core concepts:
- Aggregate historical data to different levels
- Produce forecasts at one or more levels
- Reconcile forecasts so totals are consistent across the hierarchy

We implement lightweight reconciliation methods suitable for tutorial use:
- Bottom-up: sum SKU forecasts to higher levels
- Top-down (proportional): allocate higher-level forecasts down using historical proportions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

Level = Literal["sku", "subcategory", "category"]


@dataclass(frozen=True)
class HierarchySpec:
    date_col: str = "date"
    sku_col: str = "sku_id"
    category_col: str = "category"
    subcategory_col: str = "subcategory"
    target_col: str = "units_sold"


def ensure_columns(df: pd.DataFrame, cols: Sequence[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def aggregate_to_level(
    df: pd.DataFrame,
    spec: HierarchySpec,
    level: Level,
) -> pd.DataFrame:
    """
    Aggregate data to a hierarchy level.

    Returns a dataframe with columns:
    - date
    - id columns for the level (category/subcategory/sku)
    - target (summed)
    """
    ensure_columns(df, [spec.date_col, spec.target_col, spec.sku_col, spec.category_col])
    d = df.copy()
    d[spec.date_col] = pd.to_datetime(d[spec.date_col])

    if level == "category":
        keys = [spec.date_col, spec.category_col]
    elif level == "subcategory":
        ensure_columns(d, [spec.subcategory_col])
        keys = [spec.date_col, spec.category_col, spec.subcategory_col]
    elif level == "sku":
        ensure_columns(d, [spec.subcategory_col])
        keys = [spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col]
    else:
        raise ValueError("level must be one of: sku, subcategory, category")

    out = d.groupby(keys, as_index=False)[spec.target_col].sum()
    return out.sort_values(keys).reset_index(drop=True)


def bottom_up_reconcile(
    sku_forecasts: pd.DataFrame,
    spec: HierarchySpec,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Bottom-up reconciliation:
    - subcategory forecast = sum(sku forecasts)
    - category forecast = sum(subcategory forecasts)

    Expects `sku_forecasts` to have columns:
    - date, category, subcategory, sku_id, y_pred
    """
    ensure_columns(
        sku_forecasts,
        [spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, "y_pred"],
    )
    d = sku_forecasts.copy()
    d[spec.date_col] = pd.to_datetime(d[spec.date_col])

    subcat = (
        d.groupby([spec.date_col, spec.category_col, spec.subcategory_col], as_index=False)["y_pred"].sum()
        .rename(columns={"y_pred": "y_pred_subcategory"})
    )
    cat = (
        subcat.groupby([spec.date_col, spec.category_col], as_index=False)["y_pred_subcategory"].sum()
        .rename(columns={"y_pred_subcategory": "y_pred_category"})
    )
    return subcat, cat


def compute_topdown_proportions(
    history: pd.DataFrame,
    spec: HierarchySpec,
    window_days: int = 90,
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Compute allocation proportions for top-down reconciliation based on recent history.

    Returns rows keyed by (category, subcategory, sku_id) with a `prop` column that
    sums to 1 within each category (or category/subcategory depending on use).
    """
    ensure_columns(history, [spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, spec.target_col])
    d = history.copy()
    d[spec.date_col] = pd.to_datetime(d[spec.date_col])
    if as_of is None:
        as_of = d[spec.date_col].max()
    as_of = pd.to_datetime(as_of)

    start = as_of - pd.Timedelta(days=window_days)
    recent = d[(d[spec.date_col] > start) & (d[spec.date_col] <= as_of)].copy()
    if recent.empty:
        raise ValueError("No data in the selected history window for computing proportions.")

    # Sum demand by sku within category
    sku_sum = recent.groupby([spec.category_col, spec.subcategory_col, spec.sku_col], as_index=False)[spec.target_col].sum()
    cat_sum = sku_sum.groupby([spec.category_col], as_index=False)[spec.target_col].sum().rename(columns={spec.target_col: "cat_total"})
    merged = sku_sum.merge(cat_sum, on=[spec.category_col], how="left")
    merged["prop_in_category"] = merged[spec.target_col] / (merged["cat_total"] + 1e-9)

    # Also compute within-subcategory proportions (often useful)
    sub_sum = sku_sum.groupby([spec.category_col, spec.subcategory_col], as_index=False)[spec.target_col].sum().rename(
        columns={spec.target_col: "sub_total"}
    )
    merged = merged.merge(sub_sum, on=[spec.category_col, spec.subcategory_col], how="left")
    merged["prop_in_subcategory"] = merged[spec.target_col] / (merged["sub_total"] + 1e-9)

    return merged[[spec.category_col, spec.subcategory_col, spec.sku_col, "prop_in_category", "prop_in_subcategory"]]


def top_down_reconcile(
    higher_level_forecast: pd.DataFrame,
    history: pd.DataFrame,
    spec: HierarchySpec,
    from_level: Literal["category", "subcategory"] = "category",
    to_level: Literal["subcategory", "sku"] = "sku",
    window_days: int = 90,
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Top-down (proportional) reconciliation.

    - If from_level='category' and to_level='sku': allocate category forecast to SKUs using prop_in_category
    - If from_level='subcategory' and to_level='sku': allocate subcategory forecast to SKUs using prop_in_subcategory

    Expected forecast columns:
    - category forecast: date, category, y_pred
    - subcategory forecast: date, category, subcategory, y_pred

    Returns:
    - reconciled forecasts at the `to_level`
    """
    ensure_columns(history, [spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, spec.target_col])
    props = compute_topdown_proportions(history, spec=spec, window_days=window_days, as_of=as_of)

    f = higher_level_forecast.copy()
    f[spec.date_col] = pd.to_datetime(f[spec.date_col])

    if from_level == "category" and to_level == "sku":
        ensure_columns(f, [spec.date_col, spec.category_col, "y_pred"])
        out = f.merge(props, on=[spec.category_col], how="left")
        out["y_pred"] = out["y_pred"] * out["prop_in_category"]
        return out[[spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, "y_pred"]]

    if from_level == "subcategory" and to_level == "sku":
        ensure_columns(f, [spec.date_col, spec.category_col, spec.subcategory_col, "y_pred"])
        out = f.merge(props, on=[spec.category_col, spec.subcategory_col], how="left")
        out["y_pred"] = out["y_pred"] * out["prop_in_subcategory"]
        return out[[spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, "y_pred"]]

    raise ValueError("Unsupported from_level/to_level combination for top-down reconciliation.")


def reconcile_to_category_totals(
    sku_forecasts: pd.DataFrame,
    category_forecasts: pd.DataFrame,
    spec: HierarchySpec,
) -> pd.DataFrame:
    """
    Simple reconciliation: scale SKU forecasts within each category/date so that
    sum_sku == category_forecast.

    This is a lightweight alternative to MinT-style reconciliation.
    """
    ensure_columns(sku_forecasts, [spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, "y_pred"])
    ensure_columns(category_forecasts, [spec.date_col, spec.category_col, "y_pred"])

    s = sku_forecasts.copy()
    c = category_forecasts.copy()
    s[spec.date_col] = pd.to_datetime(s[spec.date_col])
    c[spec.date_col] = pd.to_datetime(c[spec.date_col])

    s_sum = s.groupby([spec.date_col, spec.category_col], as_index=False)["y_pred"].sum().rename(columns={"y_pred": "sum_sku"})
    m = s.merge(s_sum, on=[spec.date_col, spec.category_col], how="left").merge(
        c.rename(columns={"y_pred": "cat_pred"}), on=[spec.date_col, spec.category_col], how="left"
    )
    scale = m["cat_pred"] / (m["sum_sku"] + 1e-9)
    m["y_pred_reconciled"] = m["y_pred"] * scale
    return m[[spec.date_col, spec.category_col, spec.subcategory_col, spec.sku_col, "y_pred_reconciled"]].rename(
        columns={"y_pred_reconciled": "y_pred"}
    )


