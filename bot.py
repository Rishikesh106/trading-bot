"""
Main trading bot runner.

Usage:
    python bot.py

The bot connects to the Binance Spot Testnet, polls for new candlestick
data every minute, runs the SMA crossover strategy, and places market
orders when a signal fires.
"""

from __future__ import annotations

import signal
import sys
import time

from binance.client import Client

from config import Config
from exchange.binance_testnet import BinanceTestnetClient
from strategies.sma_crossover import Signal, SMAStrategy
from utils.logger import setup_logger

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

config = Config()
logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)

_running = True


def _handle_shutdown(signum: int, frame: object) -> None:  # noqa: ARG001
    global _running
    logger.info("Shutdown signal received (%d). Stopping bot…", signum)
    _running = False


# ---------------------------------------------------------------------------
# Bot logic
# ---------------------------------------------------------------------------

def _base_asset(symbol: str) -> str:
    """Return the base asset of a trading pair (e.g. 'BTC' from 'BTCUSDT')."""
    # Common quote assets, longest first so we strip correctly.
    for quote in ("USDT", "BUSD", "BTC", "ETH", "BNB"):
        if symbol.endswith(quote):
            return symbol[: -len(quote)]
    return symbol


def run_bot() -> None:
    """Start and run the trading bot loop until interrupted."""
    config.validate()

    exchange = BinanceTestnetClient(config)
    strategy = SMAStrategy(
        short_period=config.SHORT_MA_PERIOD,
        long_period=config.LONG_MA_PERIOD,
    )

    # We need at least long_period + 1 candles for a crossover check.
    kline_limit = config.LONG_MA_PERIOD + 2
    symbol = config.SYMBOL
    base = _base_asset(symbol)

    logger.info(
        "Bot started | symbol=%s short_ma=%d long_ma=%d qty=%s",
        symbol,
        config.SHORT_MA_PERIOD,
        config.LONG_MA_PERIOD,
        config.TRADE_QUANTITY,
    )

    while _running:
        try:
            # ----------------------------------------------------------------
            # Fetch market data
            # ----------------------------------------------------------------
            klines = exchange.get_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1MINUTE,
                limit=kline_limit,
            )
            current_price = exchange.get_symbol_price(symbol)
            logger.debug("Current price of %s: %.6f", symbol, current_price)

            # ----------------------------------------------------------------
            # Evaluate strategy
            # ----------------------------------------------------------------
            signal = strategy.calculate(klines)

            # ----------------------------------------------------------------
            # Execute orders
            # ----------------------------------------------------------------
            open_orders = exchange.get_open_orders(symbol)

            if signal == Signal.BUY:
                if len(open_orders) < config.MAX_OPEN_ORDERS:
                    exchange.place_market_buy(symbol, config.TRADE_QUANTITY)
                else:
                    logger.warning(
                        "BUY signal skipped: max open orders (%d) reached.",
                        config.MAX_OPEN_ORDERS,
                    )

            elif signal == Signal.SELL:
                base_balance = exchange.get_balance(base)
                if base_balance >= config.TRADE_QUANTITY:
                    exchange.place_market_sell(symbol, config.TRADE_QUANTITY)
                else:
                    logger.warning(
                        "SELL signal skipped: insufficient %s balance (%.6f < %.6f).",
                        base,
                        base_balance,
                        config.TRADE_QUANTITY,
                    )

            else:
                logger.debug("No trade signal — holding.")

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt — stopping bot.")
            break
        except Exception as exc:  # noqa: BLE001
            logger.error("Unexpected error: %s", exc, exc_info=True)

        # Wait for the next candle close (60 seconds).
        if _running:
            logger.debug("Sleeping 60 s until next candle…")
            time.sleep(60)

    logger.info("Bot stopped.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    try:
        run_bot()
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)
