#!/usr/bin/env python3
"""Quick test script"""
import sys
import asyncio

print("=== BaseFlow Quick Test Suite ===", flush=True)

# Test 1: Database
print("\n[1/4] Testing Database...", flush=True)
try:
    from store_to_db import init_db, get_trade_count
    init_db()
    count = get_trade_count(12345)
    print(f"  ✅ Database OK (trade count: {count})", flush=True)
except Exception as e:
    print(f"  ❌ Database Error: {e}", flush=True)

# Test 2: Wallet
print("\n[2/4] Testing Wallet Generation...", flush=True)
try:
    from generate_wallet import generate_wallet
    async def gen(): return await generate_wallet()
    pk, addr = asyncio.run(gen())
    print(f"  ✅ Wallet OK: {addr[:16]}...", flush=True)
except Exception as e:
    print(f"  ❌ Wallet Error: {e}", flush=True)

# Test 3: Network
print("\n[3/4] Testing Base Network...", flush=True)
try:
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org', request_kwargs={'timeout': 15}))
    connected = w3.is_connected()
    if connected:
        chain_id = w3.eth.chain_id
        block = w3.eth.block_number
        print(f"  ✅ Network OK (Chain: {chain_id}, Block: {block})", flush=True)
    else:
        print("  ❌ Network: Not connected", flush=True)
except Exception as e:
    print(f"  ❌ Network Error: {e}", flush=True)

# Test 4: Trading Engine
print("\n[4/4] Testing Trading Engine...", flush=True)
try:
    from mainet import BaseFlowTrader
    trader = BaseFlowTrader()
    
    async def test_trader():
        balance = await trader.check_eth_balance("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")  # vitalik.eth
        price = await trader.get_eth_price()
        return balance, price
    
    balance, price = asyncio.run(test_trader())
    print(f"  ✅ Trader OK (ETH Price: ${price:,.2f})", flush=True)
except Exception as e:
    print(f"  ❌ Trader Error: {e}", flush=True)

print("\n=== Tests Complete ===", flush=True)
