# trading-bot

[![CI](https://github.com/Rishikesh106/trading-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/Rishikesh106/trading-bot/actions/workflows/ci.yml)

A Python-based cryptocurrency trading bot for the **Binance Spot Testnet**. It implements a Simple Moving Average (SMA) crossover strategy and places market orders automatically — no real funds are ever at risk.

---

## Features

- 🔗 Connects to the [Binance Spot Testnet](https://testnet.binance.vision/)
- 📈 SMA crossover strategy (configurable short / long periods)
- 🛡 Risk management: max open orders, configurable trade quantity
- 📝 Structured logging to console and file
- ✅ Unit-tested core logic

---

## Project structure

```
trading-bot/
├── bot.py                   # Main entry point
├── config.py                # Configuration loader
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── exchange/
│   └── binance_testnet.py   # Binance Testnet API wrapper
├── strategies/
│   └── sma_crossover.py     # SMA crossover strategy
├── utils/
│   └── logger.py            # Logging setup
└── tests/
    ├── test_bot.py
    ├── test_config.py
    └── test_sma_strategy.py
```

---

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/Rishikesh106/trading-bot.git
cd trading-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your [Binance Testnet](https://testnet.binance.vision/) API key and secret:

```env
BINANCE_TESTNET_API_KEY=<your_key>
BINANCE_TESTNET_API_SECRET=<your_secret>
```

All other settings are optional — sensible defaults are provided.

### 4. Run the bot

```bash
python bot.py
```

The bot polls for a new 1-minute candle every 60 seconds and places market orders when the SMA crossover fires.

---

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `BINANCE_TESTNET_API_KEY` | *(required)* | Testnet API key |
| `BINANCE_TESTNET_API_SECRET` | *(required)* | Testnet API secret |
| `SYMBOL` | `BTCUSDT` | Trading pair |
| `TRADE_QUANTITY` | `0.001` | Order size in base asset |
| `SHORT_MA_PERIOD` | `10` | Fast SMA period (candles) |
| `LONG_MA_PERIOD` | `30` | Slow SMA period (candles) |
| `MAX_OPEN_ORDERS` | `3` | Max concurrent open orders |
| `STOP_LOSS_PCT` | `0.02` | Stop-loss percentage (informational) |
| `TAKE_PROFIT_PCT` | `0.04` | Take-profit percentage (informational) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`/`INFO`/`WARNING`/`ERROR`) |
| `LOG_FILE` | `trading_bot.log` | Log file path |

---

## Strategy

The bot uses a **Simple Moving Average (SMA) crossover** strategy:

- **BUY** — short SMA crosses *above* long SMA (bullish crossover)
- **SELL** — short SMA crosses *below* long SMA (bearish crossover)
- **HOLD** — no crossover detected

---

## Running tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

---

## Disclaimer

This bot is intended **for educational purposes only** and operates exclusively on the Binance Testnet. It does not use real funds. Always backtest and paper-trade any strategy before deploying with real capital.
