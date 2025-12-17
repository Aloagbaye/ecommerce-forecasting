"""
Prefect orchestration for the batch forecasting pipeline (Module 8).

Run locally:
  python pipelines/prefect_forecasting_flow.py

Or from CLI (after `pip install prefect`):
  prefect server start
  python pipelines/prefect_forecasting_flow.py

This flow reuses the same forecasting logic as `pipelines/forecasting_pipeline.py`,
but adds:
- task-level retries
- structured logging
- a first step toward scheduling/deployments
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from prefect import flow, get_run_logger, task
import json

# Ensure `src/` imports work regardless of current working directory.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.loaders import load_sales_data
from src.models.baseline import forecast_by_sku

from pipelines.forecasting_pipeline import PipelineConfig, compute_cutoff, load_config


@task(retries=2, retry_delay_seconds=5)
def load_raw_data(raw_path: str) -> pd.DataFrame:
    p = Path(raw_path)
    if not p.exists():
        raise FileNotFoundError(f"Raw data not found: {p}")
    return load_sales_data(p)


@task
def make_forecasts(df: pd.DataFrame, cfg: PipelineConfig) -> pd.DataFrame:
    cutoff = compute_cutoff(
        df,
        date_col="date",
        horizon=cfg.horizon_days,
        cutoff_mode=cfg.cutoff_mode,
        cutoff_date=cfg.cutoff_date,
    )
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

    forecasts.attrs["cutoff"] = str(cutoff)
    return forecasts


@task
def write_artifacts(df_raw: pd.DataFrame, forecasts: pd.DataFrame, cfg: PipelineConfig, run_id: str) -> dict:
    Path(cfg.forecasts_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.reports_dir).mkdir(parents=True, exist_ok=True)

    forecast_path = Path(cfg.forecasts_dir) / f"{run_id}_sku_forecasts.csv"
    forecasts.to_csv(forecast_path, index=False)

    report = {
        "run_id": run_id,
        "config": asdict(cfg),
        "data": {
            "raw_path": cfg.raw_path,
            "rows": int(len(df_raw)),
            "date_min": str(pd.to_datetime(df_raw["date"]).min()),
            "date_max": str(pd.to_datetime(df_raw["date"]).max()),
            "unique_skus": int(df_raw["sku_id"].nunique()),
        },
        "forecast": {
            "cutoff": forecasts.attrs.get("cutoff"),
            "horizon_days": int(cfg.horizon_days),
            "method": cfg.method,
            "rows": int(len(forecasts)),
            "output": str(forecast_path),
        },
    }

    report_path = Path(cfg.reports_dir) / f"{run_id}_prefect_pipeline_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {"forecast_path": str(forecast_path), "report_path": str(report_path)}


@flow(name="ecommerce-forecasting-batch-forecast")
def batch_forecast_flow(config_path: str = "config/pipeline.yaml", raw_path_override: Optional[str] = None) -> dict:
    logger = get_run_logger()
    cfg = load_config(config_path)
    if raw_path_override:
        cfg = PipelineConfig(**{**asdict(cfg), "raw_path": raw_path_override})

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger.info(f"Starting batch forecast run_id={run_id}")
    logger.info(f"Config: {cfg}")

    df_raw = load_raw_data(cfg.raw_path)
    forecasts = make_forecasts(df_raw, cfg)
    artifacts = write_artifacts(df_raw, forecasts, cfg, run_id)

    logger.info(f"Done. Forecasts: {artifacts['forecast_path']}")
    logger.info(f"Report: {artifacts['report_path']}")
    return artifacts


if __name__ == "__main__":
    batch_forecast_flow()


