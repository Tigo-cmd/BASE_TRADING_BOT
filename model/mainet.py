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

# DEX Configuration
UNISWAP_V3_QUOTER = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399AF7227c093af81De11938d96"

# BaseFlow Custom Router (Sprint 2 - On-chain Attribution)
BASEFLOW_ROUTER_ADDRESS = os.getenv('BASEFLOW_ROUTER_ADDRESS', '0x0000000000000000000000000000000000000000')

# Common token addresses on Base
TOKENS = {
    "WETH": "0x4200000000000000000000000000000000000006",
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "cbETH": "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
}

# ABIs
ERC20_ABI = json.loads('''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}]''')

QUOTER_ABI = json.loads('''[{"inputs":[{"components":[{"name":"tokenIn","type":"address"},{"name":"tokenOut","type":"address"},{"name":"amountIn","type":"uint256"},{"name":"fee","type":"uint24"},{"name":"sqrtPriceLimitX96","type":"uint160"}],"name":"params","type":"tuple"}],"name":"quoteExactInputSingle","outputs":[{"name":"amountOut","type":"uint256"},{"name":"sqrtPriceX96After","type":"uint160"},{"name":"initializedTicksCrossed","type":"uint32"},{"name":"gasEstimate","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]''')

BASEFLOW_ROUTER_ABI = json.loads('''[{"inputs":[{"name":"tokenOut","type":"address"},{"name":"amountOutMin","type":"uint256"},{"name":"deadline","type":"uint256"}],"name":"swapETHForTokens","outputs":[{"name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"name":"tokenIn","type":"address"},{"name":"amountIn","type":"uint256"},{"name":"amountOutMin","type":"uint256"},{"name":"deadline","type":"uint256"}],"name":"swapTokensForETH","outputs":[{"name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]''')

