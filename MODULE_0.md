# Module 0: Project Setup & Business Context

## 🎯 Learning Objectives

By the end of this module, you will:

1. **Understand** why demand forecasting is critical in e-commerce
2. **Recognize** the unique challenges of e-commerce demand forecasting
3. **Distinguish** between different forecasting approaches (SKU-level vs category-level)
4. **Appreciate** the impact of promotions and intermittent demand
5. **Set up** your development environment
6. **Navigate** the project structure

---

## 📚 Why Demand Forecasting Matters in E-commerce

### The Business Impact

Demand forecasting is the foundation of effective e-commerce operations. Accurate forecasts drive:

#### 1. **Inventory Optimization**
- **Reduce Stockouts:** Predict demand to maintain optimal inventory levels
- **Minimize Overstock:** Avoid tying up capital in slow-moving products
- **Improve Cash Flow:** Better inventory turnover means more working capital

**Real Impact:**
- Companies with accurate forecasts reduce inventory costs by 20-30%
- Stockouts can result in 20-40% lost sales
- Overstock ties up 25-30% of working capital unnecessarily

#### 2. **Replenishment Decisions**
- **When to Order:** Time purchases to meet demand without stockouts
- **How Much to Order:** Optimize order quantities based on forecasted demand
- **Supplier Coordination:** Better planning improves supplier relationships

#### 3. **Promotion Planning**
- **Promotion Timing:** Schedule promotions when they'll have maximum impact
- **Promotion Sizing:** Forecast lift to plan inventory for promotional periods
- **ROI Optimization:** Allocate promotional budget based on expected returns

#### 4. **Operational Efficiency**
- **Warehouse Planning:** Forecast demand to optimize storage and picking
- **Staffing:** Plan workforce based on expected order volumes
- **Shipping:** Coordinate logistics based on demand patterns

### The Cost of Poor Forecasting

**Under-Forecasting:**
- Stockouts → Lost sales → Customer dissatisfaction
- Emergency orders → Higher costs → Reduced margins
- Poor customer experience → Brand damage

**Over-Forecasting:**
- Excess inventory → Storage costs → Capital tied up
- Obsolescence risk → Markdowns → Profit loss
- Cash flow issues → Reduced investment capacity

**Industry Statistics:**
- Average forecast error in retail: 20-40%
- Top performers achieve: 10-15% forecast error
- Each 1% improvement in forecast accuracy can increase profit by 2-3%

---

## 🏪 E-Commerce Demand Challenges

E-commerce forecasting presents unique challenges compared to traditional retail:

### 1. **High SKU Count**
- **Challenge:** Thousands or millions of products to forecast
- **Impact:** Can't manually review each SKU
- **Solution:** Automated, scalable forecasting systems

