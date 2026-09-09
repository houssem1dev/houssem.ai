import streamlit as st
from groq import Groq
import time
from datetime import datetime

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Page Configuration
st.set_page_config(
    page_title="Houssem AI | أول ذكاء اصطناعي تونسـي", 
    page_icon="🇹🇳", 
    layout="wide"
)

# ========== TUNISIAN THEME CSS ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 30%, #0d0d0d 100%);
    }
    
    /* ===== CREATOR BADGE ===== */
    .tunisian-badge {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 50%, #E70000 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        margin-bottom: 25px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 8px 32px rgba(231, 0, 0, 0.4);
        animation: badgePulse 3s ease-in-out infinite;
    }
    
    @keyframes badgePulse {
        0%, 100% { box-shadow: 0 8px 32px rgba(231, 0, 0, 0.4); }
        50% { box-shadow: 0 8px 48px rgba(231, 0, 0, 0.8); }
    }
    
    /* ===== MAIN TITLE ===== */
    .main-title h1 {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #E70000 0%, #FFFFFF 30%, #E70000 60%, #FFFFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        animation: titleGlow 4s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(231, 0, 0, 0.3)); }
        50% { filter: drop-shadow(0 0 40px rgba(231, 0, 0, 0.6)); }
    }
    
    /* ===== SIDEBAR ===== */
    .css-1d391kg {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a0505 100%) !important;
        border-right: 2px solid #E70000 !important;
    }
    
    /* ===== CHAT CONTAINER ===== */
    .chat-wrapper {
        background: rgba(13, 13, 13, 0.9);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(231, 0, 0, 0.2);
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
        backdrop-filter: blur(10px);
    }
    
    .chat-wrapper::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-wrapper::-webkit-scrollbar-track {
        background: rgba(231, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    .chat-wrapper::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #E70000, #CC0000);
        border-radius: 10px;
    }
    
    /* ===== MESSAGES - NO TIME STAMPS ===== */
    .user-message {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 20px rgba(231, 0, 0, 0.4);
        animation: slideInRight 0.3s ease-out;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a0a0a 100%);
        color: #e6edf3;
        padding: 12px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid rgba(231, 0, 0, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        animation: slideInLeft 0.3s ease-out;
        word-wrap: break-word;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* ===== STATS CARDS ===== */
    .stat-card {
        background: linear-gradient(135deg, #1a0505 0%, #0a0a0a 100%);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(231, 0, 0, 0.3);
        text-align: center;
        transition: all 0.3s;
        margin: 5px 0;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(231, 0, 0, 0.2);
        border-color: #E70000;
    }
    
    .stat-number {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(135deg, #E70000, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ===== BUTTONS ===== */
    .stButton button {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.3s !important;
        font-family: 'Cairo', sans-serif !important;
        box-shadow: 0 4px 20px rgba(231, 0, 0, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 40px rgba(231, 0, 0, 0.6) !important;
    }
    
    /* ===== INPUT ===== */
    .stTextArea textarea {
        background: rgba(26, 5, 5, 0.8) !important;
        color: #e6edf3 !important;
        border: 2px solid rgba(231, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 16px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #E70000 !important;
        box-shadow: 0 0 30px rgba(231, 0, 0, 0.2) !important;
    }
    
    /* ===== QUICK REPLY BUTTONS ===== */
    .quick-reply {
        background: rgba(26, 5, 5, 0.8) !important;
        color: #e6edf3 !important;
        border: 1px solid rgba(231, 0, 0, 0.3) !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        margin: 3px !important;
        font-size: 13px !important;
        transition: all 0.3s !important;
        cursor: pointer !important;
    }
    
    .quick-reply:hover {
        background: rgba(231, 0, 0, 0.2) !important;
        border-color: #E70000 !important;
        transform: translateY(-2px) !important;
    }
    
    /* ===== EXPORT BUTTON ===== */
    .export-btn {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    }
    
    .export-btn:hover {
        box-shadow: 0 8px 40px rgba(56, 139, 253, 0.6) !important;
    }
    
    /* ===== TYPING INDICATOR ===== */
    .typing-indicator {
        display: inline-block;
        padding: 12px 24px;
        background: linear-gradient(135deg, #1a1a1a, #2a0a0a);
        border-radius: 20px 20px 20px 4px;
        border: 1px solid rgba(231, 0, 0, 0.3);
        margin: 8px 0;
        float: left;
        clear: both;
    }
    
    .typing-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        margin: 0 4px;
        background: #E70000;
        border-radius: 50%;
        animation: typingBounce 1.4s infinite both;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    /* ===== DIVIDERS ===== */
    .tunisian-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #E70000, #FFFFFF, #E70000, transparent);
        margin: 20px 0;
        opacity: 0.3;
    }
    
    /* ===== FOOTER ===== */
    .tunisian-footer {
        text-align: center;
        padding: 20px 0;
        border-top: 1px solid rgba(231, 0, 0, 0.2);
        margin-top: 20px;
        color: #888888;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-title h1 { font-size: 28px !important; }
        .user-message, .assistant-message { max-width: 95% !important; font-size: 14px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "export_enabled" not in st.session_state:
    st.session_state.export_enabled = False

# ========== CREATOR BADGE ==========
st.markdown("""
    <div class="tunisian-badge">
        🇹🇳 أول ذكاء اصطناعي تونسي متقدم — 🚀 مطور بواسطة <strong>حسام كسنطيني (Houssem Kessentini)</strong>
    </div>
""", unsafe_allow_html=True)

# ========== MAIN TITLE ==========
st.markdown("""
    <div class="main-title">
        <h1>⚡ Houssem AI Intelligence Hub</h1>
        <p style="text-align: center; color: #cccccc; font-size: 18px;">
            منظومة الذكاء الاصطناعي السيبرانية والتقنية المتقدمة
        </p>
    </div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### ⚙️ لوحة التحكم")
    
    # Domain Selection
    domain = st.selectbox(
        "🎯 المجال التحليلي:",
        [
            "🔐 الأمن السيبراني والهندسة العكسية",
            "💻 هندسة البرمجيات وتطوير الويب",
            "📈 استراتيجيات التداول والأسواق",
            "📱 التسويق الرقمي ونمو الأعمال",
            "📰 التحليل الاستراتيجي والأخبار التقنية"
        ],
        key="domain_selector"
    )
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 الإحصائيات")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{st.session_state.conversation_count}</div>
                <div style="color: #888; font-size: 13px;">المحادثات</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div style="color: #888; font-size: 13px;">الرسائل</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Export Chat
    if st.session_state.messages:
        chat_text = "\n".join([f"{'👤' if msg['role'] == 'user' else '🤖'}: {msg['content']}" for msg in st.session_state.messages])
        st.download_button(
            label="📥 تصدير المحادثة",
            data=chat_text,
            file_name=f"houssem_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            key="export_chat",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Clear Chat
    if st.button("🗑️ مسح المحادثة", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    
    st.markdown("---")
    
    # System Info
    st.info("""
    ✅ **100% Tunisian Made**  
    ✅ Built for Arab engineers  
    ✅ Cyber security ready  
    ✅ Multi-lingual support
    """)

# ========== CHAT INTERFACE ==========
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

# Display messages without time stamps
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; padding: 80px 20px; color: #666;">
            <div style="font-size: 60px; margin-bottom: 20px;">🇹🇳</div>
            <div style="font-size: 24px; font-weight: 700;">مرحباً بك في Houssem AI</div>
            <div style="font-size: 16px; margin-top: 10px; opacity: 0.7;">
                اكتب سؤالك في الأسفل وابدأ التحليل الذكي
            </div>
            <div style="margin-top: 20px; font-size: 14px; opacity: 0.5;">
                ★ ★ ★ ★ ★
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
                <div class="user-message">
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="assistant-message">
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ========== QUICK REPLY BUTTONS ==========
st.markdown('<div style="margin: 10px 0;">', unsafe_allow_html=True)
st.caption("💡 اقتراحات سريعة:")

cols = st.columns(4)
quick_questions = [
    ("🔐 تحليل ثغرة", "حلل ثغرة أمنية في نظام مالي"),
    ("💻 هيكلة برمجية", "قدم هيكلية مشروع ويب متكامل"),
    ("📊 استراتيجية تداول", "قدم خطة تداول للأسواق العربية"),
    ("📱 خطة تسويق", "قدم خطة تسويق رقمي للسوق التونسي")
]

for col, (label, question) in zip(cols, quick_questions):
    with col:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            user_prompt = question
            # Process the quick question
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            st.session_state.conversation_count += 1
            
            with st.spinner("🧠 جاري التحليل..."):
                try:
                    base_identity = "You are Houssem AI, created by Houssem Kessentini. "
                    
                    if "الأمن السيبراني" in domain:
                        system_instruction = base_identity + "You are a Cybersecurity Architect. Provide detailed analysis."
                    elif "هندسة البرمجيات" in domain:
                        system_instruction = base_identity + "You are a Software Architect. Provide production-ready code."
                    elif "التداول" in domain:
                        system_instruction = base_identity + "You are a Quantitative Trader. Provide market analysis."
                    elif "التسويق الرقمي" in domain:
                        system_instruction = base_identity + "You are a Growth Hacker. Provide data-driven strategies."
                    else:
                        system_instruction = base_identity + "You are a Tech Intelligence Analyst."

                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.4,
                        max_tokens=2048,
                        stream=True
                    )
                    
                    full_response = ""
                    response_placeholder = st.empty()
                    
                    for chunk in stream:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content is not None:
                                full_response += delta.content
                                response_placeholder.markdown(f"""
                                    <div class="assistant-message">
                                        {full_response} ▌
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ========== INPUT AREA ==========
st.markdown('<hr class="tunisian-divider">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:
    user_prompt = st.text_area(
        "💬 اكتب سؤالك هنا:",
        placeholder="مثال: كيف أحسن أمان موقعي الإلكتروني؟",
        height=70,
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    st.write("")
    st.write("")
    if st.button("🚀 إرسال", key="send_button", use_container_width=True):
        if user_prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            st.session_state.conversation_count += 1
            
            with st.spinner("🧠 جاري التحليل العميق..."):
                try:
                    base_identity = "You are Houssem AI, created by Houssem Kessentini. "
                    
                    if "الأمن السيبراني" in domain:
                        system_instruction = base_identity + "You are a Cybersecurity Architect. Provide detailed technical analysis."
                    elif "هندسة البرمجيات" in domain:
                        system_instruction = base_identity + "You are a Software Architect. Provide production-ready code."
                    elif "التداول" in domain:
                        system_instruction = base_identity + "You are a Quantitative Trader. Provide market analysis."
                    elif "التسويق الرقمي" in domain:
                        system_instruction = base_identity + "You are a Growth Hacker. Provide data-driven strategies."
                    else:
                        system_instruction = base_identity + "You are a Tech Intelligence Analyst."

                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.4,
                        max_tokens=2048,
                        stream=True
                    )
                    
                    full_response = ""
                    response_placeholder = st.empty()
                    
                    for chunk in stream:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content is not None:
                                full_response += delta.content
                                response_placeholder.markdown(f"""
                                    <div class="assistant-message">
                                        {full_response} ▌
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ حدث خطأ تقني: {e}")
        else:
            st.warning("⚠️ الرجاء كتابة سؤالك أولاً.")

# ========== FOOTER ==========
st.markdown("""
    <div class="tunisian-footer">
        <div style="font-size: 20px; opacity: 0.3; letter-spacing: 5px;">★ ★ ★ ★ ★</div>
        <div style="margin-top: 10px;">
            🇹🇳 Developed with ❤️ in <strong style="color: #E70000;">Sfax, Tunisia</strong> 
            by <strong style="color: #E70000;">Houssem Kessentini</strong> 🇹🇳
        </div>
        <div style="font-size: 12px; opacity: 0.5; margin-top: 5px;">
            ⚡ Powered by Groq AI | © 2026
        </div>
    </div>
""", unsafe_allow_html=True)