class BaseFlowTrader:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        self.WETH = Web3.to_checksum_address(TOKENS["WETH"])
        self.router_address = BASEFLOW_ROUTER_ADDRESS
        if self.router_address != '0x0000000000000000000000000000000000000000':
            self.router = self.w3.eth.contract(address=Web3.to_checksum_address(self.router_address), abi=BASEFLOW_ROUTER_ABI)
        else:
            self.router = None
            
        self.quoter = self.w3.eth.contract(address=Web3.to_checksum_address(UNISWAP_V3_QUOTER), abi=QUOTER_ABI)

    async def get_eth_price(self) -> float:
        # Chainlink ETH/USD Base
        feed = "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70"
        abi = '[{"inputs":[],"name":"latestRoundData","outputs":[{"name":"roundId","type":"uint80"},{"name":"answer","type":"int256"},{"name":"startedAt","type":"uint256"},{"name":"updatedAt","type":"uint256"},{"name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"name":"uint8","type":"uint8"}],"stateMutability":"view","type":"function"}]'
        try:
            contract = self.w3.eth.contract(address=feed, abi=json.loads(abi))
            data = contract.functions.latestRoundData().call()
            return float(data[1]) / 1e8
        except: return 3000.0

    async def check_eth_balance(self, address: str) -> Decimal:
        return Decimal(self.w3.eth.get_balance(Web3.to_checksum_address(address))) / Decimal(1e18)

    async def check_token_balance(self, token: str, address: str) -> Decimal:
        c = self.w3.eth.contract(address=Web3.to_checksum_address(token), abi=ERC20_ABI)
        b = c.functions.balanceOf(Web3.to_checksum_address(address)).call()
        d = c.functions.decimals().call()
        return Decimal(b) / Decimal(10**d)

    async def get_swap_quote(self, token_in: str, token_out: str, amount_in: Decimal, fee: int = 3000) -> Decimal:
        try:
            c_in = self.w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=ERC20_ABI)
            d_in = 18 if token_in.lower() == self.WETH.lower() else c_in.functions.decimals().call()
            c_out = self.w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI)
            d_out = 18 if token_out.lower() == self.WETH.lower() else c_out.functions.decimals().call()
            
            res = self.quoter.functions.quoteExactInputSingle((Web3.to_checksum_address(token_in), Web3.to_checksum_address(token_out), int(amount_in * Decimal(10**d_in)), fee, 0)).call()
            return Decimal(res[0]) / Decimal(10**d_out)
        except: return Decimal(0)

    async def get_token_info(self, address: str) -> dict:
        address = Web3.to_checksum_address(address)
        c = self.w3.eth.contract(address=address, abi=ERC20_ABI)
        symbol = c.functions.symbol().call()
        name = c.functions.name().call()
        decimals = c.functions.decimals().call()
        price = await self.get_swap_quote(self.WETH, address, Decimal("0.1"))
        eth_p = await self.get_eth_price()
        return {
            "name": name, "symbol": symbol, "address": address, "decimals": decimals,
            "price": float(eth_p / (float(price)*10)) if price > 0 else 0,
            "market_cap": 0, "liquidity": 0, "renounced": True, "frozen": False, "revoked": False,
            "eth_ratio": float(price) * 10, "website": "", "documentation": ""
        }

    async def swap_eth_for_tokens(self, token_out, wallet, key, amount_eth, slippage=Decimal("0.5"), user_id=None):
        if not self.router: return {"success": False, "error": "Router not set"}
        try:
            quote = await self.get_swap_quote(self.WETH, token_out, amount_eth)
            if quote == 0: return {"success": False, "error": "No liquidity/quote found"}
            
            c_out = self.w3.eth.contract(address=Web3.to_checksum_address(token_out), abi=ERC20_ABI)
            d_out = c_out.functions.decimals().call()
            min_out = int(quote * (Decimal(1) - slippage/100) * Decimal(10**d_out))
            
            tx = self.router.functions.swapETHForTokens(Web3.to_checksum_address(token_out), min_out, int(time.time())+300).build_transaction({
                "from": wallet, "nonce": self.w3.eth.get_transaction_count(wallet), "value": Web3.to_wei(amount_eth, 'ether'),
                "gas": 400000, "gasPrice": self.w3.eth.gas_price, "chainId": BASE_CHAIN_ID
            })
            signed = self.w3.eth.account.sign_transaction(tx, key)
            h = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            r = self.w3.eth.wait_for_transaction_receipt(h)
            if user_id and r.status == 1:
                from store_to_db import save_trade, update_volume_tracking
                await save_trade(user_id, wallet, h.hex(), "ETH", token_out, str(amount_eth), str(quote), "buy", "success", r.gasUsed, r.blockNumber)
                await update_volume_tracking(token_out, float(amount_eth))
            return {"success": r.status == 1, "tx_hash": h.hex()}
        except Exception as e: return {"success": False, "error": str(e)}

    async def swap_tokens_for_eth(self, token_in, wallet, key, amount_token, slippage=Decimal("0.5"), user_id=None):
        if not self.router: return {"success": False, "error": "Router not set"}
        try:
            token_in = Web3.to_checksum_address(token_in)
            wallet = Web3.to_checksum_address(wallet)
            c_in = self.w3.eth.contract(address=token_in, abi=ERC20_ABI)
            d_in = c_in.functions.decimals().call()
            amount_wei = int(amount_token * Decimal(10**d_in))
            
            # Check allowance
            allowance = c_in.functions.allowance(wallet, self.router_address).call()
            if allowance < amount_wei:
                # Approve router
                app_tx = c_in.functions.approve(self.router_address, 2**256-1).build_transaction({
                    "from": wallet, "nonce": self.w3.eth.get_transaction_count(wallet),
                    "gas": 100000, "gasPrice": self.w3.eth.gas_price, "chainId": BASE_CHAIN_ID
                })
                signed_app = self.w3.eth.account.sign_transaction(app_tx, key)
                self.w3.eth.send_raw_transaction(signed_app.raw_transaction)
                time.sleep(2) # Wait for approval
            
            quote = await self.get_swap_quote(token_in, self.WETH, amount_token)
            min_out = int(quote * (Decimal(1) - slippage/100) * Decimal(10**18))
            
            tx = self.router.functions.swapTokensForETH(token_in, amount_wei, min_out, int(time.time())+300).build_transaction({
                "from": wallet, "nonce": self.w3.eth.get_transaction_count(wallet),
                "gas": 400000, "gasPrice": self.w3.eth.gas_price, "chainId": BASE_CHAIN_ID
            })
            signed = self.w3.eth.account.sign_transaction(tx, key)
            h = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            r = self.w3.eth.wait_for_transaction_receipt(h)
            
            if user_id and r.status == 1:
                from store_to_db import save_trade, update_volume_tracking
                await save_trade(user_id, wallet, h.hex(), token_in, "ETH", str(amount_token), str(quote), "sell", "success", r.gasUsed, r.blockNumber)
                await update_volume_tracking(token_in, float(quote))
                
            return {"success": r.status == 1, "tx_hash": h.hex()}
        except Exception as e: return {"success": False, "error": str(e)}