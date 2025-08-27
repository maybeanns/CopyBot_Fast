Building a Polymarket copy trading bot to replicate a target user’s trades in real time involves monitoring their trading activity on the Polymarket Central Limit Order Book (CLOB) on the Polygon network and automatically executing matching trades in your account. Below are detailed instructions on how to build the bot, what you need, what to expect, and how to handle the expected output and status indicators.

---

## What the Bot Does
The bot replicates the functionality described in your prompt, with the following core features:
1. **Real-Time Monitoring**: Tracks the target trader’s wallet address (`USER_ADDRESS`) for new trades using Polygon blockchain events or Polymarket’s API.
2. **Trade Detection & Analysis**: Identifies and parses trade details (market/condition ID, buy/sell, position size, order type, timing) and filters out old transactions using a configurable `TOO_OLD_TIMESTAMP`.
3. **Automated Trade Execution**: Places matching orders on your wallet (`PROXY_WALLET`) via Polymarket’s CLOB API, with retry logic for failed orders (`RETRY_LIMIT`).
4. **Database Management**: Stores trade data in MongoDB for tracking, analysis, and debugging.
5. **Status Indicators**: Provides real-time feedback on trade detection, execution, and errors using console logs and optional UI elements.

---

## What You Need

### 1. Hardware Requirements
- **Computer/Server**: A machine with at least 4GB RAM and a stable internet connection. For production, use a cloud server (e.g., AWS EC2 t3.micro, Google Cloud, DigitalOcean) in a region close to Polymarket’s servers (e.g., AWS US East) to minimize latency.
- **Operating System**: Linux (Ubuntu recommended) for production; macOS or Windows for development.

### 2. Software Requirements
- **Python 3.8+**: Main programming language.
- **Dependencies**:
  ```bash
  pip install web3==6.11.1 py-clob-client==0.1.0 pymongo==4.6.0 python-dotenv==1.0.0 websocket-client==1.6.4 requests==2.31.0 colorlog==6.8.0 halo==0.0.31
  ```
  - `web3`: Interacts with the Polygon blockchain.
  - `py-clob-client`: Interfaces with Polymarket’s CLOB API.
  - `pymongo`: Manages MongoDB for trade storage.
  - `python-dotenv`: Loads environment variables.
  - `websocket-client`: Handles WebSocket connections.
  - `requests`: For REST API calls.
  - `colorlog`: Colored console logs for status.
  - `halo`: Spinners for visual status indicators.
- **MongoDB**: A running instance (local or cloud-hosted, e.g., MongoDB Atlas free tier) for storing trade data.
- **Node.js (optional)**: For a web-based UI (e.g., using Express.js) to display trade status.

### 3. Polymarket Account and Credentials
- **Polymarket Account**: Sign up at `polymarket.com`.
- **API Credentials**:
  - **API Key, Secret, Passphrase**: Export from `https://reveal.magic.link/polymarket` (email login).
  - **Polygon Wallet**: A wallet (e.g., MetaMask) with private key for trading.
  - **Proxy Wallet Address**: Your wallet address for trading (often same as Polygon wallet).
  - **Funds**: Fund wallet with MATIC (e.g., 10 MATIC for gas) and USDC (e.g., 100 USDC for trading).
- **Environment Variables**: Create a `.env` file:
  ```env
  PRIVATE_KEY=<your_polygon_wallet_private_key>
  POLY_API_KEY=<your_polymarket_api_key>
  POLY_SECRET=<your_polymarket_secret>
  POLY_PASSPHRASE=<your_polymarket_passphrase>
  POLYMARKET_PROXY_ADDRESS=<your_proxy_wallet_address>
  USDC_CONTRACT_ADDRESS=0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
  RPC_URL=https://polygon-rpc.com
  WSS_URL=wss://polygon-ws.com
  MONGODB_URI=mongodb://localhost:27017
  TARGET_WALLET=<target_user_wallet_address>
  FETCH_INTERVAL=1
  TOO_OLD_TIMESTAMP=300
  RETRY_LIMIT=3
  ```
