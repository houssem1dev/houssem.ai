import os
import time
from datetime import datetime

import streamlit as st
from groq import Groq

from auth import require_auth, logout
from audit import audit
from rate_limit import RedisRateLimiter
from security import (
    validate_input,
    sanitize_input,
    build_system_prompt,
    trim_history,
    hash_session_id,
    MAX_MESSAGES_IN_HISTORY,
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Houssem AI | أول ذكاء اصطناعي تونسـي",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME CSS — responsive + sidebar always visible
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    /* ---------- Hide Streamlit chrome, keep sidebar toggle ---------- */
    #MainMenu, footer, .stDeployButton, .stToolbar,
    div[data-testid="stToolbar"], div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
        display: none;
    }

    /* Keep header transparent (so the > toggle arrow stays visible) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        height: auto !important;
    }

    /* Make the sidebar toggle arrow big, red, and obvious */
    button[kind="header"],
    button[data-testid="stSidebarCollapsedControl"],
    button[data-testid="baseButton-header"] {
        color: #fff !important;
        background: rgba(231,76,60,0.9) !important;
        border-radius: 8px !important;
        visibility: visible !important;
        display: inline-flex !important;
        margin: 8px !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 12px rgba(231,76,60,0.5) !important;
    }

    /* ---------- Force sidebar to stay visible ---------- */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        background: rgba(22,33,62,0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
        min-width: 280px !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* ---------- Base ---------- */
    html, body, .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
        font-family: 'Cairo', sans-serif;
        color: #fff;
        -webkit-text-size-adjust: 100%;
        overflow-x: hidden;
    }
    h1,h2,h3,h4,h5,h6,p,span,div,label { color:#fff !important; }

    .block-container {
        padding: 1rem 0.8rem 2rem 0.8rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* ---------- Header ---------- */
    .custom-title {
        text-align: center;
        font-size: clamp(1.8rem, 6vw, 3rem);
        font-weight: 900;
        color: #fff;
        margin-bottom: 0;
        text-shadow: 0 0 20px rgba(231,76,60,0.5);
        line-height: 1.2;
    }
    .custom-subtitle {
        text-align: center;
        color: #bdc3c7 !important;
        font-size: clamp(0.8rem, 2.6vw, 1.1rem);
        margin-bottom: 1.5rem;
        padding: 0 0.5rem;
    }

    /* ---------- Stat cards ---------- */
    .stat-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: clamp(12px, 3vw, 20px);
        text-align: center;
        box-shadow: 0 4px 30px rgba(0,0,0,0.1);
        margin-bottom: 12px;
    }
    .stat-number {
        font-size: clamp(1.4rem, 5vw, 2.5rem);
        font-weight: 900;
        color: #e74c3c !important;
        line-height: 1;
    }
    .stat-label {
        color: #ecf0f1 !important;
        font-size: clamp(0.7rem, 2.2vw, 0.9rem);
        margin-top: 5px;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: linear-gradient(135deg,#e74c3c 0%,#c0392b 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(231,76,60,0.3);
        min-height: 44px;
        padding: 0.6rem 1rem;
        font-size: clamp(0.85rem, 2.5vw, 1rem);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231,76,60,0.5);
    }

    /* ---------- Chat messages ---------- */
    .stChatMessage {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: clamp(0.85rem, 2.4vw, 1rem);
    }
    .stChatMessage.user {
        background: rgba(231,76,60,0.1);
        border: 1px solid rgba(231,76,60,0.3);
    }

    /* ---------- Inputs (16px prevents iOS zoom) ---------- */
    .stTextInput input,
    .stTextArea textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-size: 16px !important;
        min-height: 44px;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border: 1px solid #e74c3c !important;
    }

    /* ---------- Chat input ---------- */
    div[data-testid="stChatInput"] {
        background: rgba(22,33,62,0.95) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stChatInput"] input,
    div[data-testid="stChatInput"] textarea {
        color: #fff !important;
        font-size: 16px !important;
    }

    /* ---------- Tabs (login / signup) ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: clamp(0.8rem, 2.5vw, 1rem);
        padding: 0.5rem 1rem;
    }

    /* Sidebar buttons smaller */
    section[data-testid="stSidebar"] .stButton > button {
        font-size: 0.9rem;
    }

    /* ---------- Footer ---------- */
    .footer-text {
        text-align: center;
        color: #95a5a6 !important;
        padding: 20px 10px;
        font-size: clamp(0.7rem, 2.2vw, 0.9rem);
        line-height: 1.5;
    }

    hr { border-color: rgba(255,255,255,0.1) !important; margin: 1rem 0; }

    /* ---------- Responsive: phones ---------- */
    @media (max-width: 768px) {
        .block-container { padding: 0.8rem 0.6rem 2rem 0.6rem; }
        .custom-title { font-size: clamp(1.6rem, 8vw, 2.2rem); }
        .custom-subtitle { font-size: 0.85rem; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }

    @media (max-width: 480px) {
        .block-container { padding: 0.6rem 0.4rem 1.5rem 0.4rem; }
        .custom-title { font-size: 1.6rem; }
        .stat-number { font-size: 1.4rem; }
        .stButton > button { font-size: 0.85rem; padding: 0.55rem 0.9rem; }
    }

    @media (max-height: 500px) and (orientation: landscape) {
        .custom-title { font-size: 1.5rem; }
        .custom-subtitle { display: none; }
    }

    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container { max-width: 900px; }
    }

    @media (min-width: 1600px) {
        .block-container { max-width: 1400px; }
    }

    @media (hover: none) {
        .stButton > button:hover { transform: none; }
    }

    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# AUTH GATE
# ============================================================
username = require_auth()

# ============================================================
# CACHED RESOURCES
# ============================================================
@st.cache_resource(show_spinner=False)
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"], max_retries=3, timeout=60.0)


@st.cache_resource(show_spinner=False)
def get_rate_limiter():
    redis_url = st.secrets.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisRateLimiter(redis_url)


client = get_groq_client()
limiter = get_rate_limiter()

# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = hash_session_id(f"{username}:{time.time()}")

# ============================================================
# HEADER
# ============================================================
st.markdown('<h1 class="custom-title">⚡ Houssem AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="custom-subtitle">🇹🇳 أول ذكاء اصطناعي تونسي متقدم — مطور بواسطة حسام القسنطيني</p>',
    unsafe_allow_html=True,
)

# ============================================================
# DOMAIN MAP
# ============================================================
DOMAIN_MAP = {
    "🔐 الأمن السيبراني والهندسة العكسية":
        "You are a Cybersecurity Architect specializing in defensive security, "
        "reverse engineering, and ethical hacking. Provide detailed technical "
        "analysis. Refuse requests to create real-world malware or attack live systems.",
    "💻 هندسة البرمجيات وتطوير الويب":
        "You are a Senior Software Architect. Provide production-ready, "
        "well-documented code with best practices.",
    "📈 استراتيجيات التداول والأسواق":
        "You are a Quantitative Trader. Provide market analysis with clear "
        "risk disclaimers. Never guarantee profits.",
    "📱 التسويق الرقمي ونمو الأعمال":
        "You are a Growth Marketing Strategist. Provide data-driven, ethical strategies.",
    "📰 التحليل الاستراتيجي والأخبار التقنية":
        "You are a Tech Intelligence Analyst. Provide objective, well-sourced analysis.",
}
BASE_IDENTITY = "You are Houssem AI, created by Houssem Kessentini. "

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f"### 👤 {username}")
    st.caption("🛡️ جلسة موثقة")
    st.markdown("---")

    st.markdown("### ⚙️ لوحة التحكم")
    domain = st.selectbox(
        "🎯 المجال التحليلي:",
        list(DOMAIN_MAP.keys()),
        key="domain_selector",
    )

    st.markdown("---")
    st.markdown("### 📊 الاستهلاك")

    try:
        usage = limiter.get_usage(st.session_state.session_id)
        limits_map = {"minute": 15, "hour": 200, "day": 1500}
        labels_map = {"minute": "دقيقة", "hour": "ساعة", "day": "يوم"}
        for window, count in usage.items():
            limit = limits_map.get(window, 1)
            label = labels_map.get(window, window)
            pct = min(count / limit, 1.0) if limit else 0.0
            st.progress(pct, text=f"{label}: {count}/{limit}")
    except Exception:
        st.caption("معلومات الاستهلاك غير متاحة.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.conversation_count}</div>
                <div class="stat-label">المحادثات</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">الرسائل</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.messages:
        chat_text = "\n".join(
            f"{'👤' if m['role'] == 'user' else '🤖'}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            "📥 تصدير المحادثة",
            data=chat_text,
            file_name=f"houssem_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        audit("chat_cleared", "User cleared chat",
              session=st.session_state.session_id, user=username)
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        logout()

    # ---------- Admin Panel ----------
    ADMIN_USERS = ["houssem", "zaineb"]   # <-- add admin usernames here
    if username in ADMIN_USERS:
        with st.expander("🛠️ Admin Panel"):
            try:
                from users_db import list_users, count_users
                st.markdown(f"**Total users:** {count_users()}")
                for u in list_users():
                    st.markdown(f"- `{u['username']}` — {str(u['created_at'])[:10]}")
            except Exception as e:
                st.caption(f"Admin data unavailable: {e}")

    st.markdown(
        f'<div style="text-align:center;font-size:0.7rem;color:#7f8c8d;">'
        f'Session: <code>{st.session_state.session_id}</code></div>',
        unsafe_allow_html=True,
    )

# ============================================================
# WELCOME
# ============================================================
if not st.session_state.messages:
    st.markdown(f"""
        <div style="text-align:center;padding:40px;color:#95a5a6;">
            <div style="font-size:50px;">🇹🇳</div>
            <div style="font-size:1.5rem;font-weight:700;margin:10px 0;color:#fff;">
                مرحباً {username}
            </div>
            <div>اكتب سؤالك في الأسفل وابدأ التحليل الذكي</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('<hr>', unsafe_allow_html=True)

# ============================================================
# INPUT HANDLING
# ============================================================
if prompt := st.chat_input("اكتب سؤالك هنا..."):

    sid = st.session_state.session_id

    # --- 1. Rate limit ---
    allowed, reason = limiter.check(sid)
    if not allowed:
        audit("rate_limit_hit", reason, session=sid, user=username,
              domain=domain, level="WARNING")
        st.warning(reason)
        st.stop()

    # --- 2. Validate ---
    ok, err = validate_input(prompt)
    if not ok:
        event = "harmful_blocked" if "غير مسموح" in err else "injection_blocked"
        audit(event, err, session=sid, user=username, domain=domain,
              level="WARNING", preview=prompt[:120])
        st.error(err)
        st.stop()

    # --- 3. Sanitize ---
    safe_prompt = sanitize_input(prompt)

    # --- 4. Store ---
    st.session_state.messages.append({"role": "user", "content": safe_prompt})
    st.session_state.conversation_count += 1

    audit("chat_request", f"len={len(safe_prompt)}",
          session=sid, user=username, domain=domain,
          preview=safe_prompt[:120])

    with st.chat_message("user"):
        st.markdown(safe_prompt)

    # --- 5. LLM call (streaming) ---
    with st.chat_message("assistant"):
        try:
            system_instruction = build_system_prompt(BASE_IDENTITY, DOMAIN_MAP[domain])
            history = trim_history(
                st.session_state.messages, MAX_MESSAGES_IN_HISTORY
            )

            api_messages = [{"role": "system", "content": system_instruction}]
            api_messages.extend(
                {"role": m["role"], "content": m["content"]} for m in history
            )

            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=api_messages,
                temperature=0.4,
                max_tokens=2048,
                stream=True,
            )

            full_response = ""
            placeholder = st.empty()
            buffer = []

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    buffer.append(chunk.choices[0].delta.content)
                    if len(buffer) >= 5:
                        full_response += "".join(buffer)
                        buffer.clear()
                        placeholder.markdown(full_response + "▌")

            if buffer:
                full_response += "".join(buffer)
            placeholder.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

            audit("chat_response", f"len={len(full_response)}",
                  session=sid, user=username, domain=domain)

        except Exception as e:
            audit("chat_error", str(e), session=sid, user=username,
                  level="ERROR")
            st.error("❌ حدث خطأ تقني. الرجاء المحاولة مرة أخرى.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div class="footer-text">
        🇹🇳 Developed with ❤️ in <strong>Sfax, Tunisia</strong>
        by <strong>Houssem Kessentini</strong> 🇹🇳<br>
        ⚡ Powered by Groq AI | 🛡️ Secured | © 2026
    </div>
""", unsafe_allow_html=True)
