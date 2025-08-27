import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
    "POLY_API_KEY": os.getenv("POLY_API_KEY"),
    "POLY_SECRET": os.getenv("POLY_SECRET"),
    "POLY_PASSPHRASE": os.getenv("POLY_PASSPHRASE"),
    "POLYMARKET_PROXY_ADDRESS": os.getenv("POLYMARKET_PROXY_ADDRESS"),
    "USDC_CONTRACT_ADDRESS": os.getenv("USDC_CONTRACT_ADDRESS", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"),
    "RPC_URL": os.getenv("RPC_URL", "https://polygon-rpc.com"),
    "WSS_URL": os.getenv("WSS_URL", "wss://polygon-mainnet.g.alchemy.com/public"),
    "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
    "TARGET_WALLET": os.getenv("TARGET_WALLET"),
    "FETCH_INTERVAL": float(os.getenv("FETCH_INTERVAL", "1")),
    "TOO_OLD_TIMESTAMP": int(os.getenv("TOO_OLD_TIMESTAMP", "300")),
    "RETRY_LIMIT": int(os.getenv("RETRY_LIMIT", "3")),
    "EXCHANGE_CONTRACT_ADDRESS": os.getenv("EXCHANGE_CONTRACT_ADDRESS", "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"),
}
