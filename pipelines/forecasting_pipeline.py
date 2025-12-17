"""
Module 8: Batch Forecasting Pipeline (CLI).

This script runs a simple, reproducible batch forecast across many SKUs and writes:
- outputs/forecasts/<run_id>_sku_forecasts.csv
- outputs/reports/<run_id>_pipeline_report.json

It intentionally keeps orchestration lightweight (pure Python) so it's easy to evolve
into Airflow/Prefect later.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

from src.data.loaders import load_sales_data
from src.models.baseline import forecast_by_sku


@dataclass(frozen=True)
class PipelineConfig:
    raw_path: str
    horizon_days: int
    cutoff_mode: str
    cutoff_date: Optional[str]
    method: str
    ma_window: int
    ses_alpha: float
    forecasts_dir: str
    reports_dir: str


def _load_yaml_config(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml is not installed. Install it or run without --config.")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(path: Optional[str]) -> PipelineConfig:
    # Defaults
    cfg = {
        "pipeline": {"horizon_days": 14, "cutoff_mode": "max_minus_horizon", "cutoff_date": None},
        "data": {"raw_path": "data/raw/sample_sales.csv"},
        "forecasting": {"method": "moving_average", "ma_window": 7, "ses_alpha": 0.3},
        "outputs": {"forecasts_dir": "outputs/forecasts", "reports_dir": "outputs/reports"},
    }

    if path:
        p = Path(path)
        loaded = _load_yaml_config(p)
        # shallow merge for our simple structure
        for k in cfg:
            if k in loaded and isinstance(loaded[k], dict):
                cfg[k].update(loaded[k])

    return PipelineConfig(
        raw_path=str(cfg["data"]["raw_path"]),
        horizon_days=int(cfg["pipeline"]["horizon_days"]),
        cutoff_mode=str(cfg["pipeline"]["cutoff_mode"]),
        cutoff_date=cfg["pipeline"].get("cutoff_date"),
        method=str(cfg["forecasting"]["method"]),
        ma_window=int(cfg["forecasting"]["ma_window"]),
        ses_alpha=float(cfg["forecasting"]["ses_alpha"]),
        forecasts_dir=str(cfg["outputs"]["forecasts_dir"]),
        reports_dir=str(cfg["outputs"]["reports_dir"]),
    )


def compute_cutoff(df: pd.DataFrame, date_col: str, horizon: int, cutoff_mode: str, cutoff_date: Optional[str]):
    max_date = pd.to_datetime(df[date_col]).max()
    if cutoff_mode == "max_minus_horizon":
        return max_date - pd.Timedelta(days=horizon)
    if cutoff_mode == "explicit":
        if not cutoff_date:
            raise ValueError("cutoff_date must be provided when cutoff_mode=explicit")
        return pd.to_datetime(cutoff_date)
    raise ValueError("cutoff_mode must be one of: max_minus_horizon, explicit")


def main():
    parser = argparse.ArgumentParser(description="Batch forecasting pipeline (Module 8)")
    parser.add_argument("--config", type=str, default="config/pipeline.yaml", help="Path to YAML config file")
    parser.add_argument("--raw-path", type=str, default=None, help="Override raw data path")
    parser.add_argument("--horizon", type=int, default=None, help="Override forecast horizon (days)")
    parser.add_argument("--method", type=str, default=None, help="Override method: naive|moving_average|ses")
    parser.add_argument("--ma-window", type=int, default=None, help="Override moving average window")
    parser.add_argument("--ses-alpha", type=float, default=None, help="Override SES alpha")
    args = parser.parse_args()

    cfg = load_config(args.config if args.config else None)
    if args.raw_path:
        cfg = PipelineConfig(**{**asdict(cfg), "raw_path": args.raw_path})
    if args.horizon:
        cfg = PipelineConfig(**{**asdict(cfg), "horizon_days": args.horizon})
    if args.method:
        cfg = PipelineConfig(**{**asdict(cfg), "method": args.method})
    if args.ma_window:
        cfg = PipelineConfig(**{**asdict(cfg), "ma_window": args.ma_window})
    if args.ses_alpha:
        cfg = PipelineConfig(**{**asdict(cfg), "ses_alpha": args.ses_alpha})

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    raw_path = Path(cfg.raw_path)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data not found: {raw_path}")

    df = load_sales_data(raw_path)

    cutoff = compute_cutoff(df, date_col="date", horizon=cfg.horizon_days, cutoff_mode=cfg.cutoff_mode, cutoff_date=cfg.cutoff_date)
    train = df[df["date"] <= cutoff].copy()

    forecasts = forecast_by_sku(
        train,
        sku_col="sku_id",
        date_col="date",
        target_col="units_sold",
        horizon=cfg.horizon_days,
        method=cfg.method,
        ma_window=cfg.ma_window,
        ses_alpha=cfg.ses_alpha,
        cutoff_date=cutoff,
    )

    # Attach hierarchy columns for downstream use
    if "category" in df.columns and "subcategory" in df.columns:
        mapping = df[["sku_id", "category", "subcategory"]].drop_duplicates("sku_id")
        forecasts = forecasts.merge(mapping, on="sku_id", how="left")

    Path(cfg.forecasts_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.reports_dir).mkdir(parents=True, exist_ok=True)

    forecast_path = Path(cfg.forecasts_dir) / f"{run_id}_sku_forecasts.csv"
    forecasts.to_csv(forecast_path, index=False)

    report = {
        "run_id": run_id,
        "config": asdict(cfg),
        "data": {
            "raw_path": str(raw_path),
            "rows": int(len(df)),
            "date_min": str(pd.to_datetime(df["date"]).min()),
            "date_max": str(pd.to_datetime(df["date"]).max()),
            "unique_skus": int(df["sku_id"].nunique()),
        },
        "forecast": {
            "cutoff": str(cutoff),
            "horizon_days": int(cfg.horizon_days),
            "method": cfg.method,
            "rows": int(len(forecasts)),
            "output": str(forecast_path),
        },
    }

    report_path = Path(cfg.reports_dir) / f"{run_id}_pipeline_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("✓ Forecast pipeline complete")
    print("Forecasts:", forecast_path)
    print("Report:", report_path)


if __name__ == "__main__":
    # Ensure relative imports work when called directly
    os.environ.setdefault("PYTHONPATH", str(Path(__file__).resolve().parents[1]))
    main()


