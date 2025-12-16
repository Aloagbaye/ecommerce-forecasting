# Module 2: Data Cleaning & Feature Engineering

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Clean** e-commerce sales data (handle missing dates, outliers, inconsistencies)
2. **Engineer** temporal features (day of week, month, seasonality)
3. **Create** lag features (historical sales patterns)
4. **Generate** rolling statistics (moving averages, standard deviations)
5. **Build** promotion and price features
6. **Construct** a reusable feature engineering pipeline
7. **Prepare** data ready for forecasting models

---

## 🎯 Business Context

Raw data is rarely ready for modeling. In e-commerce forecasting:

- **Missing dates** can break time series continuity
- **Inconsistent data** can mislead models
- **Rich features** dramatically improve forecast accuracy
- **Temporal patterns** (lags, rolling stats) capture demand dynamics
- **Promotion features** are critical for accurate predictions

This preparation phase is essential because:
- **Garbage in, garbage out**: Poor data quality leads to poor forecasts
- **Feature quality > Model complexity**: Good features beat complex models
- **Reusability**: Well-designed pipelines save time in production
- **Interpretability**: Engineered features provide business insights

---

## 📦 Module Overview

This module has two main parts:

### Part 1: Data Cleaning
- Handle missing dates
- Address outliers
- Fix data inconsistencies
- Validate data quality

### Part 2: Feature Engineering
- Temporal features (time-based)
- Lag features (historical patterns)
- Rolling statistics (moving averages)
- Promotion features
- Price features
- Interaction features

---

## 🔧 Setup Instructions

### Prerequisites

- Completed Module 1 (EDA and data understanding)
- Cleaned data from Module 1 analysis
- Understanding of your data's characteristics

### Required Libraries

All should be installed from `requirements.txt`:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scikit-learn` - Feature scaling (optional)

---

## 📓 Notebook Walkthrough

### Part 1: Data Cleaning

**Goal:** Prepare clean, consistent data for feature engineering.

#### Step 1: Load and Review Data

```python
from src.data.loaders import load_sample_data
import pandas as pd

# Load data
df = load_sample_data()

# Review data quality issues from Module 1
print(f"Shape: {df.shape}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Missing values:\n{df.isnull().sum()}")
```

#### Step 2: Handle Missing Dates

**Problem:** Some SKUs may have missing dates, breaking time series continuity.

**Solution:** Fill missing dates per SKU with zero sales (or forward fill).

```python
from src.data.cleaners import fill_missing_dates

# Fill missing dates for each SKU
df_clean = fill_missing_dates(df, date_col='date', group_col='sku_id', 
                               fill_value=0, fill_col='units_sold')
```

**Key Considerations:**
- Missing dates may indicate stockouts (zeros) or discontinued items
- Forward fill may be appropriate for some cases
- Document your approach for reproducibility

#### Step 3: Handle Outliers

**Problem:** Extreme values may be errors or legitimate promotions.

**Solution:** Investigate before removing; cap extreme values if needed.

```python
from src.data.cleaners import handle_outliers

# Option 1: Cap outliers (keep but limit extreme values)
df_clean = handle_outliers(df_clean, column='units_sold', method='cap', 
                          lower_percentile=0.01, upper_percentile=0.99)

# Option 2: Remove extreme outliers (use with caution)
# df_clean = handle_outliers(df_clean, column='units_sold', method='remove', 
#                           lower_percentile=0.01, upper_percentile=0.99)
```

**Best Practice:** 
- Investigate outliers first (may be promotions)
- Cap rather than remove when possible
- Document outlier handling approach

#### Step 4: Validate Data Quality

**Goal:** Ensure data is ready for feature engineering.

```python
from src.data.loaders import validate_data

validation = validate_data(df_clean)
print(f"Data valid: {validation['is_valid']}")
if validation['issues']:
    print("Issues:", validation['issues'])
```

---

### Part 2: Feature Engineering

**Goal:** Create features that capture demand patterns and improve forecast accuracy.

#### Step 1: Temporal Features

**Why:** Time-based patterns are critical for forecasting.

```python
from src.features.engineering import create_temporal_features

