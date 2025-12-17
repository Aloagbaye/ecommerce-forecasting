"""
Machine learning utilities for global (multi-SKU) forecasting.

This module focuses on:
- creating a horizon target (y_{t+h})
- building sklearn pipelines with categorical + numeric features
- training and evaluating models with time-based splits

The notebook (Module 5) uses these helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SupervisedDataset:
    X: pd.DataFrame
    y: pd.Series
    feature_cols: List[str]
    categorical_cols: List[str]
    numeric_cols: List[str]


def make_horizon_target(
    df: pd.DataFrame,
    group_col: str,
    date_col: str,
    target_col: str,
    horizon: int,
    target_name: str = "y",
) -> pd.DataFrame:
    """
    Add a future target column: y(t+h) per group (SKU).

    This does NOT modify features; it only creates the label.
    """
    if horizon <= 0:
        raise ValueError("horizon must be > 0")

    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    out = out.sort_values([group_col, date_col]).reset_index(drop=True)
    out[target_name] = out.groupby(group_col)[target_col].shift(-horizon)
    return out


def time_cutoff_split(
    df: pd.DataFrame,
    date_col: str,
    cutoff: pd.Timestamp,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split by time:
    - train: date <= cutoff
    - valid: date > cutoff
    """
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col])
    cutoff = pd.to_datetime(cutoff)
    train = d[d[date_col] <= cutoff].copy()
    valid = d[d[date_col] > cutoff].copy()
    return train, valid


def build_supervised_dataset(
    df: pd.DataFrame,
    date_col: str,
    target_name: str,
    drop_cols: Optional[Sequence[str]] = None,
    categorical_cols: Optional[Sequence[str]] = None,
) -> SupervisedDataset:
    """
    Prepare X/y and infer numeric/categorical columns for modeling.

    Notes:
    - We typically DROP the contemporaneous `units_sold` to avoid leakage-like behavior
      when using engineered lag features (keep lags/rollings instead).
    """
    d = df.copy()
    d = d.dropna(subset=[target_name]).reset_index(drop=True)

    drop_cols = list(drop_cols) if drop_cols is not None else []
    # Always remove the date and the label from X
    drop_cols = list(set(drop_cols + [date_col, target_name]))

    # Determine categorical columns
    if categorical_cols is None:
        categorical_cols = [c for c in d.columns if d[c].dtype == "object"]
    else:
        categorical_cols = list(categorical_cols)

    feature_cols = [c for c in d.columns if c not in drop_cols]
    X = d[feature_cols]
    y = d[target_name].astype(float)

    cat = [c for c in categorical_cols if c in feature_cols]
    num = [c for c in feature_cols if c not in cat]

    return SupervisedDataset(
        X=X,
        y=y,
        feature_cols=feature_cols,
        categorical_cols=cat,
        numeric_cols=num,
    )


def build_sklearn_pipeline(model, categorical_cols: List[str], numeric_cols: List[str]):
    """
    Build a sklearn Pipeline with:
    - OneHotEncoder for categorical columns
    - passthrough numeric columns
    - provided model
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols),
        ],
        remainder="drop",
    )

    return Pipeline([("pre", pre), ("model", model)])


def make_model(kind: str = "ridge", random_state: int = 42):
    """
    Factory for common models.

    kind:
    - ridge (fast, strong baseline)
    - rf (random forest)
    - xgb (xgboost, if installed)
    - lgbm (lightgbm, if installed)
    """
    kind = kind.lower()

    if kind == "ridge":
        from sklearn.linear_model import Ridge

        return Ridge(alpha=1.0, random_state=random_state)

    if kind == "rf":
        from sklearn.ensemble import RandomForestRegressor

        return RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=random_state,
        )

    if kind == "xgb":
        try:
            from xgboost import XGBRegressor
        except Exception as e:  # pragma: no cover
            raise ImportError("xgboost is not installed. Install xgboost or use ridge/rf.") from e
        return XGBRegressor(
            n_estimators=800,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            n_jobs=-1,
            random_state=random_state,
        )

    if kind == "lgbm":
        try:
            from lightgbm import LGBMRegressor
        except Exception as e:  # pragma: no cover
            raise ImportError("lightgbm is not installed. Install lightgbm or use ridge/rf.") from e
        return LGBMRegressor(
            n_estimators=2000,
            learning_rate=0.03,
            num_leaves=63,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            n_jobs=-1,
        )

    raise ValueError("Unknown model kind. Use: ridge, rf, xgb, lgbm")


def permutation_importance_topk(pipeline, X_valid: pd.DataFrame, y_valid: pd.Series, k: int = 20):
    """
    Compute permutation importance for a fitted sklearn pipeline and return top-k features.
    """
    from sklearn.inspection import permutation_importance

    r = permutation_importance(
        pipeline,
        X_valid,
        y_valid,
        n_repeats=5,
        random_state=42,
        scoring="neg_mean_absolute_error",
    )

    # Feature names after preprocessing (may be many due to one-hot)
    pre = pipeline.named_steps["pre"]
    n_imp = len(r.importances_mean)
    try:
        names = np.asarray(pre.get_feature_names_out(), dtype=object)
    except Exception:  # pragma: no cover
        names = np.asarray([f"f{i}" for i in range(n_imp)], dtype=object)

    # Some sklearn versions / pipeline configurations can return a different number
    # of feature names than the permutation importance vector length. Fall back to
    # generated names to avoid shape errors.
    if len(names) != n_imp:
        names = np.asarray([f"f{i}" for i in range(n_imp)], dtype=object)

    imp = pd.DataFrame({"feature": names, "importance": r.importances_mean})
    imp = imp.sort_values("importance", ascending=False).head(k).reset_index(drop=True)
    return imp


