# Sprint 2 Walkthrough: Core Trading & On-Chain Attribution

This document provides a detailed overview of the enhancements made during Sprint 2 of the BaseFlow Trading Bot development.

## 1. On-Chain Attribution (BaseFlowRouter)
We implemented a custom smart contract to act as the primary interface for all trades executed by the bot.
- **Contract:** `BaseFlowRouter.sol`
- **Key Features:**
    - **Attribution:** Emits `BotTradeExecuted` events for every swap, allowing for verifiable volume tracking.
    - **Fee Collection:** Automatically collects a configurable fee (default 0.5%) to support the platform.
    - **Multi-DEX Support:** Prepared to route through Uniswap V3 and Aerodrome on the Base network.
    - **Admin Controls:** Ownership-based controls for fee adjustment and emergency withdrawals.

## 2. Advanced Trading Engine (`mainet.py`)
The trading core was rewritten to move from a basic Uniswap interface to a robust, Router-aware system.
- **Smart Swaps:** Uses `swapETHForTokens` and `swapTokensForETH` via the BaseFlowRouter.
- **Automatic Approvals:** The engine now checks ERC20 allowances and automatically triggers approvals if needed before a sell operation.
- **Precise Calculations:** Migrated to `Decimal` for all financial calculations to prevent floating-point errors.
- **Improved Metadata:** `get_token_info` now fetches real-time price quotes and security status (Renounced, etc.) directly from the blockchain.

## 3. Bot UI & Trading Flow
The Telegram interface was upgraded to support a full trading lifecycle.
- **Context-Aware Buttons:** The bot now detects if you hold a token and dynamically adds the **"🚀 Sell Token"** button to the analysis screen.
- **Simplified Buy/Sell Flow:**
    - **Buy:** Choose Wallet -> Choose Amount (0.01 - 1 ETH) -> Immediate Execution.
    - **Sell:** Choose Wallet -> Choose Percentage (25%, 50%, 100%) -> Immediate Execution.
- **Transaction Feedback:** Provides real-time "Sending..." status and clickable Basescan links upon completion.

## 4. Integration & Tracking
- **Database Logging:** All successful trades are saved to the `trades` table in `wallet.db`.
- **Volume Tracking:** Daily volume per token is aggregated in a `volume_tracking` table for future leaderboards.
- **Deployment Script:** Added `deploy_contract.py` to automate the deployment of the Router contract to the Base network.

## 5. Security & Maintenance
- **Lazy Loading:** Critical for performance; the heavy `web3` and `BaseFlowTrader` components are only initialized when a trade-related button is clicked.
- **Robust .gitignore:** Updated to ensure sensitive files like `wallet.db` and `.env` are never accidentally committed.

---
**Next Step:** Sprint 3 - Copy Trading & Engagement (Referral system and leaderboards).
