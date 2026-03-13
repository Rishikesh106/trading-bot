"""
Tests for config.py
"""

import os
import pytest

from config import Config


def _make_config(**overrides) -> Config:
    """Return a Config with valid defaults, optionally overriding fields."""
    cfg = Config()
    cfg.API_KEY = overrides.get("API_KEY", "test_key")
    cfg.API_SECRET = overrides.get("API_SECRET", "test_secret")
    cfg.SHORT_MA_PERIOD = overrides.get("SHORT_MA_PERIOD", 10)
    cfg.LONG_MA_PERIOD = overrides.get("LONG_MA_PERIOD", 30)
    return cfg


class TestConfigValidation:
    def test_valid_config_passes(self):
        cfg = _make_config()
        cfg.validate()  # should not raise

    def test_missing_api_key_raises(self):
        cfg = _make_config(API_KEY="")
        with pytest.raises(ValueError, match="BINANCE_TESTNET_API_KEY"):
            cfg.validate()

    def test_placeholder_api_key_raises(self):
        cfg = _make_config(API_KEY="your_testnet_api_key_here")
        with pytest.raises(ValueError, match="BINANCE_TESTNET_API_KEY"):
            cfg.validate()

    def test_missing_api_secret_raises(self):
        cfg = _make_config(API_SECRET="")
        with pytest.raises(ValueError, match="BINANCE_TESTNET_API_SECRET"):
            cfg.validate()

    def test_short_period_gte_long_period_raises(self):
        cfg = _make_config(SHORT_MA_PERIOD=30, LONG_MA_PERIOD=10)
        with pytest.raises(ValueError, match="SHORT_MA_PERIOD"):
            cfg.validate()

    def test_equal_periods_raises(self):
        cfg = _make_config(SHORT_MA_PERIOD=10, LONG_MA_PERIOD=10)
        with pytest.raises(ValueError, match="SHORT_MA_PERIOD"):
            cfg.validate()
