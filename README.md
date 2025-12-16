# E-Commerce Demand Forecasting System

An end-to-end tutorial project for building production-ready demand forecasting systems for e-commerce.

## 🎯 Project Overview

This project guides you through building a complete demand forecasting system from data exploration to deployment, covering:

- **Data Exploration & Cleaning** - Understanding e-commerce sales patterns
- **Baseline to Advanced Models** - From simple averages to deep learning
- **Model Evaluation** - Business-relevant metrics and comparisons
- **Deployment** - API service with Docker
- **Monitoring** - Drift detection and automated retraining

## 📚 Getting Started

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ecommerce-forecasting
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate sample data (or use your own):
```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

## 📖 Tutorial Modules

### Module 0: Project Setup & Business Context ✅
**Status:** Ready to use

- [Tutorial Guide](MODULE_0.md) - Introduction and setup

**What you'll learn:**
- Why demand forecasting matters in e-commerce
- E-commerce demand challenges
- SKU-level vs category-level forecasting
- Setting up your development environment

**Get started:**
1. Read [MODULE_0.md](MODULE_0.md)
2. Set up your environment
3. Generate sample data

### Module 1: Understanding the Data ✅
**Status:** Ready to use

- [Tutorial Guide](MODULE_1.md) - Complete walkthrough
- [EDA Notebook](notebooks/01_eda.ipynb) - Exploratory data analysis
- [Insights Report](MODULE_1_insights.md) - Analysis insights

**What you'll learn:**
- Load and inspect e-commerce sales data
- Identify time series characteristics
- Detect seasonality, trends, and patterns
- Assess data quality

**Get started:**
1. Read [MODULE_1.md](MODULE_1.md)
2. Open `notebooks/01_eda.ipynb`
3. Follow along with the tutorial

### Module 2: Data Cleaning & Feature Engineering ✅
**Status:** Ready to use

- [Tutorial Guide](MODULE_2.md) - Complete walkthrough
- [Feature Engineering Notebook](notebooks/02_data_cleaning.ipynb) - Data cleaning and feature engineering

**What you'll learn:**
- Clean e-commerce sales data (handle missing dates, outliers)
- Engineer temporal features (day of week, month, seasonality)
- Create lag features (historical sales patterns)
- Generate rolling statistics (moving averages, standard deviations)
- Build promotion and price features
- Construct a reusable feature engineering pipeline

**Get started:**
1. Read [MODULE_2.md](MODULE_2.md)
2. Open `notebooks/02_data_cleaning.ipynb`
3. Follow along with the tutorial

### Module 3: Baseline Forecasting Models ✅
**Status:** Ready to use

- [Tutorial Guide](MODULE_3.md) - Baselines + evaluation
- [Baseline Models Notebook](notebooks/03_baseline_models.ipynb) - Run baselines and compare errors

**What you'll learn:**
- Why baselines matter
- Time-based train/test split (no leakage)
- Naive, moving average, and SES baselines
- Evaluation with MAE, RMSE, WAPE, sMAPE
- Error comparison table (overall + per-SKU)

**Get started:**
1. Ensure `data/processed/featured_sales_data.csv` exists (run Module 2)
2. Read [MODULE_3.md](MODULE_3.md)
3. Open `notebooks/03_baseline_models.ipynb`
4. Run all cells to generate the comparison tables

### Upcoming Modules
- **Module 3:** Baseline Forecasting Models
- **Module 4:** Classical Time Series Models
- **Module 5:** Machine Learning Forecasting
- **Module 6:** Deep Learning (Optional)
- **Module 7:** Model Evaluation & Business Metrics
- **Module 8:** Forecast Orchestration & Pipelines
- **Module 9:** Deployment (Forecast as a Service)
- **Module 10:** Monitoring & Drift Detection
- **Module 11:** Capstone Extensions

See [TUTORIAL_STRUCTURE.md](TUTORIAL_STRUCTURE.md) for the complete curriculum.

## 📁 Project Structure

```
ecommerce-forecasting/
├── data/
│   ├── raw/           # Original data files
│   ├── processed/     # Cleaned data
│   └── external/      # External data sources
├── notebooks/         # Jupyter notebooks for each module
├── src/               # Source code
│   ├── data/          # Data loading utilities
│   ├── features/      # Feature engineering
│   ├── models/        # Forecasting models
│   └── evaluation/    # Evaluation metrics
├── outputs/           # Generated outputs
│   ├── forecasts/     # Forecast results
│   ├── reports/       # Analysis reports
│   └── visualizations/ # Plots and charts
├── scripts/           # Utility scripts
├── config/            # Configuration files
└── tests/             # Unit tests
```

## 🚀 Quick Start

1. **Generate sample data:**
   ```bash
   python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
   ```

2. **Start with Module 1:**
   - Open `notebooks/01_eda.ipynb`
   - Follow the tutorial in `MODULE_1.md`

3. **Explore the data:**
   ```python
   from src.data.loaders import load_sample_data
   df = load_sample_data()
   print(df.head())
   ```

## 📊 Sample Data

The project includes a script to generate realistic synthetic e-commerce data with:
- Multiple product categories
- Seasonal patterns
- Promotion effects
- Realistic demand variations

Generate it with:
```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

## 🛠️ Technology Stack

- **Data Processing:** pandas, numpy
- **Visualization:** matplotlib, seaborn, plotly
- **Time Series:** statsmodels, pmdarima
- **Machine Learning:** scikit-learn, lightgbm, xgboost
- **API:** FastAPI
- **Deployment:** Docker

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a tutorial project. Feel free to:
- Report issues
- Suggest improvements
- Share your implementations

## 📚 Resources

- [Full Tutorial Structure](TUTORIAL_STRUCTURE.md)
- [Module 1 Guide](MODULE_1.md)

---

**Happy Forecasting! 🚀**
