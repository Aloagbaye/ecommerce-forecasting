# MLflow Tutorial (Monitoring + A/B Testing for this repo)

This guide shows how to use **MLflow** to:
- log evaluation runs (metrics + params + artifacts)
- compare a **champion** vs **challenger** (A/B evaluation)
- produce a simple promotion decision

We do this with the pipeline:
- `pipelines/mlflow_ab_monitoring.py`

---

## ✅ Install

From repo root:

```bash
pip install -r requirements.txt
```

Verify:

```bash
python -c "import mlflow; print(mlflow.__version__)"
```

---

## 🧠 What This Pipeline Does

On each run it:
1. Loads actuals from `data/raw/sample_sales.csv`
2. Defines an evaluation window (cutoff + horizon)
3. Generates two forecast sets:
   - champion method (e.g., moving average)
   - challenger method (e.g., SES)
4. Joins predictions to actuals
5. Computes metrics: **MAE, RMSE, WAPE, sMAPE**
6. Logs everything to MLflow
7. Writes local artifacts to `outputs/reports/` and uploads them to MLflow

Winner is chosen by **lower WAPE**.

---

## 🚀 Run A/B Monitoring

Default run (champion=MA7, challenger=SES):

```bash
python pipelines/mlflow_ab_monitoring.py
```

Try different pairs:

```bash
python pipelines/mlflow_ab_monitoring.py --champion-method moving_average --challenger-method naive
python pipelines/mlflow_ab_monitoring.py --champion-method ses --challenger-method moving_average --ses-alpha 0.5
```

Control horizon/cutoff:

```bash
python pipelines/mlflow_ab_monitoring.py --horizon 28
python pipelines/mlflow_ab_monitoring.py --cutoff-date 2025-11-30 --horizon 14
```

---

## 📊 View Results in the MLflow UI

Start the MLflow UI:

```bash
mlflow ui
```

By default, MLflow writes to a local `./mlruns` folder in your repo.

Then open the UI in your browser (MLflow prints the local address in your terminal).

---

## 📁 Artifacts Produced

Each run writes:
- `outputs/reports/<run_id>_mlflow_ab_decision.json`
- `outputs/reports/<run_id>_mlflow_ab_scored.csv`

These are also logged as MLflow artifacts.

---

## 🔄 How to Extend This to Real ML Models

Right now, champion/challenger are baseline methods so the pipeline is easy to run.

To use real ML models:
- load your trained model artifacts (Module 5)
- replace forecast generation with model inference
- keep the rest identical (join to actuals → metrics → MLflow log → decision)

---

## 🧪 Common Issues

### `ModuleNotFoundError: No module named 'mlflow'`
Install:

```bash
pip install mlflow
```

### No overlap between forecasts and actuals
Ensure your evaluation window exists in the raw data:
- cutoff + horizon must fall within the raw dataset date range

---


