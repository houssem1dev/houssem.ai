import time
from datetime import datetime
from collections import defaultdict

import streamlit as st
import requests
from groq import Groq

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Houssem AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# META
# ============================================================
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#0a0e1a">
""", unsafe_allow_html=True)

# ============================================================
# NEW DESIGN — Fresh, clean, adaptive
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Inter:wght@400;600;700&display=swap');

    /* ============================================================
       RESET
       ============================================================ */
    *, *::before, *::after {
        box-sizing: border-box;
        -webkit-tap-highlight-color: transparent;
    }
    html, body {
        margin: 0;
        padding: 0;
        background: #0a0e1a;
        font-family: 'Cairo', 'Inter', sans-serif;
        color: #e8eaf0;
        -webkit-text-size-adjust: 100%;
        overflow-x: hidden;
    }

    /* ============================================================
       HIDE STREAMLIT CHROME — softly
       ============================================================ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0;
    }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ============================================================
       APP BACKGROUND — single solid color, no gradient fighting
       ============================================================ */
    .stApp {
        background: #0a0e1a !important;
    }
    [data-testid="stAppViewContainer"] {
        background: #0a0e1a !important;
    }
    section.main {
        background: transparent !important;
    }

    /* ============================================================
       CONTAINER — adaptive padding
       ============================================================ */
    .block-container {
        padding: 1.25rem 1rem 6rem 1rem !important;
        max-width: 100% !important;
    }

    /* ============================================================
       TYPOGRAPHY
       ============================================================ */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, a {
        color: #e8eaf0 !important;
    }

    /* ============================================================
       HERO / HEADER
       ============================================================ */
    .hero {
        text-align: center;
        padding: 1rem 0 2rem 0;
        margin-bottom: 0.5rem;
    }
    .hero-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #ff4d4d, #c81e1e);
        border-radius: 18px;
        font-size: 1.8rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 8px 32px rgba(255,77,77,0.35);
    }
    .hero-title {
        font-size: clamp(1.5rem, 5vw, 2.2rem);
        font-weight: 900;
        color: #fff !important;
        line-height: 1.15;
        margin: 0.25rem 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: clamp(0.75rem, 2.5vw, 0.95rem);
        color: #8892a6 !important;
        font-weight: 500;
        margin-top: 0.35rem;
        line-height: 1.5;
        padding: 0 1rem;
    }

    /* ============================================================
       CARDS — universal building block
       ============================================================ */
    .card {
        background: #131824;
        border: 1px solid #1e2433;
        border-radius: 16px;
        padding: 1.1rem 1.15rem;
        margin-bottom: 0.85rem;
    }
    .card-accent {
        background: linear-gradient(135deg, #1a1f2e, #131824);
        border: 1px solid rgba(255,77,77,0.25);
        border-radius: 16px;
        padding: 1.1rem 1.15rem;
        margin-bottom: 0.85rem;
    }

    /* ============================================================
       WELCOME CARD
       ============================================================ */
    .welcome {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #131824, #0f1420);
        border: 1px solid #1e2433;
        border-radius: 20px;
        margin-bottom: 1rem;
    }
    .welcome-flag {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    .welcome-title {
        font-size: clamp(1.1rem, 3.5vw, 1.4rem);
        font-weight: 800;
        color: #fff !important;
        margin-bottom: 0.35rem;
    }
    .welcome-hint {
        font-size: clamp(0.8rem, 2.5vw, 0.9rem);
        color: #8892a6 !important;
        line-height: 1.6;
    }

    /* ============================================================
       CHAT MESSAGES
       ============================================================ */
    .stChatMessage {
        background: #131824 !important;
        border: 1px solid #1e2433 !important;
        border-radius: 16px !important;
        padding: 0.85rem 1rem !important;
        margin-bottom: 0.6rem !important;
        font-size: clamp(0.88rem, 2.5vw, 0.95rem) !important;
        line-height: 1.65 !important;
        color: #e8eaf0 !important;
    }
    .stChatMessage.user {
        background: linear-gradient(135deg, #2a1518, #1f1013) !important;
        border: 1px solid rgba(255,77,77,0.3) !important;
    }
    .stChatMessage p {
        color: #e8eaf0 !important;
        margin: 0 !important;
    }

    /* ============================================================
       CHAT INPUT — clean, floating
       ============================================================ */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stBottomBlockContainer"] {
        background: #0a0e1a !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0 !important;
    }
    div[data-testid="stChatInput"] {
        background: #131824 !important;
        border: 1.5px solid #2a3142 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #ff4d4d !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #e8eaf0 !important;
        background: transparent !important;
        font-size: 1rem !important;
    }
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #ff4d4d, #c81e1e) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    div[data-testid="stChatInput"] button svg {
        fill: #fff !important;
    }

    /* ============================================================
       SIDEBAR
       ============================================================ */
    section[data-testid="stSidebar"] {
        background: #0f1420 !important;
        border-right: 1px solid #1e2433 !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem 2rem 1rem !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e8eaf0 !important;
    }
    section[data-testid="stSidebar"] h3 {
        font-size: 0.8rem !important;
        color: #8892a6 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin: 1.25rem 0 0.6rem 0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: #1a1f2e !important;
        color: #e8eaf0 !important;
        border: 1px solid #2a3142 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        min-height: 42px !important;
        font-size: 0.88rem !important;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #232a3d !important;
        border-color: #3a4255 !important;
    }

    /* Dropdown */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #1a1f2e !important;
        border: 1px solid #2a3142 !important;
        color: #e8eaf0 !important;
        border-radius: 12px !important;
        min-height: 44px;
        font-size: 0.9rem !important;
    }
    div[data-baseweb="popover"] * {
        background: #1a1f2e !important;
        color: #e8eaf0 !important;
    }
    ul[role="listbox"] {
        background: #1a1f2e !important;
        border-radius: 12px !important;
    }
    li[role="option"] {
        background: #1a1f2e !important;
        color: #e8eaf0 !important;
        padding: 10px 14px !important;
        font-size: 0.88rem !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: #232a3d !important;
        color: #ff6b6b !important;
    }

    /* ============================================================
       USAGE — modern minimal
       ============================================================ */
    .usage-block {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }
    .usage-row {
        background: #131824;
        border: 1px solid #1e2433;
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
    }
    .usage-row-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .usage-row-label {
        color: #8892a6 !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .usage-row-value {
        color: #e8eaf0 !important;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }
    .usage-bar {
        width: 100%;
        height: 6px;
        background: #1e2433;
        border-radius: 3px;
        overflow: hidden;
    }
    .usage-bar-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.4s ease;
    }
    .fill-ok { background: #2ecc71; }
    .fill-mid { background: #f39c12; }
    .fill-high { background: #ff4d4d; }

    /* ============================================================
       STATS — minimal
       ============================================================ */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.6rem;
    }
    .stat-box {
        background: #131824;
        border: 1px solid #1e2433;
        border-radius: 12px;
        padding: 0.9rem 0.5rem;
        text-align: center;
    }
    .stat-box-wide {
        grid-column: 1 / -1;
    }
    .stat-box-num {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ff6b6b !important;
        line-height: 1;
        font-variant-numeric: tabular-nums;
    }
    .stat-box-label {
        font-size: 0.7rem;
        color: #8892a6 !important;
        margin-top: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }

    /* ============================================================
       SIDEBAR TOGGLE — clean
       ============================================================ */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
        z-index: 9999 !important;
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        background: #131824 !important;
        border: 1px solid #2a3142 !important;
        border-radius: 12px !important;
        padding: 8px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="collapsedControl"]:hover {
        border-color: #ff4d4d !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #e8eaf0 !important;
        color: #e8eaf0 !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* ============================================================
       FOOTER
       ============================================================ */
    .footer {
        text-align: center;
        color: #5a6478 !important;
        padding: 2rem 1rem 1rem 1rem;
        font-size: clamp(0.65rem, 2vw, 0.75rem);
        line-height: 1.7;
        border-top: 1px solid #1e2433;
        margin-top: 2rem;
    }
    .footer strong {
        color: #8892a6 !important;
    }

    /* ============================================================
       DIVIDERS
       ============================================================ */
    hr {
        border: none !important;
        border-top: 1px solid #1e2433 !important;
        margin: 1rem 0 !important;
    }

    /* ============================================================
       RESPONSIVE
       ============================================================ */

    /* Phones: tighter padding */
    @media (max-width: 640px) {
        .block-container {
            padding: 0.9rem 0.75rem 6rem 0.75rem !important;
        }
        .hero { padding: 0.5rem 0 1.25rem 0; }
        .hero-logo { width: 56px; height: 56px; font-size: 1.5rem; }
        .card, .card-accent { padding: 1rem; border-radius: 14px; }
        .stChatMessage {
            padding: 0.75rem 0.9rem !important;
            font-size: 0.88rem !important;
        }
        section[data-testid="stSidebar"] {
            min-width: 90vw !important;
            max-width: 90vw !important;
        }
    }

    /* Very small phones */
    @media (max-width: 380px) {
        .hero-title { font-size: 1.35rem; }
        .hero-subtitle { font-size: 0.72rem; }
        .stat-box-num { font-size: 1.2rem; }
    }

    /* Tablets */
    @media (min-width: 641px) and (max-width: 1024px) {
        .block-container {
            max-width: 720px !important;
            margin: 0 auto !important;
            padding: 1.5rem 1.5rem 6rem 1.5rem !important;
        }
    }

    /* Desktop */
    @media (min-width: 1025px) {
        .block-container {
            max-width: 820px !important;
            margin: 0 auto !important;
            padding: 2rem 1.5rem 5rem 1.5rem !important;
        }
        .hero { padding: 1.5rem 0 2.5rem 0; }
    }

    /* Reduce motion */
    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# GROQ CLIENT
# ============================================================
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"], max_retries=3, timeout=60.0)

client = get_groq_client()

# ============================================================
# IP + RATE LIMIT
# ============================================================
def get_client_ip() -> str:
    try:
        headers = st.context.headers
        xff = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        real_ip = headers.get("X-Real-Ip") or headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    except Exception:
        pass
    return "unknown"

client_ip = get_client_ip()

LIMITS = {
    "minute": (15, 60),
    "hour":   (200, 3600),
    "day":    (1500, 86400),
}

if "_rate_store" not in st.session_state:
    st.session_state._rate_store = defaultdict(list)

def rate_check(ip: str):
    now = time.time()
    store = st.session_state._rate_store
    key = f"ip:{ip}"
    for window, (limit, seconds) in LIMITS.items():
        store[f"{key}:{window}"] = [
            t for t in store[f"{key}:{window}"] if t > now - seconds
        ]
        if len(store[f"{key}:{window}"]) >= limit:
            return False, f"⏳ تجاوزت الحد ({limit} طلب). حاول لاحقاً."
    for window in LIMITS:
        store[f"{key}:{window}"].append(now)
    return True, ""

def rate_usage(ip: str):
    now = time.time()
    store = st.session_state._rate_store
    key = f"ip:{ip}"
    return {
        window: len([t for t in store[f"{key}:{window}"] if t > now - seconds])
        for window, (_limit, seconds) in LIMITS.items()
    }

# ============================================================
# VISITOR COUNTER
# ============================================================
if "counted_visit" not in st.session_state:
    try:
        requests.get("https://api.countapi.xyz/hit/houssem-ai-tn/visits", timeout=4)
    except Exception:
        pass
    st.session_state.counted_visit = True

@st.cache_data(ttl=60)
def get_total_visits():
    try:
        r = requests.get("https://api.countapi.xyz/get/houssem-ai-tn/visits", timeout=4)
        return r.json().get("value", 0)
    except Exception:
        return "—"

total_visits = get_total_visits()

# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0
if "domain_choice" not in st.session_state:
    st.session_state.domain_choice = "🔐 الأمن السيبراني والهندسة العكسية"

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
    # Brand block
    st.markdown("""
        <div style="text-align:center;padding:0.25rem 0 1rem 0;">
            <div style="
                display:inline-flex;
                width:48px;height:48px;
                background:linear-gradient(135deg,#ff4d4d,#c81e1e);
                border-radius:14px;
                align-items:center;justify-content:center;
                font-size:1.3rem;
                box-shadow:0 6px 24px rgba(255,77,77,0.35);
            ">⚡</div>
            <div style="font-size:1.05rem;font-weight:800;color:#fff;margin-top:0.5rem;">
                Houssem AI
            </div>
            <div style="font-size:0.72rem;color:#8892a6;margin-top:0.2rem;">
                استخدام مباشر بدون تسجيل
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Domain
    st.markdown("### المجال")
    st.session_state.domain_choice = st.selectbox(
        "المجال",
        list(DOMAIN_MAP.keys()),
        index=list(DOMAIN_MAP.keys()).index(st.session_state.domain_choice),
        key="domain_selector",
        label_visibility="collapsed",
    )
    domain = st.session_state.domain_choice

    st.markdown("---")

    # Usage
    st.markdown("### الاستهلاك")
    try:
        usage = rate_usage(client_ip)
        limits_map = {"minute": 15, "hour": 200, "day": 1500}
        icons_map = {"minute": "⏱", "hour": "⏰", "day": "📅"}
        labels_map = {"minute": "دقيقة", "hour": "ساعة", "day": "يوم"}

        st.markdown('<div class="usage-block">', unsafe_allow_html=True)
        for window in ["minute", "hour", "day"]:
            count = usage.get(window, 0)
            limit = limits_map[window]
            icon = icons_map[window]
            label = labels_map[window]
            pct = (count / limit) * 100 if limit else 0

            if pct < 50:
                fill_class = "fill-ok"
            elif pct < 85:
                fill_class = "fill-mid"
            else:
                fill_class = "fill-high"

            st.markdown(f"""
                <div class="usage-row">
                    <div class="usage-row-head">
                        <span class="usage-row-label">{icon} {label}</span>
                        <span class="usage-row-value">{count} / {limit}</span>
                    </div>
                    <div class="usage-bar">
                        <div class="usage-bar-fill {fill_class}" style="width:{max(pct,1)}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.caption("—")

    st.markdown("---")

    # Stats
    st.markdown("### الإحصائيات")
    st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-box-num">{st.session_state.conversation_count}</div>
                <div class="stat-box-label">رسائل</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-num">{len(st.session_state.messages)}</div>
                <div class="stat-box-label">محادثة</div>
            </div>
            <div class="stat-box stat-box-wide">
                <div class="stat-box-num">{total_visits}</div>
                <div class="stat-box-label">👥 زوار الموقع</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Actions
    st.markdown("### الإجراءات")

    if st.session_state.messages:
        chat_text = "\n".join(
            f"{'👤' if m['role'] == 'user' else '🤖'}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            "📥 تصدير",
            data=chat_text,
            file_name=f"houssem_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("🗑 مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

    st.markdown("---")
    st.caption(f"🌍 `{client_ip}`")

# ============================================================
# MAIN AREA — HERO
# ============================================================
st.markdown("""
    <div class="hero">
        <div class="hero-logo">⚡</div>
        <h1 class="hero-title">Houssem AI</h1>
        <p class="hero-subtitle">أول ذكاء اصطناعي تونسي متقدم — مطور بواسطة حسام القسنطيني</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# WELCOME
# ============================================================
if not st.session_state.messages:
    st.markdown("""
        <div class="welcome">
            <span class="welcome-flag">🇹🇳</span>
            <div class="welcome-title">مرحباً بك</div>
            <div class="welcome-hint">
                افتح القائمة ☰ واختر المجال<br>
                ثم اكتب سؤالك في الأسفل
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# INPUT
# ============================================================
if prompt := st.chat_input("اكتب سؤالك هنا..."):

    allowed, reason = rate_check(client_ip)
    if not allowed:
        st.warning(reason)
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_count += 1

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_instruction = BASE_IDENTITY + DOMAIN_MAP[domain]
            history = st.session_state.messages[-20:]
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

        except Exception as e:
            st.error(f"❌ خطأ تقني: {e}")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div class="footer">
        <strong>Houssem AI</strong> — Built in Sfax, Tunisia<br>
        Powered by Groq AI © 2026
    </div>
""", unsafe_allow_html=True)
