import os
from py_clob_client.client import ClobClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_api_credentials():
    host = "https://clob.polymarket.com"
    private_key = '0xadb29094aeed62269565ed3a1be8e8eb4cbfc93fe727dc609f613d4df2a594a2'  # Your exported private key
    chain_id = 137  # Polygon Mainnet

    if not private_key:
        raise ValueError("PRIVATE_KEY not found in .env")

    # Initialize the client
    client = ClobClient(host, key=private_key, chain_id=chain_id, signature_type=1)  # Use signature_type=2 for browser wallet

    # Generate or derive API credentials
    try:
        api_creds = client.create_or_derive_api_creds()
        print("API Key:", api_creds.api_key)
        print("Secret:", api_creds.api_secret)
        print("Passphrase:", api_creds.api_passphrase)
        return {
            "POLY_API_KEY": api_creds.api_key,
            "POLY_SECRET": api_creds.api_secret,
            "POLY_PASSPHRASE": api_creds.api_passphrase
        }
    except Exception as e:
        print(f"Error generating API credentials: {e}")
        return None

if __name__ == "__main__":
    creds = generate_api_credentials()
    if creds:
        # Update .env file with new credentials
        with open(".env", "a") as f:
            f.write(f"\nPOLY_API_KEY={creds['POLY_API_KEY']}")
            f.write(f"\nPOLY_SECRET={creds['POLY_SECRET']}")
            f.write(f"\nPOLY_PASSPHRASE={creds['POLY_PASSPHRASE']}")
        print("Credentials saved to .env")