# Create temporal features
df_features = create_temporal_features(df_clean, date_col='date')

# Features created:
# - year, month, day, day_of_week, day_of_month
# - week, quarter
# - is_weekend, is_month_start, is_month_end
# - day_of_week_sin, day_of_week_cos (cyclical)
# - month_sin, month_cos (cyclical)
```

**Key Features:**
- **Cyclical encoding**: Sine/cosine for day-of-week and month (preserves cyclical nature)
- **Binary flags**: is_weekend, is_holiday_season
- **Time indices**: Useful for trend modeling

#### Step 2: Lag Features

**Why:** Historical sales are strong predictors of future demand.

```python
from src.features.lag_features import create_lag_features

# Create lag features
df_features = create_lag_features(df_features, 
                                  value_col='units_sold',
                                  group_col='sku_id',
                                  date_col='date',
                                  lags=[1, 7, 14, 30, 90])

# Features created:
# - lag_1: Previous day sales
# - lag_7: Same day last week
# - lag_14: Same day 2 weeks ago
# - lag_30: Same day last month
# - lag_90: Same day 3 months ago
```

**Key Considerations:**
- Lags should respect seasonality (lag_7 for weekly, lag_30 for monthly)
- Group by SKU to get SKU-specific lags
- Handle NaN values (first few rows will have missing lags)

#### Step 3: Rolling Statistics

**Why:** Capture trends and volatility in demand.

```python
from src.features.engineering import create_rolling_features

# Create rolling statistics
df_features = create_rolling_features(df_features,
                                     value_col='units_sold',
                                     group_col='sku_id',
                                     date_col='date',
                                     windows=[7, 14, 30, 90])

# Features created:
# - rolling_mean_7, rolling_mean_14, rolling_mean_30, rolling_mean_90
# - rolling_std_7, rolling_std_14, rolling_std_30, rolling_std_90
# - rolling_min_7, rolling_max_7
# - rolling_median_7
```

**Key Features:**
- **Rolling mean**: Captures recent trend
- **Rolling std**: Captures volatility
- **Rolling min/max**: Captures range
- **Multiple windows**: Short-term (7) and long-term (30, 90) patterns

#### Step 4: Promotion Features

**Why:** Promotions significantly impact demand.

```python
from src.features.engineering import create_promotion_features

# Create promotion features
df_features = create_promotion_features(df_features,
                                        promo_col='promotion_flag',
                                        group_col='sku_id',
                                        date_col='date')

# Features created:
# - promo_last_7_days: Count of promotions in last 7 days
# - promo_last_30_days: Count of promotions in last 30 days
# - days_since_last_promo: Days since last promotion
# - days_until_next_promo: Days until next promotion (if known)
# - promo_lift_7d: Average lift from promotions in last 7 days
```

**Key Features:**
- **Promotion history**: Recent promotion activity
- **Time since promotion**: Post-promotion effects
- **Promotion lift**: Historical promotion effectiveness

#### Step 5: Price Features

**Why:** Price changes affect demand (price elasticity).

```python
from src.features.engineering import create_price_features

# Create price features
df_features = create_price_features(df_features,
                                    price_col='price',
                                    group_col='sku_id',
                                    date_col='date')

# Features created:
# - price_change_pct: Percentage change from previous period
# - price_lag_1: Previous period price
# - price_rolling_mean_7: Average price over last 7 days
# - price_relative_to_avg: Current price / average price
```

**Key Features:**
- **Price changes**: Detect discounts and price increases
- **Price relative to history**: Is current price high/low?
- **Price volatility**: How stable is pricing?

#### Step 6: Interaction Features

**Why:** Combined effects (e.g., promotion + weekend) can be powerful.

```python
from src.features.engineering import create_interaction_features

# Create interaction features
df_features = create_interaction_features(df_features)

# Features created:
# - month_day_interaction: month × day_of_week
# - holiday_weekend: is_holiday_season × is_weekend
# - promo_weekend: promotion_flag × is_weekend
# - peak_period: (Nov-Dec) × weekend
```

**Key Interactions:**
- **Time interactions**: Month × day of week
- **Promotion interactions**: Promotion × time period
- **Peak period indicators**: High-demand combinations

#### Step 7: Target Variable Preparation

**Goal:** Prepare the target variable for modeling.

```python
# Create target variable (future sales)
from src.features.engineering import create_target_variable

