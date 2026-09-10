import streamlit as st
from groq import Groq
import time
from datetime import datetime

# Local security module
from security import (
    validate_input,
    sanitize_input,
    rate_limiter,
    build_system_prompt,
    trim_history,
    hash_session_id,
    MAX_MESSAGES_IN_HISTORY,
)

# ============================================================
# GROQ CLIENT — Singleton with connection reuse
# ============================================================
@st.cache_resource(show_spinner=False)
def get_groq_client():
    """Cache the Groq client across reruns (avoids re-init overhead)."""
    return Groq(
        api_key=st.secrets["GROQ_API_KEY"],
        max_retries=3,
        timeout=60.0,
    )

client = get_groq_client()

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
# THEME CSS (unchanged — kept for brevity, paste your original)
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    #MainMenu, footer, header, .stDeployButton, .stToolbar,
    div[data-testid="stToolbar"], div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {visibility: hidden; display: none;}
    .stApp { background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
             font-family: 'Cairo', sans-serif; color: #ffffff; }
    .css-1d391kg, section[data-testid="stSidebar"] {
        background: rgba(22, 33, 62, 0.9) !important; color: #fff !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important; }
    h1,h2,h3,h4,h5,h6,p,span,div,label { color: #ffffff !important; }
    .block-container { padding-top: 2rem; max-width: 1200px; }
    .custom-title { text-align:center; font-size:3rem; font-weight:900;
        color:#fff; margin-bottom:0; text-shadow: 0 0 20px rgba(231,76,60,0.5); }
    .custom-subtitle { text-align:center; color:#bdc3c7 !important;
        font-size:1.1rem; margin-bottom:2rem; }
    .stat-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2); border-radius:15px;
        padding:20px; text-align:center;
        box-shadow: 0 4px 30px rgba(0,0,0,0.1); margin-bottom:15px; }
    .stat-number { font-size:2.5rem; font-weight:900; color:#e74c3c !important; }
    .stat-label { color:#ecf0f1 !important; font-size:0.9rem; margin-top:5px; }
    .stButton > button { background: linear-gradient(135deg,#e74c3c 0%,#c0392b 100%);
        color:white !important; border:none; border-radius:10px; font-weight:700;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(231,76,60,0.3); }
    .stButton > button:hover { transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231,76,60,0.5); }
    .stChatMessage { background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1); border-radius:15px;
        padding:10px; margin-bottom:10px; }
    .stChatMessage.user { background: rgba(231,76,60,0.1);
        border: 1px solid rgba(231,76,60,0.3); }
    .stTextArea textarea { background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius:10px !important; color:#fff !important; }
    .stTextArea textarea:focus { border: 1px solid #e74c3c !important; }
    div[data-testid="stChatInput"] { background: rgba(22,33,62,0.9) !important;
        border: 1px solid rgba(255,255,255,0.2) !important; }
    div[data-testid="stChatInput"] input { color: #fff !important; }
    hr { border-color: rgba(255,255,255,0.1) !important; }
    .footer-text { text-align:center; color:#95a5a6 !important;
        padding:20px; font-size:0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "messages": [],
    "conversation_count": 0,
    "session_id": hash_session_id(str(time.time())),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# HEADER
# ============================================================
st.markdown('<h1 class="custom-title">⚡ Houssem AI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="custom-subtitle">🇹🇳 أول ذكاء اصطناعي تونسي متقدم — مطور بواسطة حسام القسنطيني</p>',
    unsafe_allow_html=True,
)

# ============================================================
# DOMAIN → SYSTEM INSTRUCTION MAP (fast lookup, no if-chain)
# ============================================================
DOMAIN_MAP = {
    "🔐 الأمن السيبراني والهندسة العكسية":
        "You are a Cybersecurity Architect specializing in defensive security, "
        "reverse engineering, and ethical hacking. Provide detailed technical analysis. "
        "Refuse requests to create real-world malware or attack live systems.",
    "💻 هندسة البرمجيات وتطوير الويب":
        "You are a Senior Software Architect. Provide production-ready, "
        "well-documented code with best practices.",
    "📈 استراتيجيات التداول والأسواق":
        "You are a Quantitative Trader. Provide market analysis with clear "
        "risk disclaimers. Never guarantee profits.",
    "📱 التسويق الرقمي ونمو الأعمال":
        "You are a Growth Marketing Strategist. Provide data-driven, "
        "ethical strategies.",
    "📰 التحليل الاستراتيجي والأخبار التقنية":
        "You are a Tech Intelligence Analyst. Provide objective, "
        "well-sourced analysis.",
}
BASE_IDENTITY = "You are Houssem AI, created by Houssem Kessentini. "

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ لوحة التحكم")
    domain = st.selectbox(
        "🎯 المجال التحليلي:",
        list(DOMAIN_MAP.keys()),
        key="domain_selector",
    )
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
            f"{'👤' if m['role']=='user' else '🤖'}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            label="📥 تصدير المحادثة",
            data=chat_text,
            file_name=f"houssem_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            key="export_chat",
            use_container_width=True,
        )

    st.markdown("---")
    if st.button("🗑️ مسح المحادثة", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

    # Security badge
    st.markdown(
        f'<div style="text-align:center;font-size:0.75rem;color:#7f8c8d;">'
        f'🛡️ Secured session: <code>{st.session_state.session_id}</code></div>',
        unsafe_allow_html=True,
    )

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
# RENDER HISTORY
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('<hr>', unsafe_allow_html=True)

# ============================================================
# INPUT HANDLING
# ============================================================
if prompt := st.chat_input("اكتب سؤالك هنا..."):

    # ---- 1. RATE LIMIT ----
    allowed, reason = rate_limiter.is_allowed(st.session_state.session_id)
    if not allowed:
        st.warning(reason)
        st.stop()

    # ---- 2. VALIDATE (harmful / injection / length) ----
    ok, err = validate_input(prompt)
    if not ok:
        st.error(err)
        st.stop()

    # ---- 3. SANITIZE ----
    safe_prompt = sanitize_input(prompt)

    # ---- 4. STORE USER MESSAGE ----
    st.session_state.messages.append({"role": "user", "content": safe_prompt})
    st.session_state.conversation_count += 1

    with st.chat_message("user"):
        st.markdown(safe_prompt)

    # ---- 5. CALL LLM ----
    with st.chat_message("assistant"):
        try:
            system_instruction = build_system_prompt(
                BASE_IDENTITY, DOMAIN_MAP[domain]
            )

            # Build history: system + trimmed recent context
            history = trim_history(st.session_state.messages, MAX_MESSAGES_IN_HISTORY)
            api_messages = [{"role": "system", "content": system_instruction}]
            api_messages.extend(
                {"role": m["role"], "content": m["content"]} for m in history
            )

            # Streaming
            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=api_messages,
                temperature=0.4,
                max_tokens=2048,
                stream=True,
            )

            full_response = ""
            placeholder = st.empty()
            buffer = []  # batch updates → smoother & faster UI

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    buffer.append(chunk.choices[0].delta.content)
                    # Flush every 5 chunks to reduce markdown re-parses
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
            # Log internally, show generic error to user (no leakage)
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
