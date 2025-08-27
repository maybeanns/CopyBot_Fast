import json
import threading
import time
import logging
from web3 import Web3
from polymarket_copy_trading_bot.config import CONFIG
from polymarket_copy_trading_bot.database import TradeDatabase

logger = logging.getLogger(__name__)


class TradeMonitor:
    def __init__(self, trade_callback):
        self.w3 = Web3(Web3.LegacyWebSocketProvider(CONFIG["WSS_URL"]))
        if not self.w3.is_connected():
            logger.warning("Failed to connect to Polygon WebSocket; TradeMonitor will not listen to real events.")
        self.target_wallet = (CONFIG.get("TARGET_WALLET") or "").lower()
        self.db = TradeDatabase()
        self.trade_callback = trade_callback
        # load ABI if present
        try:
            with open("exchange_abi.json", "r") as f:
                self.contract_abi = json.load(f)
            self.contract = self.w3.eth.contract(address=CONFIG["EXCHANGE_CONTRACT_ADDRESS"], abi=self.contract_abi)
        except Exception:
            self.contract = None

    def handle_event(self, event):
        try:
            args = event["args"]
            maker = args["maker"].lower()
            taker = args["taker"].lower()
            if maker != self.target_wallet and taker != self.target_wallet:
                return

            is_maker = (maker == self.target_wallet)
            maker_asset_id = args["makerAssetId"]
            taker_asset_id = args["takerAssetId"]
            maker_amt = float(args["makerAmountFilled"])
            taker_amt = float(args["takerAmountFilled"])

            # Determine side from target's perspective
            if is_maker:
                side = "buy" if maker_asset_id == 0 else "sell"
                token_amt = taker_amt if side == "buy" else maker_amt
                usdc_amt = maker_amt if side == "buy" else taker_amt
            else:  # target is taker
                side = "buy" if taker_asset_id == 0 else "sell"
                token_amt = maker_amt if side == "buy" else taker_amt
                usdc_amt = taker_amt if side == "buy" else maker_amt

            price = (usdc_amt / token_amt) if token_amt > 0 else 0
            size = token_amt / 1e6
            asset_id = str(maker_asset_id if maker_asset_id != 0 else taker_asset_id)

            # Market: TODO - Resolve via CTF contract call, e.g., get conditionId from positionId
            # For now, placeholder or skip if not needed
            market = "unknown"  # Implement proper resolution

            trade_data = {
                "trade_id": event["transactionHash"].hex(),
                "market": market,
                "asset_id": asset_id,
                "side": side,
                "price": price,
                "size": size,
                "timestamp": self.w3.eth.get_block(event["blockNumber"])["timestamp"]
            }
            if trade_data["timestamp"] >= time.time() - CONFIG["TOO_OLD_TIMESTAMP"]:
                logger.info(f"New trade detected: {trade_data}")
                trade_doc = self.db.save_trade(trade_data)
                self.trade_callback(trade_doc)
            else:
                logger.warning(f"Trade too old: {trade_data['trade_id']}")
        except Exception as e:
            logger.error(f"Error handling event: {e}")

    def start(self):
        if not self.contract:
            logger.info("No contract ABI available; start() will run a dummy poll loop for testing.")
            threading.Thread(target=self._dummy_loop, daemon=True).start()
            return
        try:
            event_filter = self.contract.events.orderFilled.create_filter(fromBlock='latest')
            threading.Thread(target=self._listen_events, args=(event_filter,), daemon=True).start()
            logger.info(f"Started monitoring trades for {self.target_wallet}")
        except Exception as e:
            logger.error(f"Failed to start event listener: {e}")

    def _listen_events(self, event_filter):
        while True:
            try:
                for event in event_filter.get_new_entries():
                    self.handle_event(event)
                time.sleep(CONFIG["FETCH_INTERVAL"])
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                time.sleep(CONFIG["FETCH_INTERVAL"])

    def _dummy_loop(self):
        # For local testing when no websocket/ABI available
        while True:
            time.sleep(CONFIG["FETCH_INTERVAL"])
