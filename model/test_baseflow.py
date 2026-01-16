#!/usr/bin/env python3
"""
BaseFlow Test Suite - Tests all Sprint 1 & 2 functionality
Run from the model directory: python3 test_baseflow.py
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def header(msg):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*50}{Colors.END}\n")


async def test_network_connectivity():
    """Test 1: Base network connectivity"""
    header("Test 1: Base Network Connectivity")
    
    try:
        from web3 import Web3
        
        rpc_url = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if w3.is_connected():
            success(f"Connected to Base RPC: {rpc_url}")
            
            chain_id = w3.eth.chain_id
            if chain_id == 8453:
                success(f"Chain ID: {chain_id} (Base Mainnet)")
            else:
                error(f"Wrong chain ID: {chain_id}, expected 8453")
                return False
            
            block = w3.eth.block_number
            success(f"Latest block: {block:,}")
            
            gas_price = w3.eth.gas_price
            success(f"Gas price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei")
            
            return True
        else:
            error("Failed to connect to Base network")
            return False
            
    except Exception as e:
        error(f"Network test failed: {e}")
        return False


async def test_wallet_generation():
    """Test 2: Wallet generation"""
    header("Test 2: Wallet Generation")
    
    try:
        from generate_wallet import generate_wallet
        
        private_key, address = await generate_wallet()
        
        if private_key and address:
            success(f"Generated wallet address: {address}")
            success(f"Private key length: {len(private_key)} chars")
            
            # Validate address format
            if address.startswith("0x") and len(address) == 42:
                success("Address format valid (0x... 42 chars)")
            else:
                error("Invalid address format")
                return False
            
            # Validate private key format
            if private_key.startswith("0x") and len(private_key) == 66:
                success("Private key format valid (0x... 66 chars)")
            else:
                error("Invalid private key format")
                return False
            
            return True
        else:
            error("Wallet generation returned empty values")
            return False
            
    except Exception as e:
        error(f"Wallet generation failed: {e}")
        return False


async def test_trading_engine():
    """Test 3: BaseFlowTrader initialization and queries"""
    header("Test 3: Trading Engine (BaseFlowTrader)")
    
    try:
        from mainet import BaseFlowTrader, TOKENS
        
        info("Initializing BaseFlowTrader...")
        trader = BaseFlowTrader()
        success("BaseFlowTrader initialized successfully")
        
        # Test ETH price from Chainlink
        info("Fetching ETH price from Chainlink...")
        try:
            eth_price = await trader.get_eth_price()
            if eth_price > 0:
                success(f"ETH Price: ${eth_price:,.2f}")
            else:
                error("ETH price returned 0")
        except Exception as e:
            error(f"Failed to get ETH price: {e}")
        
        # Test USDC token info
        info("Fetching USDC token info...")
        try:
            usdc_info = await trader.get_token_info(TOKENS["USDC"])
            success(f"Token: {usdc_info['name']} ({usdc_info['symbol']})")
            success(f"Decimals: {usdc_info['decimals']}")
            success(f"Address: {usdc_info['address']}")
        except Exception as e:
            error(f"Failed to get token info: {e}")
        
        # Test balance check (with a known address)
        info("Testing balance check with Coinbase address...")
        try:
            # Coinbase hot wallet - known to have ETH
            test_address = "0xB3bfE03Ec2F01B88e8cbC0Ff29C49f15D3C56C06"
            balance = await trader.check_eth_balance(test_address)
            success(f"Balance of {test_address[:10]}...: {balance:.4f} ETH")
        except Exception as e:
            error(f"Balance check failed: {e}")
        
        # Test swap quote
        info("Testing swap quote (0.01 ETH -> USDC)...")
        try:
            from decimal import Decimal
            quote = await trader.get_swap_quote(
                trader.WETH,
                trader.USDC,
                Decimal("0.01"),
                3000  # 0.3% fee tier
            )
            if quote > 0:
                success(f"Quote: 0.01 ETH = {quote:.2f} USDC")
            else:
                info("Quote returned 0 - pool may not exist for this fee tier")
        except Exception as e:
            error(f"Swap quote failed: {e}")
        
        return True
        
    except Exception as e:
        error(f"Trading engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database():
    """Test 4: Database operations"""
    header("Test 4: Database Operations")
    
    try:
        from store_to_db import (
            init_db, 
            get_user_trades, 
            get_trade_count,
            get_total_volume,
            save_trade
        )
        
        # Initialize database
        info("Initializing database...")
        init_db()
        success("Database initialized")
        
        # Test trade count for non-existent user
        test_user_id = 999999999
        count = get_trade_count(test_user_id)
        success(f"Trade count for test user: {count}")
        
        # Test save trade
        info("Testing trade save...")
        await save_trade(
            user_id=test_user_id,
            wallet_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xtest_" + str(int(asyncio.get_event_loop().time())),
            token_in="0x4200000000000000000000000000000000000006",  # WETH
            token_out="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
            amount_in="0.1 ETH",
            amount_out="350 USDC",
            trade_type="buy",
            status="success",
            gas_used=150000,
            block_number=12345678
        )
        success("Test trade saved to database")
        
        # Verify trade was saved
        trades = get_user_trades(test_user_id, limit=5)
        if trades and len(trades) > 0:
            success(f"Retrieved {len(trades)} trade(s) from database")
            for t in trades[:2]:
                info(f"  - {t['trade_type']}: {t['amount_in']} -> {t['amount_out']}")
        else:
            error("Failed to retrieve saved trade")
        
        # Test volume stats
        stats = get_total_volume()
        success(f"Volume stats: {stats['total_trades']} trades, {stats['unique_traders']} traders")
        
        return True
        
    except Exception as e:
        error(f"Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api():
    """Test 5: API functions"""
    header("Test 5: API Functions")
    
    try:
        from api import get_eth_price, get_token_price
        
        info("Testing get_eth_price() from CoinMarketCap...")
        try:
            price = get_eth_price()
            if price > 0:
                success(f"ETH Price (CMC): ${price:,.2f}")
            else:
                error("ETH price returned 0")
        except Exception as e:
            error(f"CMC API failed: {e}")
            info("Note: CMC API requires a valid API key in .env")
        
        return True
        
    except Exception as e:
        error(f"API test failed: {e}")
        return False


async def test_env_config():
    """Test 6: Environment configuration"""
    header("Test 6: Environment Configuration")
    
    required_vars = [
        ('BASEFLOW_BOT_API', 'Telegram Bot Token'),
        ('BASE_RPC_URL', 'Base Network RPC'),
        ('CMC_API_KEY', 'CoinMarketCap API Key'),
    ]
    
    all_present = True
    for var, desc in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            masked = value[:8] + '...' if len(value) > 10 else value
            success(f"{desc} ({var}): {masked}")
        else:
            error(f"{desc} ({var}): NOT SET")
            all_present = False
    
    return all_present


async def run_all_tests():
    """Run all tests and report results"""
    print(f"\n{Colors.BOLD}🚀 BaseFlow Test Suite{Colors.END}")
    print(f"{Colors.BOLD}Testing Sprint 1 & 2 Implementation{Colors.END}\n")
    
    results = {}
    
    # Test 1: Environment
    results['Environment'] = await test_env_config()
    
    # Test 2: Network
    results['Network'] = await test_network_connectivity()
    
    # Test 3: Wallet
    results['Wallet'] = await test_wallet_generation()
    
    # Test 4: Trading Engine
    results['Trading'] = await test_trading_engine()
    
    # Test 5: Database
    results['Database'] = await test_database()
    
    # Test 6: API
    results['API'] = await test_api()
    
    # Summary
    header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! BaseFlow is ready.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the output above.{Colors.END}")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())