### 2. **Intermittent Demand**
- **Challenge:** Many products sell infrequently (sparse demand)
- **Impact:** Traditional time series methods struggle with zeros
- **Solution:** Specialized methods (Croston's, zero-inflated models)

### 3. **Rapid Product Life Cycles**
- **Challenge:** New products with limited history
- **Impact:** No historical data for new SKUs
- **Solution:** Similarity-based forecasting, category-level models

### 4. **Promotion Effects**
- **Challenge:** Promotions create demand spikes
- **Impact:** Baseline models fail during promotional periods
- **Solution:** Promotion-aware models, lift modeling

### 5. **Multiple Sales Channels**
- **Challenge:** Online, mobile, marketplace sales
- **Impact:** Different patterns across channels
- **Solution:** Channel-specific models or aggregated approaches

### 6. **External Factors**
- **Challenge:** Weather, holidays, economic conditions
- **Impact:** Unpredictable demand variations
- **Solution:** External data integration, event calendars

### 7. **Seasonality Complexity**
- **Challenge:** Multiple seasonality patterns (weekly, monthly, yearly)
- **Impact:** Simple models miss important patterns
- **Solution:** Multi-seasonal models, hierarchical approaches

### 8. **Real-Time Requirements**
- **Challenge:** Need forecasts updated frequently
- **Impact:** Batch processing may be too slow
- **Solution:** Automated pipelines, streaming updates

---

## 📊 SKU-Level vs Category-Level Forecasting

### SKU-Level Forecasting

**What it is:** Forecasting demand for individual products (Stock Keeping Units)

**Advantages:**
- ✅ **Granular Control:** Precise inventory management per product
- ✅ **Product-Specific Patterns:** Captures unique demand characteristics
- ✅ **Better Accuracy:** More detailed forecasts for high-volume items
- ✅ **Actionable:** Directly informs purchasing and inventory decisions

**Disadvantages:**
- ❌ **Computational Cost:** Thousands of models to train and maintain
- ❌ **Data Sparsity:** Many SKUs have limited history
- ❌ **Noise:** Individual SKUs can be very noisy
- ❌ **New Products:** No history for new SKUs

**When to Use:**
- High-volume, fast-moving products
- Products with distinct demand patterns
- When precise inventory control is critical
- When you have sufficient historical data

### Category-Level Forecasting

**What it is:** Forecasting demand for product categories, then allocating to SKUs

**Advantages:**
- ✅ **Stability:** Categories have more stable patterns
- ✅ **Less Data Required:** Works with limited history
- ✅ **Computational Efficiency:** Fewer models to maintain
- ✅ **New Products:** Can forecast new SKUs using category patterns

**Disadvantages:**
- ❌ **Less Granular:** May miss product-specific patterns
- ❌ **Allocation Challenge:** Need method to split category forecast to SKUs
- ❌ **Aggregation Loss:** Important details lost in aggregation

**When to Use:**
- Low-volume, slow-moving products
- New products with no history
- When computational resources are limited
- When category patterns are more stable than SKU patterns

### Hybrid Approach (Recommended)

**Best Practice:** Use both approaches strategically

1. **High-Volume SKUs:** SKU-level forecasting
2. **Low-Volume SKUs:** Category-level forecasting
3. **New Products:** Start with category, move to SKU-level as data accumulates
4. **Reconciliation:** Use hierarchical methods to ensure consistency

**Hierarchical Forecasting:**
- Forecast at multiple levels (category, subcategory, SKU)
- Reconcile forecasts to ensure consistency
- Top-down: Allocate category forecast to SKUs
- Bottom-up: Aggregate SKU forecasts to category
- Middle-out: Forecast at middle level, reconcile up and down

---

## 🎁 Intermittent Demand & Promotions

### Intermittent Demand

**What it is:** Demand that occurs sporadically, with many zero-sales periods

**Characteristics:**
- High frequency of zero sales (often 30-70% of periods)
- Irregular intervals between sales
- Variable order sizes when sales occur

**Common in E-Commerce:**
- Slow-moving products
- Specialty items
- Seasonal products
- Long-tail products

**Challenges:**
- Traditional time series methods assume regular demand
- Zero sales are meaningful (not missing data)
- Need to predict both occurrence and volume

**Solutions:**
- **Croston's Method:** Separates demand occurrence from demand size
- **Zero-Inflated Models:** Models zeros separately from non-zero demand
- **Classification + Regression:** First predict if sale occurs, then predict volume
- **Intermittent Demand Classification:** Identify intermittent SKUs, use specialized methods

### Promotions

**Impact on Demand:**
- Promotions typically increase sales by 20-50%
- Effect varies by product, category, and promotion type
- Post-promotion dip often occurs (forward buying)

**Forecasting Challenges:**
- Baseline models fail during promotions
- Need to separate baseline from promotional lift
- Promotion timing affects impact
- Cumulative effects of multiple promotions

**Solutions:**
- **Promotion-Aware Models:** Include promotion flags and features
- **Lift Modeling:** Model baseline + promotion lift separately
- **Event Detection:** Automatically identify promotional periods
- **Promotion Calendar:** Integrate planned promotions into forecasts

**Best Practices:**
- Track promotion history (type, discount, duration)
- Model promotion effects by product/category
- Account for post-promotion effects
- Plan inventory for promotional periods

---

## ⏰ Forecast Horizon: Daily, Weekly, Monthly

### Daily Forecasting

**Use Cases:**
- Real-time inventory management
- Daily replenishment decisions
- Short-term operational planning
- High-frequency products

**Characteristics:**
- Most granular, most detailed
- Captures day-of-week patterns
- Higher noise, more variability
- Requires frequent updates

**Challenges:**
- More data points to forecast
- Higher computational cost
- More sensitive to noise
- Day-of-week effects critical

**When to Use:**
- Fast-moving products
- When daily decisions are needed
- High-value, critical products
- When you have sufficient data

### Weekly Forecasting

**Use Cases:**
- Weekly inventory planning
- Replenishment cycles
- Operational planning
- Most common in practice

**Characteristics:**
- Balances detail and stability
- Reduces noise through aggregation
- Captures weekly seasonality
- More stable than daily

**Challenges:**
- May miss important daily patterns
- Aggregation loses some detail
- Still requires weekly updates

**When to Use:**
- Standard operational planning
- Most products (default choice)
- When weekly decisions are sufficient
- Balance between detail and stability

### Monthly Forecasting

**Use Cases:**
- Strategic planning
- Budgeting and financial planning
- Long-term inventory planning
- Slow-moving products

**Characteristics:**
- Most stable, least noisy
- Captures monthly/seasonal patterns
- Less frequent updates needed
- Higher level view

**Challenges:**
- May miss important weekly patterns
- Less actionable for operations
- Longer planning cycles

**When to Use:**
- Strategic planning
- Slow-moving products
- When monthly decisions are sufficient
- High-level business planning

### Choosing the Right Horizon

**Factors to Consider:**
1. **Decision Frequency:** How often do you make inventory decisions?
2. **Product Velocity:** Fast-moving products need shorter horizons
3. **Data Availability:** More data allows shorter horizons
4. **Computational Resources:** Shorter horizons require more computation
5. **Business Requirements:** What does the business need?

**Best Practice:**
- **Daily:** High-volume, critical products
- **Weekly:** Most products (default)
- **Monthly:** Strategic planning, slow-moving products
- **Multiple Horizons:** Forecast at multiple levels for different use cases

---

## 🛠️ Project Setup

### Prerequisites

Before starting, ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **Package Manager**
   - pip (comes with Python)
   - or conda (for conda environments)

3. **Git** (optional, for version control)
   ```bash
   git --version
   ```

4. **Jupyter Notebook** (for running notebooks)
   - Will be installed with requirements.txt

### Installation Steps

#### 1. Clone or Download the Repository

If using Git:
```bash
git clone <repository-url>
cd ecommerce-forecasting
```

Or download and extract the project files.

#### 2. Create a Virtual Environment (Recommended)

**Using venv:**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**Using conda:**
```bash
conda create -n ecommerce-forecasting python=3.10
conda activate ecommerce-forecasting
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Data processing: pandas, numpy
- Visualization: matplotlib, seaborn, plotly
- Time series: statsmodels, pmdarima
- Machine learning: scikit-learn, lightgbm, xgboost
- API: fastapi, uvicorn
- Development: jupyter, pytest

#### 4. Verify Installation

```bash
python -c "import pandas, numpy, matplotlib, seaborn; print('✓ Core libraries installed')"
python -c "import statsmodels, pmdarima; print('✓ Time series libraries installed')"
python -c "import sklearn, lightgbm, xgboost; print('✓ ML libraries installed')"
```

#### 5. Generate Sample Data

```bash
python scripts/generate_sample_data.py --output data/raw/sample_sales.csv --days 730 --skus 100
```

This creates 2 years of daily data for 100 SKUs with realistic patterns.

#### 6. Test Data Loading

```python
from src.data.loaders import load_sample_data
df = load_sample_data()
print(f"Loaded {len(df)} records")
print(df.head())
```

---

## 📁 Project Structure

Understanding the project structure will help you navigate the codebase:

```
ecommerce-forecasting/
│
├── data/                      # Data directory
│   ├── raw/                   # Original, unprocessed data
│   │   └── sample_sales.csv   # Sample dataset (generated)
│   ├── processed/             # Cleaned, feature-engineered data
│   └── external/              # External data sources (optional)
│
├── notebooks/                 # Jupyter notebooks
│   ├── 01_eda.ipynb          # Module 1: Exploratory Data Analysis
│   ├── 02_data_cleaning.ipynb # Module 2: Data Cleaning (upcoming)
│   └── ...                    # Additional module notebooks
│
├── src/                       # Source code
│   ├── data/                  # Data utilities
│   │   ├── __init__.py
│   │   ├── loaders.py         # Data loading functions
│   │   └── cleaners.py        # Data cleaning functions (Module 2)
│   ├── features/              # Feature engineering
│   │   ├── __init__.py
│   │   ├── engineering.py     # Feature creation (Module 2)
│   │   └── lag_features.py    # Lag feature utilities
│   ├── models/                # Forecasting models
│   │   ├── __init__.py
│   │   ├── baseline.py         # Baseline models (Module 3)
│   │   ├── classical.py        # Classical time series (Module 4)
│   │   ├── ml_models.py        # ML models (Module 5)
│   │   └── deep_learning.py    # Deep learning (Module 6)
│   └── evaluation/            # Evaluation metrics
│       ├── __init__.py
│       ├── metrics.py         # Forecast metrics (Module 7)
│       └── reports.py          # Evaluation reports
│
├── outputs/                    # Generated outputs
│   ├── forecasts/             # Forecast results
│   ├── reports/               # Analysis reports
│   │   └── eda_summary.json   # EDA summary (Module 1)
│   └── visualizations/        # Plots and charts
│       ├── sales_distribution.png
│       ├── seasonality.png
│       └── ...
│
├── scripts/                   # Utility scripts
│   └── generate_sample_data.py # Sample data generator
│
├── config/                     # Configuration files
│   ├── config.yaml            # Main configuration
│   └── model_configs.yaml     # Model configurations
│
├── tests/                      # Unit tests
│   ├── test_data.py
│   ├── test_models.py
│   └── test_features.py
│
├── api/                        # API deployment (Module 9)
│   ├── app.py                 # FastAPI application
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # API dependencies
│
├── pipelines/                  # Automation pipelines (Module 8)
│   ├── training_pipeline.py   # Model training pipeline
│   ├── forecasting_pipeline.py # Forecast generation pipeline
│   └── retraining_trigger.py  # Retraining automation
│
├── docs/                       # Documentation
│   ├── api_documentation.md   # API docs (Module 9)
│   └── deployment_guide.md    # Deployment guide
│
├── MODULE_0.md                # This file - Introduction
├── MODULE_1.md                # Module 1: Understanding the Data
├── MODULE_1_insights.md        # Module 1 insights report
├── TUTORIAL_STRUCTURE.md      # Complete tutorial overview
├── README.md                   # Project README
├── requirements.txt           # Python dependencies
└── LICENSE                     # License file
```

### Key Directories Explained

**`data/`**: All data files
- `raw/`: Original data (never modify)
- `processed/`: Cleaned data (created in Module 2)
- `external/`: External data sources (optional)

**`notebooks/`**: Learning notebooks
- One notebook per module
- Follow naming: `##_module_name.ipynb`
- Run in order for best results

**`src/`**: Reusable code
- Organized by functionality
- Import in notebooks: `from src.data.loaders import load_sample_data`
- Production-ready code

**`outputs/`**: Generated files
- `forecasts/`: Forecast results
- `reports/`: Analysis summaries
- `visualizations/`: Plots and charts

**`scripts/`**: Standalone utilities
- Data generation
- One-off processing
- Automation scripts

---

## 🎓 Learning Path

### Module Progression

This tutorial is designed as a progressive learning journey:

1. **Module 0** (This Module): Setup & Context
2. **Module 1**: Understanding the Data ← Start here after setup
3. **Module 2**: Data Cleaning & Feature Engineering
4. **Module 3**: Baseline Forecasting Models
5. **Module 4**: Classical Time Series Models
6. **Module 5**: Machine Learning Forecasting
7. **Module 6**: Deep Learning (Optional/Advanced)
8. **Module 7**: Model Evaluation & Business Metrics
9. **Module 8**: Forecast Orchestration & Pipelines
10. **Module 9**: Deployment (Forecast as a Service)
11. **Module 10**: Monitoring & Drift Detection
12. **Module 11**: Capstone Extensions

### Recommended Learning Approach

1. **Follow Modules Sequentially**: Each builds on the previous
2. **Run All Code**: Hands-on practice is essential
3. **Experiment**: Try variations and modifications
4. **Document Learnings**: Take notes on insights
5. **Apply to Your Data**: Adapt techniques to your use case

### Time Estimates

- **Module 0**: 30-60 minutes (setup)
- **Module 1**: 2-3 hours (EDA)
- **Module 2**: 2-3 hours (feature engineering)
- **Modules 3-5**: 3-4 hours each (modeling)
- **Modules 6-11**: 2-4 hours each (advanced topics)

**Total Estimated Time:** 30-40 hours for complete tutorial

---

## ✅ Module 0 Checklist

Before moving to Module 1, ensure you have:

- [ ] Python 3.8+ installed and verified
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Sample data generated (`python scripts/generate_sample_data.py`)
- [ ] Data loading tested (import works correctly)
- [ ] Project structure understood
- [ ] Jupyter Notebook working (`jupyter notebook` or `jupyter lab`)

### Quick Verification

Run this to verify everything is set up:

```python
# Test imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.data.loaders import load_sample_data

# Test data loading
df = load_sample_data()
print(f"✓ Successfully loaded {len(df)} records")
print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
print(f"✓ Unique SKUs: {df['sku_id'].nunique()}")
print("\n✓ Setup complete! Ready for Module 1.")
```

---

## 🚀 Next Steps

Once you've completed Module 0:

1. **Read [MODULE_1.md](MODULE_1.md)** - Understanding the Data
2. **Open `notebooks/01_eda.ipynb`** - Start the EDA notebook
3. **Follow along** - Work through each section
4. **Generate insights** - Document your findings

**You're ready to begin your forecasting journey!**

---

## 📚 Additional Resources

### E-Commerce Forecasting

- [Demand Forecasting in Retail](https://www.investopedia.com/terms/d/demand-forecasting.asp)
- [SKU-Level Forecasting Best Practices](https://www.sciencedirect.com/topics/engineering/sku-level-forecasting)
- [Intermittent Demand Forecasting](https://www.forecastpro.com/Trends/trends201103.html)

### Time Series Forecasting

- [Time Series Analysis Overview](https://otexts.com/fpp3/)
- [Forecasting: Principles and Practice](https://otexts.com/fpp3/)
- [Statsmodels Documentation](https://www.statsmodels.org/stable/tsa.html)

### Machine Learning for Forecasting

- [Machine Learning for Time Series](https://scikit-learn.org/stable/modules/time_series.html)
- [LightGBM Time Series Guide](https://lightgbm.readthedocs.io/)
- [XGBoost Time Series](https://xgboost.readthedocs.io/)

---

## ❓ Common Setup Issues

### Issue: Import Errors

**Problem:** `ModuleNotFoundError` when importing

**Solution:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Issue: Data Not Found

**Problem:** `FileNotFoundError` when loading data

**Solution:**
- Generate sample data: `python scripts/generate_sample_data.py --output data/raw/sample_sales.csv`
- Check file exists: `ls data/raw/` (or `dir data\raw\` on Windows)
- Verify path in code matches file location

### Issue: Jupyter Not Starting

**Problem:** Jupyter notebook won't start

**Solution:**
- Install Jupyter: `pip install jupyter`
- Try JupyterLab: `pip install jupyterlab && jupyter lab`
- Check if port is in use: Try different port `jupyter notebook --port 8889`

### Issue: Memory Errors

**Problem:** Out of memory when loading data

**Solution:**
- Reduce dataset size: `--days 365 --skus 50` (smaller sample)
- Use data chunking for large files
- Close other applications to free memory

---

**Ready to start? Head to [Module 1: Understanding the Data](MODULE_1.md)! 🎯**

