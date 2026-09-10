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
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    /* -------- Kill the black top bar -------- */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }

    /* Keep sidebar toggle alive even with header hidden */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        background: linear-gradient(135deg,#e74c3c,#c0392b) !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        box-shadow: 0 4px 15px rgba(231,76,60,0.6) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #fff !important;
        color: #fff !important;
        width: 24px !important;
        height: 24px !important;
    }

    /* -------- Base -------- */
    html, body, .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
        font-family: 'Cairo', sans-serif;
        color: #fff !important;
        overflow-x: hidden !important;
        -webkit-text-size-adjust: 100%;
    }
    h1,h2,h3,h4,h5,h6,p,span,div,label,small,strong { color:#fff !important; }
    *, *::before, *::after { box-sizing: border-box; }

    .block-container,
    section.main > div {
        padding: 0.8rem 0.8rem 4rem 0.8rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    /* -------- Title -------- */
    .custom-title {
        text-align: center;
        font-size: clamp(1.3rem, 5vw + 0.5rem, 2.6rem);
        font-weight: 900;
        color: #fff !important;
        margin: 0 0 0 0;
        text-shadow: 0 0 15px rgba(231,76,60,0.6);
        line-height: 1.15;
        word-break: break-word;
        padding: 0 4px;
    }
    .custom-subtitle {
        text-align: center;
        color: #bdc3c7 !important;
        font-size: clamp(0.7rem, 1.5vw + 0.5rem, 1rem);
        margin: 0.4rem 0 1rem 0;
        padding: 0 8px;
        line-height: 1.5;
    }

    /* -------- Welcome -------- */
    .welcome-box {
        text-align: center;
        padding: clamp(15px, 4vw, 30px) clamp(10px, 3vw, 20px);
        margin: 10px auto;
        max-width: 600px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
    }
    .welcome-box .flag { font-size: clamp(2rem, 6vw, 3.5rem); line-height: 1; }
    .welcome-box .title {
        font-size: clamp(1rem, 2.5vw, 1.4rem);
        font-weight: 700;
        margin: 10px 0 6px 0;
        line-height: 1.3;
    }
    .welcome-box .hint {
        font-size: clamp(0.75rem, 1.5vw, 0.95rem);
        color: #95a5a6 !important;
        line-height: 1.6;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%) !important;
        border-right: 2px solid rgba(231,76,60,0.4) !important;
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1rem 0.9rem 2rem 0.9rem !important;
    }
    section[data-testid="stSidebar"] * { color: #fff !important; }

    section[data-testid="stSidebar"] h2 {
        font-size: 1.3rem !important;
        font-weight: 900 !important;
        text-align: center;
        padding: 0.3rem 0 0.4rem 0;
        border-bottom: 2px solid rgba(231,76,60,0.4);
        margin-bottom: 0.8rem !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 0.95rem !important;
        color: #e74c3c !important;
        margin-top: 1rem !important;
        margin-bottom: 0.6rem !important;
        border-left: 3px solid #e74c3c;
        padding-left: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Dropdown (dark) */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(231,76,60,0.12) !important;
        border: 1px solid rgba(231,76,60,0.5) !important;
        color: #fff !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        min-height: 42px;
    }
    div[data-baseweb="popover"] * {
        background: #16213e !important;
        color: #fff !important;
    }
    ul[role="listbox"] { background: #16213e !important; }
    li[role="option"] {
        background: #16213e !important;
        color: #fff !important;
        font-size: 0.9rem !important;
        padding: 8px 12px !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: rgba(231,76,60,0.3) !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg,#e74c3c 0%,#c0392b 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 42px !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        transition: all 0.25s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231,76,60,0.5);
    }

    /* ======================================================
       USAGE BARS — redesigned, colorful, clean
       ====================================================== */
    .usage-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 8px;
    }
    .usage-item {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 10px 12px;
    }
    .usage-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .usage-label {
        color: #ecf0f1 !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .usage-count {
        color: #fff !important;
        font-weight: 900;
        font-size: 0.85rem;
        background: rgba(231,76,60,0.25);
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid rgba(231,76,60,0.4);
    }
    .usage-track {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.08);
        border-radius: 4px;
        overflow: hidden;
    }
    .usage-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.4s ease;
    }
    .usage-fill-green {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
        box-shadow: 0 0 8px rgba(46,204,113,0.5);
    }
    .usage-fill-yellow {
        background: linear-gradient(90deg, #f39c12, #f1c40f);
        box-shadow: 0 0 8px rgba(241,196,15,0.5);
    }
    .usage-fill-red {
        background: linear-gradient(90deg, #c0392b, #e74c3c);
        box-shadow: 0 0 8px rgba(231,76,60,0.5);
    }

    /* -------- Stat cards -------- */
    .stat-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: clamp(8px, 1.5vw, 14px) clamp(6px, 1vw, 12px);
        text-align: center;
        margin-bottom: 8px;
    }
    .stat-number {
        font-size: clamp(1rem, 1.5vw + 0.5rem, 1.5rem);
        font-weight: 900;
        color: #e74c3c !important;
        line-height: 1.1;
    }
    .stat-label {
        color: #ecf0f1 !important;
        font-size: clamp(0.65rem, 1vw + 0.3rem, 0.8rem);
        margin-top: 3px;
    }

    /* -------- Chat messages -------- */
    .stChatMessage {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: clamp(8px, 1.5vw, 14px) clamp(10px, 2vw, 16px) !important;
        margin-bottom: 10px !important;
        font-size: clamp(0.85rem, 1vw + 0.5rem, 1rem) !important;
        line-height: 1.6 !important;
        max-width: 100% !important;
        word-wrap: break-word;
    }
    .stChatMessage.user {
        background: rgba(231,76,60,0.12) !important;
        border: 1px solid rgba(231,76,60,0.35) !important;
    }
    .stChatMessage p {
        line-height: 1.6 !important;
        margin: 0 !important;
        word-wrap: break-word !important;
    }

    /* -------- Chat input -------- */
    div[data-testid="stChatInput"] {
        background: #16213e !important;
        border: 2px solid rgba(231,76,60,0.5) !important;
        border-radius: 12px !important;
        margin: 0 auto !important;
        max-width: 100% !important;
    }
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] input {
        color: #fff !important;
        font-size: clamp(0.95rem, 1vw + 0.5rem, 1rem) !important;
        background: transparent !important;
    }

    /* -------- Footer -------- */
    .footer-text {
        text-align: center;
        color: #7f8c8d !important;
        padding: 15px 8px;
        font-size: clamp(0.6rem, 0.5vw + 0.5rem, 0.8rem);
        line-height: 1.5;
        margin-top: 10px;
    }
    hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 0.8rem 0 !important;
    }

    /* ======================================================
       ADAPTIVE BREAKPOINTS
       ====================================================== */
    @media (max-width: 400px) {
        .block-container { padding: 0.5rem 0.5rem 4rem 0.5rem !important; }
    }
    @media (max-width: 768px) {
        .block-container { padding: 0.6rem 0.6rem 4rem 0.6rem !important; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        section[data-testid="stSidebar"] {
            min-width: 88vw !important;
            max-width: 88vw !important;
        }
    }
    @media (min-width: 1025px) and (max-width: 1440px) {
        .block-container { max-width: 1000px !important; margin: 0 auto !important; }
    }
    @media (min-width: 1441px) {
        .block-container { max-width: 1200px !important; margin: 0 auto !important; }
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
    st.markdown("""
        <div style="text-align:center;padding:6px 0 12px 0;">
            <div style="font-size:2rem;">⚡</div>
            <div style="font-size:1.3rem;font-weight:900;color:#e74c3c;">Houssem AI</div>
            <div style="font-size:0.7rem;color:#bdc3c7;">🛡️ استخدام مباشر بدون تسجيل</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🎯 المجال التحليلي")
    st.session_state.domain_choice = st.selectbox(
        "اختر المجال:",
        list(DOMAIN_MAP.keys()),
        index=list(DOMAIN_MAP.keys()).index(st.session_state.domain_choice),
        key="domain_selector",
        label_visibility="collapsed",
    )
    domain = st.session_state.domain_choice

    st.markdown("---")
    st.markdown("### 📊 استهلاكك")

    # ---- Custom colorful usage bars ----
    try:
        usage = rate_usage(client_ip)
        limits_map = {"minute": 15, "hour": 200, "day": 1500}
        icons_map = {"minute": "⏱️", "hour": "⏰", "day": "📅"}
        labels_map = {"minute": "الدقيقة", "hour": "الساعة", "day": "اليوم"}

        st.markdown('<div class="usage-container">', unsafe_allow_html=True)

        for window in ["minute", "hour", "day"]:
            count = usage.get(window, 0)
            limit = limits_map[window]
            icon = icons_map[window]
            label = labels_map[window]
            pct = (count / limit) * 100 if limit else 0

            # Color based on usage
            if pct < 50:
                fill_class = "usage-fill-green"
            elif pct < 85:
                fill_class = "usage-fill-yellow"
            else:
                fill_class = "usage-fill-red"

            st.markdown(f"""
                <div class="usage-item">
                    <div class="usage-header">
                        <span class="usage-label">{icon} {label}</span>
                        <span class="usage-count">{count} / {limit}</span>
                    </div>
                    <div class="usage-track">
                        <div class="usage-fill {fill_class}" style="width: {max(pct, 2)}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.caption("استهلاك غير متاح")

    st.markdown("---")
    st.markdown("### 📈 إحصائيات")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.conversation_count}</div>
                <div class="stat-label">رسائل</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">محادثة</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_visits}</div>
            <div class="stat-label">👥 زوار الموقع</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ إجراءات")

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
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

    st.markdown("---")
    st.caption(f"🌍 IP: `{client_ip}`")

# ============================================================
# MAIN AREA
# ============================================================
st.markdown('<h1 class="custom-title">⚡ Houssem AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="custom-subtitle">🇹🇳 أول ذكاء اصطناعي تونسي متقدم — مطور بواسطة حسام القسنطيني</p>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("""
        <div class="welcome-box">
            <div class="flag">🇹🇳</div>
            <div class="title">مرحباً بك في Houssem AI</div>
            <div class="hint">
                افتح القائمة ☰ واختر المجال<br>
                ثم اكتب سؤالك في الأسفل
            </div>
        </div>
    """, unsafe_allow_html=True)

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
    <div class="footer-text">
        🇹🇳 <strong>Houssem AI</strong> — Developed in Sfax, Tunisia<br>
        ⚡ Powered by Groq AI | © 2026
    </div>
""", unsafe_allow_html=True)
