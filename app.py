import time
from datetime import datetime, date
from collections import defaultdict

import streamlit as st
import requests
from groq import Groq

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Houssem AI | أول ذكاء اصطناعي تونسـي",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    /* Hide Streamlit chrome */
    #MainMenu, footer, .stDeployButton,
    div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* Base */
    html, body, .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
        font-family: 'Cairo', sans-serif;
        color: #fff !important;
    }
    h1,h2,h3,h4,h5,h6,p,span,div,label,small,strong { color:#fff !important; }

    /* ==== SIDEBAR ==== */
    section[data-testid="stSidebar"] {
        background: #16213e !important;
        border-right: 2px solid rgba(231,76,60,0.5) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #fff !important;
    }

    /* Dropdown in sidebar — dark */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(231,76,60,0.15) !important;
        border: 1px solid rgba(231,76,60,0.5) !important;
        color: #fff !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #fff !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="popover"] * {
        color: #fff !important;
        background: #16213e !important;
    }
    ul[role="listbox"] {
        background: #16213e !important;
    }
    li[role="option"] {
        background: #16213e !important;
        color: #fff !important;
    }
    li[role="option"]:hover {
        background: rgba(231,76,60,0.3) !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg,#e74c3c 0%,#c0392b 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 40px !important;
        font-size: 0.9rem !important;
        width: 100% !important;
    }

    /* Progress bars in sidebar */
    section[data-testid="stSidebar"] .stProgress > div > div > div {
        background: linear-gradient(90deg, #e74c3c, #c0392b) !important;
    }
    section[data-testid="stSidebar"] .stProgress > div > div {
        background: rgba(255,255,255,0.1) !important;
    }

    /* Main container */
    .block-container {
        padding: 1rem 0.8rem 4rem 0.8rem;
        max-width: 1000px;
    }

    /* Header */
    .custom-title {
        text-align: center;
        font-size: clamp(1.6rem, 5vw, 2.6rem);
        font-weight: 900;
        color: #fff;
        margin: 0.5rem 0 0 0;
        text-shadow: 0 0 20px rgba(231,76,60,0.5);
        line-height: 1.2;
    }
    .custom-subtitle {
        text-align: center;
        color: #bdc3c7 !important;
        font-size: clamp(0.75rem, 2.2vw, 1rem);
        margin-bottom: 1rem;
        padding: 0 0.5rem;
        line-height: 1.5;
    }

    /* Stat cards */
    .stat-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        margin-bottom: 8px;
    }
    .stat-number {
        font-size: clamp(1.1rem, 3.5vw, 1.5rem);
        font-weight: 900;
        color: #e74c3c !important;
        line-height: 1.1;
    }
    .stat-label {
        color: #ecf0f1 !important;
        font-size: clamp(0.65rem, 2vw, 0.8rem);
        margin-top: 4px;
    }

    /* Chat messages */
    .stChatMessage {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: 10px 14px !important;
        margin-bottom: 10px !important;
        font-size: clamp(0.85rem, 2.3vw, 1rem) !important;
    }
    .stChatMessage.user {
        background: rgba(231,76,60,0.12) !important;
        border: 1px solid rgba(231,76,60,0.35) !important;
    }
    .stChatMessage p {
        line-height: 1.6 !important;
        margin: 0 !important;
    }

    /* Chat input at bottom */
    div[data-testid="stChatInput"] {
        background: #16213e !important;
        border: 1px solid rgba(231,76,60,0.4) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] input {
        color: #fff !important;
        font-size: 16px !important;
        background: transparent !important;
    }

    /* Welcome card */
    .welcome-box {
        text-align: center;
        padding: 30px 15px;
        color: #bdc3c7;
    }
    .welcome-box .flag {
        font-size: clamp(2rem, 8vw, 3rem);
    }
    .welcome-box .title {
        font-size: clamp(1.1rem, 3.5vw, 1.4rem);
        font-weight: 700;
        margin: 10px 0;
        color: #fff;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #7f8c8d !important;
        padding: 15px 10px;
        font-size: clamp(0.65rem, 2vw, 0.8rem);
        line-height: 1.6;
        margin-top: 20px;
    }

    hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 0.8rem 0 !important;
    }

    /* ==== SIDEBAR TOGGLE — always visible on mobile ==== */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        color: #fff !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #fff !important;
        width: 24px !important;
        height: 24px !important;
    }

    /* ==== MOBILE TWEAKS ==== */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem 0.6rem 5rem 0.6rem;
        }
        .custom-title { margin-top: 0.3rem; }
        .custom-subtitle { margin-bottom: 0.8rem; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        .stChatMessage {
            padding: 8px 12px !important;
            font-size: 0.9rem !important;
        }
    }

    @media (max-width: 480px) {
        .block-container { padding: 0.4rem 0.5rem 5rem 0.5rem; }
        .custom-title { font-size: 1.4rem; }
        .custom-subtitle { font-size: 0.75rem; }
        .stat-number { font-size: 1.1rem; }
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
    return Groq(
        api_key=st.secrets["GROQ_API_KEY"],
        max_retries=3,
        timeout=60.0,
    )

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
# VISITOR COUNTER (persistent via CountAPI)
# ============================================================
if "counted_visit" not in st.session_state:
    try:
        requests.get(
            "https://api.countapi.xyz/hit/houssem-ai-tn/visits",
            timeout=4
        )
    except Exception:
        pass
    st.session_state.counted_visit = True

@st.cache_data(ttl=60)
def get_total_visits():
    try:
        r = requests.get(
            "https://api.countapi.xyz/get/houssem-ai-tn/visits",
            timeout=4
        )
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
    st.markdown("## ⚡ Houssem AI")
    st.caption("🛡️ بدون تسجيل — استخدام مباشر")
    st.markdown("---")

    st.markdown("### ⚙️ لوحة التحكم")
    st.session_state.domain_choice = st.selectbox(
        "🎯 المجال التحليلي:",
        list(DOMAIN_MAP.keys()),
        index=list(DOMAIN_MAP.keys()).index(st.session_state.domain_choice),
        key="domain_selector",
    )
    domain = st.session_state.domain_choice

    st.markdown("---")
    st.markdown("### 📊 استهلاكك")

    try:
        usage = rate_usage(client_ip)
        limits_map = {"minute": 15, "hour": 200, "day": 1500}
        labels_map = {"minute": "دقيقة", "hour": "ساعة", "day": "يوم"}
        for window, count in usage.items():
            limit = limits_map.get(window, 1)
            label = labels_map.get(window, window)
            pct = min(count / limit, 1.0) if limit else 0.0
            st.progress(pct, text=f"{label}: {count}/{limit}")
    except Exception as e:
        st.caption(f"استهلاك غير متاح: {e}")

    st.markdown("---")

    st.markdown("### 👥 الزوار")
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_visits}</div>
            <div class="stat-label">إجمالي الزيارات</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.conversation_count}</div>
                <div class="stat-label">الرسائل</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">المحادثة</div>
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
            <div>اختر المجال من القائمة الجانبية ☰ ثم اكتب سؤالك في الأسفل</div>
        </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('<hr>', unsafe_allow_html=True)

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
        🇹🇳 Developed with ❤️ in <strong>Sfax, Tunisia</strong>
        by <strong>Houssem Kessentini</strong> 🇹🇳<br>
        ⚡ Powered by Groq AI | 🛡️ Secured | © 2026
    </div>
""", unsafe_allow_html=True)
