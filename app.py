import time
from datetime import datetime
from collections import defaultdict

import streamlit as st
import requests
from groq import Groq

st.set_page_config(
    page_title="Houssem AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#1a1a1a">
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    *, *::before, *::after { box-sizing: border-box; }
    html, body {
        margin: 0; padding: 0;
        background: #1a1a1a;
        font-family: 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #ececec;
        -webkit-text-size-adjust: 100%;
        overflow-x: hidden;
    }

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    .stDeployButton { display: none !important; }

    .stApp, [data-testid="stAppViewContainer"] { background: #1a1a1a !important; }
    section.main { background: #1a1a1a !important; }

    .block-container {
        padding: 1rem 1rem 5rem 1rem !important;
        max-width: 820px !important;
        margin: 0 auto !important;
    }

    h1,h2,h3,h4,h5,h6,p,span,div,label,li,a {
        color: #ececec !important;
        font-family: 'Cairo', sans-serif !important;
    }

    /* Material icons font fix */
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: #141414 !important;
        border-right: 1px solid #2a2a2a !important;
        min-width: 280px !important;
        width: 280px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem 2rem 1rem !important;
        width: 280px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ececec !important;
        white-space: normal !important;
        overflow: visible !important;
    }

    .sidebar-brand {
        display: flex; align-items: center; gap: 0.7rem;
        padding: 0.4rem 0.4rem 1.2rem 0.4rem;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 1.1rem;
    }
    .sidebar-logo {
        width: 34px; height: 34px; border-radius: 8px;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/c/ce/Flag_of_Tunisia.svg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .sidebar-name {
        font-size: 1rem; font-weight: 700;
        color: #fff !important; letter-spacing: -0.01em;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 0.7rem !important;
        color: #8a8a8a !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin: 1.2rem 0 0.6rem 0 !important;
        padding: 0 !important;
        border: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: #1f1f1f !important;
        color: #ececec !important;
        border: 1px solid #2f2f2f !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        min-height: 40px !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 0.9rem !important;
        text-align: right !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #262626 !important;
        border-color: #3a3a3a !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #1f1f1f !important;
        border: 1px solid #2f2f2f !important;
        color: #ececec !important;
        border-radius: 10px !important;
        min-height: 42px;
        font-size: 0.85rem !important;
        direction: rtl !important;
    }
    div[data-baseweb="popover"] * { background: #1f1f1f !important; color: #ececec !important; }
    ul[role="listbox"] { background: #1f1f1f !important; border-radius: 10px !important; }
    li[role="option"] {
        background: #1f1f1f !important;
        color: #ececec !important;
        padding: 10px 14px !important;
        font-size: 0.85rem !important;
        direction: rtl !important;
        text-align: right !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: #2a2a2a !important;
    }

    /* USAGE */
    .usage-mini { display: flex; flex-direction: column; gap: 0.5rem; }
    .usage-item-mini {
        background: #1a1a1a;
        border: 1px solid #262626;
        border-radius: 10px;
        padding: 0.6rem 0.75rem;
    }
    .usage-head-mini {
        display: flex; justify-content: space-between;
        font-size: 0.72rem; color: #b8b8b8 !important;
        font-weight: 500; margin-bottom: 0.35rem;
    }
    .usage-bar-mini {
        height: 4px; background: #262626;
        border-radius: 2px; overflow: hidden;
    }
    .usage-bar-mini-fill {
        height: 100%; background: #e70013;
        border-radius: 2px;
    }

    /* STATS */
    .stats-mini { display: flex; gap: 0.4rem; flex-wrap: wrap; }
    .stat-mini {
        flex: 1; min-width: 70px;
        background: #1a1a1a;
        border: 1px solid #262626;
        border-radius: 10px;
        padding: 0.6rem 0.4rem;
        text-align: center;
    }
    .stat-mini-num {
        font-size: 1.05rem; font-weight: 700;
        color: #fff !important; line-height: 1;
    }
    .stat-mini-label {
        font-size: 0.62rem; color: #8a8a8a !important;
        margin-top: 0.2rem; text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* HERO */
    .hero-ds { text-align: center; padding: 3rem 1rem 2rem 1rem; }
    .hero-ds-logo {
        display: inline-block;
        width: 88px; height: 88px;
        border-radius: 22px;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/c/ce/Flag_of_Tunisia.svg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 40px rgba(231,0,19,0.35);
        border: 2px solid rgba(255,255,255,0.08);
    }
    .hero-ds-title {
        font-size: clamp(1.75rem, 5vw, 2.5rem);
        font-weight: 700; color: #fff !important;
        margin: 0 0 0.6rem 0;
        letter-spacing: -0.02em; line-height: 1.15;
    }
    .hero-ds-sub {
        font-size: clamp(0.85rem, 2.5vw, 1rem);
        color: #8a8a8a !important;
        font-weight: 400; line-height: 1.6;
        margin: 0 auto; max-width: 480px;
    }

    /* SUGGESTIONS */
    .suggest-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.65rem; margin: 2rem 0 1rem 0;
    }
    .suggest-card {
        background: #1f1f1f;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        text-align: right;
        direction: rtl;
    }
    .suggest-title {
        font-size: 0.88rem; font-weight: 600;
        color: #ececec !important; margin-bottom: 0.25rem;
    }
    .suggest-desc {
        font-size: 0.72rem; color: #8a8a8a !important; line-height: 1.4;
    }

    /* CHAT */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        margin-bottom: 0 !important;
        border-bottom: 1px solid #262626 !important;
        border-radius: 0 !important;
    }

    /* Kill the avatar column */
    .stChatMessage > div:first-child {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    .stChatMessage > div:nth-child(2) {
        display: block !important;
        visibility: visible !important;
        padding-left: 0 !important;
        margin-left: 0 !important;
        width: 100% !important;
    }

    .stChatMessage p {
        color: #ececec !important;
        font-size: clamp(0.9rem, 2.4vw, 1rem) !important;
        line-height: 1.7 !important;
        margin: 0 !important;
    }
    .stChatMessage.user {
        background: #1a1a1a !important;
        border-left: 3px solid #e70013 !important;
        border-bottom: 1px solid #262626 !important;
        padding: 1rem 1rem 1rem 1.1rem !important;
        border-radius: 0 12px 12px 0 !important;
        margin-bottom: 0.4rem !important;
    }
    .stChatMessage.assistant {
        background: transparent !important;
        padding: 1.1rem 0 !important;
    }

    /* INPUT */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stBottomBlockContainer"] {
        background: linear-gradient(180deg, rgba(26,26,26,0) 0%, #1a1a1a 40%) !important;
        border: none !important;
        box-shadow: none !important;
        padding: 1.5rem 1rem !important;
    }
    div[data-testid="stChatInput"] {
        background: #262626 !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 24px !important;
        box-shadow: 0 4px 30px rgba(0,0,0,0.4) !important;
        max-width: 820px !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        padding: 6px !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #e70013 !important;
        box-shadow: 0 4px 30px rgba(231,0,19,0.2) !important;
    }
    div[data-testid="stChatInput"] textarea {
        color: #ececec !important;
        background: transparent !important;
        font-size: 1rem !important;
        padding: 0.6rem 0.9rem !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #6a6a6a !important;
    }
    div[data-testid="stChatInput"] button {
        width: 40px !important; height: 40px !important;
        min-width: 40px !important;
        border-radius: 50% !important;
        background: #e70013 !important;
        border: none !important;
        flex-shrink: 0 !important;
        margin: 0 6px 0 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stChatInput"] button svg {
        fill: #fff !important;
        color: #fff !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* TOGGLE */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
        z-index: 9999 !important;
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        background: #262626 !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 10px !important;
        padding: 6px !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: #ececec !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* FOOTER */
    .footer-ds {
        text-align: center;
        color: #6a6a6a !important;
        padding: 2rem 1rem;
        font-size: 0.72rem;
        line-height: 1.7;
        border-top: 1px solid #262626;
        margin-top: 3rem;
    }
    .footer-ds strong { color: #8a8a8a !important; }

    hr {
        border: none !important;
        border-top: 1px solid #262626 !important;
        margin: 1rem 0 !important;
    }

    @media (max-width: 640px) {
        .block-container { padding: 0.75rem 0.9rem 6rem 0.9rem !important; }
        .hero-ds { padding: 2rem 0.5rem 1.5rem 0.5rem; }
        .hero-ds-logo { width: 72px; height: 72px; }
        .hero-ds-title { font-size: 1.6rem; }
        .hero-ds-sub { font-size: 0.85rem; }
        .suggest-grid { grid-template-columns: 1fr; margin-top: 1.2rem; }
        section[data-testid="stSidebar"] {
            min-width: 88vw !important;
            max-width: 88vw !important;
            width: 88vw !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            width: 88vw !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# GROQ
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
        store[f"{key}:{window}"] = [t for t in store[f"{key}:{window}"] if t > now - seconds]
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
# SESSION
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0
if "domain_choice" not in st.session_state:
    st.session_state.domain_choice = ""

# ============================================================
# DOMAIN MAP
# ============================================================
DOMAIN_MAP = {
    "🔐 الأمن السيبراني": "You are a Cybersecurity Architect. Provide detailed defensive security analysis.",
    "💻 هندسة البرمجيات": "You are a Senior Software Architect. Provide production-ready code.",
    "📈 استراتيجيات التداول": "You are a Quantitative Trader. Provide market analysis with risk disclaimers.",
    "📱 التسويق الرقمي": "You are a Growth Marketing Strategist.",
    "📰 التحليل الاستراتيجي": "You are a Tech Intelligence Analyst.",
}
BASE_IDENTITY = "You are Houssem AI, created by Houssem Kessentini from Tunisia. "

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-logo"></div>
            <div class="sidebar-name">Houssem AI</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 المجال")

    _domain_options = list(DOMAIN_MAP.keys())
    if st.session_state.domain_choice not in _domain_options:
        st.session_state.domain_choice = _domain_options[0]

    st.session_state.domain_choice = st.selectbox(
        "المجال",
        _domain_options,
        index=_domain_options.index(st.session_state.domain_choice),
        key="domain_selector",
        label_visibility="collapsed",
    )
    domain = st.session_state.domain_choice

    st.markdown("### 📊 الاستهلاك")
    try:
        usage = rate_usage(client_ip)
        limits_map = {"minute": 15, "hour": 200, "day": 1500}
        labels_map = {"minute": "دقيقة", "hour": "ساعة", "day": "يوم"}
        st.markdown('<div class="usage-mini">', unsafe_allow_html=True)
        for window in ["minute", "hour", "day"]:
            count = usage.get(window, 0)
            limit = limits_map[window]
            label = labels_map[window]
            pct = (count / limit) * 100 if limit else 0
            st.markdown(f"""
                <div class="usage-item-mini">
                    <div class="usage-head-mini">
                        <span>{label}</span>
                        <span>{count} / {limit}</span>
                    </div>
                    <div class="usage-bar-mini">
                        <div class="usage-bar-mini-fill" style="width:{max(pct,1)}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("### 📈 الإحصائيات")
    st.markdown(f"""
        <div class="stats-mini">
            <div class="stat-mini">
                <div class="stat-mini-num">{st.session_state.conversation_count}</div>
                <div class="stat-mini-label">رسائل</div>
            </div>
            <div class="stat-mini">
                <div class="stat-mini-num">{total_visits}</div>
                <div class="stat-mini-label">زوار</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ الإجراءات")

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

    if st.button("🗑 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

# ============================================================
# MAIN — HERO
# ============================================================
if not st.session_state.messages:
    st.markdown("""
        <div class="hero-ds">
            <div class="hero-ds-logo"></div>
            <h1 class="hero-ds-title">كيف يمكنني مساعدتك؟</h1>
            <p class="hero-ds-sub">Houssem AI — أول ذكاء اصطناعي تونسي متقدم</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="suggest-grid">
            <div class="suggest-card">
                <div class="suggest-title">🔐 اختراق أخلاقي</div>
                <div class="suggest-desc">تحليل الثغرات والأمن السيبراني</div>
            </div>
            <div class="suggest-card">
                <div class="suggest-title">💻 كود احترافي</div>
                <div class="suggest-desc">تطوير ويب وتطبيقات</div>
            </div>
            <div class="suggest-card">
                <div class="suggest-title">📈 تحليل الأسواق</div>
                <div class="suggest-desc">استراتيجيات التداول</div>
            </div>
            <div class="suggest-card">
                <div class="suggest-title">📰 تحليل الأخبار</div>
                <div class="suggest-desc">أخبار التقنية والذكاء الاصطناعي</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHAT — using emoji avatars (Streamlit accepts these)
# ============================================================
for message in st.session_state.messages:
    avatar = "⚡" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if st.session_state.messages:
    st.markdown("""
        <div class="footer-ds">
            <strong>Houssem AI</strong> · Built in Sfax, Tunisia 🇹🇳<br>
            Powered by Groq AI
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# INPUT
# ============================================================
if prompt := st.chat_input("اكتب رسالتك هنا..."):

    allowed, reason = rate_check(client_ip)
    if not allowed:
        st.warning(reason)
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_count += 1

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
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
