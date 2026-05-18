import pandas as pd
import numpy as np
import pytest

from src.features.engineering import (
    create_temporal_features,
    create_rolling_features,
    create_promotion_features,
    create_price_features,
    create_interaction_features,
)


@pytest.fixture
def base_df():
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    np.random.seed(0)
    return pd.DataFrame(
        {
            "date": dates,
            "sku_id": "SKU001",
            "units_sold": np.random.randint(5, 50, size=30).astype(float),
            "price": np.random.uniform(10, 100, size=30),
            "promotion_flag": np.random.choice([True, False], size=30),
        }
    )


class TestTemporalFeatures:
    def test_adds_expected_columns(self, base_df):
        result = create_temporal_features(base_df)
        for col in ["year", "month", "day_of_week", "is_weekend", "month_sin", "month_cos"]:
            assert col in result.columns

    def test_does_not_mutate_input(self, base_df):
        original_cols = set(base_df.columns)
        create_temporal_features(base_df)
        assert set(base_df.columns) == original_cols

    def test_is_weekend_correct(self, base_df):
        result = create_temporal_features(base_df)
        # Jan 1 2023 is Sunday (dayofweek=6 → weekend)
        assert result.iloc[0]["is_weekend"] == 1
        # Jan 2 2023 is Monday (dayofweek=0 → weekday)
        assert result.iloc[1]["is_weekend"] == 0

    def test_missing_date_column_raises(self, base_df):
        with pytest.raises(ValueError):
            create_temporal_features(base_df, date_col="nonexistent")

    def test_cyclical_encoding_range(self, base_df):
        result = create_temporal_features(base_df)
        assert result["day_of_week_sin"].between(-1, 1).all()
        assert result["month_cos"].between(-1, 1).all()


class TestRollingFeatures:
    def test_adds_rolling_columns(self, base_df):
        result = create_rolling_features(base_df, windows=[7], functions=["mean"])
        assert "rolling_mean_7" in result.columns

    def test_no_nans_with_min_periods(self, base_df):
        result = create_rolling_features(base_df, windows=[7], functions=["mean", "std"])
        # min_periods=1 means no NaN for mean; std may have NaN for first row only
        assert result["rolling_mean_7"].isna().sum() == 0

    def test_does_not_mutate_input(self, base_df):
        cols_before = list(base_df.columns)
        create_rolling_features(base_df, windows=[7], functions=["mean"])
        assert list(base_df.columns) == cols_before

    def test_multiple_windows(self, base_df):
        result = create_rolling_features(base_df, windows=[7, 14], functions=["mean"])
        assert "rolling_mean_7" in result.columns
        assert "rolling_mean_14" in result.columns


class TestPromotionFeatures:
    def test_adds_promo_columns(self, base_df):
        result = create_promotion_features(base_df, windows=[7])
        assert "promo_last_7_days" in result.columns
        assert "days_since_last_promo" in result.columns

    def test_no_promo_column_returns_unchanged(self, base_df):
        df_no_promo = base_df.drop(columns=["promotion_flag"])
        result = create_promotion_features(df_no_promo)
        assert "promo_last_7_days" not in result.columns

    def test_days_since_promo_non_negative(self, base_df):
        result = create_promotion_features(base_df, windows=[7])
        # After fillna(999), all values should be >= 0
        assert (result["days_since_last_promo"] >= 0).all()


class TestPriceFeatures:
    def test_adds_price_columns(self, base_df):
        result = create_price_features(base_df, windows=[7])
        assert "price_change_pct" in result.columns
        assert "price_rolling_mean_7" in result.columns

    def test_no_price_column_returns_unchanged(self, base_df):
        df_no_price = base_df.drop(columns=["price"])
        result = create_price_features(df_no_price)
        assert "price_change_pct" not in result.columns

    def test_relative_price_around_one(self, base_df):
        # price / rolling_mean should be close to 1 for stable prices
        df_stable = base_df.copy()
        df_stable["price"] = 50.0
        result = create_price_features(df_stable, windows=[7])
        assert result["price_relative_to_avg_7"].between(0.99, 1.01).all()


class TestInteractionFeatures:
    def test_creates_interaction_columns(self, base_df):
        df_with_temporal = create_temporal_features(base_df)
        result = create_interaction_features(df_with_temporal)
        assert "month_day_interaction" in result.columns
        assert "holiday_weekend" in result.columns

    def test_peak_period_binary(self, base_df):
        df_with_temporal = create_temporal_features(base_df)
        result = create_interaction_features(df_with_temporal)
        assert set(result["is_peak_period"].unique()).issubset({0, 1})
