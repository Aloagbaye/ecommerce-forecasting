"""
MLflow-based model monitoring + A/B (champion/challenger) evaluation.

This pipeline evaluates two forecasting approaches on the same evaluation window,
logs metrics & artifacts to MLflow, and writes a decision report.

We keep it tutorial-friendly by supporting baseline forecasters as "models":
- champion_method: naive | moving_average | ses
- challenger_method: naive | moving_average | ses

You can later swap these for true ML models (Module 5) while keeping the same logging pattern.

Artifacts written:
- outputs/reports/<run_id>_mlflow_ab_decision.json
- outputs/reports/<run_id>_mlflow_ab_scored.csv

MLflow tracking:
- default local ./mlruns
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

import mlflow

from src.data.loaders import load_sales_data
from src.evaluation.metrics import mae, rmse, wape, smape
from src.models.baseline import forecast_by_sku


def compute_metrics(y_true, y_pred) -> Dict[str, float]:
    return {
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "wape": wape(y_true, y_pred),
        "smape": smape(y_true, y_pred),
    }


def latest_forecast_csv(forecasts_dir: Path) -> Path:
    files = sorted(forecasts_dir.glob("*_sku_forecasts.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No forecast files found in: {forecasts_dir}")
    return files[0]


def run_forecast(df: pd.DataFrame, cutoff: pd.Timestamp, horizon: int, method: str, ma_window: int, ses_alpha: float) -> pd.DataFrame:
    train = df[df["date"] <= cutoff].copy()
    fc = forecast_by_sku(
        train,
        sku_col="sku_id",
        date_col="date",
        target_col="units_sold",
        horizon=horizon,
        method=method,
        ma_window=ma_window,
        ses_alpha=ses_alpha,
        cutoff_date=cutoff,
    )
    return fc


def main():
    p = argparse.ArgumentParser(description="MLflow A/B monitoring pipeline (champion vs challenger)")
    p.add_argument("--raw", default="data/raw/sample_sales.csv", help="Raw data CSV with date/sku_id/units_sold")
    p.add_argument("--forecasts-dir", default="outputs/forecasts", help="Where forecast CSVs live (optional)")
    p.add_argument("--forecast-csv", default=None, help="Optional: use this forecast file to define cutoff/horizon")
    p.add_argument("--horizon", type=int, default=14, help="Forecast horizon days")
    p.add_argument("--cutoff-date", default=None, help="Optional cutoff YYYY-MM-DD; default: max_date - horizon")

    p.add_argument("--champion-method", default="moving_average", choices=["naive", "moving_average", "ses"])
    p.add_argument("--challenger-method", default="ses", choices=["naive", "moving_average", "ses"])
    p.add_argument("--ma-window", type=int, default=7)
    p.add_argument("--ses-alpha", type=float, default=0.3)

    p.add_argument("--experiment", default="ecommerce-forecasting-ab", help="MLflow experiment name")
    p.add_argument("--tracking-uri", default=None, help="MLflow tracking URI (default local ./mlruns)")
    p.add_argument("--reports-dir", default="outputs/reports", help="Where to write decision artifacts")
    args = p.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data not found: {raw_path}")

    df = load_sales_data(raw_path)
    df["date"] = pd.to_datetime(df["date"])

    horizon = int(args.horizon)

    # Determine cutoff
    cutoff = None
    if args.cutoff_date:
        cutoff = pd.to_datetime(args.cutoff_date)
    elif args.forecast_csv:
        fc_tmp = pd.read_csv(args.forecast_csv, parse_dates=["date"])
        cutoff = fc_tmp["date"].min() - pd.Timedelta(days=1)
    else:
        cutoff = df["date"].max() - pd.Timedelta(days=horizon)

    cutoff = pd.to_datetime(cutoff)
    eval_start = cutoff + pd.Timedelta(days=1)
    eval_end = cutoff + pd.Timedelta(days=horizon)

    # Build evaluation actuals window
    actuals = df[(df["date"] >= eval_start) & (df["date"] <= eval_end)][["sku_id", "date", "units_sold"]].rename(
        columns={"units_sold": "y_true"}
    )

    # Generate champion/challenger forecasts
    champ_fc = run_forecast(df, cutoff=cutoff, horizon=horizon, method=args.champion_method, ma_window=args.ma_window, ses_alpha=args.ses_alpha)
    chal_fc = run_forecast(df, cutoff=cutoff, horizon=horizon, method=args.challenger_method, ma_window=args.ma_window, ses_alpha=args.ses_alpha)

    champ_scored = champ_fc.merge(actuals, on=["sku_id", "date"], how="left").rename(columns={"y_pred": "y_pred_champion"})
    chal_scored = chal_fc.merge(actuals, on=["sku_id", "date"], how="left").rename(columns={"y_pred": "y_pred_challenger"})

    scored = champ_scored.merge(
        chal_scored[["sku_id", "date", "y_pred_challenger"]],
        on=["sku_id", "date"],
        how="inner",
    )

    scored = scored.dropna(subset=["y_true"]).reset_index(drop=True)
    if scored.empty:
        raise RuntimeError("No overlapping actuals for the evaluation window. Ensure raw data covers forecast horizon.")

    champ_metrics = compute_metrics(scored["y_true"], scored["y_pred_champion"])
    chal_metrics = compute_metrics(scored["y_true"], scored["y_pred_challenger"])

    # Decide winner by WAPE (lower is better)
    winner = "champion" if champ_metrics["wape"] <= chal_metrics["wape"] else "challenger"

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    # MLflow logging
    if args.tracking_uri:
        mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    with mlflow.start_run(run_name=f"ab-{run_id}"):
        mlflow.log_params(
            {
                "raw_path": str(raw_path),
                "cutoff": str(cutoff.date()),
                "horizon": horizon,
                "champion_method": args.champion_method,
                "challenger_method": args.challenger_method,
                "ma_window": args.ma_window,
                "ses_alpha": args.ses_alpha,
            }
        )

        for k, v in champ_metrics.items():
            mlflow.log_metric(f"champion_{k}", float(v))
        for k, v in chal_metrics.items():
            mlflow.log_metric(f"challenger_{k}", float(v))

        mlflow.log_metric("delta_wape_challenger_minus_champion", float(chal_metrics["wape"] - champ_metrics["wape"]))
        mlflow.log_param("winner", winner)

        # Write artifacts locally then log them
        reports_dir = Path(args.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)

        decision = {
            "run_id": run_id,
            "window": {"cutoff": str(cutoff), "eval_start": str(eval_start), "eval_end": str(eval_end)},
            "champion": {"method": args.champion_method, "metrics": champ_metrics},
            "challenger": {"method": args.challenger_method, "metrics": chal_metrics},
            "winner": winner,
        }

        decision_path = reports_dir / f"{run_id}_mlflow_ab_decision.json"
        decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

        scored_path = reports_dir / f"{run_id}_mlflow_ab_scored.csv"
        scored.to_csv(scored_path, index=False)

        mlflow.log_artifact(str(decision_path))
        mlflow.log_artifact(str(scored_path))

    print("✓ MLflow A/B monitoring complete")
    print("Winner:", winner)
    print("Decision artifact:", decision_path)
    print("Scored artifact:", scored_path)


if __name__ == "__main__":
    main()


