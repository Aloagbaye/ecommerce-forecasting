# A/B Testing Tutorial for Forecasting & Machine Learning

This guide explains **how to A/B test forecasting and ML models** in a way that matches real production workflows: a model (or policy) produces predictions, and you measure the downstream impact and model quality over time.

---

## 🎯 What “A/B Testing” Means in ML

In product A/B testing, you randomize users into variants (A vs B).

In **forecasting**, it’s a bit different:
- forecasts are often used for **operations** (inventory, procurement, staffing)
- the “treatment” can affect the future (feedback loops)
- you usually want **both**:
  - **offline** evaluation (backtests on historical data)
  - **online** evaluation (shadow / limited rollout)

**Goal:** choose the best model or policy by comparing **impact** and **risk** under controlled conditions.

---

## 🧪 Two Types of A/B Tests for Forecasting

### 1) Offline A/B (Backtesting)

You compare models on historical windows:
- Train on past data
- Predict the next \(H\) days
- Compare predictions vs actuals

**Pros**
- Fast and cheap
- No business risk
- Reproducible

**Cons**
- Can’t measure real downstream business effects (stockouts, ops costs)
- Doesn’t capture feedback loops (forecast → decisions → demand)

### 2) Online A/B (Live Experiment)

You route real forecasting requests or decision workflows through two versions:
- A = “champion” (current model)
- B = “challenger” (new model)

**Pros**
- Measures real impact
- Captures feedback loops

**Cons**
- Higher risk
- Requires instrumentation + careful design

**Best practice:** start with **offline**, then progress to **shadow** → **small rollout** → **full rollout**.

---

## 🧱 What’s Being Tested?

For forecasting, you can A/B test:

- **Model**: ETS vs ML model
- **Feature set**: with vs without promotions
- **Training recipe**: different hyperparameters
- **Decision policy** built on forecasts:
  - reorder points
  - safety stock settings
  - allocation logic

Often the *decision policy* matters more than raw forecast accuracy.

---

## 📏 Metrics for Forecasting A/B Tests

### Offline metrics (prediction quality)

Use metrics robust to zeros and skew:
- **MAE**
- **RMSE**
- **WAPE** (often best for retail ops)
- **sMAPE**

Also evaluate by slices:
- weekends vs weekdays
- peak season vs off-peak
- high-volume SKUs vs low-volume SKUs

### Online metrics (business impact)

Define metrics aligned to your objective:

- **Service level / fill rate**
- **Stockouts** (% days OOS)
- **Overstock / holding cost**
- **Waste / markdown**
- **Revenue lost** (estimated)
- **On-time replenishment**

Often use a **cost function**:

\[
  \text{cost} = c_u \\cdot \\max(0, y - \\hat{y}) + c_o \\cdot \\max(0, \\hat{y} - y)
\]

Where:
- \(c_u\) = under-forecast cost
- \(c_o\) = over-forecast cost

---

## 🔒 Avoiding Common Pitfalls

### 1) Leakage and unfair comparisons (offline)
- Ensure both models train on the same history window
- Use the same forecast horizon
- Don’t let one model see future features the other can’t

### 2) Feedback loops (online)
Forecast → ordering decisions → inventory availability → observed sales.
Your observed “demand” can be censored by stockouts.

Mitigation:
- track **stock_available** and flag stockouts
- measure **unconstrained demand** if possible

### 3) Non-random assignment
If you assign Model B only to “easy SKUs,” results are biased.

Mitigation:
- randomize assignment within strata (category, volume segment)

### 4) Seasonality and timing
If Model A runs in November and Model B runs in January, your results are meaningless.

Mitigation:
- run variants concurrently
- use matched time windows for offline backtests

---

## ✅ Recommended Workflow (Practical)

### Step 1: Offline A/B backtest (required)
- run 3–5 rolling backtests
- compute metrics + confidence intervals (bootstrapping)
- validate on segments (top SKUs, intermittent SKUs, categories)

### Step 2: Shadow mode (safe online)
- Model B runs in parallel but **doesn’t affect decisions**
- log predictions and compute “what-if” outcomes

### Step 3: Limited rollout (online A/B)
- route a subset of SKUs/regions to Model B
- start at 5–10%, then ramp up
- define stop conditions (guardrails)

### Step 4: Promote challenger → champion
- only after it wins on both prediction + business metrics
- keep rollback ability

---

## 🧪 A/B Testing Design Patterns

### Pattern A: SKU-level randomization (common)
- Randomly assign SKUs to A or B for a fixed period
- Best when operations can treat SKU groups differently

### Pattern B: Region / warehouse randomization
- Assign fulfillment centers to A vs B
- Useful when inventory is managed by location

### Pattern C: Request-level randomization (rare for forecasting)
- For APIs serving forecast requests directly
- Works when forecasts don’t change behavior (e.g., analytics only)

---

## 🧾 Logging and Experiment Tracking (MLflow)

To make A/B tests reproducible, always log:

- **params**: horizon, cutoff, features, model type, hyperparameters
- **metrics**: MAE/RMSE/WAPE + business KPIs
- **artifacts**: predictions, evaluation tables, plots
- **decision**: winner + reasons

In this repo, we provide an MLflow-based A/B evaluation pipeline:
- `pipelines/mlflow_ab_monitoring.py`
- Tutorial: `tutorials/MLFLOW_TUTORIAL.md`

---

## 🔍 What “Winning” Looks Like

Don’t promote a model just because one metric improved slightly.

Use a decision rubric:

- **Primary metric** (e.g., WAPE or business cost) improves by a meaningful margin
- **No major regressions** in critical segments (top SKUs, peak season)
- **Guardrails** hold (stockouts not worse, ops costs stable)
- Model is stable, debuggable, and has rollback

---

## ✅ Checklist

- [ ] Same horizon and evaluation windows
- [ ] No leakage
- [ ] Segment-level analysis included
- [ ] Confidence intervals or statistical tests
- [ ] Online guardrails defined
- [ ] Logging + artifacts stored (MLflow)
- [ ] Clear promote/rollback criteria

---

## 🔗 Next Steps in This Repo

- Run offline A/B evaluation:
  - `python pipelines/mlflow_ab_monitoring.py`
- Add business KPI simulation (inventory cost model) as a follow-up
- Integrate A/B routing in the FastAPI service (Module 9) for shadow mode