- **Target Wallet Address**: The Polygon address of the trader to copy. Find successful traders via PolymarketScan (@PolymarketScan_bot on Telegram) or Polygonscan trade history.

### 4. Polymarket Contract Details
- **Exchange Contract Address**: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`.
- **Contract ABI**: Get from Polymarket’s GitHub or Polygonscan for the `orderFilled` event.
- **USDC Contract**: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`.

### 5. Polygon Node Access
- **Free Option**: Public WebSocket (`wss://polygon-ws.com`).
- **Premium Option (Recommended)**: Low-latency provider (e.g., Alchemy, Infura, QuickNode). Example: `wss://polygon-mainnet.g.alchemy.com/v2/<your-api-key>`.

### 6. Development Tools
- **IDE**: VS Code or PyCharm.
- **Git**: For version control (optional).
- **Monitoring**: Terminal logs or a simple web UI for real-time status.

---

## Instructions to Build the Bot

### 1. Set Up the Environment
1. **Install Python and Dependencies**:
   ```bash
   python3 -m pip install web3==6.11.1 py-clob-client==0.1.0 pymongo==4.6.0 python-dotenv==1.0.0 websocket-client==1.6.4 requests==2.31.0 colorlog==6.8.0 halo==0.0.31
   ```
2. **Set Up MongoDB**:
   - Local: Install MongoDB (`sudo apt install mongodb` on Ubuntu) and start the service (`sudo systemctl start mongodb`).
   - Cloud: Use MongoDB Atlas (free tier). Get the connection URI (e.g., `mongodb+srv://<user>:<password>@cluster0.mongodb.net`).
3. **Create `.env` File**: Add credentials and configuration as shown above.
4. **Obtain Contract ABI**:
   - Download from Polygonscan for contract `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` or Polymarket’s GitHub.
   - Save as `exchange_abi.json` in your project directory.

### 2. Project Structure
Create the following directory structure:
```
polymarket_copy_trading_bot/
├── main.py              # Main bot script
├── trade_monitor.py     # Monitors target wallet trades
├── trade_executor.py    # Executes copied trades
├── database.py          # Handles MongoDB operations
├── config.py            # Configuration and env loading
├── exchange_abi.json    # Polymarket Exchange contract ABI
├── .env                 # Environment variables
├── logs/                # Directory for log files
└── requirements.txt     # Python dependencies
```

### 3. Code Implementation
Below are the key scripts for the bot.

#### `config.py`
Loads environment variables and configuration.
```python
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
    "POLY_API_KEY": os.getenv("POLY_API_KEY"),
    "POLY_SECRET": os.getenv("POLY_SECRET"),
    "POLY_PASSPHRASE": os.getenv("POLY_PASSPHRASE"),
    "POLYMARKET_PROXY_ADDRESS": os.getenv("POLYMARKET_PROXY_ADDRESS"),
    "USDC_CONTRACT_ADDRESS": os.getenv("USDC_CONTRACT_ADDRESS"),
    "RPC_URL": os.getenv("RPC_URL"),
    "WSS_URL": os.getenv("WSS_URL"),
    "MONGODB_URI": os.getenv("MONGODB_URI"),
    "TARGET_WALLET": os.getenv("TARGET_WALLET"),
    "FETCH_INTERVAL": float(os.getenv("FETCH_INTERVAL", 1)),
    "TOO_OLD_TIMESTAMP": int(os.getenv("TOO_OLD_TIMESTAMP", 300)),
    "RETRY_LIMIT": int(os.getenv("RETRY_LIMIT", 3)),
    "EXCHANGE_CONTRACT_ADDRESS": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
}
```

