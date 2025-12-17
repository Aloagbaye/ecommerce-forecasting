# Module 6: Deep Learning Forecasting with PyTorch

## 📚 Learning Objectives

By the end of this module, you will be able to:

1. **Understand** when deep learning helps (and when it doesn't) for forecasting
2. **Train** LSTM and GRU models for time series forecasting
3. **Handle** sequence data preparation and autoregressive forecasting
4. **Evaluate** deep learning models vs baselines and classical methods
5. **Recognize** computational trade-offs and training strategies

---

## 🎯 When to Use Deep Learning

Deep learning can excel when:
- **Complex patterns**: Non-linear interactions, long-range dependencies
- **Rich features**: Multiple time series, external regressors, embeddings
- **Large datasets**: Many SKUs with sufficient history per SKU
- **Multi-horizon**: Predicting multiple steps ahead simultaneously

**But be cautious:**
- **Small datasets**: DL often underperforms simple models
- **Intermittent demand**: Zeros and sparsity hurt DL performance
- **Interpretability**: Harder to explain than baselines/classical models
- **Training time**: Much slower than baselines/ML models

**Rule of thumb**: Try baselines → classical → ML first. Use DL if you have:
- 100+ observations per SKU
- Complex seasonality/interactions
- Sufficient compute budget

---

## 🧱 What We Build

We implement:
- **LSTM Forecaster** (`src/models/dl_models.py`)
- **GRU Forecaster** (lighter alternative to LSTM)
- **Sequence preparation** utilities
- **Autoregressive multi-step forecasting**

---

## 🔧 Setup

### 1. Install PyTorch

```bash
pip install torch>=2.0.0
```

Or with CUDA (if you have a GPU):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Verify Installation

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

---

## 📓 Notebook Walkthrough

### Part 1: Data Preparation

**Goal:** Prepare sequences for deep learning.

**Key Steps:**
1. Load a SKU with sufficient history (100+ observations)
2. Normalize/scale the data (important for neural networks)
3. Create sequences: `(seq_len, 1)` input → `(1,)` target
4. Split into train/validation sets

**Questions to Answer:**
- How long should the input sequence be? (Try 7, 14, 30, 60 days)
- Should we normalize? (Yes, typically min-max or z-score)
- How much data do we need? (At least 100+ observations)

### Part 2: LSTM Training

**Goal:** Train an LSTM model.

**Key Steps:**
1. Define model architecture (hidden_size, num_layers)
2. Set up loss function (MSE) and optimizer (Adam)
3. Train for multiple epochs with batching
4. Monitor training loss

**Hyperparameters to Tune:**
- `seq_len`: 14-60 days (longer = more context, but slower)
- `hidden_size`: 32-128 (larger = more capacity, but overfitting risk)
- `num_layers`: 1-3 (deeper = more complex patterns)
- `learning_rate`: 0.0001-0.01 (start with 0.001)
- `epochs`: 50-200 (early stopping recommended)

### Part 3: GRU Training

**Goal:** Train a GRU model (faster alternative to LSTM).

**Key Steps:**
1. Same as LSTM, but using GRU architecture
2. Compare training speed vs LSTM
3. Compare forecast quality

**When to Prefer GRU:**
- Faster training/inference
- Similar performance to LSTM for many tasks
- Less memory usage

### Part 4: Autoregressive Forecasting

**Goal:** Generate multi-step forecasts.

**Key Steps:**
1. Use last `seq_len` values as initial sequence
2. Predict next step
3. Append prediction to sequence, shift window
4. Repeat for `horizon` steps

**Challenges:**
- **Error accumulation**: Errors compound over long horizons
- **Distribution shift**: Future distributions may differ from training
- **Cold start**: First few steps are most accurate

### Part 5: Evaluation & Comparison

**Goal:** Compare DL models vs baselines/classical/ML.

**Key Steps:**
1. Evaluate on held-out test set
2. Compute MAE, RMSE, WAPE, sMAPE
3. Compare against:
   - Baseline (naive, moving average)
   - Classical (SARIMA, ETS)
   - ML (LightGBM, XGBoost)

**Questions to Answer:**
- Does DL outperform simpler models?
- Is the extra training time worth it?
- Which SKUs benefit most from DL?

---

## 💡 Key Concepts

### Sequence-to-One Architecture

```
Input:  [y_{t-seq_len}, ..., y_{t-1}]  (seq_len values)
Output: y_t                              (1 value)
```

For multi-step forecasting, we use **autoregressive** approach:
1. Predict `y_t` from `[y_{t-seq_len}, ..., y_{t-1}]`
2. Predict `y_{t+1}` from `[y_{t-seq_len+1}, ..., y_t]` (includes predicted `y_t`)
3. Continue for `horizon` steps

### Normalization

Neural networks are sensitive to input scale. Common approaches:
- **Min-Max**: `(x - min) / (max - min)` → [0, 1]
- **Z-score**: `(x - mean) / std` → mean 0, std 1

**Important**: Normalize using training statistics only, then denormalize predictions.

### Overfitting Prevention

- **Early stopping**: Stop when validation loss stops improving
- **Dropout**: Randomly zero neurons during training
- **Regularization**: L2 weight decay
- **Smaller models**: Reduce hidden_size/num_layers if overfitting

---

## 📊 Example Usage

### Basic LSTM Forecast

```python
from src.models.dl_models import lstm_forecast
import numpy as np

# Sample time series
y_train = np.random.randn(200).cumsum() + 100

# Forecast
result = lstm_forecast(
    y_train=y_train,
    horizon=14,
    seq_len=30,
    hidden_size=64,
    num_layers=2,
    epochs=50,
    verbose=True
)

print(f"Forecast: {result.y_pred}")
```

### GRU Forecast

```python
from src.models.dl_models import gru_forecast

result = gru_forecast(
    y_train=y_train,
    horizon=14,
    seq_len=30,
    hidden_size=64,
    epochs=50
)
```

---

## 🚨 Common Pitfalls

1. **Not normalizing data**
   - Neural networks need normalized inputs
   - Solution: Always normalize before training

2. **Too short sequences**
   - `seq_len=7` may miss weekly patterns
   - Solution: Try 14, 30, 60 days

3. **Too few observations**
   - DL needs 100+ observations per SKU
   - Solution: Use baselines/ML for short histories

4. **Overfitting**
   - Training loss decreases but validation loss increases
   - Solution: Early stopping, dropout, regularization

5. **Ignoring computational cost**
   - DL is slow to train (minutes to hours per SKU)
   - Solution: Only use for high-value SKUs or when simpler models fail

6. **Autoregressive error accumulation**
   - Errors compound over long horizons
   - Solution: Use direct multi-output models for long horizons (advanced)

---

## ✅ Deliverables

By the end of this module, you should have:

1. **✅ Trained LSTM/GRU models** on sample SKUs
2. **✅ Evaluation metrics** comparing DL vs baselines/classical/ML
3. **✅ Understanding** of when DL helps vs hurts
4. **✅ Notebook** (`notebooks/06_deep_learning.ipynb`) with full workflow

---

## 🔗 Next Steps

After Module 6:
- **Module 7**: Advanced topics (ensemble methods, uncertainty quantification)
- **Module 8**: Orchestration & pipelines
- **Module 9**: Deployment (FastAPI)
- **Module 10**: Monitoring & drift detection

---

## 📚 Additional Resources

### PyTorch Time Series
- [PyTorch Time Series Tutorial](https://pytorch.org/tutorials/beginner/transformer_tutorial.html)
- [LSTM for Time Series Forecasting](https://machinelearningmastery.com/lstm-for-time-series-forecasting-in-python/)

### Deep Learning for Forecasting
- [DeepAR (Amazon)](https://arxiv.org/abs/1704.04110)
- [Temporal Fusion Transformer](https://arxiv.org/abs/1912.09363)
- [N-BEATS](https://arxiv.org/abs/1905.10437)

### When Not to Use DL
- [The Unreasonable Effectiveness of Simple Baselines](https://arxiv.org/abs/1901.02452)
- [Do We Really Need Deep Learning Models for Time Series?](https://arxiv.org/abs/2101.02118)

---

## ❓ Exercises

### Exercise 1: Basic LSTM
Train an LSTM on a single SKU with 200+ observations. Compare forecast vs moving average baseline.

### Exercise 2: Sequence Length Tuning
Train LSTMs with `seq_len=[7, 14, 30, 60]` and compare performance. Which works best?

### Exercise 3: GRU vs LSTM
Train both GRU and LSTM on the same SKU. Compare:
- Training time
- Forecast accuracy
- Model size

### Exercise 4: Normalization Impact
Train an LSTM with and without normalization. What happens?

### Exercise 5: Overfitting Detection
Train an LSTM with too many epochs. Plot training vs validation loss. When does overfitting start?

---

## 🎓 Learning Check

Before moving forward, ensure you can:

- [ ] Prepare sequences for deep learning
- [ ] Train LSTM and GRU models
- [ ] Generate multi-step forecasts autoregressively
- [ ] Evaluate DL models vs simpler alternatives
- [ ] Recognize when DL is appropriate vs overkill

---

**Happy Learning! 🚀**

