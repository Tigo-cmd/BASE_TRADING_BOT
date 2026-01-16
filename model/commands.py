from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from telegram.ext import ContextTypes
from decimal import Decimal
from utils import shorten_address
from store_to_db import (
    create_wallet_db, 
    fetch_all_from_wallet, 
    fetch_from_wallet, 
    init_db, 
    balance_check, 
    delete_wallets_by_user,
    delete_specific_wallet,
    save_trade,
    register_user,
    get_referral_stats,
    get_leaderboard,
    update_user_settings,
    save_ai_signal,
    get_latest_ai_signals,
    create_alert,
    get_user_alerts,
    get_trade_count
)
from api import get_eth_price
from telegram.helpers import escape_markdown
from generate_wallet import generate_wallet
import asyncio

# Note: web3 and trader are imported lazily to avoid slow startup
_trader = None

def get_trader():
    """Get or create BaseFlowTrader instance (lazy loading)"""
    global _trader
    if _trader is None:
        try:
            from mainet import BaseFlowTrader
            _trader = BaseFlowTrader()
        except Exception as e:
            print(f"Warning: Could not initialize trader: {e}")
            return None
    return _trader

_ai = None

def get_ai():
    """Get or create AIService instance (lazy loading)"""
    global _ai
    if _ai is None:
        try:
            from ai_service import get_ai_service
            _ai = get_ai_service()
        except Exception as e:
            print(f"Warning: Could not initialize AI service: {e}")
            return None
    return _ai


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - shows premium welcome message with ETH price."""
    # Fetch ETH price in a non-blocking way
    try:
        eth_price_val = await asyncio.to_thread(get_eth_price)
        eth_price = f"${eth_price_val:,.2f}" if eth_price_val > 0 else "N/A"
    except Exception:
        eth_price = "N/A"

    username = update.effective_user.username
    user_id = update.effective_user.id
    display_name = f"@{username}" if username else "Trader"
    
    # Handle Referral (Sprint 3)
    referred_by = None
    if context.args:
        try:
            referred_by = int(context.args[0])
            if referred_by == user_id: referred_by = None # Can't refer self
        except: pass
    
    await register_user(user_id, username, referred_by)
    
    welcome_text = (
        f"👋 *Welcome, {display_name}!*\n\n"
        f"🚀 *BaseFlow* is your ultimate companion for high-speed trading on the *Base Network* 🔵\n\n"
        f"💰 *Current ETH Price:* `{eth_price}`\n\n"
        f"🔥 *Features:*\n"
        f"• Instant Wallet Generation\n"
        f"• Lightning Fast Swaps\n"
        f"• Copy Trading & Referrals (NEW!)\n"
        f"• On-chain Attribution\n\n"
        f"🔗 [Website](https://base-trading-bot.vercel.app) | [Docs](https://docs.baseflow.xyz) | [Twitter](https://x.com/baseflow)\n\n"
        f"👇 *Select an option below to get started:*"
    )

    # Create a premium layout keyboard
    keyboard = [
        [
            InlineKeyboardButton("📊 Trades", callback_data='trades'),
            InlineKeyboardButton("💳 Wallets", callback_data='wallet')
        ],
        [
            InlineKeyboardButton("🤖 AI Intelligence", callback_data='ai_intelligence'),
            InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')
        ],
        [
            InlineKeyboardButton("🤝 Referrals", callback_data='referral'),
            InlineKeyboardButton("👥 Copy Trading", callback_data='copytrade')
        ],
        [
            InlineKeyboardButton("💱 Buy/Sell", callback_data='buysell'),
            InlineKeyboardButton("🔎 Token Lookup", callback_data='look')
        ],
        [
            InlineKeyboardButton("👤 Profile", callback_data='profile'),
            InlineKeyboardButton("🎲 Fun Facts", callback_data='fun_facts')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
            InlineKeyboardButton("📖 Help", callback_data='help')
        ],
        [InlineKeyboardButton("📢 Join Community", url="https://t.me/+jNYLaVDd7lpjODJk")],
        [
            InlineKeyboardButton("❌ Close Menu", callback_data="close")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # If this was a button click, edit the message. Otherwise send new.
    if update.callback_query:
        await update.callback_query.message.edit_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup, 
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


# Helper: General message sender/editor for consistent UX
async def send_or_edit(update: Update, text: str, reply_markup: InlineKeyboardMarkup = None, parse_mode: str = "Markdown", disable_web_page_preview: bool = True):
    """Sends a new message or edits existing one based on context."""
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )
        except Exception as e:
            # If edit fails (e.g. same content), just try to answer query
            print(f"Edit failed: {e}")
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        # === CLOSE BUTTON ===
        if query.data == "close":
            try:
                await query.message.delete()
            except:
                await query.message.edit_text("✅ *Menu Closed*", parse_mode="Markdown")
            return
        
        # === NAVIGATION ===
        elif query.data == "return_" or query.data == "wallet":
            await CreateWallet_command(update, context)
        
        elif query.data == "trades":
            await Trades_command(update, context)
        
        elif query.data == "profile":
            await profile_command(update, context)
        
        elif query.data == "referral":
            await referral_command(update, context)
            
        elif query.data == "copytrade":
            await Copytrading_command(update, context)
            
        elif query.data == "leaderboard":
            await Leaderboard_command(update, context)
        
        elif query.data == "settings":
            await Settings_command(update, context)
        
        elif query.data == "help":
            await help_command(update, context)
        
        elif query.data == "buysell":
            await Buysell_command(update, context)
        
        elif query.data == "prices":
            await price_command(update, context)
        
        elif query.data == "start":
            await start_command(update, context)
            
        elif query.data == "ai_intelligence":
            await AI_intelligence_command(update, context)
            
        elif query.data == "ai_scan_trends":
            await AI_scan_trends_callback(update, context)
            
        elif query.data == "fun_facts":
            await fun_facts_command(update, context)
            
        elif query.data == "look":
            await look_command(update, context)
            
        elif query.data.startswith('look_'):
            token_address = query.data.split('_')[1]
            await look_token(update, context, token_address)
        
        # === WALLET ACTIONS ===
        elif query.data == "Generate_wallet":
            await wallet_callback_handler(update, context, 0)
        
        elif query.data == "5_wallets":
            await wallet_callback_handler(update, context, 5)
        
        elif query.data == "10_wallets":
            await wallet_callback_handler(update, context, 10)
        
        elif query.data == "remove_all":
            text = "⚠️ *Remove All Wallets?*\n\nThis action cannot be undone. All private keys will be purged from our database.\n\nType *CONFIRM* to proceed."
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="wallet")]])
            await send_or_edit(update, text, reply_markup)
            context.user_data["awaiting_confirmation"] = "remove_all"
        
        elif query.data.startswith("address_"):
            address = query.data.split("_", 1)[1]
            await show_wallet_details(update, address)
        
        elif query.data.startswith("delete_"):
            address = query.data.split("_", 1)[1]
            text = f"⚠️ *Delete Wallet?*\n\n`{address}`\n\nType *CONFIRM* to proceed."
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="wallet")]])
            await send_or_edit(update, text, reply_markup)
            context.user_data["awaiting_confirmation"] = "delete"
            context.user_data["delete_address"] = address
        
        # === TOKEN ACTIONS ===
        elif query.data == 'enter_token_address':
            text = "📝 *Enter Token Address*\n\nPlease paste the contract address of the token you want to trade below:"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buysell")]])
            await send_or_edit(update, text, reply_markup)
            context.user_data['awaiting_token_address'] = True
        
        elif query.data == "swap_tokens":
            await token_swap(update, context)
        
        elif query.data.startswith('buy_'):
            # This is the initial "Buy Token" click from analyze_token
            token_address = query.data.split('_')[1]
            user_id = update.effective_user.id
            wallets = fetch_all_from_wallet(user_id)
            
            if not wallets:
                text = "❌ *No Wallets Found*\n\nYou need to generate or connect a wallet before you can trade."
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Create Wallet", callback_data="wallet")]])
                await send_or_edit(update, text, reply_markup)
                return
            
            wallet_buttons = []
            for wallet in wallets:
                short_address = shorten_address(wallet["address"])
                wallet_buttons.append([
                    InlineKeyboardButton(f"💳 {short_address}", callback_data=f"select_wallet_{wallet['address']}_{token_address}")
                ])
            wallet_buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f'refresh_{token_address}')])
            
            await send_or_edit(update, "🎯 *Select Trading Wallet:*", InlineKeyboardMarkup(wallet_buttons))

        # === SETTINGS ACTIONS (Sprint 4) ===
        elif query.data.startswith("toggle_autobuy_"):
            mode = query.data.split("_")[2]
            enabled = True if mode == "on" else False
            await update_user_settings(user_id, auto_buy_enabled=enabled)
            await Settings_command(update, context)

        elif query.data == "config_slippage":
            text = "⚡ *Set Default Slippage*\n\nEnter the desired slippage percentage (e.g., 0.5, 1.0, 5.0):"
            context.user_data["awaiting_config"] = "slippage"
            await send_or_edit(update, text, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="settings")]]))

        elif query.data == "config_autobuy_amt":
            text = "💰 *Set Auto-Buy Amount*\n\nEnter the default ETH amount for auto-buys (e.g., 0.1, 0.5):"
            context.user_data["awaiting_config"] = "auto_buy_amount"
            await send_or_edit(update, text, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="settings")]]))

        elif query.data == "config_gas":
            text = "⛽ *Set Gas Priority*\n\nSelect your preferred gas mode:"
            keyboard = [
                [InlineKeyboardButton("Normal", callback_data="set_gas_normal"), InlineKeyboardButton("Fast", callback_data="set_gas_fast")],
                [InlineKeyboardButton("Rapid", callback_data="set_gas_rapid")],
                [InlineKeyboardButton("⬅️ Back", callback_data="settings")]
            ]
            await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

        elif query.data.startswith("set_gas_"):
            mode = query.data.split("_")[2]
            await update_user_settings(user_id, gas_price_mode=mode)
            await Settings_command(update, context)

        elif query.data == "config_tpsl":
            text = "🚀 *Set TP/SL Targets*\n\nEnter the Take Profit % (e.g., 100):"
            context.user_data["awaiting_config"] = "auto_sell_tp"
            await send_or_edit(update, text, InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="settings")]]))

        elif query.data.startswith('select_wallet_'):
            # Data format: select_wallet_{address}_{token_address}
            parts = query.data.split('_')
            wallet_address = parts[2]
            token_address = parts[3]
            
            # Show amount selection keyboard
            text = (
                f"🎯 *Wallet Selected:* `{wallet_address[:8]}...{wallet_address[-6:]}`\n"
                f"🪙 *Token:* `{token_address[:8]}...{token_address[-6:]}`\n\n"
                f"💰 *Select Purchase Amount:* "
            )
            keyboard = [
                [
                    InlineKeyboardButton("0.01 ETH", callback_data=f"buy_amt_{wallet_address}_{token_address}_0.01"),
                    InlineKeyboardButton("0.05 ETH", callback_data=f"buy_amt_{wallet_address}_{token_address}_0.05")
                ],
                [
                    InlineKeyboardButton("0.1 ETH", callback_data=f"buy_amt_{wallet_address}_{token_address}_0.1"),
                    InlineKeyboardButton("0.5 ETH", callback_data=f"buy_amt_{wallet_address}_{token_address}_0.5")
                ],
                [
                    InlineKeyboardButton("1.0 ETH", callback_data=f"buy_amt_{wallet_address}_{token_address}_1.0"),
                    InlineKeyboardButton("⌨️ Custom", callback_data=f"buy_amt_custom_{wallet_address}_{token_address}")
                ],
                [InlineKeyboardButton("⬅️ Back to Wallets", callback_data=f"buy_{token_address}")]
            ]
            await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

        elif query.data.startswith('buy_amt_'):
            # Data format: buy_amt_{wallet}_{token}_{amount}
            parts = query.data.split('_')
            wallet_addr = parts[2]
            token_addr = parts[3]
            amount = parts[4]
            
            await execute_buy(update, context, wallet_addr, token_addr, amount)

        elif query.data.startswith('sell_init_'):
            token_addr = query.data.split('_')[2]
            user_id = update.effective_user.id
            wallets = fetch_all_from_wallet(user_id)
            
            # Find wallets that have this token
            held_wallets = []
            trader = get_trader()
            for w in wallets:
                bal = await trader.check_token_balance(token_addr, w["address"])
                if bal > 0:
                    held_wallets.append((w["address"], bal))
            
            if not held_wallets:
                await query.message.edit_text("❌ *Error:* No wallets with this token found.")
                return
                
            text = "🚀 *Sell Token*\n\nSelect a wallet to sell from:"
            wallet_buttons = []
            for addr, bal in held_wallets:
                short = shorten_address(addr)
                wallet_buttons.append([InlineKeyboardButton(f"💳 {short} ({bal:.2f})", callback_data=f"sell_wallet_{addr}_{token_addr}_{bal}")])
            
            wallet_buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"refresh_{token_addr}")])
            await send_or_edit(update, text, InlineKeyboardMarkup(wallet_buttons))

        elif query.data.startswith('sell_wallet_'):
            # sell_wallet_{addr}_{token}_{bal}
            parts = query.data.split('_')
            addr, token, bal = parts[2], parts[3], parts[4]
            
            text = f"🚀 *Sell Token*\n\nWallet: `{shorten_address(addr)}`\nBalance: `{bal}`\n\nSelect amount to sell:"
            keyboard = [
                [
                    InlineKeyboardButton("25%", callback_data=f"sell_exec_{addr}_{token}_{float(bal)*0.25}"),
                    InlineKeyboardButton("50%", callback_data=f"sell_exec_{addr}_{token}_{float(bal)*0.5}"),
                    InlineKeyboardButton("100%", callback_data=f"sell_exec_{addr}_{token}_{bal}")
                ],
                [InlineKeyboardButton("⬅️ Back", callback_data=f"sell_init_{token}")]
            ]
            await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

        elif query.data.startswith('sell_exec_'):
            # sell_exec_{addr}_{token}_{amt}
            parts = query.data.split('_')
            addr, token, amt = parts[2], parts[3], parts[4]
            await execute_sell(update, context, addr, token, amt)

        elif query.data.startswith('refresh_'):
            token_address = query.data.split('_')[1]
            await analyze_token(update, context, token_address)

        elif query.data.startswith('ai_analyze_'):
            token_address = query.data.split('_')[2]
            await AI_security_analysis_command(update, context, token_address)

    except Exception as e:
        print(f"Callback Error: {e}")

async def execute_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_addr: str, token_addr: str, amount: str):
    """Executes the actual buy transaction."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    await query.message.edit_text(
        f"⏳ *Sending Transaction...*\n\nBuying `{amount} ETH` worth of token `{token_addr[:10]}...`",
        parse_mode="Markdown"
    )
    
    try:
        trader = get_trader()
        # Find private key from DB
        wallets = fetch_all_from_wallet(user_id)
        pk = next((w["private_key"] for w in wallets if w["address"].lower() == wallet_addr.lower()), None)
        
        if not pk:
            await query.message.edit_text("❌ *Error:* Could not find private key for this wallet.")
            return

        # Execute Swap
        result = await trader.swap_eth_for_tokens(
            token_out=token_addr,
            wallet=wallet_addr,
            key=pk,
            amount_eth=Decimal(amount),
            user_id=user_id
        )
        
        if result["success"]:
            text = (
                f"✅ *Swap Successful!*\n━━━━━━━━━━━━━━━\n"
                f"💰 *Sent:* `{amount} ETH`\n"
                f"🔗 [View on Basescan](https://basescan.org/tx/{result['tx_hash']})\n"
                f"━━━━━━━━━━━━━━━"
            )
            keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            print(f"Swap Failed: {result.get('error')}")
            await query.message.edit_text("❌ *Swap Failed:* We couldn't complete the purchase. This could be due to gas issues or price movement.")
            
    except Exception as e:
        print(f"ERROR in execute_buy: {e}")
        await query.message.edit_text("❌ *Execution Error:* An unexpected error occurred while processing your buy. Please try again later.")

