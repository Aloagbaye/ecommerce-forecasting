# Module 8: Forecast Orchestration & Pipelines

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Run** batch forecasting for many SKUs with a single command
2. **Produce** reproducible forecast artifacts (CSV + JSON run report)
3. **Design** pipelines that are idempotent and production-friendly
4. **Understand** orchestration patterns (cron, Airflow/Prefect-ready structure)
5. **Organize** outputs for downstream deployment and monitoring

---

## 🎯 Why Orchestration Matters

A forecasting model is not useful unless it runs reliably on schedule.

In production, you need:
- automated runs (daily/weekly)
- consistent outputs (for downstream apps)
- run metadata (what data/model/config produced this forecast?)
- failure handling + retry patterns

This module introduces a minimal pipeline that you can evolve into a full orchestrated system.

---

## 🧱 What We Build

We implement a simple batch forecasting pipeline:

- **Input**: `data/raw/sample_sales.csv` (or your own raw dataset)
- **Process**:
  - pick a cutoff date
  - train a baseline forecaster (per SKU)
  - generate forecasts for a horizon
  - attach hierarchy columns (category/subcategory)
- **Outputs**:
  - `outputs/forecasts/<run_id>_sku_forecasts.csv`
  - `outputs/reports/<run_id>_pipeline_report.json`

The pipeline is implemented as a CLI script:
- `pipelines/forecasting_pipeline.py`

---

## 🗂️ Output Artifacts (Contract)

### Forecast output (CSV)

`outputs/forecasts/<run_id>_sku_forecasts.csv`

Expected columns:
- `sku_id`
- `date` (forecast date)
- `y_pred`
- `method`
- (optional) `category`, `subcategory`

### Run report (JSON)

`outputs/reports/<run_id>_pipeline_report.json`

Captures:
- run ID + timestamp
- config used (horizon, method)
- data stats (row count, date range, SKUs)
- output file locations

---

## ⚙️ Configuration

Defaults live in:
- `config/pipeline.yaml`

You can override via CLI flags when running.

---

## 🚀 How to Run (CLI)

From the repo root:

```bash
python pipelines/forecasting_pipeline.py --config config/pipeline.yaml
```

Overrides:

```bash
python pipelines/forecasting_pipeline.py --horizon 28 --method naive
python pipelines/forecasting_pipeline.py --method moving_average --ma-window 14
python pipelines/forecasting_pipeline.py --method ses --ses-alpha 0.4
```

---

## 🧠 Production Notes (Best Practices)

### Idempotency
- Each run writes outputs with a unique `run_id` so it doesn’t overwrite prior runs.

### Contracts
- Define stable output schemas for downstream consumers.

### Observability
- Always write a run report (inputs, config, outputs).

### Scheduling (next step)
- start with OS scheduler (cron / Windows Task Scheduler)
- later migrate to Airflow/Prefect

---

## ✅ Deliverables

1. **✅ Forecast pipeline**: `pipelines/forecasting_pipeline.py`
2. **✅ Config file**: `config/pipeline.yaml`
3. **✅ Forecast artifacts**: `outputs/forecasts/*.csv`
4. **✅ Run metadata**: `outputs/reports/*_pipeline_report.json`

---

## 🔗 Next Steps

After Module 8:
- integrate ML model inference (Module 5) into the pipeline
- add batch evaluation against actuals (Module 7)
- deploy as an API (Module 9)
- add monitoring + retraining triggers (Module 10)


