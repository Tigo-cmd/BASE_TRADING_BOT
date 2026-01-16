#!/usr/bin/python3 env
"""
BaseFlow - Telegram-first trading bot for Base launchpad assets
"""
from typing import Final
from store_to_db import init_db
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from telegram.ext import (
    Application, 
    ApplicationBuilder,
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackQueryHandler
)
from telegram.request import HTTPXRequest
import requests
from commands import (
    start_command,
    price_command,
    Trades_command,
    help_command,
    Buysell_command,
    Settings_command,
    CreateWallet_command,
    tip_command,
    profile_command,
    referral_command,
    Leaderboard_command,
    Copytrading_command,
    AI_intelligence_command,
    AI_security_analysis_command,
    look_command,
    error,
    button_callback,
    message_handler
)
from dotenv import load_dotenv
import os

load_dotenv()

init_db()  # Initialize the database when the script runs

# BaseFlow Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('BASEFLOW_BOT_API')
ALERTS_CHANNEL = os.getenv('BASEFLOW_ALERTS_CHANNEL') # e.g. @BaseFlowAlerts or -100...
TOKEN: Final = TELEGRAM_TOKEN

# Global reference to Application (for background tasks to use the bot)
_bot_app = None

if not TOKEN:
    print("❌ Error: BASEFLOW_BOT_API not found in .env file!")
    print("Please make sure your .env file contains: BASEFLOW_BOT_API=your_bot_token")
    import sys
    sys.exit(1)

async def monitor_callback(token_address, pool_address):
    """
    Called by the monitor when a new pool is detected.
    Broadcasts the alert to the community channel.
    """
    from store_to_db import save_ai_signal
    from utils import shorten_address
    
    print(f"🚀 New Pool Detected: {token_address} at {pool_address}")
    
    # Save to DB for the dashboard
    await save_ai_signal(token_address, "listing", f"New pool detected at {pool_address}")
    
    # Send to Community Channel
    if ALERTS_CHANNEL and _bot_app:
        try:
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            
            text = (
                "🚀 *New Base Listing Detected!* 🚀\n"
                "━━━━━━━━━━━━━━━\n"
                f"🪙 *Token:* `{token_address}`\n"
                f"💧 *Pool:* `{pool_address}`\n\n"
                "🔍 *Quick Actions:*\n"
                "• [Basescan](https://basescan.org/token/" + token_address + ")\n"
                "• [DexScreener](https://dexscreener.com/base/" + token_address + ")\n"
                "━━━━━━━━━━━━━━━\n"
                "🤖 *Analyze instantly in @de_base_bot*"
            )
            
            await _bot_app.bot.send_message(
                chat_id=ALERTS_CHANNEL,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            print(f"📢 Alert sent to channel {ALERTS_CHANNEL}")
        except Exception as e:
            print(f"❌ Failed to send alert to channel: {e}")

async def post_init(application: Application):
    """
    Setup background tasks after bot initialization.
    """
    global _bot_app
    _bot_app = application
    
    from monitor import get_monitor
    monitor = get_monitor()
    asyncio.create_task(monitor.watch_new_pools(monitor_callback))
    print("✅ Background monitor started.")


if __name__ == '__main__':
    print('Starting BaseFlow Bot......')
    import asyncio
    
    # Configure request with longer timeouts for slower connections
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    
    # Build application with custom request settings
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(request)
        .post_init(post_init)
        .build()
    )

    # Default commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('prices', price_command))
    app.add_handler(CommandHandler('buysell', Buysell_command))
    app.add_handler(CommandHandler('wallet', CreateWallet_command))
    app.add_handler(CommandHandler('tip', tip_command))
    app.add_handler(CommandHandler('profile', profile_command))
    app.add_handler(CommandHandler('Trades', Trades_command))
    app.add_handler(CommandHandler('settings', Settings_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('referral', referral_command))
    app.add_handler(CommandHandler('leaderboard', Leaderboard_command))
    app.add_handler(CommandHandler('copytrade', Copytrading_command))
    app.add_handler(CommandHandler('ai', AI_intelligence_command))
    app.add_handler(CommandHandler('look', look_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    # Errors
    app.add_error_handler(error)

    # Bot Polling with longer timeout
    print('BaseFlow is now running...')
    print('Waiting for user interactions...')
    print('(If you see timeout errors, check your internet connection)')
    
    try:
        app.run_polling(
            poll_interval=3,
            timeout=30,
            drop_pending_updates=True  # Start fresh, ignore old messages
        )
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("\\nPossible causes:")
        print("1. No internet connection")
        print("2. Telegram is blocked in your network (try VPN)")
        print("3. Invalid bot token")
        print("4. Firewall blocking outgoing connections")