async def execute_sell(update: Update, context: ContextTypes.DEFAULT_TYPE, wallet_addr: str, token_addr: str, amount: str):
    """Executes the actual sell transaction."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    await query.message.edit_text(
        f"⏳ *Sending Transaction...*\n\nSelling `{amount}` tokens...",
        parse_mode="Markdown"
    )
    
    try:
        trader = get_trader()
        wallets = fetch_all_from_wallet(user_id)
        pk = next((w["private_key"] for w in wallets if w["address"].lower() == wallet_addr.lower()), None)
        
        if not pk:
            await query.message.edit_text("❌ *Error:* Could not find private key for this wallet.")
            return

        # Execute Swap (Sell)
        result = await trader.swap_tokens_for_eth(
            token_in=token_addr,
            wallet=wallet_addr,
            key=pk,
            amount_token=Decimal(amount),
            user_id=user_id
        )
        
        if result["success"]:
            text = (
                f"✅ *Sell Successful!*\n━━━━━━━━━━━━━━━\n"
                f"💰 *Sold:* `{amount}` tokens\n"
                f"🔗 [View on Basescan](https://basescan.org/tx/{result['tx_hash']})\n"
                f"━━━━━━━━━━━━━━━"
            )
            keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            print(f"Sell Failed: {result.get('error')}")
            await query.message.edit_text("❌ *Sell Failed:* We couldn't complete the sale. This could be due to low liquidity or extreme volatility.")
            
    except Exception as e:
        print(f"ERROR in execute_sell: {e}")
        await query.message.edit_text("❌ *Execution Error:* An unexpected error occurred while processing your sell. Please try again later.")

async def show_wallet_details(update: Update, address: str):
    """Shows detailed view of a single wallet."""
    # Note: In a real app, we might fetch the actual balance here
    # For now, we'll use a placeholder or 0
    balance = await check_balance_command(address)
    
    text = (
        f"💳 *Wallet Details*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📍 *Address:*\n`{address}`\n\n"
        f"💰 *Balance:* `{balance:.4f} ETH`\n"
        f"🔗 [View on Basescan](https://basescan.org/address/{address})\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ *Security Tip:* Never share your private keys. BaseFlow encypts all keys, but your safety is your priority."
    )
    
    keyboard = [
        [InlineKeyboardButton("🗑️ Delete Wallet", callback_data=f"delete_{address}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="wallet"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def Trades_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    trades = get_user_trades(user_id, limit=5)
    
    if not trades:
        text = "📊 *Recent Trades*\n\nNo trades found in your history. Go to /buysell to start trading!"
    else:
        text = "📊 *Recent Trades*\n━━━━━━━━━━━━━━━\n"
        for t in trades:
            status = "🟢" if t["status"] == "success" else "🔴"
            text += f"{status} *{t['trade_type'].upper()}* | {t['amount_in']} → {t['amount_out']}\n"
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def CreateWallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    wallets = fetch_all_from_wallet(user_id)
    
    text = "💳 *Your Wallets*\n"
    if wallets:
        text += f"Total active: {len(wallets)}\n\n"
        wallet_buttons = []
        for i, w in enumerate(wallets, 1):
            short = shorten_address(w["address"])
            wallet_buttons.append([InlineKeyboardButton(f"{i}. {short}", callback_data=f"address_{w['address']}")])
    else:
        text += "\nYou haven't created any wallets yet. Use the buttons below to generate your first trading wallet."
        wallet_buttons = []

    nav_buttons = [
        [InlineKeyboardButton("➕ Generate 1 Wallet", callback_data='Generate_wallet')],
        [InlineKeyboardButton("➕ Generate 5 Wallets", callback_data='5_wallets')],
        [InlineKeyboardButton("🗑️ Remove All", callback_data='remove_all')],
        [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await send_or_edit(update, text, InlineKeyboardMarkup(wallet_buttons + nav_buttons))

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    wallets = fetch_all_from_wallet(user_id)
    trade_count = get_trade_count(user_id)
    
    text = (
        f"👤 *Profile: @{update.effective_user.username or 'Trader'}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💳 *Wallets:* `{len(wallets)}` active\n"
        f"📊 *Total Trades:* `{trade_count}`\n"
        f"🏅 *Rank:* `Newcomer`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📈 Join our community to unlock pro features!"
    )
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def Buysell_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "💱 *Fast Trading Engine*\n"
        "━━━━━━━━━━━━━━━\n"
        "Scan any token address on Base network to get instant analytics and trading options.\n\n"
        "💡 *How it works:*\n"
        "1. Click the button below\n"
        "2. Paste the contract address\n"
        "3. Choose amount and swap!\n"
        "━━━━━━━━━━━━━━━"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔍 Enter Token Address", callback_data='enter_token_address')],
        [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 *BaseFlow Academy*\n"
        "━━━━━━━━━━━━━━━\n"
        "• `/start` - Access main dashboard\n"
        "• `/wallet` - Manage your trading wallets\n"
        "• `/buysell` - Analyze and trade tokens\n"
        "• `/profile` - View your stats\n"
        "• `/settings` - Configure slippage & fees\n\n"
        "❓ *Need Help?* Check our [Documentation](https://docs.baseflow.xyz) or join our [Community](https://t.me/baseflow_community)."
    )
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def Settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    settings = get_user_settings(user_id)
    
    text = (
        "⚙️ *Settings*\n"
        "━━━━━━━━━━━━━━━\n"
        f"⚡ *Slippage:* `{settings['slippage']}%`\n"
        f"🤖 *Auto-Buy:* `{'✅ ON' if settings['auto_buy_enabled'] else '❌ OFF'}`\n"
        f"💰 *Auto-Buy Amount:* `{settings['auto_buy_amount']} ETH`\n"
        f"🚀 *Auto-Sell (TP/SL):* `{settings['auto_sell_tp']}%` / `{settings['auto_sell_sl']}%` \n"
        f"⛽ *Gas Priority:* `{settings['gas_price_mode'].capitalize()}`\n"
        "━━━━━━━━━━━━━━━\n"
        "Configure your high-speed trading parameters below:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"{'🔴 Disable' if settings['auto_buy_enabled'] else '🟢 Enable'} Auto-Buy", callback_data=f"toggle_autobuy_{'off' if settings['auto_buy_enabled'] else 'on'}"),
        ],
        [
            InlineKeyboardButton("✏️ Slippage", callback_data="config_slippage"),
            InlineKeyboardButton("✏️ Auto-Buy Amt", callback_data="config_autobuy_amt")
        ],
        [
            InlineKeyboardButton("⛽ Gas Price", callback_data="config_gas"),
            InlineKeyboardButton("🚀 TP/SL", callback_data="config_tpsl")
        ],
        [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Just a quick ETH price check for now
    try:
        price = await asyncio.to_thread(get_eth_price)
        text = f"📊 *Base Ecosystem Prices*\n\n🔵 *Native ETH:* `${price:,.2f}`\n\nMore token prices coming soon!"
    except:
        text = "📊 *Base Ecosystem Prices*\n\nPrice service currently unavailable."
        
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def analyze_token(update: Update, context: ContextTypes.DEFAULT_TYPE, token_address: str) -> None:
    # If update is from callback, message is in query
    loading_msg = await (update.callback_query.message.edit_text("🔍 *Analyzing Token...*", parse_mode="Markdown") if update.callback_query else update.message.reply_text("🔍 *Analyzing Token...*", parse_mode="Markdown"))
    
    try:
        user_id = update.effective_user.id
        trader = get_trader()
        if trader is None:
            await loading_msg.edit_text("❌ Trading engine offline.")
            return

        # Sprint 4: Auto-Buy Logic
        settings = get_user_settings(user_id)
        if settings.get("auto_buy_enabled") and settings.get("auto_buy_amount", 0) > 0:
            # Auto-execute buy!
            auto_amt = settings["auto_buy_amount"]
            # Find a wallet with balance
            wallets_full = fetch_all_from_wallet(user_id)
            exec_wallet = wallets_full[0]["address"] if wallets_full else None
            
            if exec_wallet:
                await loading_msg.edit_text(f"🤖 *Auto-Buy Triggered!*\n\nExecuting buy for `{auto_amt} ETH` via `{shorten_address(exec_wallet)}`...", parse_mode="Markdown")
                # We need the PK, which fetch_all_from_wallet now provides
                pk = next((w["private_key"] for w in wallets_full if w["address"] == exec_wallet), None)
                
                result = await trader.swap_eth_for_tokens(
                    token_out=token_address,
                    wallet=exec_wallet,
                    key=pk,
                    amount_eth=Decimal(str(auto_amt)),
                    user_id=user_id
                )
                
                info = await trader.get_token_info(token_address)
                if result["success"]:
                    await loading_msg.edit_text(f"✅ *Auto-Buy Successful!*\n\nBought `{info['symbol']}`\n🔗 [Basescan](https://basescan.org/tx/{result['tx_hash']})", parse_mode="Markdown")
                    return
                else:
                    await loading_msg.edit_text(f"❌ *Auto-Buy Failed:* {result.get('error')}\n\nFalling back to manual analysis...", parse_mode="Markdown")
                    await asyncio.sleep(2)
                
        # (Continue with normal analysis if auto-buy failed or was off)
        info = await trader.get_token_info(token_address)
        wallets = fetch_all_from_wallet(user_id)
        total_token_balance = Decimal("0")
        held_wallets = []
        
        for w in wallets:
            bal = await trader.check_token_balance(token_address, w["address"])
            if bal > 0:
                total_token_balance += bal
                held_wallets.append((w["address"], bal))

        text = (
            f"🪙 *{info['name']} ({info['symbol']})*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 *Price:* `${info['price']:.8f}`\n"
            f"📈 *MCap:* `${info['market_cap']:,.0f}`\n"
            f"💧 *Liquidity:* `${info['liquidity']:,.0f}`\n\n"
            f"👤 *Your Balance:* `{total_token_balance} {info['symbol']}`\n\n"
            f"🛡️ *Safety Check:*\n"
            f"- Renounced: {'✅' if info['renounced'] else '❌'}\n"
            f"- Honeypot: {'✅ Clean' if not info.get('honeypot', False) else '🚨 Warning'}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 [Basescan](https://basescan.org/token/{token_address}) | [DexScreener](https://dexscreener.com/base/{token_address})"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 Buy Token", callback_data=f"buy_{token_address}")],
        ]
        
        if total_token_balance > 0:
            keyboard.append([InlineKeyboardButton("🚀 Sell Token", callback_data=f"sell_init_{token_address}")])
        
        keyboard.append([InlineKeyboardButton("🤖 AI Security Analysis", callback_data=f"ai_analyze_{token_address}")])
        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{token_address}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="buysell"), InlineKeyboardButton("❌ Close", callback_data="close")])
        
        await loading_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        print(f"ERROR in analyze_token: {e}")
        await loading_msg.edit_text("❌ *Analysis Error*\n\nWe couldn't analyze this token. It might be an invalid address or the network is congested.")


async def wallet_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, num: int) -> None:
    user_id = update.effective_user.id
    query = update.callback_query
    
    await query.message.edit_text("⏳ *Generating Secure Wallets...*", parse_mode="Markdown")
    
    try:
        count = num if num > 0 else 1
        results = []
        for _ in range(count):
            pk, addr = await generate_wallet()
            await create_wallet_db(user_id, addr, pk, 0.0)
            results.append((addr, pk))
        
        text = f"✅ *{count} Wallet(s) Generated!*\n━━━━━━━━━━━━━━━\n"
        for addr, pk in results:
            text += f"📍 `{addr}`\n🔑 `<tg-spoiler>{pk}</tg-spoiler>`\n\n"
        
        text += "⚠️ *Save your private keys safely!* They will only be shown once."
        
        keyboard = [[InlineKeyboardButton("⬅️ My Wallets", callback_data="wallet"), InlineKeyboardButton("❌ Close", callback_data="close")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    except Exception as e:
        print(f"ERROR in wallet_callback_handler: {e}")
        await query.message.edit_text("❌ *Generation Failed:* We encountered an error while generating your wallets. Please try again.")

async def check_balance_command(address: str) -> float:
    try:
        trader = get_trader()
        if trader:
            return float(await trader.check_eth_balance(address))
        return 0.0
    except:
        return 0.0

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")

async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_or_edit(update, "💡 *BaseFlow Tips*\n\nTrading on Base is fast and cheap. Always keep at least 0.005 ETH for gas fees!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text: return
    
    user_message = update.message.text.strip()
    user_id = update.effective_user.id
    
    if context.user_data.get("awaiting_confirmation") == "remove_all":
        if user_message.upper() == "CONFIRM":
            await delete_wallets_by_user(user_id)
            context.user_data["awaiting_confirmation"] = None
            await update.message.reply_text("🗑️ *All wallets removed.*", parse_mode="Markdown")
            await CreateWallet_command(update, context)
        else:
            context.user_data["awaiting_confirmation"] = None
            await update.message.reply_text("❌ *Action cancelled.*", parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_confirmation") == "delete":
        if user_message.upper() == "CONFIRM":
            addr = context.user_data.get("delete_address")
            await delete_specific_wallet(user_id, addr)
            context.user_data["awaiting_confirmation"] = None
            await update.message.reply_text("🗑️ *Wallet deleted.*", parse_mode="Markdown")
            await CreateWallet_command(update, context)
        else:
            context.user_data["awaiting_confirmation"] = None
            await update.message.reply_text("❌ *Action cancelled.*", parse_mode="Markdown")
        return

    if context.user_data.get('awaiting_token_address'):
        from web3 import Web3
        if Web3.is_address(user_message):
            context.user_data['awaiting_token_address'] = False
            await analyze_token(update, context, user_message)
        else:
            await update.message.reply_text("❌ *Invalid address.* Please enter a valid Base contract address.")
        return

    # === CONFIG UPDATES (Sprint 4) ===
    config_field = context.user_data.get("awaiting_config")
    if config_field:
        try:
            val = float(user_message)
            await update_user_settings(user_id, **{config_field: val})
            context.user_data["awaiting_config"] = None
            await update.message.reply_text(f"✅ *Updated:* `{config_field.replace('_', ' ').capitalize()}` set to `{val}`", parse_mode="Markdown")
            await Settings_command(update, context)
        except ValueError:
            await update.message.reply_text("❌ *Invalid input.* Please enter a numeric value.")
        return

    # Handle /look token address input
    if context.user_data.get('awaiting_look_address'):
        from web3 import Web3
        if Web3.is_address(user_message):
            context.user_data['awaiting_look_address'] = False
            await look_token(update, context, user_message)
        else:
            await update.message.reply_text("❌ *Invalid address.* Please enter a valid Base contract address.")
        return

async def token_swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Placeholder for token swap selection
    text = "💱 *Select Token Flow*\n\nFeature arriving in next update!"
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="buysell")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

# ============ Referral & Engagement (Sprint 3) ============

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the user's referral dashboard."""
    user_id = update.effective_user.id
    stats = get_referral_stats(user_id)
    bot_username = context.bot.username
    
    # Generate referral link
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    text = (
        f"🤝 *Referral Program*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Share your link and earn *20%* of all trading fees generated by your referrals! 💸\n\n"
        f"👥 *Total Referred:* `{stats['referral_count']}`\n"
        f"💰 *Total Earned:* `{stats['total_earned_eth']:.4f} ETH`\n\n"
        f"🔗 *Your Referral Link:*\n`{ref_link}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Rewards are credited instantly to your primary wallet upon trade execution."
    )
    
    keyboard = [
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={ref_link}&text=Trade%20on%20Base%20lightning%20fast%20with%20BaseFlow!")],
        [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def Copytrading_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dashboard for copy trading settings."""
    text = (
        f"👥 *Copy Trading (Beta)*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Automatically follow and copy the trades of top-performing wallets on Base.\n\n"
        f"⚠️ *Status:* This feature is currently in internal testing. Stay tuned for the public release!\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Features coming soon:\n"
        f"• Master Leaderboard\n"
        f"• Custom Slippage per Master\n"
        f"• Risk Management (Stop Loss)"
    )
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def Leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows global top traders."""
    top_traders = get_leaderboard(10)
    
    text = "🏆 *Global Leaderboard*\n━━━━━━━━━━━━━━━\n"
    if not top_traders:
        text += "No trades recorded yet. Be the first to top the chart!"
    else:
        for i, t in enumerate(top_traders, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
            text += f"{medal} *{t['username']}*\n   Vol: `{t['volume']:.2f} ETH` | `{t['trades']}` trades\n"
    
    text += "━━━━━━━━━━━━━━━\nGlobal ranking updates every 5 minutes."
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

# ============ AI & Intelligence (Sprint 5) ============

async def AI_intelligence_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dashboard for AI-driven market insights."""
    ai = get_ai()
    if not ai or not ai.is_active:
        text = "🤖 *AI Intelligence*\n\nAI services are currently offline. Please configure `GEMINI_API_KEY` to unlock real-time trends."
        keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start")]]
        await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))
        return

    # Fetch latest signals from DB
    signals = get_latest_ai_signals(3)
    
    text = (
        "🤖 *BaseFlow AI Intelligence*\n"
        "━━━━━━━━━━━━━━━\n"
        "*Recent AI Signals:*\n"
    )
    
    if not signals:
        text += "_Scanning Base for emerging opportunities..._\n"
    else:
        for s in signals:
            text += f"• `{s['token'][:8]}...`: {s['insight'][:60]}...\n"
            
    text += (
        "\n━━━━━━━━━━━━━━━\n"
        "🔥 *AI-Powered Features:*\n"
        "• Security Deep-Scan\n"
        "• Narrative Detection\n"
        "• Dynamic Risk Scoring"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Scan Trends", callback_data="ai_scan_trends")],
        [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def AI_scan_trends_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Triggers a real-time AI scan of the Base network market."""
    query = update.callback_query
    await query.message.edit_text("🤖 *AI Scanning Base DeFi Market...*", parse_mode="Markdown")
    
    try:
        trader = get_trader()
        ai = get_ai()
        if not ai or not ai.is_active:
            await query.message.edit_text("❌ AI Service offline.")
            return

        # Fetch volume data as a proxy for market activity
        from store_to_db import get_total_volume
        market_stats = get_total_volume()
        
        # Get latest signals
        signals = get_latest_ai_signals(5)
        
        context_data = {
            "market_stats": market_stats,
            "recent_signals": signals
        }
        
        trend_summary = await ai.detect_market_trends(context_data)
        
        # Escape markdown special characters in AI response
        safe_summary = trend_summary.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")
        
        text = (
            "🤖 *AI Trend Analysis*\n"
            "━━━━━━━━━━━━━━━\n"
            f"{safe_summary}\n"
            "━━━━━━━━━━━━━━━\n"
            "Market scan complete. Recommendations updated."
        )
        
        keyboard = [[InlineKeyboardButton("⬅️ AI Dashboard", callback_data="ai_intelligence"), InlineKeyboardButton("❌ Close", callback_data="close")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    except Exception as e:
        print(f"ERROR in AI_scan_trends: {e}")
        await query.message.edit_text("❌ *Trend Scan Error:* AI service encountered an issue. Please try again shortly.")

async def AI_security_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE, token_address: str) -> None:
    """Runs a dedicated AI security scan for a token."""
    query = update.callback_query
    # Handle both direct message and callback
    msg = query.message if query else update.message
    loading_msg = await msg.edit_text("🤖 *AI Deep-Scan in progress...*", parse_mode="Markdown") if query else await msg.reply_text("🤖 *AI Deep-Scan in progress...*", parse_mode="Markdown")
    
    try:
        trader = get_trader()
        ai = get_ai()
        if not ai or not ai.is_active:
            await loading_msg.edit_text("❌ AI Service offline.")
            return

        info = await trader.get_token_info(token_address)
        insight = await ai.analyze_token_security(info)
        
        # Save insight to DB
        await save_ai_signal(token_address, "security", insight)
        
        # Escape markdown special characters in AI response
        safe_insight = insight.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")
        
        text = (
            f"🤖 *AI Security Report*\n"
            f"🪙 `{info['symbol']}` | `{shorten_address(token_address)}`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{safe_insight}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🚨 *Warning:* AI analysis is probabilistic. Always DYOR."
        )
        
        keyboard = [[InlineKeyboardButton("⬅️ Analysis", callback_data=f"refresh_{token_address}"), InlineKeyboardButton("❌ Close", callback_data="close")]]
        await loading_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    except Exception as e:
        print(f"ERROR: {e}")
        await loading_msg.edit_text("❌ *AI Scan Error:* AI scan failed. Check logs.")

async def fun_facts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows a random AI-generated fun fact about trading or Base."""
    query = update.callback_query
    msg = query.message if query else update.message
    loading_msg = await msg.edit_text("🎲 *Generating Fun Fact...*", parse_mode="Markdown") if query else await msg.reply_text("🎲 *Generating Fun Fact...*", parse_mode="Markdown")
    
    try:
        ai = get_ai()
        if not ai or not ai.is_active:
            await loading_msg.edit_text("🎲 *Fun Fact*\n━━━━━━━━━━━━━━━\nAI services are offline. Here's a classic:\n\n_The first Bitcoin transaction was for two pizzas, costing 10,000 BTC!_")
            return

        fact = await ai.get_fun_fact()
        
        # Escape markdown special characters in AI response
        safe_fact = fact.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")
        
        text = (
            "🎲 *Fun Fact*\n"
            "━━━━━━━━━━━━━━━\n"
            f"{safe_fact}\n"
            "━━━━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Another Fact", callback_data="fun_facts")],
            [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        await loading_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    except Exception as e:
        print(f"ERROR in fun_facts: {e}")
        await loading_msg.edit_text("🎲 *Fun Fact*\n━━━━━━━━━━━━━━━\n_Base Network launched in August 2023 and quickly became one of the top L2s by TVL!_")

async def look_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts user to enter a token address for comprehensive read-only analysis."""
    text = (
        "🔎 *Token Lookup*\n"
        "━━━━━━━━━━━━━━━\n"
        "Paste any Base network token address below to get comprehensive information:\n\n"
        "• Price & Market Cap\n"
        "• Liquidity Depth\n"
        "• Safety & Security Check\n"
        "• AI Risk Assessment\n\n"
        "_No wallet required. Read-only analysis._"
    )
    
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    
    context.user_data['awaiting_look_address'] = True
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))

async def look_token(update: Update, context: ContextTypes.DEFAULT_TYPE, token_address: str) -> None:
    """Shows comprehensive read-only token info without buy/sell options."""
    loading_msg = await update.message.reply_text("🔎 *Looking up token...*", parse_mode="Markdown")
    
    try:
        trader = get_trader()
        if trader is None:
            await loading_msg.edit_text("❌ Trading engine offline.")
            return

        info = await trader.get_token_info(token_address)
        
        # Get AI insight if available
        ai = get_ai()
        ai_summary = ""
        if ai and ai.is_active:
            try:
                insight = await ai.analyze_token_security(info)
                safe_insight = insight.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")
                ai_summary = f"\n🤖 *AI Assessment:*\n{safe_insight}\n"
            except:
                ai_summary = ""

        text = (
            f"🔎 *Token Lookup: {info['name']}*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🪙 *Symbol:* `{info['symbol']}`\n"
            f"📍 *Address:* `{shorten_address(token_address)}`\n\n"
            f"💰 *Price:* `${info['price']:.8f}`\n"
            f"📈 *Market Cap:* `${info['market_cap']:,.0f}`\n"
            f"💧 *Liquidity:* `${info['liquidity']:,.0f}`\n\n"
            f"🛡️ *Security:*\n"
            f"• Renounced: {'✅ Yes' if info['renounced'] else '⚠️ No'}\n"
            f"• Honeypot: {'✅ Clean' if not info.get('honeypot', False) else '🚨 Detected'}\n"
            f"{ai_summary}"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 [Basescan](https://basescan.org/token/{token_address}) | "
            f"[DexScreener](https://dexscreener.com/base/{token_address}) | "
            f"[GeckoTerminal](https://www.geckoterminal.com/base/pools/{token_address})"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"look_{token_address}")],
            [InlineKeyboardButton("💱 Trade This Token", callback_data=f"refresh_{token_address}")],
            [InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        await loading_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        print(f"ERROR in look_token: {e}")
        await loading_msg.edit_text("❌ *Lookup Error*\n\nCouldn't find this token. Check the address and try again.")
