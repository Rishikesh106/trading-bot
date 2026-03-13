"""
Simple Moving Average (SMA) crossover strategy.

Generates a BUY signal when the short-period SMA crosses **above** the
long-period SMA, and a SELL signal when it crosses **below**.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

import pandas as pd

from utils.logger import setup_logger
from config import Config


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SMAStrategy:
    """SMA crossover strategy.

    Args:
        short_period: Lookback window for the fast SMA.
        long_period: Lookback window for the slow SMA.
    """

    def __init__(
        self,
        short_period: int,
        long_period: int,
        config: Optional[Config] = None,
    ) -> None:
        if short_period >= long_period:
            raise ValueError(
                f"short_period ({short_period}) must be less than long_period ({long_period})."
            )
        self.short_period = short_period
        self.long_period = long_period
        self._previous_signal: Signal = Signal.HOLD
        cfg = config or Config()
        self._logger = setup_logger(__name__, cfg.LOG_FILE, cfg.LOG_LEVEL)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(self, klines: list[list]) -> Signal:
        """Compute the current signal from raw kline data.

        Args:
            klines: List of kline lists as returned by the Binance API.
                    Each entry is ``[open_time, open, high, low, close, ...]``.

        Returns:
            :class:`Signal` enum value.
        """
        close_prices = self._extract_close_prices(klines)

        if len(close_prices) < self.long_period:
            self._logger.debug(
                "Not enough data (%d candles) for long SMA (%d).",
                len(close_prices),
                self.long_period,
            )
            return Signal.HOLD

        short_sma = self._sma(close_prices, self.short_period)
        long_sma = self._sma(close_prices, self.long_period)

        self._logger.debug(
            "SMA(%d)=%.6f  SMA(%d)=%.6f  last_close=%.6f",
            self.short_period,
            short_sma.iloc[-1],
            self.long_period,
            long_sma.iloc[-1],
            close_prices.iloc[-1],
        )

        signal = self._crossover_signal(short_sma, long_sma)
        if signal != self._previous_signal:
            self._logger.info(
                "Signal changed: %s → %s", self._previous_signal.value, signal.value
            )
        self._previous_signal = signal
        return signal

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_close_prices(klines: list[list]) -> pd.Series:
        """Return a Series of close prices from raw kline data."""
        closes = [float(k[4]) for k in klines]
        return pd.Series(closes)

    @staticmethod
    def _sma(series: pd.Series, period: int) -> pd.Series:
        """Compute the simple moving average of *series* with window *period*."""
        return series.rolling(window=period).mean()

    @staticmethod
    def _crossover_signal(short_sma: pd.Series, long_sma: pd.Series) -> Signal:
        """Derive a signal from the last two data points of each SMA."""
        if len(short_sma) < 2 or len(long_sma) < 2:
            return Signal.HOLD

        prev_short = short_sma.iloc[-2]
        curr_short = short_sma.iloc[-1]
        prev_long = long_sma.iloc[-2]
        curr_long = long_sma.iloc[-1]

        if pd.isna(prev_short) or pd.isna(curr_short) or pd.isna(prev_long) or pd.isna(curr_long):
            return Signal.HOLD

        # Bullish crossover: short crosses above long
        if prev_short <= prev_long and curr_short > curr_long:
            return Signal.BUY

        # Bearish crossover: short crosses below long
        if prev_short >= prev_long and curr_short < curr_long:
            return Signal.SELL

        return Signal.HOLD
