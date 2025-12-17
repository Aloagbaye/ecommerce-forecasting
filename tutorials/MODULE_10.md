# Module 10: Monitoring & Drift Detection

This module teaches how to keep forecasts reliable in production by monitoring:
- **Data drift** (inputs changing)
- **Performance decay** (errors increasing)
- **Retraining triggers** (when to retrain)

---

## ✅ What’s Implemented in This Repo

### Monitoring utilities
- `src/monitoring/drift.py`
  - **PSI** (Population Stability Index)
  - **KS statistic** (optional; uses SciPy if installed)
- `src/monitoring/performance.py`
  - rolling **MAE**
  - rolling **WAPE**

### Retraining trigger pipeline
- `pipelines/retraining_trigger.py`

It combines drift + performance into a single decision report:
- `outputs/reports/<run_id>_module10_monitoring_report.json`
- plus CSV artifacts:
  - `<run_id>_module10_drift.csv`
  - `<run_id>_module10_performance.csv`

---

## 🧠 Key Concepts

### 1) Data drift
Your model expects the world to look like training.
If input distributions shift, forecasts degrade.

We use:
- **PSI** (works without heavy dependencies)
- **KS statistic** (if SciPy available)

Typical PSI thresholds:
- **< 0.10**: low drift
- **0.10–0.25**: moderate drift
- **> 0.25**: high drift (investigate / retrain)

### 2) Performance decay
Even without drift, performance can decay (competitors, pricing, behavior changes).

We track:
- rolling WAPE (business-friendly)
- rolling MAE (units)

### 3) Retraining triggers
Don’t retrain constantly—retrain when there is evidence.

In this repo:
- trigger if **max PSI** exceeds a threshold (default 0.25)
- or if **rolling WAPE** exceeds a threshold (default 0.45)

---

## 🚀 Run Monitoring (CLI)

From repo root:

```bash
python pipelines/retraining_trigger.py
```

Common overrides:

```bash
python pipelines/retraining_trigger.py --drift-window-days 60 --perf-window-days 14
python pipelines/retraining_trigger.py --psi-threshold 0.2 --wape-threshold 0.4
python pipelines/retraining_trigger.py --forecast-csv outputs/forecasts/<your_file>.csv
```

---

## ✅ What “Good” Looks Like

- PSI stays low over time (stable inputs)
- Rolling WAPE is stable and within acceptable bounds
- Triggers happen rarely and are explainable (e.g., big promo season)

---

## 🔗 Next Steps

To productionize further:
- log monitoring metrics to a time series DB
- alerting (Slack/email)
- scheduled daily runs (Prefect/Airflow)
- automatic retraining pipelines (Module 8 + Module 10 integration)


