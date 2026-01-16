from web3 import Web3
import json
import time
from decimal import Decimal
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import asyncio

load_dotenv()

# Base Network Configuration
BASE_RPC_URL = os.getenv('BASE_RPC_URL', 'https://mainnet.base.org')
BASE_CHAIN_ID = int(os.getenv('BASE_CHAIN_ID', '8453'))

# Uniswap V3 SwapRouter02 on Base
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"

# Uniswap V3 Quoter V2 on Base
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"

# Common token addresses on Base
TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "USDbC": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    "cbETH": "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
}

# Uniswap V3 pool fees
POOL_FEES = {
    "LOW": 500,      # 0.05%
    "MEDIUM": 3000,  # 0.3%
    "HIGH": 10000,   # 1%
}

# Minimal Uniswap V3 SwapRouter ABI for exactInputSingle
SWAP_ROUTER_ABI = json.loads('''[
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "recipient", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "deadline", "type": "uint256"},
            {"name": "data", "type": "bytes[]"}
        ],
        "name": "multicall",
        "outputs": [{"name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    }
]''')

# Minimal Quoter V2 ABI
QUOTER_ABI = json.loads('''[
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "fee", "type": "uint24"},
                    {"name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"name": "amountOut", "type": "uint256"},
            {"name": "sqrtPriceX96After", "type": "uint160"},
            {"name": "initializedTicksCrossed", "type": "uint32"},
            {"name": "gasEstimate", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]''')

# ERC20 ABI
ERC20_ABI = json.loads('''[
    {"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
    {"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},
    {"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},
    {"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}
]''')


