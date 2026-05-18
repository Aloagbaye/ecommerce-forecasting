"""
API endpoint tests.

The forecast and explain endpoints require data — we patch DATASET_CACHE.get()
with a small in-memory DataFrame so tests run without any CSV files on disk.
"""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def fake_df():
    """Minimal in-memory sales DataFrame covering 60 days for two SKUs."""
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    rows = []
    np.random.seed(42)
    for sku in ["SKU001", "SKU002"]:
        for d in dates:
            rows.append(
                {
                    "date": d,
                    "sku_id": sku,
                    "units_sold": float(np.random.randint(5, 50)),
                    "price": float(np.random.uniform(10, 100)),
                    "promotion_flag": bool(np.random.random() < 0.1),
                }
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /forecast
# ---------------------------------------------------------------------------


class TestForecastEndpoint:
    def test_returns_200_for_valid_sku(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            response = client.post(
                "/forecast",
                json={"sku_id": "SKU001", "horizon": 7, "method": "naive"},
            )
        assert response.status_code == 200

    def test_response_schema(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            data = client.post(
                "/forecast",
                json={"sku_id": "SKU001", "horizon": 7, "method": "moving_average"},
            ).json()
        assert data["sku_id"] == "SKU001"
        assert data["horizon"] == 7
        assert len(data["forecast"]) == 7
        assert len(data["forecast_dates"]) == 7

    def test_all_methods_accepted(self, client, fake_df):
        for method in ("naive", "moving_average", "ses"):
            with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
                resp = client.post(
                    "/forecast",
                    json={"sku_id": "SKU001", "horizon": 5, "method": method},
                )
            assert resp.status_code == 200, f"method={method} failed"

    def test_unknown_sku_returns_404(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            resp = client.post(
                "/forecast",
                json={"sku_id": "DOES_NOT_EXIST", "horizon": 7},
            )
        assert resp.status_code == 404

    def test_invalid_horizon_returns_422(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            resp = client.post(
                "/forecast",
                json={"sku_id": "SKU001", "horizon": 0},
            )
        assert resp.status_code == 422

    def test_forecast_values_are_finite(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            data = client.post(
                "/forecast",
                json={"sku_id": "SKU001", "horizon": 14, "method": "ses"},
            ).json()
        assert all(np.isfinite(v) for v in data["forecast"])

    def test_cutoff_date_respected(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            data = client.post(
                "/forecast",
                json={"sku_id": "SKU001", "horizon": 3, "cutoff_date": "2023-01-15"},
            ).json()
        assert data["cutoff_date"] == "2023-01-15"
        # First forecast date should be the day after cutoff
        assert data["forecast_dates"][0] == "2023-01-16"


# ---------------------------------------------------------------------------
# /explain
# ---------------------------------------------------------------------------


class TestExplainEndpoint:
    def test_returns_200(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            resp = client.post(
                "/explain",
                json={"sku_id": "SKU001", "horizon": 7, "method": "moving_average"},
            )
        assert resp.status_code == 200

    def test_response_has_explanation(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            data = client.post(
                "/explain",
                json={"sku_id": "SKU001", "horizon": 7, "method": "naive"},
            ).json()
        assert isinstance(data["explanation"], str)
        assert len(data["explanation"]) > 0
        assert isinstance(data["bullets"], list)

    def test_unknown_sku_returns_404(self, client, fake_df):
        with patch("api.app.DATASET_CACHE.get", return_value=fake_df):
            resp = client.post(
                "/explain",
                json={"sku_id": "GHOST_SKU", "horizon": 7},
            )
        assert resp.status_code == 404