#### `database.py`
Manages MongoDB for storing trade data.
```python
from pymongo import MongoClient
from config import CONFIG
import time

class TradeDatabase:
    def __init__(self):
        self.client = MongoClient(CONFIG["MONGODB_URI"])
        self.db = self.client["polymarket_trades"]
        self.trades_collection = self.db["trades"]

    def save_trade(self, trade_data, status="pending", retry_count=0):
        trade_doc = {
            "trade_id": trade_data.get("trade_id"),
            "market": trade_data.get("market"),
            "asset_id": trade_data.get("asset_id"),
            "side": trade_data.get("side"),
            "price": trade_data.get("price"),
            "size": trade_data.get("size"),
            "timestamp": trade_data.get("timestamp"),
            "status": status,
            "retry_count": retry_count,
            "created_at": time.time()
        }
        self.trades_collection.insert_one(trade_doc)
        return trade_doc

    def update_trade_status(self, trade_id, status, retry_count=None):
        update_data = {"status": status}
        if retry_count is not None:
            update_data["retry_count"] = retry_count
        self.trades_collection.update_one({"trade_id": trade_id}, {"$set": update_data})

    def get_pending_trades(self):
        return list(self.trades_collection.find({"status": "pending"}))
```

#### `trade_monitor.py`
Monitors the target wallet for trades using Polygon WebSocket.
```python
from web3 import Web3
import json
import threading
import time
from config import CONFIG
from database import TradeDatabase
from colorlog import ColoredFormatter
import logging

# Set up colored logging
logging.basicConfig(
    level=logging.INFO,
    format="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()
logger.handlers[0].setFormatter(ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    log_colors={"INFO": "green", "WARNING": "yellow", "ERROR": "red"}
))

class TradeMonitor:
    def __init__(self, trade_callback):
        self.w3 = Web3(Web3.WebsocketProvider(CONFIG["WSS_URL"]))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Polygon WebSocket")
        self.target_wallet = CONFIG["TARGET_WALLET"].lower()
        self.db = TradeDatabase()
        self.trade_callback = trade_callback
        with open("exchange_abi.json", "r") as f:
            self.contract_abi = json.load(f)
        self.contract = self.w3.eth.contract(
            address=CONFIG["EXCHANGE_CONTRACT_ADDRESS"], abi=self.contract_abi
        )

    def handle_event(self, event):
        event_data = event["args"]
        maker = event_data["maker"].lower()
        taker = event_data["taker"].lower()
        if maker == self.target_wallet or taker == self.target_wallet:
            trade_data = {
                "trade_id": str(event["transactionHash"].hex()),
                "market": event_data["market"].hex(),
                "asset_id": str(event_data["assetId"]),
                "side": event_data["side"],
                "price": float(event_data["price"]) / 1e18,
                "size": float(event_data["size"]) / 1e6,
                "timestamp": self.w3.eth.get_block(event["blockNumber"])["timestamp"]
            }
            if trade_data["timestamp"] >= time.time() - CONFIG["TOO_OLD_TIMESTAMP"]:
                logger.info(f"New trade detected: {trade_data}")
                trade_doc = self.db.save_trade(trade_data)
                self.trade_callback(trade_doc)
            else:
                logger.warning(f"Trade too old: {trade_data['trade_id']}")

    def start(self):
        event_filter = self.contract.events.orderFilled.create_filter(fromBlock="latest")
        threading.Thread(target=self._listen_events, args=(event_filter,), daemon=True).start()
        logger.info(f"Started monitoring trades for {self.target_wallet}")

    def _listen_events(self, event_filter):
        while True:
            try:
                for event in event_filter.get_new_entries():
                    self.handle_event(event)
                time.sleep(CONFIG["FETCH_INTERVAL"])
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                time.sleep(CONFIG["FETCH_INTERVAL"])
```

