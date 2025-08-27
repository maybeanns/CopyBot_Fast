import time
from typing import Optional
from pymongo import MongoClient, errors
from polymarket_copy_trading_bot.config import CONFIG
import logging

logger = logging.getLogger(__name__)


class TradeDatabase:
    def __init__(self):
        uri = CONFIG.get("MONGODB_URI")
        self.client: Optional[MongoClient] = None
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            # trigger server selection to detect missing DB
            self.client.server_info()
            self.db = self.client["polymarket_trades"]
            self.trades_collection = self.db["trades"]
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB at {uri}: {e}. Falling back to in-memory store.")
            self.client = None
            self._in_memory = []

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
        if self.client:
            self.trades_collection.insert_one(trade_doc)
        else:
            self._in_memory.append(trade_doc)
        return trade_doc

    def update_trade_status(self, trade_id, status, retry_count=None):
        update_data = {"status": status}
        if retry_count is not None:
            update_data["retry_count"] = retry_count
        if self.client:
            self.trades_collection.update_one({"trade_id": trade_id}, {"$set": update_data})
        else:
            for t in self._in_memory:
                if t.get("trade_id") == trade_id:
                    t.update(update_data)
                    break

    def get_pending_trades(self):
        if self.client:
            return list(self.trades_collection.find({"status": "pending"}))
        else:
            return [t for t in self._in_memory if t.get("status") == "pending"]
