"""
Configuration loader for the trading bot.
Reads settings from environment variables / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Binance Testnet credentials
    API_KEY: str = os.getenv("BINANCE_TESTNET_API_KEY", "")
    API_SECRET: str = os.getenv("BINANCE_TESTNET_API_SECRET", "")

    # Trading parameters
    SYMBOL: str = os.getenv("SYMBOL", "BTCUSDT")
    TRADE_QUANTITY: float = float(os.getenv("TRADE_QUANTITY", "0.001"))

    # Strategy parameters
    SHORT_MA_PERIOD: int = int(os.getenv("SHORT_MA_PERIOD", "10"))
    LONG_MA_PERIOD: int = int(os.getenv("LONG_MA_PERIOD", "30"))

    # Risk management
    MAX_OPEN_ORDERS: int = int(os.getenv("MAX_OPEN_ORDERS", "3"))
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "0.02"))
    TAKE_PROFIT_PCT: float = float(os.getenv("TAKE_PROFIT_PCT", "0.04"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "trading_bot.log")

    # Binance Testnet base URLs
    TESTNET_BASE_URL: str = "https://testnet.binance.vision"
    TESTNET_WS_URL: str = "wss://testnet.binance.vision/ws"

    def validate(self) -> None:
        """Raise ValueError if required settings are missing."""
        if not self.API_KEY or self.API_KEY == "your_testnet_api_key_here":
            raise ValueError(
                "BINANCE_TESTNET_API_KEY is not set. "
                "Copy .env.example to .env and fill in your credentials."
            )
        if not self.API_SECRET or self.API_SECRET == "your_testnet_api_secret_here":
            raise ValueError(
                "BINANCE_TESTNET_API_SECRET is not set. "
                "Copy .env.example to .env and fill in your credentials."
            )
        if self.SHORT_MA_PERIOD >= self.LONG_MA_PERIOD:
            raise ValueError(
                f"SHORT_MA_PERIOD ({self.SHORT_MA_PERIOD}) must be less than "
                f"LONG_MA_PERIOD ({self.LONG_MA_PERIOD})."
            )
