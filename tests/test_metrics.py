import numpy as np
import pytest

from src.evaluation.metrics import mae, rmse, wape, smape


PERFECT = ([10, 20, 30], [10, 20, 30])
SIMPLE = ([10, 20, 30], [12, 18, 33])


class TestMAE:
    def test_perfect_forecast(self):
        assert mae(*PERFECT) == pytest.approx(0.0)

    def test_known_value(self):
        # |10-12| + |20-18| + |30-33| = 2 + 2 + 3 = 7  → mean = 7/3
        assert mae(*SIMPLE) == pytest.approx(7 / 3)

    def test_single_element(self):
        assert mae([5], [3]) == pytest.approx(2.0)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            mae([1, 2], [1])

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            mae([], [])


class TestRMSE:
    def test_perfect_forecast(self):
        assert rmse(*PERFECT) == pytest.approx(0.0)

    def test_known_value(self):
        # (4 + 4 + 9) / 3 = 17/3 → sqrt(17/3)
        assert rmse(*SIMPLE) == pytest.approx(np.sqrt(17 / 3))

    def test_rmse_ge_mae(self):
        y_true = [1, 5, 10, 2]
        y_pred = [2, 3, 15, 2]
        assert rmse(y_true, y_pred) >= mae(y_true, y_pred)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            rmse([1, 2], [1])


class TestWAPE:
    def test_perfect_forecast(self):
        assert wape(*PERFECT) == pytest.approx(0.0, abs=1e-9)

    def test_bounded(self):
        # WAPE should be in [0, ~2] for reasonable forecasts
        val = wape(*SIMPLE)
        assert val >= 0

    def test_all_zeros_actuals(self):
        # When actuals are zero the eps prevents division by zero
        val = wape([0, 0, 0], [1, 2, 3])
        assert np.isfinite(val)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            wape([1, 2], [1])


class TestSMAPE:
    def test_perfect_forecast(self):
        assert smape(*PERFECT) == pytest.approx(0.0, abs=1e-9)

    def test_bounded(self):
        # sMAPE ∈ [0, 2]
        val = smape(*SIMPLE)
        assert 0 <= val <= 2

    def test_symmetric(self):
        # sMAPE(y, yhat) == sMAPE(yhat, y)
        a, b = [10, 20], [15, 25]
        assert smape(a, b) == pytest.approx(smape(b, a))

    def test_zero_actuals_and_preds(self):
        val = smape([0, 0], [0, 0])
        assert val == pytest.approx(0.0, abs=1e-6)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            smape([1, 2], [1])