# For forecasting, we'll predict future sales
# This will be done during train/test split, but we can prepare here
df_features['target'] = df_features['units_sold']

# Optional: Log transform for models that benefit from it
import numpy as np
df_features['units_sold_log'] = np.log1p(df_features['units_sold'])  # log1p handles zeros
```

---

## 📊 Feature Engineering Pipeline

### Complete Pipeline Example

```python
from src.data.loaders import load_sample_data
from src.data.cleaners import fill_missing_dates, handle_outliers
from src.features.engineering import (
    create_temporal_features,
    create_rolling_features,
    create_promotion_features,
    create_price_features,
    create_interaction_features
)
from src.features.lag_features import create_lag_features

def create_feature_pipeline(df):
    """Complete feature engineering pipeline."""
    
    # Step 1: Data Cleaning
    print("Step 1: Cleaning data...")
    df_clean = fill_missing_dates(df, date_col='date', group_col='sku_id')
    df_clean = handle_outliers(df_clean, column='units_sold', method='cap')
    
    # Step 2: Temporal Features
    print("Step 2: Creating temporal features...")
    df_features = create_temporal_features(df_clean, date_col='date')
    
    # Step 3: Lag Features
    print("Step 3: Creating lag features...")
    df_features = create_lag_features(df_features,
                                      value_col='units_sold',
                                      group_col='sku_id',
                                      date_col='date',
                                      lags=[1, 7, 14, 30, 90])
    
    # Step 4: Rolling Statistics
    print("Step 4: Creating rolling features...")
    df_features = create_rolling_features(df_features,
                                         value_col='units_sold',
                                         group_col='sku_id',
                                         date_col='date',
                                         windows=[7, 14, 30, 90])
    
    # Step 5: Promotion Features
    print("Step 5: Creating promotion features...")
    if 'promotion_flag' in df_features.columns:
        df_features = create_promotion_features(df_features,
                                               promo_col='promotion_flag',
                                               group_col='sku_id',
                                               date_col='date')
    
    # Step 6: Price Features
    print("Step 6: Creating price features...")
    if 'price' in df_features.columns:
        df_features = create_price_features(df_features,
                                           price_col='price',
                                           group_col='sku_id',
                                           date_col='date')
    
    # Step 7: Interaction Features
    print("Step 7: Creating interaction features...")
    df_features = create_interaction_features(df_features)
    
    print(f"✓ Feature engineering complete! Shape: {df_features.shape}")
    return df_features

