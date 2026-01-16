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

if not TOKEN:
    print("❌ Error: BASEFLOW_BOT_API not found in .env file!")
    print("Please make sure your .env file contains: BASEFLOW_BOT_API=your_bot_token")
    exit(1)


if __name__ == '__main__':
    print('Starting BaseFlow Bot......')
    
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
