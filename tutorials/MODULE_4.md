# Module 4: Classical Time Series Models (ARIMA/SARIMA, ETS)

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Understand** when classical models are a great fit (and when they aren’t)
2. **Train** ETS (Holt-Winters) models with weekly seasonality
3. **Train** SARIMAX models with seasonal components (weekly)
4. **Run** residual diagnostics (autocorrelation, Ljung–Box)
5. **Compare** classical models to Module 3 baselines using robust metrics
6. **Explain** why classical per-SKU models don’t scale well (and how industry handles this)

---

## 🎯 Why Classical Models?

Classical time series models are excellent when:
- you have a single series (or a few series),
- patterns are strong and stable (trend + seasonality),
- interpretability is important,
- you want strong baselines before ML.

But they can be painful at scale (1000+ SKUs) because each SKU typically needs its own model fit.

---

## 🧠 Models in This Module

### 1) ETS (Holt-Winters / Exponential Smoothing)

**Strengths**
- Captures level + trend + seasonality
- Often strong for stable seasonality (weekly, yearly)
- Fast to fit compared to ARIMA-family

**Key knobs**
- `trend`: add / mul / None
- `seasonal`: add / mul / None
- `seasonal_periods`: e.g. **7** for weekly seasonality in daily data

### 2) SARIMAX (Seasonal ARIMA)

**Strengths**
- Flexible autocorrelation structure
- Seasonal terms can capture repeated cycles (weekly)

**Key knobs**
- `order = (p,d,q)`
- `seasonal_order = (P,D,Q,s)` where `s=7` for weekly seasonality

---

## 📏 Seasonality Detection (Practical)

For daily e-commerce data, common seasonalities:
- **7** (weekly)
- **365** (yearly) — requires more history; may be too heavy for SARIMA on many SKUs

In this tutorial we start with **weekly seasonality (7)** because it’s strong and consistent in retail/e-commerce.

---

## ✅ Residual Diagnostics (What “Good” Looks Like)

After fitting a model, residuals should look like **white noise**:
- mean ~ 0
- no strong autocorrelation
- Ljung–Box test not significant (fails to reject independence)

If residuals show structure, the model is missing important dynamics (seasonality, trend, promotions).

---

## 🧪 Scaling Limitations (Why You’ll Move to ML Soon)

Classical models are “local” by default:
- 500 SKUs → 500 separate fits
- tuning per SKU is expensive
- failures are common (convergence, non-stationarity)

Industry approaches at scale:
- segment SKUs and apply different model families
- use global ML models (Module 5)
- use hierarchical + reconciliation approaches (later modules)

---

## ✅ Deliverables

1. **✅ Classical forecasts** for a representative SKU sample
2. **✅ Residual diagnostics** (plots + Ljung–Box)
3. **✅ Comparison table** vs baselines (MAE/RMSE/WAPE/sMAPE)
4. **✅ Implementations** in `src/models/classical.py`
5. **✅ Notebook**: `notebooks/04_classical_models.ipynb`

---

## 🚀 How to Run

1. Ensure Module 2 produced:
- `data/processed/featured_sales_data.csv`

2. Open:
- `notebooks/04_classical_models.ipynb`

3. Run all cells.

---

## 🔗 Next Steps

If classical models struggle to beat baselines consistently (or are too slow), that’s normal.

**Next Module:** Module 5 (ML Forecasting) — global models scale better and learn cross-SKU patterns.


