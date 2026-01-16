import sqlite3


# Create a SQLite database and a table to store wallet information
# This code creates a SQLite database and a table to store wallet information if it doesn't already exist.




def init_db() -> None:
    """
    Initialize the SQLite database and create tables for wallets and trades.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Wallets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        address TEXT UNIQUE NOT NULL,
        private_key TEXT UNIQUE NOT NULL,
        balance REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Trades table for transaction tracking (Sprint 2)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_address TEXT NOT NULL,
        tx_hash TEXT UNIQUE NOT NULL,
        token_in TEXT NOT NULL,
        token_out TEXT NOT NULL,
        amount_in TEXT NOT NULL,
        amount_out TEXT NOT NULL,
        trade_type TEXT NOT NULL,
        status TEXT NOT NULL,
        gas_used INTEGER,
        block_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Users table (Sprint 3)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        referred_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Volume tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volume_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_address TEXT NOT NULL,
        volume_eth REAL NOT NULL,
        trade_count INTEGER NOT NULL,
        date TEXT NOT NULL,
        UNIQUE(token_address, date)
    )''')

    # Referral earnings table (Sprint 3)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referral_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL,
        referred_user_id INTEGER NOT NULL,
        amount_eth REAL DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # User Settings table (Sprint 4)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER PRIMARY KEY,
        slippage REAL DEFAULT 0.5,
        auto_buy_enabled INTEGER DEFAULT 0,
        auto_buy_amount REAL DEFAULT 0.1,
        auto_sell_tp REAL DEFAULT 100.0,
        auto_sell_sl REAL DEFAULT 50.0,
        gas_price_mode TEXT DEFAULT 'normal'
    )''')
    
    # Pending Orders table (Sprint 4)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pending_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_address TEXT NOT NULL,
        token_address TEXT NOT NULL,
        order_type TEXT NOT NULL, -- 'limit_buy', 'limit_sell', 'auto_buy'
        trigger_price REAL,
        amount_eth REAL,
        amount_tokens REAL,
        status TEXT DEFAULT 'pending', -- 'pending', 'filled', 'cancelled'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # AI Signals table (Sprint 5)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_address TEXT NOT NULL,
        signal_type TEXT NOT NULL, -- 'security', 'trend'
        insight TEXT NOT NULL,
        reliability REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Alerts table (Sprint 5)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        alert_type TEXT NOT NULL, -- 'price', 'new_listing', 'volume'
        target_address TEXT,
        target_value REAL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with all tables through Sprint 5 (AI & Alerts)")

  # The database file will be named 'wallet.db'
  # and will be created in the current working directory.
  # The connection object is used to interact with the database.

  # The cursor object is used to execute SQL commands.
  # The commit() method is used to save changes to the database.
  # The close() method is used to close the connection to the database.

  
async def create_wallet_db(user_id:int, address: str, private_key: str, balance: float) -> None:
  """
  Create a SQLite database and a table to store wallet information.
  """
  conn = sqlite3.connect('wallet.db')
  cursor = conn.cursor()
  cursor.execute("INSERT INTO wallets (user_id, address, private_key, balance) VALUES (?, ?, ?, ?)", 
                (user_id, address, private_key, balance))
  conn.commit()  # Save changes
  conn.close()



async def fetch_from_wallet(user_id:int, address:str, private_key:str) -> (str, str):
  """
  Fetch a wallet address and private key from the database.
  """
  # Connect to the SQLite database (or create it if it doesn't exist)
  conn = sqlite3.connect('wallet.db')
  cursor = conn.cursor()
  cursor.execute("SELECT private_key FROM wallets WHERE address = ?", (address,))
  result = cursor.fetchone()  # Returns (private_key,) or None

  cusor.execute("SELECT address FROM wallets WHERE private_key = ?", (private_key,))
  result2 = cursor.fetchone()

  if (result, result2):
     return (result, result2)
  else:
      return "Wallet not found."


def balance_check(address):
    """
    Check the balance of a wallet address.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM wallets WHERE address = ?", (address,))
    result = cursor.fetchone()  # Returns (balance,) or None

    conn.close()

    if result:
        return result[0]  # Return the balance
    else:
        return "Wallet not found."


