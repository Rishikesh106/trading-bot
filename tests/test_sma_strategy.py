"""
Tests for the SMA crossover strategy.
"""

import pytest

from strategies.sma_crossover import Signal, SMAStrategy


def _make_klines(close_prices: list[float]) -> list[list]:
    """Build minimal kline lists from a list of close prices."""
    return [
        [0, "0", "0", "0", str(price), "0", 0, "0", 0, "0", "0", "0"]
        for price in close_prices
    ]


class TestSMAStrategyInit:
    def test_valid_periods(self):
        strategy = SMAStrategy(short_period=5, long_period=20)
        assert strategy.short_period == 5
        assert strategy.long_period == 20

    def test_invalid_periods_raise(self):
        with pytest.raises(ValueError):
            SMAStrategy(short_period=20, long_period=5)

    def test_equal_periods_raise(self):
        with pytest.raises(ValueError):
            SMAStrategy(short_period=10, long_period=10)


class TestSMAStrategySignals:
    SHORT = 3
    LONG = 5

    def _strategy(self) -> SMAStrategy:
        return SMAStrategy(short_period=self.SHORT, long_period=self.LONG)

    def test_hold_when_insufficient_data(self):
        strategy = self._strategy()
        # Only 4 prices — not enough for LONG=5
        klines = _make_klines([100.0, 101.0, 102.0, 103.0])
        assert strategy.calculate(klines) == Signal.HOLD

    def test_hold_when_no_crossover(self):
        # Flat prices → SMAs stay equal → no crossover
        strategy = self._strategy()
        prices = [100.0] * 10
        klines = _make_klines(prices)
        assert strategy.calculate(klines) == Signal.HOLD

    def test_buy_signal_on_bullish_crossover(self):
        """Short SMA crosses above long SMA → BUY."""
        strategy = self._strategy()
        # Prices fall then spike sharply at the last candle so that
        # SMA(3) was below SMA(5) at the penultimate point and crosses
        # above it at the final point.
        prices = [100.0, 100.0, 100.0, 90.0, 80.0, 70.0, 200.0]
        klines = _make_klines(prices)
        signal = strategy.calculate(klines)
        assert signal == Signal.BUY

    def test_sell_signal_on_bearish_crossover(self):
        """Short SMA crosses below long SMA → SELL."""
        strategy = self._strategy()
        # Prices rise then crash sharply at the last candle so that
        # SMA(3) was above SMA(5) at the penultimate point and crosses
        # below it at the final point.
        prices = [100.0, 100.0, 100.0, 110.0, 120.0, 130.0, 30.0]
        klines = _make_klines(prices)
        signal = strategy.calculate(klines)
        assert signal == Signal.SELL

    def test_previous_signal_tracked(self):
        strategy = self._strategy()
        prices_hold = [100.0] * 10
        strategy.calculate(_make_klines(prices_hold))
        assert strategy._previous_signal == Signal.HOLD


class TestSMAStrategyHelpers:
    def test_extract_close_prices(self):
        klines = _make_klines([1.0, 2.0, 3.0])
        series = SMAStrategy._extract_close_prices(klines)
        assert list(series) == [1.0, 2.0, 3.0]

    def test_sma_calculation(self):
        import pandas as pd
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = SMAStrategy._sma(series, 3)
        assert result.iloc[-1] == pytest.approx(4.0)

    def test_crossover_signal_returns_hold_for_short_series(self):
        import pandas as pd
        short = pd.Series([1.0])
        long_ = pd.Series([1.0])
        assert SMAStrategy._crossover_signal(short, long_) == Signal.HOLD
