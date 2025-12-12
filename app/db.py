"""
Database module for SQLite persistence
Handles purchase transactions storage
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "companion_camp.db")


def init_db():
    """
    Initialize the database and create tables if they don't exist
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create purchases table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            coin_symbol TEXT NOT NULL,
            amount REAL NOT NULL,
            tx_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def insert_purchase(username: str, coin_symbol: str, amount: float, tx_hash: str) -> int:
    """
    Insert a new purchase record into the database
    
    Args:
        username: Username of the purchaser
        coin_symbol: Symbol of the coin purchased (e.g., "BONK", "WIF")
        amount: Amount of coins purchased
        tx_hash: Transaction hash from blockchain
    
    Returns:
        int: The ID of the inserted record
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (username, coin_symbol, amount, tx_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, coin_symbol.upper(), amount, tx_hash, datetime.now().isoformat()))
        conn.commit()
        return cursor.lastrowid


def get_history_by_username(username: str) -> List[Dict]:
    """
    Get purchase history for a specific username
    
    Args:
        username: Username to query
    
    Returns:
        List[Dict]: List of purchase records
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, coin_symbol, amount, tx_hash, created_at
            FROM purchases
            WHERE username = ?
            ORDER BY created_at DESC
        """, (username,))
        
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "username": row["username"],
                "coin_symbol": row["coin_symbol"],
                "amount": row["amount"],
                "tx_hash": row["tx_hash"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