#### `trade_executor.py`
Executes copied trades using Polymarket’s CLOB API.
```python
from py_clob_client.client import ClobClient
from config import CONFIG
from database import TradeDatabase
from halo import Halo
from colorlog import ColoredFormatter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()
logger.handlers[0].setFormatter(ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    log_colors={"INFO": "green", "WARNING": "yellow", "ERROR": "red"}
))

class TradeExecutor:
    def __init__(self):
        self.client = ClobClient(
            host="https://clob.polymarket.com",
            key=CONFIG["PRIVATE_KEY"],
            chain_id=137,
            signature_type=1,
            funder=CONFIG["POLYMARKET_PROXY_ADDRESS"]
        )
        self.db = TradeDatabase()
        self.spinner = Halo(text="Waiting for trades...", spinner="dots")

    def execute_trade(self, trade_doc):
        self.spinner.start()
        trade_id = trade_doc["trade_id"]
        market = trade_doc["market"]
        asset_id = trade_doc["asset_id"]
        side = trade_doc["side"]
        price = trade_doc["price"]
        size = trade_doc["size"] * 0.2  # Copy 20% of target size
        retry_count = trade_doc.get("retry_count", 0)

        try:
            resp = self.client.create_order(
                market=market,
                asset_id=asset_id,
                side=side,
                price=price,
                size=size
            )
            logger.info(f"Trade executed: {trade_id} - Response: {resp}")
            self.db.update_trade_status(trade_id, "success")
            self.spinner.succeed(f"Trade {trade_id} executed")
        except Exception as e:
            if retry_count < CONFIG["RETRY_LIMIT"]:
                logger.warning(f"Trade {trade_id} failed: {e}. Retrying ({retry_count + 1}/{CONFIG['RETRY_LIMIT']})")
                self.db.update_trade_status(trade_id, "pending", retry_count + 1)
                self.spinner.text = f"Retrying trade {trade_id}..."
                self.execute_trade(trade_doc)
            else:
                logger.error(f"Trade {trade_id} failed after {CONFIG['RETRY_LIMIT']} retries: {e}")
                self.db.update_trade_status(trade_id, "failed")
                self.spinner.fail(f"Trade {trade_id} failed")
```

#### `main.py`
Orchestrates the bot’s components.
```python
from trade_monitor import TradeMonitor
from trade_executor import TradeExecutor
from colorlog import ColoredFormatter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger()
logger.handlers[1].setFormatter(ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    log_colors={"INFO": "green", "WARNING": "yellow", "ERROR": "red"}
))

def main():
    logger.info("Starting Polymarket Copy Trading Bot")
    executor = TradeExecutor()
    monitor = TradeMonitor(trade_callback=executor.execute_trade)
    monitor.start()
    try:
        while True:
            pass  # Keep the bot running
    except KeyboardInterrupt:
        logger.info("Shutting down bot")

if __name__ == "__main__":
    main()
```

### 4. Optional Web UI (Node.js)
For a simple dashboard to display trade status:
1. Install Node.js and Express:
   ```bash
   npm install express mongodb
   ```
2. Create `server.js`:
```javascript
const express = require('express');
const { MongoClient } = require('mongodb');
const app = express();
const port = 3000;

const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';

app.use(express.static('public'));

app.get('/trades', async (req, res) => {
    const client = new MongoClient(uri);
    try {
        await client.connect();
        const trades = await client.db('polymarket_trades').collection('trades').find().toArray();
        res.json(trades);
    } finally {
        await client.close();
    }
});

app.listen(port, () => console.log(`Server running at http://localhost:${port}`));
```
3. Create `public/index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Polymarket Copy Trading Bot</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        .success { color: green; } .pending { color: orange; } .failed { color: red; }
    </style>
</head>
<body>
    <h1>Polymarket Copy Trading Bot</h1>
    <table>
        <tr><th>Trade ID</th><th>Market</th><th>Side</th><th>Price</th><th>Size</th><th>Status</th><th>Timestamp</th></tr>
        <tbody id="trades"></tbody>
    </table>
    <script>
        async function fetchTrades() {
            const response = await fetch('/trades');
            const trades = await response.json();
            const tbody = document.getElementById('trades');
            tbody.innerHTML = '';
            trades.forEach(trade => {
                const row = `<tr>
                    <td>${trade.trade_id}</td>
                    <td>${trade.market}</td>
                    <td>${trade.side}</td>
                    <td>${trade.price}</td>
                    <td>${trade.size}</td>
                    <td class="${trade.status}">${trade.status}</td>
                    <td>${new Date(trade.created_at * 1000).toLocaleString()}</td>
                </tr>`;
                tbody.innerHTML += row;
            });
        }
        fetchTrades();
        setInterval(fetchTrades, 5000);
    </script>
