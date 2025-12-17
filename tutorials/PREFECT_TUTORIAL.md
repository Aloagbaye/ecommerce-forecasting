# Prefect Tutorial (for this repo)

This guide shows how to orchestrate the forecasting pipeline using **Prefect** in this project.

---

## ✅ Prerequisites

- Python installed (your environment may be Python 3.9+)
- From the repo root, dependencies installed:

```bash
pip install -r requirements.txt
```

Verify Prefect:

```bash
python -c "import prefect; print(prefect.__version__)"
```

---

## 🧠 What Prefect Adds

Compared to running a Python script directly, Prefect gives you:
- **Task retries** (automatic retry on transient failures)
- **Structured logging**
- **Run history**
- **Scheduling + deployments** (when you’re ready)
- **UI** to monitor flow runs

In this repo, Prefect orchestrates the same forecasting logic used by the CLI pipeline.

---

## 📌 Files Used

- **Prefect flow**: `pipelines/prefect_forecasting_flow.py`
- **CLI pipeline (same logic)**: `pipelines/forecasting_pipeline.py`
- **Config**: `config/pipeline.yaml`
- **Outputs**:
  - Forecasts: `outputs/forecasts/<run_id>_sku_forecasts.csv`
  - Reports:
    - CLI: `outputs/reports/<run_id>_pipeline_report.json`
    - Prefect: `outputs/reports/<run_id>_prefect_pipeline_report.json`

---

## 🚀 Run the Prefect Flow (Local)

From the repo root:

```bash
python pipelines/prefect_forecasting_flow.py
```

If everything is configured correctly, you’ll see log output and new artifacts created in:
- `outputs/forecasts/`
- `outputs/reports/`

---

## ⚙️ Use a Different Config or Data File

The flow loads defaults from `config/pipeline.yaml`.

If you want to use a different raw dataset, edit `config/pipeline.yaml`:

```yaml
data:
  raw_path: "data/raw/sample_sales.csv"
```

Or update the flow call in `pipelines/prefect_forecasting_flow.py` (the flow supports a `raw_path_override`).

---

## 🖥️ Start the Prefect UI (Optional)

Start a local Prefect server:

```bash
prefect server start
```

Then run the flow again in another terminal:

```bash
python pipelines/prefect_forecasting_flow.py
```

You should be able to see the flow run and logs in the Prefect UI.

---

## 🗓️ Scheduling (Next Step)

When you’re ready to schedule runs, you typically:
- create a **deployment** for the flow
- attach a schedule (cron / interval)
- run a Prefect **worker**

Prefect’s deployment patterns evolve across versions, so the most reliable reference is the official docs:
- `https://docs.prefect.io/latest/`

For this repo, the first practical milestone is:
- keep the flow as-is
- run it via Task Scheduler / cron OR via Prefect deployment

---

## 🧪 Troubleshooting

### 1) `ModuleNotFoundError: No module named 'src'`

- Run from repo root, or ensure the flow/script adds repo root to `sys.path`.
- This repo’s `pipelines/prefect_forecasting_flow.py` already inserts repo root into `sys.path`.

### 2) `Raw data not found`

Ensure the raw dataset exists at:
- `data/raw/sample_sales.csv`

If not, generate it:

```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

### 3) Prefect not installed / version issues

Install (or upgrade) Prefect:

```bash
pip install -U prefect
```

---

## ✅ What “Done” Looks Like

After running the flow you should have:
- a new forecast CSV in `outputs/forecasts/`
- a new Prefect report JSON in `outputs/reports/`

That’s a complete “forecast run” with orchestration, logs, and artifacts.


