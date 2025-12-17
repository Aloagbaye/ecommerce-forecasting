# Module 5: Machine Learning Forecasting (Global Models)

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Build** a supervised learning dataset from time series (create a horizon target)
2. **Train** global (multi-SKU) ML forecasting models
3. **Compare** ML models vs Module 3 baselines (and Module 4 classical, if desired)
4. **Run** time-based validation (no leakage)
5. **Interpret** feature importance (what drives demand)
6. **Understand** global vs local modeling trade-offs

---

## 🎯 Why ML for Forecasting?

Classical models (ETS/SARIMA) are strong but often **don’t scale** well across hundreds/thousands of SKUs.

ML models scale because they can be trained as **global models**:
- one model learns patterns across all SKUs
- categorical features (SKU/category) help transfer learning
- features (lags, rolling stats, promo/price) encode time-series structure

---

## 🧠 Global vs Local Models

### Local model (per SKU)
- ✅ captures SKU-specific dynamics easily
- ❌ doesn’t scale well (hundreds/thousands of model fits)
- ❌ fragile (convergence failures, per-SKU tuning)

### Global model (one model for all SKUs)
- ✅ scales well
- ✅ learns shared patterns across SKUs
- ✅ simple deployment (one artifact)
- ❌ must encode SKU identity (e.g., category, SKU, embeddings/one-hot)
- ❌ can underfit rare/special SKUs without segmentation

In practice, many production systems use **global models** + **segmentation**.

---

## 🧪 Turning Time Series into a Supervised Dataset

We want to predict demand \(h\) days ahead:

\[
  y_{t+h} = f(X_t)
\]

Where \(X_t\) includes:
- lag features: `lag_1`, `lag_7`, `lag_30`, ...
- rolling stats: `rolling_mean_7`, `rolling_std_30`, ...
- promo/price features
- calendar features: day-of-week, month, holiday season
- identifiers: SKU/category (encoded)

**Critical rule:** features must be known at time \(t\) (no future leakage).

---

## 🧰 Models in This Module

We’ll implement and compare:

- **Linear model** (Ridge): strong baseline for tabular features
- **Random Forest**: robust, handles non-linearities, but can be heavy
- **LightGBM / XGBoost** (optional): often best-in-class for tabular forecasting

The notebook is designed to **work even if LightGBM/XGBoost are not installed** (falls back to sklearn models).

---

## 📏 Evaluation Setup

### Simple and realistic validation

- Use a time cutoff date
- Train on history up to cutoff
- Validate on the next `HORIZON` days

### Metrics (same as Module 3)

- MAE, RMSE
- WAPE, sMAPE

---

## ✅ Deliverables

1. **✅ Trained ML models** (in memory; optional saving later modules)
2. **✅ Feature importance output** (top drivers)
3. **✅ Performance comparison** table across ML models
4. **✅ Implementation** in `src/models/ml_models.py`
5. **✅ Notebook**: `notebooks/05_ml_forecasting.ipynb`

---

## 🚀 How to Run

1. Open:
- `notebooks/05_ml_forecasting.ipynb`

2. The notebook will:
- load `data/processed/featured_sales_data.csv` if present
- otherwise regenerate features from `data/raw/sample_sales.csv` using Module 2 functions

---

## 🔗 Next Steps

Once ML models beat baselines consistently:
- move to **Module 7** for more rigorous evaluation
- move to **Module 8** for batch pipelines
- move to **Module 9** for deployment

If you need hierarchy/scale next:
- **Module 5.1** Hierarchical forecasting
- **Module 5.2** Scalability patterns


