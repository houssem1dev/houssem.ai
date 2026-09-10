"""
Houssem AI - Authentication module.
bcrypt password hashing + login attempt throttling.
"""

import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

import streamlit as st

from audit import audit

SESSION_TTL_MINUTES = 60 * 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def load_users() -> dict:
    try:
        users = st.secrets.get("users", [])
        return {u["username"]: u["password_hash"] for u in users}
    except Exception:
        return {}


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


_attempts: dict = {}


def _check_lockout(username: str) -> Tuple[bool, int]:
    record = _attempts.get(username)
    if not record:
        return False, 0
    count, first_ts, locked_until = record
    if locked_until and time.time() < locked_until:
        return True, int(locked_until - time.time())
    if locked_until and time.time() >= locked_until:
        _attempts.pop(username, None)
    return False, 0


def _record_failure(username: str):
    now = time.time()
    record = _attempts.get(username, (0, now, 0))
    count = record[0] + 1
    locked_until = 0
    if count >= MAX_LOGIN_ATTEMPTS:
        locked_until = now + LOCKOUT_MINUTES * 60
    _attempts[username] = (count, record[1], locked_until)


def _reset_attempts(username: str):
    _attempts.pop(username, None)


def create_session(username: str) -> dict:
    return {
        "user": username,
        "token": secrets.token_urlsafe(32),
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=SESSION_TTL_MINUTES),
    }


def is_session_valid(session: Optional[dict]) -> bool:
    if not session:
        return False
    return datetime.utcnow() < session["expires_at"]


def login_form() -> bool:
    session = st.session_state.get("auth")
    if is_session_valid(session):
        return True

    st.markdown("""
        <div style="max-width:420px;margin:80px auto;padding:36px 32px;
                    background:rgba(255,255,255,0.06);backdrop-filter:blur(14px);
                    border:1px solid rgba(255,255,255,0.15);border-radius:20px;
                    box-shadow:0 8px 40px rgba(0,0,0,0.4);">
            <div style="text-align:center;font-size:2.4rem;">🇹🇳</div>
            <h2 style="text-align:center;margin:8px 0 4px;color:#fff;">Houssem AI</h2>
            <p style="text-align:center;color:#bdc3c7;font-size:0.9rem;margin-top:0;">
                سجّل الدخول للمتابعة
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        username = st.text_input("👤 اسم المستخدم", key="login_user")
        password = st.text_input("🔒 كلمة المرور", type="password", key="login_pass")
        submit = st.button("🚀 دخول", use_container_width=True, key="login_btn")

    if submit:
        if not username or not password:
            st.error("⚠️ الرجاء إدخال جميع الحقول.")
            return False

        locked, remaining = _check_lockout(username)
        if locked:
            st.error(f"🔒 الحساب مقفل مؤقتاً. حاول بعد {remaining} ثانية.")
            audit("login_locked", "Attempt on locked account",
                  user=username, level="WARNING")
            return False

        users = load_users()
        stored = users.get(username)

        if not stored or not verify_password(password, stored):
            _record_failure(username)
            audit("login_failure", "Invalid credentials",
                  user=username, level="WARNING")
            remaining = MAX_LOGIN_ATTEMPTS - _attempts.get(username, (0,))[0]
            st.error(f"❌ بيانات خاطئة. محاولات متبقية: {max(remaining, 0)}")
            return False

        _reset_attempts(username)
        st.session_state["auth"] = create_session(username)
        audit("login_success", "User logged in", user=username)
        st.rerun()

    return False


def logout():
    user = st.session_state.get("auth", {}).get("user")
    if user:
        audit("logout", "User logged out", user=user)
    st.session_state.pop("auth", None)
    st.rerun()


def current_user() -> Optional[str]:
    session = st.session_state.get("auth")
    if is_session_valid(session):
        return session["user"]
    return None


def require_auth() -> str:
    if not login_form():
        st.stop()
    return current_user()
