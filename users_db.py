"""
Houssem AI - Simple JSON-based user storage.
For production, swap this for SQLite/Postgres.
"""

import json
import os
from typing import Optional, Dict

USERS_FILE = "users.json"


def _load() -> Dict[str, dict]:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, dict]) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def user_exists(username: str) -> bool:
    return username.lower() in {u.lower() for u in _load().keys()}


def create_user(username: str, password_hash: str) -> bool:
    if user_exists(username):
        return False
    data = _load()
    data[username] = {"password_hash": password_hash}
    _save(data)
    return True


def get_user(username: str) -> Optional[dict]:
    data = _load()
    for stored_name, info in data.items():
        if stored_name.lower() == username.lower():
            return {"username": stored_name, **info}
    return None
