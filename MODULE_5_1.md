# Module 5.1: Hierarchical Forecasting (Category → Subcategory → SKU)

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Define** a retail hierarchy (category → subcategory → SKU)
2. **Aggregate** history to multiple hierarchy levels
3. **Produce** forecasts at multiple levels (SKU / subcategory / category)
4. **Reconcile** forecasts so they are **hierarchically consistent**
5. **Compare** reconciliation strategies (top-down vs bottom-up)

---

## 🎯 Why Hierarchical Forecasting?

Businesses make decisions at multiple levels:
- **SKU level**: replenishment, purchase orders, safety stock
- **Category level**: budgeting, strategy, promotions planning
- **Warehouse/region level**: capacity planning

If forecasts aren’t consistent across levels, you get problems like:
- Sum of SKU forecasts ≠ category forecast
- Inventory totals don’t match financial plans

Hierarchical forecasting solves this by **reconciling** forecasts across levels.

---

## 🧱 Hierarchy in This Project

We use:

```
Category
  └── Subcategory
        └── SKU
```

Columns (expected):
- `category`
- `subcategory`
- `sku_id`
- `date`
- `units_sold`

---

## 🧠 Reconciliation Methods (Tutorial Versions)

### 1) Bottom-up

**Idea:** Forecast at SKU level, then aggregate upward.

- Category forecast = sum(SKU forecasts)
- Subcategory forecast = sum(SKU forecasts)

**Pros**
- Simple, consistent by construction
- Great if SKU forecasts are strong

**Cons**
- Noisy SKUs can pollute category forecasts

### 2) Top-down (proportional)

**Idea:** Forecast at category (or subcategory) level, then allocate down using historical proportions.

Example:
- Forecast category total
- Allocate to SKUs using last-90-day SKU share of category demand

**Pros**
- Category forecasts can be stable
- Useful when many SKUs are sparse/noisy

**Cons**
- Allocation may miss SKU-level dynamics (promos, trends)

### 3) Simple scaling reconciliation (category totals)

**Idea:** Start from SKU forecasts, but scale them within each category/date so the category sum matches the category forecast.

This is a lightweight “reconciliation” step that:
- keeps SKU shape,
- enforces category consistency.

---

## 🛠️ Implementation in This Repo

We implement helper utilities in:
- `src/hierarchy.py`

Key functions:
- `aggregate_to_level(...)`
- `bottom_up_reconcile(...)`
- `compute_topdown_proportions(...)`
- `top_down_reconcile(...)`
- `reconcile_to_category_totals(...)`

---

## ✅ Deliverables

1. **✅ Aggregated datasets** at category/subcategory/SKU levels
2. **✅ Reconciled forecasts** using top-down and bottom-up
3. **✅ Consistency checks** (do sums match?)
4. **✅ Notebook** walkthrough: `notebooks/11_hierarchical_forecasting.ipynb`

---

## 🚀 How to Run

Open:
- `notebooks/11_hierarchical_forecasting.ipynb`

The notebook will:
- load `data/raw/sample_sales.csv`
- build hierarchy aggregates
- create simple forecasts (for demonstration)
- reconcile them and validate consistency

---

## 🔗 Next Steps

After this module:
- extend reconciliation to include **multiple levels simultaneously** (MinT / optimal reconciliation)
- add SKU segmentation and run reconciliation per segment
- integrate reconciliation into the batch forecasting pipeline (Module 8)


