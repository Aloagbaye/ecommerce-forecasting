# Module 3: Baseline Forecasting Models

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Explain** why baselines matter (and how they prevent “fake progress”)
2. **Build** baseline forecasts (naive, moving average, SES)
3. **Choose** a forecast horizon aligned to business needs
4. **Split** time series data correctly (no leakage)
5. **Evaluate** forecasts using robust metrics (MAE, RMSE, WAPE, sMAPE)
6. **Compare** baselines in an error table (overall + per-SKU)

---

## 🎯 Why Baselines Matter

Baselines answer the question: **“Is this problem actually hard?”**

If a fancy ML model can’t beat a naive baseline, then:
- your features may be wrong,
- your split may be leaking,
- your evaluation may be misaligned,
- or the “improvement” isn’t real.

Baselines are also essential in production: they’re cheap, stable, and often surprisingly strong.

---

## 🧠 Forecast Horizon Alignment

Pick a horizon based on how the forecast is used:

- **7 days**: staffing, short-term replenishment, promo ops
- **14 days**: standard replenishment cycles
- **28–30 days**: monthly planning and procurement

**Rule:** Always evaluate models at the horizon you’ll use in the business.

---

## 🧪 Train/Test Splitting (No Leakage)

Time series data must be split **by time**, not randomly.

### Recommended split (simple + practical)

- **Train**: all data up to a cutoff date
- **Test**: next `horizon` days (or a rolling window)

### Avoid these mistakes

- ❌ Random train/test split
- ❌ Creating features using future values
- ❌ Aggregating across SKUs before splitting

---

## 🧰 Baseline Models Included

### 1. Naive Forecast (Last Value)

**Idea:** tomorrow ≈ today  
Good for stable series; terrible for strong trend/seasonality.

### 2. Moving Average

**Idea:** forecast = average of last `k` days  
Smooths noise; can lag trends.

Common windows:
- 7 (weekly)
- 14 (biweekly)
- 30 (monthly)

### 3. Simple Exponential Smoothing (SES)

**Idea:** a weighted moving average where recent observations matter more  
Single parameter \(\\alpha\\) controls how fast the level adapts.

---

## 📏 Metrics (Baseline-Friendly)

Use metrics that behave well with zeros and skewed demand:

- **MAE**: easy to interpret in “units”
- **RMSE**: penalizes big mistakes more
- **WAPE**: business-friendly percentage-like metric that handles zeros better
- **sMAPE**: symmetric and more stable than MAPE on small values

Avoid plain **MAPE** when there are zeros / low volumes.

---

## ✅ Deliverables

By the end of this module, you should have:

1. **✅ Baseline forecast outputs**
2. **✅ Error comparison table** (overall + optionally per-SKU)
3. **✅ Baseline implementations** in `src/models/baseline.py`
4. **✅ Notebook**: `notebooks/03_baseline_models.ipynb`

---

## 🚀 How to Run

1. Ensure Module 2 has produced:
- `data/processed/featured_sales_data.csv`

2. Open:
- `notebooks/03_baseline_models.ipynb`

3. Run all cells to produce:
- baseline forecasts
- error comparison table

---

## 🔗 Next Steps

Once you’ve established baselines:

- Move to **Module 4** for classical time series models, or
- Move to **Module 5** for ML models

**Next Module:** `MODULE_4.md` (coming next)


