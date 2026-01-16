#!/usr/bin/python3 env
"""
swell trading bot implentation and intergration
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
  CommandHandler, 
  MessageHandler, 
  filters, 
  ContextTypes,
  CallbackQueryHandler
)
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
# Telegram bot token from BotFather
TELEGRAM_TOKEN = os.getenv('SWELL_BOT_API')
TOKEN: Final = TELEGRAM_TOKEN


if __name__ == '__main__':
    print('Starting Bot......')
    app = Application.builder().token(TOKEN).build()

    # default commands
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

    # bot Polling
    print('Polling......')
    print('Waiting For User Input......')
    app.run_polling(poll_interval=3)
