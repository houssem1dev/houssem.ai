"""
Houssem AI - Authentication with Signup + Login.
"""

import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

import streamlit as st

from audit import audit
from users_db import create_user, get_user, user_exists

SESSION_TTL_MINUTES = 60 * 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
MIN_USERNAME_LEN = 3
MAX_USERNAME_LEN = 20
MIN_PASSWORD_LEN = 6


# ============================================================
# PASSWORDS
# ============================================================
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ============================================================
# LOCKOUT
# ============================================================
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


# ============================================================
# SESSIONS
# ============================================================
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


# ============================================================
# VALIDATION
# ============================================================
def _validate_signup(username: str, password: str, confirm: str) -> Optional[str]:
    username = username.strip()
    if not username or not password:
        return "⚠️ املأ جميع الحقول."
    if len(username) < MIN_USERNAME_LEN or len(username) > MAX_USERNAME_LEN:
        return f"⚠️ اسم المستخدم يجب أن يكون بين {MIN_USERNAME_LEN} و {MAX_USERNAME_LEN} أحرف."
    if not username.replace("_", "").replace("-", "").isalnum():
        return "⚠️ اسم المستخدم: أحرف، أرقام، شرطات فقط."
    if len(password) < MIN_PASSWORD_LEN:
        return f"⚠️ كلمة المرور يجب ألا تقل عن {MIN_PASSWORD_LEN} أحرف."
    if password != confirm:
        return "⚠️ كلمتا المرور غير متطابقتين."
    if user_exists(username):
        return "⚠️ اسم المستخدم موجود بالفعل."
    return None


# ============================================================
# UI - HEADER CARD
# ============================================================
def _render_header(subtitle: str):
    st.markdown(f"""
        <div style="max-width:420px;margin:60px auto 20px;padding:30px 32px;
                    background:rgba(255,255,255,0.06);backdrop-filter:blur(14px);
                    border:1px solid rgba(255,255,255,0.15);border-radius:20px;
                    box-shadow:0 8px 40px rgba(0,0,0,0.4);">
            <div style="text-align:center;font-size:2.4rem;">🇹🇳</div>
            <h2 style="text-align:center;margin:8px 0 4px;color:#fff;">Houssem AI</h2>
            <p style="text-align:center;color:#bdc3c7;font-size:0.9rem;margin-top:0;">
                {subtitle}
            </p>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# UI - LOGIN FORM
# ============================================================
def _login_tab():
    _render_header("سجّل الدخول للمتابعة")

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        username = st.text_input("👤 اسم المستخدم", key="login_user")
        password = st.text_input("🔒 كلمة المرور", type="password", key="login_pass")
        submit = st.button("🚀 دخول", use_container_width=True, key="login_btn")

        if submit:
            if not username or not password:
                st.error("⚠️ الرجاء إدخال جميع الحقول.")
                return

            locked, remaining = _check_lockout(username)
            if locked:
                st.error(f"🔒 الحساب مقفل مؤقتاً. حاول بعد {remaining} ثانية.")
                audit("login_locked", "Attempt on locked account",
                      user=username, level="WARNING")
                return

            user = get_user(username)
            if not user or not verify_password(password, user["password_hash"]):
                _record_failure(username)
                audit("login_failure", "Invalid credentials",
                      user=username, level="WARNING")
                remaining = MAX_LOGIN_ATTEMPTS - _attempts.get(username, (0,))[0]
                st.error(f"❌ بيانات خاطئة. محاولات متبقية: {max(remaining, 0)}")
                return

            _reset_attempts(username)
            st.session_state["auth"] = create_session(user["username"])
            audit("login_success", "User logged in", user=user["username"])
            st.rerun()


# ============================================================
# UI - SIGNUP FORM
# ============================================================
def _signup_tab():
    _render_header("أنشئ حساباً جديداً")

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        username = st.text_input("👤 اسم المستخدم", key="signup_user")
        password = st.text_input("🔒 كلمة المرور", type="password", key="signup_pass")
        confirm = st.text_input("🔒 تأكيد كلمة المرور", type="password", key="signup_confirm")
        submit = st.button("✨ إنشاء حساب", use_container_width=True, key="signup_btn")

        if submit:
            err = _validate_signup(username, password, confirm)
            if err:
                st.error(err)
                return

            try:
                pwd_hash = hash_password(password)
                ok = create_user(username.strip(), pwd_hash)
                if not ok:
                    st.error("⚠️ تعذّر إنشاء الحساب. جرّب اسماً آخر.")
                    return

                audit("signup_success", "New account created", user=username.strip())
                st.success("✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
                st.balloons()
            except Exception as e:
                audit("signup_error", str(e), level="ERROR")
                st.error("❌ حدث خطأ أثناء إنشاء الحساب.")


# ============================================================
# MAIN ENTRY
# ============================================================
def login_form() -> bool:
    """Show login/signup. Returns True if authenticated."""
    session = st.session_state.get("auth")
    if is_session_valid(session):
        return True

    tab_login, tab_signup = st.tabs(["🔑 تسجيل الدخول", "✨ إنشاء حساب"])
    with tab_login:
        _login_tab()
    with tab_signup:
        _signup_tab()

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
