"""
Deep Learning forecasting models using PyTorch.

This module provides LSTM, GRU, and simple Transformer architectures for time series forecasting.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Install with: pip install torch")

from src.models.baseline import ForecastResult, _to_1d_array


class TimeSeriesDataset(Dataset):
    """PyTorch Dataset for time series sequences."""

    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        """
        Args:
            sequences: (N, seq_len) array of input sequences
            targets: (N,) array of target values
        """
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]


class LSTMForecaster(nn.Module):
    """LSTM-based forecaster."""

    def __init__(self, input_size: int = 1, hidden_size: int = 64, num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Take last output
        last_out = lstm_out[:, -1, :]  # (batch, hidden_size)
        output = self.fc(last_out)  # (batch, 1)
        return output.squeeze(-1)  # (batch,)


class GRUForecaster(nn.Module):
    """GRU-based forecaster."""

    def __init__(self, input_size: int = 1, hidden_size: int = 64, num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        gru_out, _ = self.gru(x)
        last_out = gru_out[:, -1, :]  # (batch, hidden_size)
        output = self.fc(last_out)  # (batch, 1)
        return output.squeeze(-1)  # (batch,)


def _create_sequences(data: np.ndarray, seq_len: int, horizon: int = 1):
    """
    Create sequences for training/testing.

    Args:
        data: 1D array of time series values
        seq_len: Length of input sequence
        horizon: Number of steps ahead to predict (default 1)

    Returns:
        X: (N, seq_len, 1) sequences
        y: (N,) targets
    """
    if len(data) < seq_len + horizon:
        raise ValueError(f"Data length ({len(data)}) must be >= seq_len + horizon ({seq_len + horizon})")

    X, y = [], []
    for i in range(len(data) - seq_len - horizon + 1):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len + horizon - 1])

    return np.array(X).reshape(-1, seq_len, 1), np.array(y)


def _train_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int = 50,
    lr: float = 0.001,
    device: Optional[torch.device] = None,
    verbose: bool = True,
):
    """Train a PyTorch model."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required. Install with: pip install torch")

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if verbose and (epoch + 1) % 10 == 0:
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    return model


def _forecast_autoregressive(
    model: nn.Module,
    last_sequence: np.ndarray,
    horizon: int,
    device: Optional[torch.device] = None,
) -> np.ndarray:
    """
    Generate multi-step forecast using autoregressive approach.

    Args:
        model: Trained PyTorch model
        last_sequence: Last seq_len values from training data
        horizon: Number of steps to forecast
        device: PyTorch device

    Returns:
        Forecast array of length horizon
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required. Install with: pip install torch")

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.eval()
    forecast = []
    current_seq = last_sequence.copy()

    with torch.no_grad():
        for _ in range(horizon):
            x = torch.FloatTensor(current_seq).unsqueeze(0).to(device)  # (1, seq_len, 1)
            pred = model(x).cpu().numpy()[0]
            forecast.append(pred)
            # Update sequence: remove first, append prediction
            current_seq = np.roll(current_seq, -1, axis=0)
            current_seq[-1] = pred

    return np.array(forecast)


def lstm_forecast(
    y_train: Iterable[float],
    horizon: int,
    seq_len: int = 30,
    hidden_size: int = 64,
    num_layers: int = 2,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 0.001,
    train_split: float = 0.8,
    device: Optional[torch.device] = None,
    verbose: bool = True,
) -> ForecastResult:
    """
    Train an LSTM model and generate forecasts.

    Args:
        y_train: Training time series (1D iterable)
        horizon: Forecast horizon
        seq_len: Input sequence length
        hidden_size: LSTM hidden size
        num_layers: Number of LSTM layers
        epochs: Training epochs
        batch_size: Batch size
        lr: Learning rate
        train_split: Fraction of data for training (rest for validation)
        device: PyTorch device (auto-detected if None)
        verbose: Print training progress

    Returns:
        ForecastResult with predictions
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required. Install with: pip install torch")

    y = _to_1d_array(y_train)
    if len(y) < seq_len + 10:
        raise ValueError(f"Need at least {seq_len + 10} observations, got {len(y)}")

    # Create sequences
    X, y_targets = _create_sequences(y, seq_len, horizon=1)

    # Train/val split
    split_idx = int(len(X) * train_split)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train_seq, y_val_seq = y_targets[:split_idx], y_targets[split_idx:]

    # Create data loaders
    train_dataset = TimeSeriesDataset(X_train, y_train_seq)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Build model
    model = LSTMForecaster(input_size=1, hidden_size=hidden_size, num_layers=num_layers)

    # Train
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = _train_model(model, train_loader, epochs=epochs, lr=lr, device=device, verbose=verbose)

    # Forecast: use last seq_len values
    last_seq = y[-seq_len:].reshape(-1, 1)
    forecast = _forecast_autoregressive(model, last_seq, horizon, device=device)

    return ForecastResult(y_pred=forecast)


def gru_forecast(
    y_train: Iterable[float],
    horizon: int,
    seq_len: int = 30,
    hidden_size: int = 64,
    num_layers: int = 2,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 0.001,
    train_split: float = 0.8,
    device: Optional[torch.device] = None,
    verbose: bool = True,
) -> ForecastResult:
    """
    Train a GRU model and generate forecasts.

    Args:
        y_train: Training time series (1D iterable)
        horizon: Forecast horizon
        seq_len: Input sequence length
        hidden_size: GRU hidden size
        num_layers: Number of GRU layers
        epochs: Training epochs
        batch_size: Batch size
        lr: Learning rate
        train_split: Fraction of data for training (rest for validation)
        device: PyTorch device (auto-detected if None)
        verbose: Print training progress

    Returns:
        ForecastResult with predictions
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required. Install with: pip install torch")

    y = _to_1d_array(y_train)
    if len(y) < seq_len + 10:
        raise ValueError(f"Need at least {seq_len + 10} observations, got {len(y)}")

    # Create sequences
    X, y_targets = _create_sequences(y, seq_len, horizon=1)

    # Train/val split
    split_idx = int(len(X) * train_split)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train_seq, y_val_seq = y_targets[:split_idx], y_targets[split_idx:]

    # Create data loaders
    train_dataset = TimeSeriesDataset(X_train, y_train_seq)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Build model
    model = GRUForecaster(input_size=1, hidden_size=hidden_size, num_layers=num_layers)

    # Train
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = _train_model(model, train_loader, epochs=epochs, lr=lr, device=device, verbose=verbose)

    # Forecast: use last seq_len values
    last_seq = y[-seq_len:].reshape(-1, 1)
    forecast = _forecast_autoregressive(model, last_seq, horizon, device=device)

    return ForecastResult(y_pred=forecast)

