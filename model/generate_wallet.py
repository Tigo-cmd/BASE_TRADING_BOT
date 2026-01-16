from web3 import Web3
import secrets
from dotenv import load_dotenv
import os

load_dotenv()

# Base Network RPC Configuration
BASE_RPC_URL = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')


async def generate_wallet() -> tuple[str, str]:
    """
    Generate a new Base network wallet.
    Returns tuple of (private_key, address)
    """
    w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
    private_key = "0x" + secrets.token_hex(32)
    account = w3.eth.account.from_key(private_key)
    address = account.address
    
    return (private_key, address)