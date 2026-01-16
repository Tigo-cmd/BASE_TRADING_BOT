from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from telegram.ext import ContextTypes
from utils import shorten_address
from store_to_db import (
    create_wallet_db, 
    fetch_all_from_wallet, 
    fetch_from_wallet, 
    init_db, 
    balance_check, 
    delete_wallets_by_user,
    delete_specific_wallet,
    get_user_trades,
    get_trade_count,
    save_trade
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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - shows premium welcome message with ETH price."""
    # Fetch ETH price in a non-blocking way
    try:
        eth_price_val = await asyncio.to_thread(get_eth_price)
        eth_price = f"${eth_price_val:,.2f}" if eth_price_val > 0 else "N/A"
    except Exception:
        eth_price = "N/A"

    username = update.effective_user.username
    display_name = f"@{username}" if username else "Trader"
    
    welcome_text = (
        f"👋 *Welcome, {display_name}!*\n\n"
        f"🚀 *BaseFlow* is your ultimate companion for high-speed trading on the *Base Network* 🔵\n\n"
        f"💰 *Current ETH Price:* `{eth_price}`\n\n"
        f"🔥 *Features:*\n"
        f"• Instant Wallet Generation\n"
        f"• Lightning Fast Swaps\n"
        f"• Real-time Price Tracking\n"
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
            InlineKeyboardButton("📈 Prices", callback_data='prices'),
            InlineKeyboardButton("💱 Buy/Sell", callback_data='buysell')
        ],
        [
            InlineKeyboardButton("👤 Profile", callback_data='profile'),
            InlineKeyboardButton("⚙️ Settings", callback_data='settings')
        ],
        [
            InlineKeyboardButton("📖 Help & Tutorial", callback_data='help')
        ],
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
        
        elif query.data.startswith('refresh_'):
            token_address = query.data.split('_')[1]
            await analyze_token(update, context, token_address)

    except Exception as e:
        print(f"Callback Error: {e}")

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
    text = (
        "⚙️ *Settings*\n"
        "━━━━━━━━━━━━━━━\n"
        "⚡ *Default Slippage:* `0.5%`\n"
        "⛽ *Gas Priority:* `Normal`\n"
        "🛡️ *Anti-Rug:* `Enabled`\n"
        "━━━━━━━━━━━━━━━\n"
        "Full settings coming soon in v2.0!"
    )
    keyboard = [[InlineKeyboardButton("⬅️ Menu", callback_data="start"), InlineKeyboardButton("❌ Close", callback_data="close")]]
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
        trader = get_trader()
        if trader is None:
            await loading_msg.edit_text("❌ Trading engine offline.")
            return

        info = await trader.get_token_info(token_address)
        
        text = (
            f"🪙 *{info['name']} ({info['symbol']})*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 *Price:* `${info['price']:.8f}`\n"
            f"📈 *MCap:* `${info['market_cap']:,.0f}`\n"
            f"💧 *Liquidity:* `${info['liquidity']:,.0f}`\n\n"
            f"🛡️ *Safety Check:*\n"
            f"- Renounced: {'✅' if info['renounced'] else '❌'}\n"
            f"- Honeypot: {'✅ Clean' if not info.get('honeypot', False) else '🚨 Warning'}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 [Basescan](https://basescan.org/token/{token_address}) | [DexScreener](https://dexscreener.com/base/{token_address})"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 Buy Token", callback_data=f"buy_{token_address}")],
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_{token_address}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buysell"), InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await loading_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ *Analysis Error*\n\n{str(e)[:100]}")

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
        await query.message.edit_text(f"❌ *Generation Failed:* {e}")

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

async def token_swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Placeholder for token swap selection
    text = "💱 *Select Token Flow*\n\nFeature arriving in next update!"
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="buysell")]]
    await send_or_edit(update, text, InlineKeyboardMarkup(keyboard))