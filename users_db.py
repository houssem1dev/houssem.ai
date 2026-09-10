"""
Houssem AI - SQLite user storage.
Single file database: users.db
"""

import sqlite3
import os
from typing import Optional

DB_FILE = "users.db"


def _get_conn() -> sqlite3.Connection:
    """Open (or create) the SQLite database."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Create the users table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


# Initialize on import
_init_db()


def user_exists(username: str) -> bool:
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        )
        return cur.fetchone() is not None


def create_user(username: str, password_hash: str) -> bool:
    username = username.strip()
    if user_exists(username):
        return False
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False


def get_user(username: str) -> Optional[dict]:
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT username, password_hash, created_at FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "username": row["username"],
            "password_hash": row["password_hash"],
            "created_at": row["created_at"],
        }


def list_users() -> list:
    """Return all users (for admin panel)."""
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT username, created_at FROM users ORDER BY created_at DESC"
        )
        return [dict(r) for r in cur.fetchall()]


def count_users() -> int:
    with _get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) as c FROM users")
        return cur.fetchone()["c"]
