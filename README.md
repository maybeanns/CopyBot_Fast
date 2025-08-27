Polymarket Copy Trading Bot

This repo contains a minimal starter implementation of a Polymarket copy trading bot.

Files created:
- polymarket_copy_trading_bot/config.py - loads environment variables
- polymarket_copy_trading_bot/database.py - MongoDB wrapper (falls back to in-memory)
- polymarket_copy_trading_bot/trade_monitor.py - listens for orderFilled events (or dummy loop)
- polymarket_copy_trading_bot/trade_executor.py - executes (or simulates) orders
- polymarket_copy_trading_bot/main.py - runner to start the bot
- requirements.txt - Python dependencies to install

Quick start (Windows PowerShell):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Create a `.env` file with the required variables. See `howto.md` for a sample.

3. Run the bot:

```powershell
python -m polymarket_copy_trading_bot.main
```

Notes:
- This starter is deliberately defensive: if Web3, MongoDB or the clob client are missing, it will still run in a simulated mode for local testing.
- Before connecting real funds, review and audit the code.
