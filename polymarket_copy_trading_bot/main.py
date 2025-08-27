import logging
import time
from polymarket_copy_trading_bot.trade_executor import TradeExecutor
from polymarket_copy_trading_bot.trade_monitor import TradeMonitor


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logs/bot.log")
    sh = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)


def main():
    setup_logging()
    logging.info("Starting Polymarket Copy Trading Bot")
    executor = TradeExecutor()
    monitor = TradeMonitor(trade_callback=executor.execute_trade)
    monitor.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down bot")


if __name__ == "__main__":
    main()