def fetch_all_from_wallet(user_id:int)->[dict]:
    """
    Fetches all wallet addresses and private keys as a list of dicts.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()

    cursor.execute("SELECT address, private_key FROM wallets WHERE user_id = ?", (user_id,))
    wallets = cursor.fetchall()  # List of tuples

    conn.close()

    return [{"address": addr, "private_key": key} for addr, key in wallets]


async def delete_wallets_by_user(user_id: int) -> None:
    """
    Delete all wallets for a specific user.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wallets WHERE user_id = ?", (user_id,))
    conn.commit()  # Save changes
    conn.close()
    print(f"All wallets for user {user_id} have been deleted.")

async def delete_specific_wallet(user_id: int, addr: str) -> None:
    """
    Delete specific wallet from database based on user id.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wallets WHERE address = ? AND user_id = ?", (addr, user_id))
    conn.commit()
    conn.close()
    print(f"Wallet with address {addr} for user {user_id} has been deleted.")


# ============ Trade Functions (Sprint 2) ============

async def save_trade(
    user_id: int,
    wallet_address: str,
    tx_hash: str,
    token_in: str,
    token_out: str,
    amount_in: str,
    amount_out: str,
    trade_type: str,
    status: str,
    gas_used: int = None,
    block_number: int = None
) -> None:
    """
    Save a trade to the database for tracking.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (user_id, wallet_address, tx_hash, token_in, token_out, 
                          amount_in, amount_out, trade_type, status, gas_used, block_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, wallet_address, tx_hash, token_in, token_out, 
          amount_in, amount_out, trade_type, status, gas_used, block_number))
    conn.commit()
    conn.close()


def get_user_trades(user_id: int, limit: int = 10) -> list:
    """
    Get recent trades for a user.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tx_hash, token_in, token_out, amount_in, amount_out, 
               trade_type, status, created_at
        FROM trades 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    trades = cursor.fetchall()
    conn.close()
    
    return [{
        "tx_hash": t[0],
        "token_in": t[1],
        "token_out": t[2],
        "amount_in": t[3],
        "amount_out": t[4],
        "trade_type": t[5],
        "status": t[6],
        "created_at": t[7]
    } for t in trades]


def get_trade_count(user_id: int) -> int:
    """
    Get total trade count for a user.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM trades WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


async def update_volume_tracking(token_address: str, volume_eth: float) -> None:
    """
    Update volume tracking for a token (daily aggregation).
    """
    from datetime import date
    today = date.today().isoformat()
    
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Try to update existing record
    cursor.execute('''
        UPDATE volume_tracking 
        SET volume_eth = volume_eth + ?, trade_count = trade_count + 1
        WHERE token_address = ? AND date = ?
    ''', (volume_eth, token_address, today))
    
    # If no record exists, insert new one
    if cursor.rowcount == 0:
        cursor.execute('''
            INSERT INTO volume_tracking (token_address, volume_eth, trade_count, date)
            VALUES (?, ?, 1, ?)
        ''', (token_address, volume_eth, today))
    
    conn.commit()
    conn.close()


