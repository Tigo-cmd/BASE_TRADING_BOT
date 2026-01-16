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
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with wallets, trades, and volume_tracking tables")
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