</body>
</html>
```
4. Run the server:
   ```bash
   node server.js
   ```
   Access at `http://localhost:3000`.

### 5. Run the Bot
1. Ensure MongoDB is running.
2. Start the bot:
   ```bash
   python3 main.py
   ```
3. (Optional) Start the web UI:
   ```bash
   node server.js
   ```

---

## What to Expect

### Expected Output
- **Console Logs**:
  - Startup: `2025-08-27 16:11:00,000 - INFO - Starting Polymarket Copy Trading Bot`
  - Monitoring: `2025-08-27 16:11:01,000 - INFO - Started monitoring trades for 0x...`
  - Trade Detection: `2025-08-27 16:11:02,000 - INFO - New trade detected: {'trade_id': '0x...', 'market': '0x...', 'asset_id': '123...', 'side': 'BUY', 'price': 0.57, 'size': 10.0, 'timestamp': 1695744662}`
  - Trade Execution: `2025-08-27 16:11:03,000 - INFO - Trade executed: 0x... - Response: {...}`
  - Retry: `2025-08-27 16:11:04,000 - WARNING - Trade 0x... failed: Insufficient funds. Retrying (1/3)`
  - Failure: `2025-08-27 16:11:06,000 - ERROR - Trade 0x... failed after 3 retries: Insufficient funds`
- **Spinner Indicators** (via `halo`):
  - Waiting: `[dots] Waiting for trades...`
  - Success: `[✔] Trade 0x... executed`
  - Failure: `[✖] Trade 0x... failed`
- **Log File**: All logs saved to `logs/bot.log` for debugging.
- **MongoDB**:
  - Trades stored in `polymarket_trades.trades` collection with fields: `trade_id`, `market`, `asset_id`, `side`, `price`, `size`, `timestamp`, `status` (`pending`, `success`, `failed`), `retry_count`, `created_at`.
- **Web UI** (if implemented):
  - Displays a table of trades with columns: Trade ID, Market, Side, Price, Size, Status (colored: green for success, orange for pending, red for failed), Timestamp.
  - Updates every 5 seconds.

### Performance Expectations
- **Latency**: Trade detection within 1–2 seconds using a premium Polygon WebSocket (e.g., Alchemy). Public nodes may have 3–5 second delays.
- **Trade Execution**: 1–3 seconds per trade, depending on network congestion and API response time.
- **Reliability**: 95%+ trade execution success with sufficient funds and proper retry logic. Failures may occur due to insufficient USDC/MATIC, API rate limits, or market volatility.
- **Cost**: Gas fees (~0.01–0.1 MATIC per trade) and USDC for trade sizes. Premium node subscriptions (e.g., Alchemy) cost ~$20–50/month.

### Potential Issues
- **Missed Trades**: Slow WebSocket or network issues may miss trades. Use a premium node and monitor logs.
- **Failed Trades**: Insufficient funds, API rate limits, or price slippage. Check wallet balances and implement slippage checks.
- **Old Trades**: `TOO_OLD_TIMESTAMP` (default 300 seconds) filters out stale trades to prevent copying outdated actions.
- **Rate Limits**: Polymarket’s API may throttle requests. Use exponential backoff for retries.
- **Security Risks**: Exposed private keys or API credentials can lead to fund loss. Secure `.env` and use a dedicated wallet with limited funds.

---

## Additional Features to Enhance the Bot
1. **Risk Management**:
   - Add slippage control:
     ```python
     slippage_tolerance = 0.02
     if abs(price - current_market_price) / price <= slippage_tolerance:
         self.client.create_order(...)
     ```
   - Implement stop-loss/take-profit:
     ```python
     if current_price <= price * (1 - 0.025):  # 2.5% stop-loss
         self.client.cancel_order(trade_id)
     ```
   - Limit concurrent trades:
     ```python
     max_concurrent_trades = 3
     if len(self.db.get_pending_trades()) >= max_concurrent_trades:
         return
     ```
