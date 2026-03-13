"""
Tests for bot.py helper utilities (no live API calls).
"""

import pytest

from bot import _base_asset


class TestBaseAsset:
    def test_usdt_pair(self):
        assert _base_asset("BTCUSDT") == "BTC"

    def test_busd_pair(self):
        assert _base_asset("ETHBUSD") == "ETH"

    def test_btc_pair(self):
        assert _base_asset("BNBBTC") == "BNB"

    def test_eth_pair(self):
        assert _base_asset("ADAETH") == "ADA"

    def test_bnb_pair(self):
        assert _base_asset("DOTBNB") == "DOT"

    def test_unknown_quote(self):
        # Falls back to returning the full symbol unchanged
        assert _base_asset("XYZABC") == "XYZABC"
