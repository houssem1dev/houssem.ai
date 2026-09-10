import time
from datetime import datetime

import streamlit as st
from groq import Groq

from security import (
    validate_input,
    sanitize_input,
    build_system_prompt,
    trim_history,
)
from rate_limit import RedisRateLimiter

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
# THEME CSS
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    #MainMenu, footer, .stDeployButton,
    div[data-testid="stToolbar"], div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        height: auto !important;
        min-height: 40px !important;
    }

    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        visibility: visible !important;
        display: inline-flex !important;
        opacity: 1 !important;
        color: #fff !important;
        background: rgba(231,76,60,0.95) !important;
        border-radius: 8px !important;
        margin: 6px !important;
        padding: 6px !important;
        z-index: 9999999 !important;
        box-shadow: 0 4px 12px rgba(231,76,60,0.6) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg,
    button[kind="header"] svg,
    button[kind="headerNoPadding"] svg {
        fill: #fff !important;
        color: #fff !important;
        width: 22px !important;
        height: 22px !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(22,33,62,0.98) !important;
        border-right: 2px solid rgba(231,76,60,0.4) !important;
    }

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

    .footer-text {
        text-align: center;
        color: #95a5a6 !important;
        padding: 20px 10px;
        font-size: clamp(0.7rem, 2.2vw, 0.9rem);
        line-height: 1.5;
    }

    hr { border-color: rgba(255,255,255,0.1) !important; margin: 1rem 0; }

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

    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# CLIENT IP DETECTION (for rate limiting)
# ============================================================
def get_client_ip() -> str:
    """Get the real client IP (works on Streamlit Cloud via X-Forwarded-For)."""
    try:
        headers = st.context.headers
        # Streamlit Cloud sets these
        xff = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        real_ip = headers.get("X-Real-Ip") or headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    except Exception:
        pass
    return "unknown"


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

client_ip = get_client_ip()

# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

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
    st.markdown("## ⚡ Houssem AI")
    st.caption("🛡️ بدون تسجيل — استخدام مباشر")
    st.markdown("---")

    st.markdown("### ⚙️ لوحة التحكم")
    if "domain_choice" not in st.session_state:
        st.session_state.domain_choice = list(DOMAIN_MAP.keys())[0]

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
        usage = limiter.get_usage(f"ip:{client_ip}")
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
    st.caption(f"🌍 IP: `{client_ip}`")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.conversation_count}</div>
                <div class="stat-label">الرسائل المرسلة</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">في المحادثة</div>
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

# ============================================================
# WELCOME
# ============================================================
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align:center;padding:40px;color:#95a5a6;">
            <div style="font-size:50px;">🇹🇳</div>
            <div style="font-size:1.5rem;font-weight:700;margin:10px 0;color:#fff;">
                مرحباً بك في Houssem AI
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

    # ---- Rate limit keyed by IP ----
    rate_key = f"ip:{client_ip}"
    allowed, reason = limiter.check(rate_key)
    if not allowed:
        st.warning(reason)
        st.stop()

    # ---- Validation ----
    ok, err = validate_input(prompt)
    if not ok:
        st.error(err)
        st.stop()

    safe_prompt = sanitize_input(prompt)

    st.session_state.messages.append({"role": "user", "content": safe_prompt})
    st.session_state.conversation_count += 1

    with st.chat_message("user"):
        st.markdown(safe_prompt)

    # ---- LLM call ----
    with st.chat_message("assistant"):
        try:
            system_instruction = build_system_prompt(BASE_IDENTITY, DOMAIN_MAP[domain])
            history = trim_history(st.session_state.messages, 20)

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