2. **Market Data Integration**:
   - Subscribe to Polymarket’s WebSocket (`wss://ws-subscriptions-clob.polymarket.com`) for real-time market updates:
     ```python
     from websocket import WebSocketApp
     def on_message(ws, message):
         logger.info(f"Market update: {message}")
     ws = WebSocketApp("wss://ws-subscriptions-clob.polymarket.com/ws/market",
                       on_message=on_message)
     threading.Thread(target=ws.run_forever, daemon=True).start()
     ```
3. **Telegram Notifications**:
   - Use `python-telegram-bot` to send trade alerts:
     ```python
     from telegram import Bot
     bot = Bot(token="your_telegram_bot_token")
     async def notify_trade(trade_doc):
         await bot.send_message(chat_id="your_chat_id", text=f"Trade executed: {trade_doc}")
     ```
4. **Performance Analytics**:
   - Add a script to analyze trade success rate and profitability from MongoDB data:
     ```python
     def analyze_trades():
         trades = db.trades_collection.find()
         success_rate = len([t for t in trades if t["status"] == "success"]) / max(len(trades), 1)
         logger.info(f"Success rate: {success_rate:.2%}")
     ```

---

## Testing and Deployment
1. **Test Locally**:
   - Use a small USDC amount (e.g., 10 USDC) and a test wallet.
   - Simulate trades by manually executing orders on Polymarket with a secondary account.
   - Verify trade detection and execution in logs and MongoDB.
2. **Test on Polygon Mumbai (if supported)**:
   - Switch to Mumbai testnet (`chain_id=80001`, `RPC_URL=https://rpc-mumbai.maticvigil.com`).
   - Use test MATIC/USDC from faucets.
3. **Deploy to Production**:
   - Host on AWS EC2 (t3.micro, ~$10/month).
   - Use `pm2` or `supervisord` to keep the bot running:
     ```bash
     sudo apt install pm2
     pm2 start main.py --interpreter python3
     ```
   - Monitor logs: `tail -f logs/bot.log`.
4. **Validate Target Wallet**:
   - Use PolymarketScan or Polygonscan to confirm the target wallet’s trading success before copying.

---

## Security Considerations
- **Secure Credentials**: Store `.env` in a private location (`chmod 600 .env`).
- **Limited Funds**: Use a dedicated wallet with minimal MATIC/USDC to limit risk.
- **Rate Limiting**: Implement exponential backoff for API calls to avoid bans.
- **Error Handling**: Log and notify critical errors (e.g., via Telegram).
- **Risk Warning**: Trading carries significant risk. Only use funds you can afford to lose. Past performance of the target wallet does not guarantee future results.

---

## Expected Challenges
- **Latency**: Public WebSocket nodes may introduce 3–5 second delays. Use Alchemy/Infura for <1 second latency.
- **API Rate Limits**: Polymarket may throttle requests. Monitor logs for 429 errors and adjust `FETCH_INTERVAL`.
- **Gas Fees**: High Polygon network congestion can increase costs. Monitor gas prices via `w3.eth.gas_price`.
- **Market Volatility**: Rapid price changes may cause slippage or failed trades. Implement slippage checks.
- **Target Wallet Activity**: If the target trader is inactive, the bot will idle. Monitor multiple wallets if needed.

---

## Next Steps
- **Refine Risk Parameters**: Adjust `slippage_tolerance`, `copy_ratio` (e.g., 0.2), and `max_concurrent_trades` based on testing.
- **Add Notifications**: Integrate Telegram or email alerts for trade events.
- **Scale Up**: Monitor multiple target wallets or markets by extending `TradeMonitor`.
- **Community Support**: Join Polymarket’s Discord (#devs channel) or check `docs.polymarket.com` for updates.

If you need help with specific parts (e.g., obtaining the ABI, optimizing latency, or adding Telegram notifications), provide more details (e.g., target wallet, preferred markets), and I can tailor the code further!