class BaseFlowTrader:
    """
    BaseFlow Trading Engine for Base Network
    Handles token swaps via Uniswap V3, balance checks, and transaction execution.
    """
    
    def __init__(self):
        # Connect to Base network
        self.w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Base network")
        
        # Verify chain ID
        chain_id = self.w3.eth.chain_id
        if chain_id != BASE_CHAIN_ID:
            raise ValueError(f"Connected to wrong chain. Expected {BASE_CHAIN_ID}, got {chain_id}")
        
        # Initialize contract addresses
        self.WETH = Web3.to_checksum_address(TOKENS["WETH"])
        self.USDC = Web3.to_checksum_address(TOKENS["USDC"])
        
        # Initialize Uniswap V3 contracts
        self.swap_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V3_ROUTER),
            abi=SWAP_ROUTER_ABI
        )
        self.quoter = self.w3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V3_QUOTER),
            abi=QUOTER_ABI
        )
        
        print(f"✅ BaseFlowTrader initialized on Base (Chain ID: {chain_id})")
    
    # ============ Balance Functions ============
    
    async def check_eth_balance(self, address: str) -> Decimal:
        """Check native ETH balance for a given address on Base."""
        try:
            address = Web3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(address)
            balance = Decimal(balance_wei) / Decimal(10 ** 18)
            return balance
        except Exception as e:
            raise Exception(f"Failed to check ETH balance: {str(e)}")
    
    async def check_token_balance(self, token_address: str, wallet_address: str) -> Decimal:
        """Check ERC20 token balance for a given address."""
        try:
            token_address = Web3.to_checksum_address(token_address)
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            balance_wei = token_contract.functions.balanceOf(wallet_address).call()
            decimals = token_contract.functions.decimals().call()
            balance = Decimal(balance_wei) / Decimal(10 ** decimals)
            
            return balance
        except Exception as e:
            raise Exception(f"Failed to check token balance: {str(e)}")
    
    async def check_allowance(self, token_address: str, owner_address: str, spender_address: str = None) -> Decimal:
        """Check if tokens are approved for trading."""
        try:
            if spender_address is None:
                spender_address = UNISWAP_V3_ROUTER
                
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            
            allowance = token_contract.functions.allowance(
                Web3.to_checksum_address(owner_address),
                Web3.to_checksum_address(spender_address)
            ).call()
            
            decimals = token_contract.functions.decimals().call()
            return Decimal(allowance) / Decimal(10 ** decimals)
        except Exception as e:
            raise Exception(f"Failed to check allowance: {str(e)}")
    
    # ============ Token Info Functions ============
    
    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Fetch and analyze token information from the blockchain."""
        try:
            token_address = Web3.to_checksum_address(token_address)
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            # Fetch basic token details
            try:
                symbol = token_contract.functions.symbol().call()
            except:
                symbol = "UNKNOWN"
            
            try:
                name = token_contract.functions.name().call()
            except:
                name = "Unknown Token"
            
            try:
                decimals = token_contract.functions.decimals().call()
            except:
                decimals = 18
            
            try:
                total_supply = token_contract.functions.totalSupply().call()
                total_supply_formatted = Decimal(total_supply) / Decimal(10 ** decimals)
            except:
                total_supply_formatted = 0
            
            # Get quote for 1 ETH -> Token (to calculate price)
            eth_price = await self.get_eth_price()
            token_price = 0.0
            eth_ratio = 0.0
            
            try:
                quote = await self.get_swap_quote(
                    self.WETH, 
                    token_address, 
                    Decimal("0.1"),  # Quote for 0.1 ETH
                    POOL_FEES["MEDIUM"]
                )
                if quote > 0:
                    eth_ratio = float(quote) / 0.1  # Tokens per ETH
                    token_price = eth_price / eth_ratio if eth_ratio > 0 else 0
            except:
                pass
            
            market_cap = float(total_supply_formatted) * token_price
            
            return {
                "name": name,
                "symbol": symbol,
                "address": token_address,
                "decimals": decimals,
                "total_supply": float(total_supply_formatted),
                "launch_date": "N/A",
                "exchange": "Uniswap V3 on Base",
                "market_cap": market_cap,
                "liquidity": 0.0,  # Would need to query pool
                "price": token_price,
                "pooled_eth": 0.0,  # Would need to query pool
                "renounced": await self.check_contract_renounced(token_address),
                "frozen": False,
                "revoked": False,
                "eth_ratio": eth_ratio,
                "price_impact": 0.0,
                "website": "N/A",
                "documentation": "N/A"
            }
        except Exception as e:
            raise Exception(f"Failed to fetch token info: {str(e)}")
    
    # ============ Quote Functions ============
    
    async def get_swap_quote(
        self, 
        token_in: str, 
        token_out: str, 
        amount_in: Decimal,
        fee: int = 3000
    ) -> Decimal:
        """Get quote for a swap without executing it."""
        try:
            token_in = Web3.to_checksum_address(token_in)
            token_out = Web3.to_checksum_address(token_out)
            
            # Get token decimals
            if token_in.lower() == self.WETH.lower():
                decimals_in = 18
            else:
                contract = self.w3.eth.contract(address=token_in, abi=ERC20_ABI)
                decimals_in = contract.functions.decimals().call()
            
            if token_out.lower() == self.WETH.lower():
                decimals_out = 18
            else:
                contract = self.w3.eth.contract(address=token_out, abi=ERC20_ABI)
                decimals_out = contract.functions.decimals().call()
            
            amount_in_wei = int(amount_in * Decimal(10 ** decimals_in))
            
            # Call quoter (this is a static call, no gas needed)
            quote_params = (token_in, token_out, amount_in_wei, fee, 0)
            
            result = self.quoter.functions.quoteExactInputSingle(quote_params).call()
            amount_out_wei = result[0]
            
            return Decimal(amount_out_wei) / Decimal(10 ** decimals_out)
        except Exception as e:
            # Pool might not exist for this fee tier
            return Decimal(0)
    
    # ============ Swap Functions ============
    
    async def approve_tokens(
        self, 
        token_address: str, 
        wallet_address: str, 
        private_key: str, 
        amount: Decimal
    ) -> str:
        """Approve tokens for trading on Uniswap V3."""
        try:
            token_address = Web3.to_checksum_address(token_address)
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(amount * Decimal(10 ** decimals))
            
            # Build approval transaction
            tx = token_contract.functions.approve(
                Web3.to_checksum_address(UNISWAP_V3_ROUTER),
                amount_wei
            ).build_transaction({
                "from": wallet_address,
                "nonce": self.w3.eth.get_transaction_count(wallet_address),
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": BASE_CHAIN_ID,
            })
            
            # Sign and send transaction
            signed = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            return tx_hash.hex()
        except Exception as e:
            raise Exception(f"Failed to approve tokens: {str(e)}")
    
    async def swap_eth_for_tokens(
        self,
        token_out: str,
        wallet_address: str,
        private_key: str,
        amount_eth: Decimal,
        slippage_percent: Decimal = Decimal("0.5"),
        fee: int = 3000
    ) -> Dict[str, Any]:
        """
        Swap ETH for tokens using Uniswap V3 on Base.
        
        Args:
            token_out: Address of token to receive
            wallet_address: User's wallet address
            private_key: User's private key
            amount_eth: Amount of ETH to swap
            slippage_percent: Maximum slippage (default 0.5%)
            fee: Pool fee tier (500, 3000, or 10000)
        
        Returns:
            Dict with tx_hash, amount_in, amount_out
        """
        try:
            token_out = Web3.to_checksum_address(token_out)
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            # Check ETH balance
            balance = await self.check_eth_balance(wallet_address)
            if balance < amount_eth:
                raise Exception(f"Insufficient ETH. Have: {balance}, Need: {amount_eth}")
            
            amount_in_wei = Web3.to_wei(amount_eth, 'ether')
            
            # Get quote for minimum output
            quote = await self.get_swap_quote(self.WETH, token_out, amount_eth, fee)
            if quote <= 0:
                raise Exception("Could not get swap quote. Pool may not exist.")
            
            # Apply slippage
            min_out = quote * (Decimal(1) - slippage_percent / Decimal(100))
            token_contract = self.w3.eth.contract(address=token_out, abi=ERC20_ABI)
            decimals_out = token_contract.functions.decimals().call()
            min_out_wei = int(min_out * Decimal(10 ** decimals_out))
            
            # Build swap params
            deadline = int(time.time()) + 300  # 5 minutes
            
            swap_params = (
                self.WETH,          # tokenIn
                token_out,          # tokenOut
                fee,                # fee
                wallet_address,     # recipient
                amount_in_wei,      # amountIn
                min_out_wei,        # amountOutMinimum
                0                   # sqrtPriceLimitX96 (0 = no limit)
            )
            
            # Build transaction with multicall (handles WETH wrapping)
            tx = self.swap_router.functions.exactInputSingle(swap_params).build_transaction({
                "from": wallet_address,
                "nonce": self.w3.eth.get_transaction_count(wallet_address),
                "value": amount_in_wei,  # Send ETH
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": BASE_CHAIN_ID,
            })
            
            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                "success": receipt.status == 1,
                "tx_hash": tx_hash.hex(),
                "amount_in": str(amount_eth),
                "amount_out_expected": str(quote),
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber,
            }
        except Exception as e:
            raise Exception(f"Swap failed: {str(e)}")
    
    async def swap_tokens_for_eth(
        self,
        token_in: str,
        wallet_address: str,
        private_key: str,
        amount_tokens: Decimal,
        slippage_percent: Decimal = Decimal("0.5"),
        fee: int = 3000
    ) -> Dict[str, Any]:
        """Swap tokens for ETH using Uniswap V3 on Base."""
        try:
            token_in = Web3.to_checksum_address(token_in)
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            # Check token balance
            balance = await self.check_token_balance(token_in, wallet_address)
            if balance < amount_tokens:
                raise Exception(f"Insufficient tokens. Have: {balance}, Need: {amount_tokens}")
            
            # Check and handle allowance
            allowance = await self.check_allowance(token_in, wallet_address)
            if allowance < amount_tokens:
                print("Approving tokens...")
                approve_tx = await self.approve_tokens(
                    token_in, wallet_address, private_key, 
                    amount_tokens * Decimal(2)  # Approve 2x for future trades
                )
                # Wait for approval
                self.w3.eth.wait_for_transaction_receipt(approve_tx, timeout=60)
                print(f"Approved: {approve_tx}")
            
            # Get decimals and convert amount
            token_contract = self.w3.eth.contract(address=token_in, abi=ERC20_ABI)
            decimals_in = token_contract.functions.decimals().call()
            amount_in_wei = int(amount_tokens * Decimal(10 ** decimals_in))
            
            # Get quote
            quote = await self.get_swap_quote(token_in, self.WETH, amount_tokens, fee)
            if quote <= 0:
                raise Exception("Could not get swap quote. Pool may not exist.")
            
            # Apply slippage
            min_out = quote * (Decimal(1) - slippage_percent / Decimal(100))
            min_out_wei = Web3.to_wei(min_out, 'ether')
            
            deadline = int(time.time()) + 300
            
            swap_params = (
                token_in,           # tokenIn
                self.WETH,          # tokenOut
                fee,                # fee
                wallet_address,     # recipient (will receive WETH then unwrap)
                amount_in_wei,      # amountIn
                min_out_wei,        # amountOutMinimum
                0                   # sqrtPriceLimitX96
            )
            
            tx = self.swap_router.functions.exactInputSingle(swap_params).build_transaction({
                "from": wallet_address,
                "nonce": self.w3.eth.get_transaction_count(wallet_address),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": BASE_CHAIN_ID,
            })
            
            signed = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                "success": receipt.status == 1,
                "tx_hash": tx_hash.hex(),
                "amount_in": str(amount_tokens),
                "amount_out_expected": str(quote),
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber,
            }
        except Exception as e:
            raise Exception(f"Swap failed: {str(e)}")
    
    # ============ Helper Functions ============
    
    async def check_contract_renounced(self, token_address: str) -> bool:
        """Check if contract ownership is renounced."""
        try:
            # Common owner() function ABI
            owner_abi = json.loads('[{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"type":"function"}]')
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=owner_abi
            )
            
            try:
                owner = token_contract.functions.owner().call()
                return owner == "0x0000000000000000000000000000000000000000"
            except:
                return False
        except:
            return False
    
    async def get_eth_price(self) -> float:
        """Get current ETH price in USD using Chainlink on Base."""
        try:
            # Chainlink ETH/USD Price Feed on Base
            chainlink_eth_usd = "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70"
            
            price_feed_abi = json.loads('''[
                {"inputs":[],"name":"latestRoundData","outputs":[
                    {"name":"roundId","type":"uint80"},
                    {"name":"answer","type":"int256"},
                    {"name":"startedAt","type":"uint256"},
                    {"name":"updatedAt","type":"uint256"},
                    {"name":"answeredInRound","type":"uint80"}
                ],"stateMutability":"view","type":"function"},
                {"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"}
            ]''')
            
            price_feed = self.w3.eth.contract(
                address=Web3.to_checksum_address(chainlink_eth_usd),
                abi=price_feed_abi
            )
            
            decimals = price_feed.functions.decimals().call()
            round_data = price_feed.functions.latestRoundData().call()
            price = round_data[1] / (10 ** decimals)
            
            return float(price)
        except Exception as e:
            print(f"Warning: Could not fetch ETH price from Chainlink: {e}")
            return 3000.0  # Fallback price


# Backward compatibility alias
SwellSwapper = BaseFlowTrader


# Test function
async def test_trader():
    """Test the BaseFlowTrader class."""
    try:
        trader = BaseFlowTrader()
        
        # Test ETH price
        eth_price = await trader.get_eth_price()
        print(f"ETH Price: ${eth_price:,.2f}")
        
        # Test getting USDC info
        usdc_info = await trader.get_token_info(TOKENS["USDC"])
        print(f"USDC Symbol: {usdc_info['symbol']}")
        print(f"USDC Decimals: {usdc_info['decimals']}")
        
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_trader())