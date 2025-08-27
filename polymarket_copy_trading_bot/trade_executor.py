import logging
import time
from polymarket_copy_trading_bot.config import CONFIG
from polymarket_copy_trading_bot.database import TradeDatabase
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

logger = logging.getLogger(__name__)


class TradeExecutor:
    def __init__(self):
        self.db = TradeDatabase()
        try:
            self.client = ClobClient(
                host="https://clob.polymarket.com",
                key=CONFIG.get("PRIVATE_KEY"),
                chain_id=137,
                signature_type=1,
                funder=CONFIG.get("POLYMARKET_PROXY_ADDRESS")
            )
            self.client.set_api_creds(self.client.create_or_derive_api_creds())
        except Exception:
            logger.warning("py-clob-client not available or failed to init; trades will be logged but not sent")
            self.client = None

    def execute_trade(self, trade_doc):
        trade_id = trade_doc.get("trade_id")
        asset_id = trade_doc.get("asset_id")
        side = trade_doc.get("side")
        price = trade_doc.get("price")
        size = trade_doc.get("size") * 0.2 if trade_doc.get("size") else 0

        side_constant = BUY if side.lower() == "buy" else SELL

        for attempt in range(CONFIG.get("RETRY_LIMIT", 3) + 1):
            try:
                if not self.client:
                    # simulate execution
                    logger.info(f"Simulated execution of {trade_id}: {side} {size}@{price} on asset {asset_id}")
                    self.db.update_trade_status(trade_id, "success")
                    return {"status": "simulated", "trade_id": trade_id}

                # # Balance Validation (placeholder)
                # if side_constant == BUY:
                #     balance = self.client.get_balance()
                #     if balance['usdc'] < size * price:
                #         raise ValueError("Insufficient USDC")

                # # Allowance check (placeholder)
                # if self.client.get_usdc_allowance() < size * price:
                #     self.client.approve_usdc()

                order_args = OrderArgs(price=price, size=size, side=side_constant, token_id=asset_id)
                signed_order = self.client.create_order(order_args)
                resp = self.client.post_order(signed_order, OrderType.GTC)

                logger.info(f"Trade executed: {trade_id} - Response: {resp}")
                self.db.update_trade_status(trade_id, "success")
                return resp
            except Exception as e:
                if attempt < CONFIG.get("RETRY_LIMIT", 3):
                    logger.warning(f"Retry {attempt + 1}: {e}")
                    time.sleep(1)
                else:
                    logger.error(f"Trade {trade_id} failed after {CONFIG.get('RETRY_LIMIT')} retries: {e}")
                    self.db.update_trade_status(trade_id, "failed")
                    return {"status": "failed", "error": str(e)}