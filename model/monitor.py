import asyncio
import time
from web3 import Web3
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()

# Uniswap V3 Factory on Base
V3_FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
FACTORY_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "token0", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "token1", "type": "address"},
            {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"},
            {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"},
            {"indexed": False, "internalType": "address", "name": "pool", "type": "address"}
        ],
        "name": "PoolCreated",
        "type": "event"
    }
]

class BaseMonitor:
    def __init__(self, rpc_url: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.factory = self.w3.eth.contract(address=V3_FACTORY, abi=FACTORY_ABI)
        self.running = False

    async def watch_new_pools(self, callback):
        """
        Polls for new Uniswap V3 PoolCreated events.
        """
        print("🔍 Monitoring Base Network for new pools...")
        last_block = self.w3.eth.block_number
        self.running = True
        
        while self.running:
            try:
                current_block = self.w3.eth.block_number
                if current_block > last_block:
                    # Scan blocks for PoolCreated events
                    events = self.factory.events.PoolCreated.get_logs(from_block=last_block + 1, to_block=current_block)
                    for event in events:
                        token0 = event.args.token0
                        token1 = event.args.token1
                        pool = event.args.pool
                        # We are mainly interested in tokens paired with WETH
                        # (WETH is 0x4200000000000000000000000000000000000006 on Base)
                        weth = "0x4200000000000000000000000000000000000006"
                        new_token = token1 if token0.lower() == weth.lower() else token0
                        
                        await callback(new_token, pool)
                    
                    last_block = current_block
                
                await asyncio.sleep(15) # Poll every 15 seconds
            except Exception as e:
                print(f"❌ Monitor Error: {e}")
                await asyncio.sleep(30)

    def stop(self):
        self.running = False

# Global instance for use in the bot
_monitor = None

def get_monitor():
    global _monitor
    if _monitor is None:
        rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        _monitor = BaseMonitor(rpc)
    return _monitor
