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
TOKEN: Final = TELEGRAM_TOKEN

    exit(1)

async def monitor_callback(token_address, pool_address):
    """
    Called by the monitor when a new pool is detected.
    """
    from store_to_db import save_ai_signal, get_ai_service
    # Broadcast to registered users (simplified for beta)
    # In a real app, we would query users who enabled 'listing_alerts'
    print(f"🚀 New Pool Detected: {token_address} at {pool_address}")
    
    # We could also trigger an automatic AI analysis here
    # and save it to the DB so users can see it in their dashboard.
    await save_ai_signal(token_address, "listing", f"New pool detected at {pool_address}")

async def post_init(application: Application):
    """
    Setup background tasks after bot initialization.
    """
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
