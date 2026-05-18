# E-Commerce Demand Forecasting System

A production-grade demand forecasting platform for e-commerce operations, covering the full lifecycle from raw sales data to deployed forecast APIs with automated monitoring and retraining.

## The Problem

Inventory decisions in e-commerce are made under uncertainty. Overstock ties up working capital and increases carrying costs. Stockouts erode customer trust and hand revenue to competitors. The gap between intuition-based ordering and data-driven forecasting directly impacts margin.

This system addresses that gap by producing SKU-level demand forecasts that account for seasonality, promotions, price sensitivity, and trend — at the granularity and cadence required for operational procurement decisions.

## What This System Does

- **Ingests and cleans** raw transactional sales data, handling missing dates, outliers, and irregular SKU activity
- **Engineers demand signals** including temporal patterns, lag features, rolling statistics, and promotion indicators
- **Trains and compares** a model hierarchy from statistical baselines through gradient boosting to deep learning (LSTM/Transformer)
- **Evaluates forecasts** against business-relevant metrics: MAE, RMSE, WAPE, and sMAPE with per-SKU breakdown
- **Serves forecasts** via a FastAPI endpoint, containerized for deployment
- **Monitors production** for distribution drift and triggers automated retraining when forecast degradation is detected

## Getting Started

### Prerequisites

- Python 3.8+
- pip or conda
- Docker (for deployment)

### Installation

```bash
git clone <repository-url>
cd ecommerce-forecasting
pip install -r requirements.txt
```

### Data

Generate a synthetic dataset representative of real e-commerce demand patterns (seasonal spikes, promotion lifts, multi-SKU variability):

```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

Or drop your own CSV into `data/raw/` and configure the schema mapping in `config/`.

## System Components

### Data Pipeline

Handles raw sales ingestion, date gap imputation, outlier treatment, and feature construction. Outputs a model-ready feature matrix with temporal, lag, rolling, and promotion features.

```python
from src.data.loaders import load_sample_data
from src.features.engineering import build_feature_matrix

df = load_sample_data()
features = build_feature_matrix(df)
```

### Forecasting Models

The system implements a model hierarchy for structured benchmarking and selection:

| Tier | Models | Use Case |
|------|--------|----------|
| Baseline | Naive, Moving Average, SES | Performance floor, sanity checks |
| Classical | ARIMA, ETS, Prophet | Interpretable univariate forecasts |
| ML | LightGBM, XGBoost | Cross-SKU patterns, feature-rich forecasting |
| Deep Learning | LSTM, Temporal Fusion Transformer | Complex seasonality, large SKU catalogs |

### Forecast API

A FastAPI service that accepts SKU identifiers and a forecast horizon, returning point forecasts and prediction intervals.

```bash
docker build -t forecast-api .
docker run -p 8000:8000 forecast-api
```

```bash
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"sku_id": "SKU_001", "horizon_days": 30}'
```

### Monitoring & Retraining

Tracks forecast accuracy and input feature distributions in production. When drift exceeds configurable thresholds, the retraining pipeline is triggered automatically, producing a challenger model evaluated against the current champion before promotion.

## Project Structure

```
ecommerce-forecasting/
├── data/
│   ├── raw/                # Source data files
│   ├── processed/          # Cleaned and feature-engineered data
│   └── external/           # External signals (holidays, promotions)
├── notebooks/              # Exploratory analysis and model development
├── src/
│   ├── data/               # Ingestion and loading utilities
│   ├── features/           # Feature engineering pipeline
│   ├── models/             # Model implementations
│   └── evaluation/         # Metrics and comparison framework
├── outputs/
│   ├── forecasts/          # Forecast outputs
│   ├── reports/            # Evaluation reports
│   └── visualizations/     # Charts and plots
├── scripts/                # Operational scripts
├── config/                 # Environment and model configuration
└── tests/                  # Unit and integration tests
```

## Technology Stack

| Layer | Libraries |
|-------|-----------|
| Data Processing | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Time Series | statsmodels, pmdarima, Prophet |
| Machine Learning | scikit-learn, LightGBM, XGBoost |
| Deep Learning | PyTorch |
| API | FastAPI |
| Deployment | Docker |

## License

See [LICENSE](LICENSE) for details.
