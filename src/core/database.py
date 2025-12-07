"""Database operations for trading simulation"""
import sqlite3
import json
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

DB_PATH = Path("data/trading.db")

def init_database():
    """Initialize database with required tables"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Accounts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        name TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """)
    
    # Market data cache table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        date TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """)
    
    # Activity logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Account operations
def write_account(name: str, data: Dict[str, Any]):
    """Save account data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO accounts (name, data) VALUES (?, ?)",
        (name.lower(), json.dumps(data))
    )
    conn.commit()
    conn.close()

def read_account(name: str) -> Optional[Dict[str, Any]]:
    """Load account data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM accounts WHERE name = ?", (name.lower(),))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

# Market data operations
def write_market(date: str, data: Dict[str, float]):
    """Cache market data for a date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO market_data (date, data) VALUES (?, ?)",
        (date, json.dumps(data))
    )
    conn.commit()
    conn.close()

def read_market(date: str) -> Optional[Dict[str, float]]:
    """Load cached market data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM market_data WHERE date = ?", (date,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

# Logging operations
def write_log(name: str, log_type: str, message: str):
    """Write activity log"""
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%H:%M:%S")
    cursor.execute(
        "INSERT INTO logs (name, timestamp, type, message) VALUES (?, ?, ?, ?)",
        (name.lower(), timestamp, log_type, message)
    )
    conn.commit()
    conn.close()

def read_log(name: str, last_n: int = 10) -> List[Tuple[str, str, str]]:
    """Read recent activity logs"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, type, message FROM logs WHERE name = ? ORDER BY id DESC LIMIT ?",
        (name.lower(), last_n)
    )
    results = cursor.fetchall()
    conn.close()
    return list(reversed(results))

# Initialize database on import
init_database()