def get_total_volume() -> dict:
    """
    Get total volume statistics.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(volume_eth), SUM(trade_count) FROM volume_tracking')
    result = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM trades')
    unique_traders = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_volume_eth": result[0] or 0,
        "total_trades": result[1] or 0,
        "unique_traders": unique_traders or 0
    }

# ============ User & Referral Functions (Sprint 3) ============

async def register_user(user_id: int, username: str, referred_by: int = None) -> None:
    """
    Register a new user and their referrer if applicable.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO users (user_id, username, referred_by)
            VALUES (?, ?, ?)
        ''', (user_id, username, referred_by))
        conn.commit()
    
    conn.close()

def get_referral_stats(user_id: int) -> dict:
    """
    Get referral statistics for a user.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Count people referred
    cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (user_id,))
    referral_count = cursor.fetchone()[0]
    
    # Total earnings
    cursor.execute('SELECT SUM(amount_eth) FROM referral_earnings WHERE referrer_id = ?', (user_id,))
    total_earned = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "referral_count": referral_count,
        "total_earned_eth": total_earned
    }

def get_leaderboard(limit: int = 10) -> list:
    """
    Get top users by trading volume.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Sum up amount_in as a proxy for volume (expressed as strings in DB, so we cast)
    cursor.execute('''
        SELECT u.username, u.user_id, COUNT(t.id) as trades, SUM(CAST(t.amount_in AS REAL)) as volume
        FROM users u
        JOIN trades t ON u.user_id = t.user_id
        GROUP BY u.user_id
        ORDER BY volume DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "username": r[0] or f"User_{r[1]}",
        "trades": r[2],
        "volume": r[3]
    } for r in rows]

# ============ Automation & Settings (Sprint 4) ============

def get_user_settings(user_id: int) -> dict:
    """
    Get user-specific trading settings.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('SELECT slippage, auto_buy_enabled, auto_buy_amount, auto_sell_tp, auto_sell_sl, gas_price_mode FROM settings WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "slippage": row[0],
            "auto_buy_enabled": bool(row[1]),
            "auto_buy_amount": row[2],
            "auto_sell_tp": row[3],
            "auto_sell_sl": row[4],
            "gas_price_mode": row[5]
        }
    else:
        # Return default settings
        return {
            "slippage": 0.5,
            "auto_buy_enabled": False,
            "auto_buy_amount": 0.1,
            "auto_sell_tp": 100.0,
            "auto_sell_sl": 50.0,
            "gas_price_mode": "normal"
        }

async def update_user_settings(user_id: int, **kwargs) -> None:
    """
    Update user-specific trading settings.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    
    # Ensure settings entry exists
    cursor.execute('SELECT user_id FROM settings WHERE user_id = ?', (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO settings (user_id) VALUES (?)', (user_id,))
    
    # Dynamically update provided fields
    for key, value in kwargs.items():
        if key == "auto_buy_enabled":
            value = 1 if value else 0
        cursor.execute(f'UPDATE settings SET {key} = ? WHERE user_id = ?', (value, user_id))
    
    conn.commit()
    conn.close()

async def create_pending_order(user_id: int, wallet: str, token: str, order_type: str, amount_eth: float = None, amount_tokens: float = None, trigger_price: float = None) -> int:
    """
    Store a pending limit order or auto-trade trigger.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pending_orders (user_id, wallet_address, token_address, order_type, trigger_price, amount_eth, amount_tokens)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, wallet, token, order_type, trigger_price, amount_eth, amount_tokens))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

# ============ AI & Alerts (Sprint 5) ============

async def save_ai_signal(token_address: str, signal_type: str, insight: str, reliability: float = 1.0) -> None:
    """
    Save an AI-generated insight for a token.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_signals (token_address, signal_type, insight, reliability)
        VALUES (?, ?, ?, ?)
    ''', (token_address, signal_type, insight, reliability))
    conn.commit()
    conn.close()

def get_latest_ai_signals(limit: int = 5) -> list:
    """
    Fetch the most recent AI insights.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('SELECT token_address, signal_type, insight, created_at FROM ai_signals ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"token": r[0], "type": r[1], "insight": r[2], "time": r[3]} for r in rows]

async def create_alert(user_id: int, alert_type: str, target_address: str = None, target_value: float = None) -> None:
    """
    Create a new user alert.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (user_id, alert_type, target_address, target_value)
        VALUES (?, ?, ?, ?)
    ''', (user_id, alert_type, target_address, target_value))
    conn.commit()
    conn.close()

def get_user_alerts(user_id: int) -> list:
    """
    Fetch all active alerts for a user.
    """
    conn = sqlite3.connect('wallet.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, alert_type, target_address, target_value FROM alerts WHERE user_id = ? AND is_active = 1', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "target": r[2], "value": r[3]} for r in rows]