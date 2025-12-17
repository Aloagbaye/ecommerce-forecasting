"""
Module 10: Monitoring + Retraining Trigger

This script generates a monitoring report that combines:
- data drift (PSI/KS) on selected numeric features
- performance decay (rolling WAPE/MAE) comparing forecasts vs actuals

It writes a decision report to outputs/reports/.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from src.data.loaders import load_sales_data
from src.monitoring.drift import drift_report
from src.monitoring.performance import rolling_error_report


def find_latest_forecast_csv(forecasts_dir: Path) -> Path:
    files = sorted(forecasts_dir.glob("*_sku_forecasts.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No forecast CSVs found in {forecasts_dir}")
    return files[0]


def main():
    parser = argparse.ArgumentParser(description="Monitoring and retraining trigger (Module 10)")
    parser.add_argument("--raw", type=str, default="data/raw/sample_sales.csv", help="Raw data CSV path")
    parser.add_argument("--forecast-csv", type=str, default=None, help="Forecast CSV path (defaults to latest)")
    parser.add_argument("--forecasts-dir", type=str, default="outputs/forecasts", help="Forecasts directory")
    parser.add_argument("--reports-dir", type=str, default="outputs/reports", help="Reports directory")
    parser.add_argument("--drift-window-days", type=int, default=90, help="Reference/current drift windows (days)")
    parser.add_argument("--perf-window-days", type=int, default=28, help="Rolling window for performance (days)")
    parser.add_argument("--psi-threshold", type=float, default=0.25, help="PSI threshold to trigger retraining")
    parser.add_argument("--wape-threshold", type=float, default=0.45, help="Rolling WAPE threshold to trigger retraining")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data not found: {raw_path}")

    forecasts_dir = Path(args.forecasts_dir)
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    fc_path = Path(args.forecast_csv) if args.forecast_csv else find_latest_forecast_csv(forecasts_dir)
    if not fc_path.exists():
        raise FileNotFoundError(f"Forecast CSV not found: {fc_path}")

    df = load_sales_data(raw_path)
    fc = pd.read_csv(fc_path, parse_dates=["date"])

    # Join forecasts with actuals (same sku/date)
    actuals = df[["sku_id", "date", "units_sold"]].rename(columns={"units_sold": "y_true"})
    scored = fc.merge(actuals, on=["sku_id", "date"], how="left")

    # Performance report
    perf = rolling_error_report(scored.dropna(subset=["y_true"]), date_col="date", y_true_col="y_true", y_pred_col="y_pred", window_days=args.perf_window_days)

    # Drift report: compare recent history windows on a few numeric columns if present
    df["date"] = pd.to_datetime(df["date"])
    as_of = df["date"].max()
    cur_start = as_of - pd.Timedelta(days=args.drift_window_days)
    ref_start = cur_start - pd.Timedelta(days=args.drift_window_days)

    ref = df[(df["date"] > ref_start) & (df["date"] <= cur_start)]
    cur = df[(df["date"] > cur_start) & (df["date"] <= as_of)]

    numeric_candidates = ["price", "stock_available", "units_sold"]
    numeric_cols = [c for c in numeric_candidates if c in df.columns]
    drift = drift_report(ref, cur, numeric_cols=numeric_cols, buckets=10)

    max_psi = float(drift["psi"].max()) if not drift.empty else float("nan")
    latest_wape = float(perf["rolling_wape"].dropna().iloc[-1]) if not perf.empty else float("nan")

    trigger = False
    reasons: List[str] = []
    if not pd.isna(max_psi) and max_psi >= args.psi_threshold:
        trigger = True
        reasons.append(f"PSI drift threshold exceeded: max_psi={max_psi:.3f} >= {args.psi_threshold}")
    if not pd.isna(latest_wape) and latest_wape >= args.wape_threshold:
        trigger = True
        reasons.append(f"Performance threshold exceeded: rolling_wape={latest_wape:.3f} >= {args.wape_threshold}")

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    report = {
        "run_id": run_id,
        "inputs": {"raw": str(raw_path), "forecast_csv": str(fc_path)},
        "drift": {
            "window_days": args.drift_window_days,
            "numeric_cols": numeric_cols,
            "max_psi": max_psi,
            "top_drift": drift.head(10).to_dict(orient="records"),
        },
        "performance": {
            "window_days": args.perf_window_days,
            "latest_rolling_wape": latest_wape,
        },
        "decision": {"trigger_retrain": trigger, "reasons": reasons},
    }

    out_path = reports_dir / f"{run_id}_module10_monitoring_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Also write csv artifacts
    drift.to_csv(reports_dir / f"{run_id}_module10_drift.csv", index=False)
    perf.to_csv(reports_dir / f"{run_id}_module10_performance.csv", index=False)

    print("✓ Monitoring report written:", out_path)
    if trigger:
        print("⚠ Retraining trigger: TRUE")
        for r in reasons:
            print(" -", r)
    else:
        print("✓ Retraining trigger: FALSE")


if __name__ == "__main__":
    main()