# Run pipeline
df_raw = load_sample_data()
df_engineered = create_feature_pipeline(df_raw)
```

---

## 🔍 Feature Categories

### 1. Temporal Features

**Purpose:** Capture time-based patterns

| Feature | Description | Use Case |
|---------|-------------|----------|
| `day_of_week` | 0-6 (Mon-Sun) | Weekly seasonality |
| `day_of_week_sin/cos` | Cyclical encoding | Preserves weekly cycle |
| `month` | 1-12 | Monthly seasonality |
| `month_sin/cos` | Cyclical encoding | Preserves annual cycle |
| `is_weekend` | Binary flag | Weekend effect |
| `is_holiday_season` | Oct-Dec flag | Holiday shopping |
| `quarter` | Q1-Q4 | Quarterly patterns |
| `year` | Year value | Long-term trends |

### 2. Lag Features

**Purpose:** Historical demand patterns

| Feature | Description | Captures |
|---------|-------------|----------|
| `lag_1` | Previous day | Short-term memory |
| `lag_7` | Same day last week | Weekly seasonality |
| `lag_14` | 2 weeks ago | Bi-weekly patterns |
| `lag_30` | Same day last month | Monthly seasonality |
| `lag_90` | 3 months ago | Quarterly patterns |

### 3. Rolling Statistics

**Purpose:** Recent trends and volatility

| Feature | Description | Captures |
|---------|-------------|----------|
| `rolling_mean_7` | 7-day average | Recent trend |
| `rolling_mean_30` | 30-day average | Monthly trend |
| `rolling_std_7` | 7-day std dev | Short-term volatility |
| `rolling_std_30` | 30-day std dev | Long-term volatility |
| `rolling_min/max_7` | 7-day range | Demand range |

### 4. Promotion Features

**Purpose:** Promotion impact

| Feature | Description | Captures |
|---------|-------------|----------|
| `promo_last_7_days` | Promotion count | Recent promo activity |
| `days_since_last_promo` | Days since promo | Post-promo effects |
| `promo_lift_7d` | Historical lift | Promo effectiveness |

### 5. Price Features

**Purpose:** Price elasticity

| Feature | Description | Captures |
|---------|-------------|----------|
| `price_change_pct` | % price change | Price sensitivity |
| `price_relative_to_avg` | Price / avg price | Price positioning |
| `price_rolling_mean_7` | 7-day avg price | Price trend |

### 6. Interaction Features

**Purpose:** Combined effects

| Feature | Description | Captures |
|---------|-------------|----------|
| `month_day_interaction` | month × day_of_week | Time interactions |
| `holiday_weekend` | holiday × weekend | Peak period effect |
| `promo_weekend` | promo × weekend | Promo timing effect |

---

## 📝 Feature Engineering Best Practices

### 1. Handle Missing Values

**Lag Features:**
- First rows will have NaN for lags
- Options: Drop rows, forward fill, or use 0

**Rolling Features:**
- First rows will have NaN until window is filled
- Options: Drop rows, use expanding window, or forward fill

**Best Practice:**
```python
# Drop rows with missing critical features
df_features = df_features.dropna(subset=['lag_7', 'rolling_mean_7'])

# Or forward fill for some features
df_features['rolling_mean_7'] = df_features.groupby('sku_id')['rolling_mean_7'].fillna(method='ffill')
```

### 2. Feature Scaling

**When to Scale:**
- Linear models (regression) benefit from scaling
- Tree-based models (LightGBM, XGBoost) don't need scaling
- Neural networks require scaling

**Methods:**
- StandardScaler: Mean 0, std 1
- MinMaxScaler: Range 0-1
- RobustScaler: Median-based (handles outliers)

### 3. Feature Selection

**Remove Low-Variance Features:**
- Features with constant values
- Features with very low variance

**Remove Highly Correlated Features:**
- Redundant information
- Can cause multicollinearity

**Best Practice:**
```python
# Remove constant features
constant_features = [col for col in df_features.columns 
                     if df_features[col].nunique() == 1]
df_features = df_features.drop(columns=constant_features)

# Check correlation
correlation_matrix = df_features.select_dtypes(include=[np.number]).corr()
```

### 4. Feature Documentation

**Document:**
- What each feature represents
- How it was created
- Expected range/values
- Business interpretation

**Example:**
```python
feature_documentation = {
    'lag_7': {
        'description': 'Sales from same day last week',
        'type': 'lag',
        'range': '0 to max(units_sold)',
        'business_meaning': 'Captures weekly seasonality pattern'
    },
    'rolling_mean_7': {
        'description': '7-day moving average of sales',
        'type': 'rolling_statistic',
        'range': '0 to max(units_sold)',
        'business_meaning': 'Recent demand trend'
    }
}
```

---

## 🚨 Common Pitfalls

1. **Data Leakage**
   - ❌ Using future information to predict past
   - ✅ Only use lag features (past data)
   - ✅ Ensure features are computed correctly per SKU

2. **Ignoring Missing Values**
   - ❌ Leaving NaN values in features
   - ✅ Handle missing values explicitly
   - ✅ Document handling approach

3. **Over-Engineering**
   - ❌ Creating too many features
   - ✅ Start with essential features, add incrementally
   - ✅ Focus on features with business meaning

4. **Not Grouping by SKU**
   - ❌ Computing lags/rolling stats across all SKUs
   - ✅ Always group by SKU for SKU-specific features
   - ✅ Use `groupby('sku_id')` before operations

5. **Forgetting Cyclical Encoding**
   - ❌ Using raw day_of_week (0-6) as numeric
   - ✅ Use sine/cosine for cyclical features
   - ✅ Preserves that day 6 (Sunday) is close to day 0 (Monday)

6. **Not Validating Features**
   - ❌ Assuming features are correct
   - ✅ Visualize features, check ranges
   - ✅ Verify feature logic makes sense

---

## 🔍 Feature Validation

### Visual Inspection

```python
# Check feature distributions
import matplotlib.pyplot as plt
import seaborn as sns

