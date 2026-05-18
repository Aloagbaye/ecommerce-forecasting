import numpy as np
import pandas as pd
import pytest

from src.models.baseline import (
    naive_forecast,
    moving_average_forecast,
    simple_exponential_smoothing_forecast,
    forecast_by_sku,
)


TRAIN = [10.0, 12.0, 8.0, 15.0, 20.0]


class TestNaiveForecast:
    def test_repeats_last_value(self):
        result = naive_forecast(TRAIN, horizon=3)
        assert list(result.y_pred) == [20.0, 20.0, 20.0]

    def test_horizon_one(self):
        result = naive_forecast([5], horizon=1)
        assert result.y_pred[0] == pytest.approx(5.0)

    def test_output_length(self):
        result = naive_forecast(TRAIN, horizon=7)
        assert len(result.y_pred) == 7

    def test_invalid_horizon_raises(self):
        with pytest.raises(ValueError):
            naive_forecast(TRAIN, horizon=0)

    def test_empty_train_raises(self):
        with pytest.raises(ValueError):
            naive_forecast([], horizon=1)


class TestMovingAverageForecast:
    def test_full_window(self):
        y = [2.0, 4.0, 6.0]
        result = moving_average_forecast(y, horizon=2, window=3)
        assert result.y_pred == pytest.approx([4.0, 4.0])

    def test_window_larger_than_series(self):
        # window=10 but only 3 values — should use all 3
        y = [3.0, 6.0, 9.0]
        result = moving_average_forecast(y, horizon=1, window=10)
        assert result.y_pred[0] == pytest.approx(6.0)

    def test_window_one_equals_naive(self):
        result_ma = moving_average_forecast(TRAIN, horizon=4, window=1)
        result_naive = naive_forecast(TRAIN, horizon=4)
        np.testing.assert_array_almost_equal(result_ma.y_pred, result_naive.y_pred)

    def test_invalid_horizon_raises(self):
        with pytest.raises(ValueError):
            moving_average_forecast(TRAIN, horizon=-1)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            moving_average_forecast(TRAIN, horizon=1, window=0)


class TestSESForecast:
    def test_flat_series_returns_same_value(self):
        y = [5.0] * 10
        result = simple_exponential_smoothing_forecast(y, horizon=3, alpha=0.3)
        assert result.y_pred == pytest.approx([5.0, 5.0, 5.0])

    def test_output_is_flat(self):
        # SES produces a flat forecast
        result = simple_exponential_smoothing_forecast(TRAIN, horizon=5, alpha=0.5)
        assert len(set(result.y_pred.round(8))) == 1

    def test_alpha_one_equals_naive(self):
        result_ses = simple_exponential_smoothing_forecast(TRAIN, horizon=3, alpha=1.0)
        result_naive = naive_forecast(TRAIN, horizon=3)
        np.testing.assert_array_almost_equal(result_ses.y_pred, result_naive.y_pred)

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            simple_exponential_smoothing_forecast(TRAIN, horizon=1, alpha=0.0)
        with pytest.raises(ValueError):
            simple_exponential_smoothing_forecast(TRAIN, horizon=1, alpha=1.5)

    def test_invalid_horizon_raises(self):
        with pytest.raises(ValueError):
            simple_exponential_smoothing_forecast(TRAIN, horizon=0)


class TestForecastBySku:
    @pytest.fixture
    def sample_df(self):
        dates = pd.date_range("2023-01-01", periods=30, freq="D")
        rows = []
        for sku in ["A", "B"]:
            for d in dates:
                rows.append({"date": d, "sku_id": sku, "units_sold": float(d.day)})
        return pd.DataFrame(rows)

    def test_returns_dataframe(self, sample_df):
        result = forecast_by_sku(sample_df, "sku_id", "date", "units_sold", horizon=7)
        assert isinstance(result, pd.DataFrame)

    def test_correct_columns(self, sample_df):
        result = forecast_by_sku(sample_df, "sku_id", "date", "units_sold", horizon=7)
        for col in ["sku_id", "date", "y_pred", "method"]:
            assert col in result.columns

    def test_output_row_count(self, sample_df):
        horizon = 5
        result = forecast_by_sku(sample_df, "sku_id", "date", "units_sold", horizon=horizon)
        assert len(result) == 2 * horizon  # 2 SKUs × horizon

    def test_all_methods_run(self, sample_df):
        for method in ("naive", "moving_average", "ses"):
            result = forecast_by_sku(
                sample_df, "sku_id", "date", "units_sold", horizon=3, method=method
            )
            assert not result.empty

    def test_invalid_method_raises(self, sample_df):
        with pytest.raises(ValueError):
            forecast_by_sku(
                sample_df, "sku_id", "date", "units_sold", horizon=3, method="arima"
            )
