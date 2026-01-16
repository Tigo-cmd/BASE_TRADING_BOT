import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Configuration
RPC_URL = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY") # User should add this to .env
FEE_COLLECTOR = os.getenv("FEE_COLLECTOR_ADDRESS") # User should add this to .env

# DEX Addresses on Base
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
AERODROME_ROUTER = "0xcF77a3Ba9A5CA399AF7227c093af81De11938d96"

def deploy_router():
    if not PRIVATE_KEY or not FEE_COLLECTOR:
        print("❌ Error: DEPLOYER_PRIVATE_KEY or FEE_COLLECTOR_ADDRESS missing in .env")
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    deployer = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"🚀 Deploying from: {deployer.address}")
    print(f"💰 Balance: {w3.eth.get_balance(deployer.address) / 1e18} ETH")

    # Load contract artifacts (assuming they are compiled or using a simple version)
    # For this demo, we'll assume the contract is compiled using 'solc' or similar
    # In a real environment, we'd use the JSON output from Hardhat/Foundry
    
    # Placeholder for Bytecode and ABI
    # (In a real scenario, you'd read these from ./artifacts)
    try:
        with open("../contracts/BaseFlowRouter.json", "r") as f:
            artifact = json.load(f)
            abi = artifact["abi"]
            bytecode = artifact["bytecode"]
    except:
        print("❌ Error: Compiled contract artifact not found at ../contracts/BaseFlowRouter.json")
        print("Please compile the contract first using: npx hardhat compile")
        return

    Router = w3.eth.contract(abi=abi, bytecode=bytecode)

    # Build constructor transaction
    construct_tx = Router.constructor(
        UNISWAP_V3_ROUTER,
        AERODROME_ROUTER,
        FEE_COLLECTOR
    ).build_transaction({
        "from": deployer.address,
        "nonce": w3.eth.get_transaction_count(deployer.address),
        "gas": 4000000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })

    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(construct_tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"📨 Deployment tx sent: {tx_hash.hex()}")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ BaseFlowRouter deployed at: {receipt.contractAddress}")
    print(f"Update your .env with: BASEFLOW_ROUTER_ADDRESS={receipt.contractAddress}")

if __name__ == "__main__":
    deploy_router()
