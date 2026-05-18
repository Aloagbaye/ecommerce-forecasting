import pandas as pd
import numpy as np
import pytest
import tempfile
import os

from src.data.loaders import validate_data, load_sales_data


@pytest.fixture
def valid_df():
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "sku_id": ["SKU001"] * 60,
            "units_sold": np.random.randint(0, 100, size=60),
        }
    )


class TestValidateData:
    def test_valid_data_passes(self, valid_df):
        result = validate_data(valid_df)
        assert result["is_valid"] is True
        assert result["issues"] == []

    def test_missing_required_column_detected(self, valid_df):
        df = valid_df.drop(columns=["units_sold"])
        result = validate_data(df)
        assert not result["is_valid"]
        assert any("units_sold" in issue for issue in result["issues"])

    def test_missing_sku_id_detected(self, valid_df):
        df = valid_df.drop(columns=["sku_id"])
        result = validate_data(df)
        assert not result["is_valid"]

    def test_negative_sales_detected(self, valid_df):
        df = valid_df.copy()
        df.loc[0, "units_sold"] = -5
        result = validate_data(df)
        assert not result["is_valid"]
        assert any("Negative" in issue for issue in result["issues"])

    def test_duplicate_date_sku_detected(self, valid_df):
        df = pd.concat([valid_df, valid_df.iloc[:1]], ignore_index=True)
        result = validate_data(df)
        assert not result["is_valid"]
        assert any("Duplicate" in issue for issue in result["issues"])

    def test_short_date_range_flagged(self):
        dates = pd.date_range("2023-01-01", periods=10, freq="D")
        df = pd.DataFrame(
            {
                "date": dates,
                "sku_id": ["SKU001"] * 10,
                "units_sold": [5] * 10,
            }
        )
        result = validate_data(df)
        assert not result["is_valid"]
        assert any("Short date range" in issue for issue in result["issues"])

    def test_returns_shape(self, valid_df):
        result = validate_data(valid_df)
        assert result["shape"] == valid_df.shape

    def test_returns_date_range(self, valid_df):
        result = validate_data(valid_df)
        assert result["date_range"] is not None


class TestLoadSalesData:
    def test_loads_csv_file(self, valid_df):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            valid_df.to_csv(f.name, index=False)
            tmp_path = f.name
        try:
            df = load_sales_data(tmp_path)
            assert len(df) == len(valid_df)
            assert "date" in df.columns
            assert pd.api.types.is_datetime64_any_dtype(df["date"])
        finally:
            os.unlink(tmp_path)

    def test_sorted_by_date_and_sku(self, valid_df):
        shuffled = valid_df.sample(frac=1, random_state=42)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            shuffled.to_csv(f.name, index=False)
            tmp_path = f.name
        try:
            df = load_sales_data(tmp_path)
            assert df["date"].is_monotonic_increasing
        finally:
            os.unlink(tmp_path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_sales_data("nonexistent/path/file.csv")