# Plot lag features
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
df_features[['lag_1', 'lag_7', 'lag_30']].hist(ax=axes, bins=50)
plt.suptitle('Lag Feature Distributions')
plt.show()

# Check for correlations
corr_matrix = df_features[['lag_1', 'lag_7', 'rolling_mean_7', 'units_sold']].corr()
sns.heatmap(corr_matrix, annot=True)
plt.title('Feature Correlations with Target')
plt.show()
```

### Statistical Checks

```python
# Check for missing values
print("Missing values per feature:")
print(df_features.isnull().sum().sort_values(ascending=False))

# Check feature ranges
print("\nFeature ranges:")
print(df_features.describe())

# Check for infinite values
print("\nInfinite values:")
print((df_features == np.inf).sum().sum())
```

---

## 📊 Deliverables

By the end of this module, you should have:

1. **✅ Cleaned Dataset**
   - Missing dates handled
   - Outliers addressed
   - Data validated

2. **✅ Feature-Engineered Dataset**
   - Temporal features
   - Lag features
   - Rolling statistics
   - Promotion features
   - Price features
   - Interaction features

3. **✅ Feature Engineering Pipeline**
   - Reusable functions in `src/features/engineering.py`
   - Pipeline script that can be run end-to-end
   - Well-documented code

4. **✅ Feature Documentation**
   - List of all features created
   - Description of each feature
   - Business interpretation

5. **✅ Data Quality Report**
   - Missing value handling
   - Outlier treatment
   - Feature validation results

---

## 🔗 Next Steps

After completing Module 2:

1. **Save processed data** to `data/processed/` for use in modeling
2. **Review feature importance** (will be done in Module 5)
3. **Prepare for train/test split** (will be done in Module 3)
4. **Document feature engineering decisions**

**Next Module:** [Module 3: Baseline Forecasting Models](MODULE_3.md)

---

## 📚 Additional Resources

### Feature Engineering
- [Feature Engineering for Machine Learning](https://www.oreilly.com/library/view/feature-engineering-for/9781491953235/)
- [Time Series Feature Engineering](https://www.kaggle.com/learn/time-series)

### Data Cleaning
- [Pandas Data Cleaning](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Outlier Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)

### Time Series Features
- [Time Series Feature Extraction](https://tsfresh.readthedocs.io/)
- [Lag Features in Time Series](https://otexts.com/fpp3/features.html)

---

## ❓ Exercises

### Exercise 1: Basic Feature Engineering
Create temporal features for your dataset:
- Day of week (with cyclical encoding)
- Month (with cyclical encoding)
- Is weekend flag
- Is holiday season flag

### Exercise 2: Lag Features
Create lag features:
- lag_1, lag_7, lag_30
- Verify lags are computed per SKU
- Handle missing values appropriately

### Exercise 3: Rolling Statistics
Create rolling features:
- 7-day and 30-day rolling means
- 7-day and 30-day rolling standard deviations
- Visualize how rolling stats change over time

### Exercise 4: Promotion Features
If you have promotion data:
- Create promotion history features
- Calculate days since last promotion
- Analyze promotion patterns

### Exercise 5: Complete Pipeline
Build a complete feature engineering pipeline:
- Combine all feature creation steps
- Save processed data
- Document all features created

---

## 🎓 Learning Check

Before moving to Module 3, ensure you can:

- [ ] Clean data (handle missing dates, outliers)
- [ ] Create temporal features (day, month, cyclical encoding)
- [ ] Generate lag features (respecting SKU grouping)
- [ ] Compute rolling statistics (multiple windows)
- [ ] Build promotion and price features
- [ ] Create interaction features
- [ ] Handle missing values in engineered features
- [ ] Validate feature quality
- [ ] Document feature engineering pipeline

---

**Happy Feature Engineering! 🚀**

