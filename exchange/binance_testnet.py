"""
Binance Testnet exchange connector.

Uses the python-binance library pointed at the Binance Spot Testnet
(https://testnet.binance.vision/) so no real funds are ever at risk.
"""

from __future__ import annotations

import time
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from config import Config
from utils.logger import setup_logger


class BinanceTestnetClient:
    """Thin wrapper around :class:`binance.client.Client` for the testnet."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)
        self.client = Client(
            api_key=config.API_KEY,
            api_secret=config.API_SECRET,
            testnet=True,
        )
        self._logger.info("Connected to Binance Spot Testnet.")

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_klines(self, symbol: str, interval: str, limit: int) -> list[list]:
        """Fetch OHLCV candlestick data.

        Args:
            symbol: Trading pair, e.g. ``"BTCUSDT"``.
            interval: Candlestick interval string, e.g. ``Client.KLINE_INTERVAL_1MINUTE``.
            limit: Number of candles to fetch (max 1000).

        Returns:
            List of raw kline lists as returned by the Binance API.
        """
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_symbol_price(self, symbol: str) -> float:
        """Return the current market price for *symbol*."""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_balance(self, asset: str) -> float:
        """Return the free balance of *asset* on the testnet account."""
        account = self.client.get_account()
        for balance in account["balances"]:
            if balance["asset"] == asset:
                return float(balance["free"])
        return 0.0

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def place_market_buy(self, symbol: str, quantity: float) -> Optional[dict]:
        """Place a market BUY order.

        Args:
            symbol: Trading pair.
            quantity: Asset quantity to buy.

        Returns:
            Order response dict on success, ``None`` on failure.
        """
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity,
            )
            self._logger.info(
                "Market BUY placed | symbol=%s qty=%s orderId=%s",
                symbol,
                quantity,
                order.get("orderId"),
            )
            return order
        except (BinanceAPIException, BinanceOrderException) as exc:
            self._logger.error("Failed to place market BUY: %s", exc)
            return None

    def place_market_sell(self, symbol: str, quantity: float) -> Optional[dict]:
        """Place a market SELL order.

        Args:
            symbol: Trading pair.
            quantity: Asset quantity to sell.

        Returns:
            Order response dict on success, ``None`` on failure.
        """
        try:
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity,
            )
            self._logger.info(
                "Market SELL placed | symbol=%s qty=%s orderId=%s",
                symbol,
                quantity,
                order.get("orderId"),
            )
            return order
        except (BinanceAPIException, BinanceOrderException) as exc:
            self._logger.error("Failed to place market SELL: %s", exc)
            return None

    def get_open_orders(self, symbol: str) -> list[dict]:
        """Return all open orders for *symbol*."""
        return self.client.get_open_orders(symbol=symbol)

    def cancel_order(self, symbol: str, order_id: int) -> Optional[dict]:
        """Cancel an open order by ID."""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            self._logger.info("Cancelled order %s for %s", order_id, symbol)
            return result
        except (BinanceAPIException, BinanceOrderException) as exc:
            self._logger.error("Failed to cancel order %s: %s", order_id, exc)
            return None

    def ping(self) -> bool:
        """Return True if the testnet API is reachable."""
        try:
            self.client.ping()
            return True
        except Exception:  # noqa: BLE001
            return False
