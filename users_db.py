"""
Houssem AI - User storage.
Uses Supabase (Postgres) when DATABASE_URL is set.
Falls back to local SQLite for development.
"""

import os
import sqlite3
from typing import Optional

import streamlit as st

# ============================================================
# Detect backend
# ============================================================
DATABASE_URL = None
try:
    DATABASE_URL = st.secrets.get("DATABASE_URL")
except Exception:
    pass

print(f"[users_db] DATABASE_URL detected: {bool(DATABASE_URL)}")


# ============================================================
# SUPABASE / POSTGRES BACKEND
# ============================================================
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from contextlib import contextmanager

    @contextmanager
    def _pg_conn():
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def user_exists(username: str) -> bool:
        with _pg_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE lower(username) = lower(%s)",
                (username.strip(),),
            )
            return cur.fetchone() is not None

    def create_user(username: str, password_hash: str) -> bool:
        if user_exists(username):
            return False
        try:
            with _pg_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username.strip(), password_hash),
                )
            return True
        except Exception as e:
            print(f"[users_db/postgres] create_user error: {e}")
            return False

    def get_user(username: str) -> Optional[dict]:
        with _pg_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT username, password_hash, created_at FROM users WHERE lower(username) = lower(%s)",
                (username.strip(),),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def list_users() -> list:
        with _pg_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT username, created_at FROM users ORDER BY created_at DESC"
            )
            return [dict(r) for r in cur.fetchall()]

    def count_users() -> int:
        with _pg_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as c FROM users")
            return cur.fetchone()["c"]

    print("[users_db] Using Supabase (Postgres) backend")


# ============================================================
# SQLITE BACKEND (local dev fallback)
# ============================================================
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "users.db")

    def _get_conn() -> sqlite3.Connection:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db() -> None:
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
        except Exception as e:
            print(f"[users_db/sqlite] create_user error: {e}")
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
        with _get_conn() as conn:
            cur = conn.execute(
                "SELECT username, created_at FROM users ORDER BY created_at DESC"
            )
            return [dict(r) for r in cur.fetchall()]

    def count_users() -> int:
        with _get_conn() as conn:
            cur = conn.execute("SELECT COUNT(*) as c FROM users")
            return cur.fetchone()["c"]

    print(f"[users_db] Using local SQLite at: {DB_FILE}")
