import streamlit as st
from groq import Groq
import time
from datetime import datetime
import base64
import random

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
    /* ===== TUNISIAN COLOR PALETTE ===== */
    /* Red: #E70000 | White: #FFFFFF | Star: #E70000 */
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    /* ===== MAIN BACKGROUND ===== */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 30%, #0d0d0d 100%);
        position: relative;
    }
    
    /* Tunisian Flag Pattern Overlay */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            repeating-linear-gradient(
                45deg,
                transparent,
                transparent 50px,
                rgba(231, 0, 0, 0.02) 50px,
                rgba(231, 0, 0, 0.02) 51px
            ),
            repeating-linear-gradient(
                -45deg,
                transparent,
                transparent 50px,
                rgba(231, 0, 0, 0.02) 50px,
                rgba(231, 0, 0, 0.02) 51px
            );
        pointer-events: none;
        z-index: 0;
    }
    
    /* ===== TUNISIAN STAR DECORATION ===== */
    .tunisian-star {
        position: fixed;
        font-size: 60px;
        opacity: 0.03;
        animation: floatStar 20s infinite linear;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes floatStar {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1); }
    }
    
    /* ===== CREATOR BADGE - TUNISIAN STYLE ===== */
    .tunisian-badge {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 50%, #E70000 100%);
        color: white;
        padding: 18px 30px;
        border-radius: 16px;
        text-align: center;
        font-weight: 700;
        margin-bottom: 30px;
        border: 2px solid #FFFFFF;
        box-shadow: 
            0 8px 32px rgba(231, 0, 0, 0.4),
            inset 0 -2px 0 rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
        animation: badgePulse 3s ease-in-out infinite;
    }
    
    .tunisian-badge::before {
        content: '★';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 30px;
        color: rgba(255,255,255,0.2);
        animation: starSpin 8s linear infinite;
    }
    
    .tunisian-badge::after {
        content: '★';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 30px;
        color: rgba(255,255,255,0.2);
        animation: starSpin 8s linear infinite reverse;
    }
    
    @keyframes starSpin {
        0% { transform: translateY(-50%) rotate(0deg); }
        100% { transform: translateY(-50%) rotate(360deg); }
    }
    
    @keyframes badgePulse {
        0%, 100% { box-shadow: 0 8px 32px rgba(231, 0, 0, 0.4); }
        50% { box-shadow: 0 8px 48px rgba(231, 0, 0, 0.8); }
    }
    
    .badge-creator {
        font-size: 20px;
        font-weight: 900;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .badge-sub {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 5px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 8px;
    }
    
    /* ===== MAIN TITLE ===== */
    .main-title {
        text-align: center;
        padding: 20px 0;
        position: relative;
    }
    
    .main-title h1 {
        font-size: 52px;
        font-weight: 900;
        background: linear-gradient(135deg, #E70000 0%, #FFFFFF 30%, #E70000 60%, #FFFFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        animation: titleGlow 4s ease-in-out infinite;
        letter-spacing: 2px;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(231, 0, 0, 0.3)); }
        50% { filter: drop-shadow(0 0 40px rgba(231, 0, 0, 0.6)); }
    }
    
    .main-title p {
        color: #cccccc;
        font-size: 20px;
        margin-top: 10px;
        -webkit-text-fill-color: #cccccc;
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    .main-title .tunisia-flag {
        font-size: 30px;
        display: inline-block;
        animation: flagWave 3s ease-in-out infinite;
    }
    
    @keyframes flagWave {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(5deg); }
    }
    
    /* ===== SIDEBAR - TUNISIAN STYLE ===== */
    .css-1d391kg {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a0505 100%) !important;
        border-right: 2px solid #E70000 !important;
    }
    
    .sidebar-title {
        color: #E70000;
        font-size: 24px;
        font-weight: 900;
        text-align: center;
        padding: 15px 0;
        border-bottom: 2px solid #E70000;
        margin-bottom: 20px;
        text-shadow: 0 0 20px rgba(231, 0, 0, 0.3);
    }
    
    /* ===== CHAT MESSAGES ===== */
    .chat-container {
        background: rgba(13, 13, 13, 0.8);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid rgba(231, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: inset 0 0 60px rgba(231, 0, 0, 0.05);
    }
    
    /* Scrollbar Styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(231, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #E70000, #CC0000);
        border-radius: 10px;
    }
    
    /* User Message - Tunisian Red */
    .user-message {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 100%);
        color: white;
        padding: 14px 22px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 20px rgba(231, 0, 0, 0.4);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        animation: slideInRight 0.3s ease-out;
    }
    
    .user-message::before {
        content: '★';
        position: absolute;
        right: -8px;
        top: -8px;
        font-size: 14px;
        color: #E70000;
        opacity: 0.5;
    }
    
    /* Assistant Message - Tunisian Style */
    .assistant-message {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a0a0a 100%);
        color: #e6edf3;
        padding: 14px 22px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid rgba(231, 0, 0, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        position: relative;
        animation: slideInLeft 0.3s ease-out;
    }
    
    .assistant-message::before {
        content: '★';
        position: absolute;
        left: -8px;
        top: -8px;
        font-size: 14px;
        color: #E70000;
        opacity: 0.3;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Message Metadata */
    .message-time {
        font-size: 10px;
        opacity: 0.5;
        margin-top: 5px;
        display: block;
    }
    
    /* ===== STATS CARDS - TUNISIAN ===== */
    .stat-card {
        background: linear-gradient(135deg, #1a0505 0%, #0a0a0a 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(231, 0, 0, 0.3);
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(231, 0, 0, 0.2);
        border-color: #E70000;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 900;
        background: linear-gradient(135deg, #E70000, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #cccccc;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* ===== BUTTONS - TUNISIAN ===== */
    .stButton button {
        background: linear-gradient(135deg, #E70000 0%, #CC0000 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.3s !important;
        font-size: 16px !important;
        font-family: 'Cairo', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 20px rgba(231, 0, 0, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 40px rgba(231, 0, 0, 0.6) !important;
        background: linear-gradient(135deg, #FF0000 0%, #E70000 100%) !important;
    }
    
    .stButton button:active {
        transform: scale(0.95) !important;
    }
    
    /* Clear Button */
    .clear-button button {
        background: linear-gradient(135deg, #660000 0%, #440000 100%) !important;
        box-shadow: 0 4px 20px rgba(231, 0, 0, 0.2) !important;
    }
    
    .clear-button button:hover {
        background: linear-gradient(135deg, #880000 0%, #660000 100%) !important;
        box-shadow: 0 8px 30px rgba(231, 0, 0, 0.4) !important;
    }
    
    /* ===== INPUT AREA ===== */
    .stTextArea textarea {
        background: rgba(26, 5, 5, 0.8) !important;
        color: #e6edf3 !important;
        border: 2px solid rgba(231, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-family: 'Cairo', sans-serif !important;
        transition: all 0.3s !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #E70000 !important;
        box-shadow: 0 0 30px rgba(231, 0, 0, 0.2) !important;
        background: rgba(26, 5, 5, 0.9) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #666666 !important;
    }
    
    /* ===== SELECT BOX ===== */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(26, 5, 5, 0.8) !important;
        border-color: rgba(231, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: #E70000 !important;
    }
    
    /* ===== DIVIDERS ===== */
    .tunisian-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #E70000, #FFFFFF, #E70000, transparent);
        margin: 30px 0;
        opacity: 0.3;
    }
    
    /* ===== FOOTER ===== */
    .tunisian-footer {
        text-align: center;
        padding: 30px 0 20px 0;
        border-top: 1px solid rgba(231, 0, 0, 0.2);
        margin-top: 30px;
    }
    
    .tunisian-footer .footer-text {
        color: #888888;
        font-size: 14px;
    }
    
    .tunisian-footer .footer-text strong {
        color: #E70000;
        font-weight: 700;
    }
    
    .tunisian-footer .footer-flag {
        font-size: 20px;
        animation: flagWave 3s ease-in-out infinite;
        display: inline-block;
    }
    
    /* ===== TYPING INDICATOR ===== */
    .typing-indicator {
        display: inline-block;
        padding: 12px 24px;
        background: linear-gradient(135deg, #1a1a1a, #2a0a0a);
        border-radius: 20px 20px 20px 4px;
        border: 1px solid rgba(231, 0, 0, 0.3);
        margin: 10px 0;
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
    
    /* ===== TUNISIAN PATTERN DECORATION ===== */
    .pattern-divider {
        height: 4px;
        background: repeating-linear-gradient(
            90deg,
            #E70000 0px,
            #E70000 10px,
            transparent 10px,
            transparent 20px,
            #FFFFFF 20px,
            #FFFFFF 30px,
            transparent 30px,
            transparent 40px
        );
        margin: 20px 0;
        opacity: 0.3;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main-title h1 {
            font-size: 32px !important;
        }
        .user-message, .assistant-message {
            max-width: 95% !important;
            font-size: 14px !important;
        }
        .tunisian-badge {
            padding: 12px 15px !important;
            font-size: 14px !important;
        }
    }
    
    /* ===== TUNISIAN MAP BACKGROUND (subtle) ===== */
    .tunisia-map {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 80px;
        opacity: 0.03;
        pointer-events: none;
        z-index: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ========== TUNISIAN STAR DECORATIONS ==========
st.markdown("""
    <div class="tunisian-star" style="top: 10%; left: 5%;">★</div>
    <div class="tunisian-star" style="bottom: 20%; right: 5%; animation-delay: 5s;">★</div>
    <div class="tunisian-star" style="top: 50%; left: 2%; animation-delay: 10s; font-size: 40px;">★</div>
    <div class="tunisian-star" style="top: 30%; right: 2%; animation-delay: 15s; font-size: 40px;">★</div>
    <div class="tunisia-map">🇹🇳</div>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# ========== TUNISIAN CREATOR BADGE ==========
st.markdown("""
    <div class="tunisian-badge">
        <div class="badge-creator">
            🇹🇳 أول ذكاء اصطناعي تونسي متقدم
        </div>
        <div style="font-size: 16px; margin: 5px 0;">
            🚀 مطور ومبتكر بواسطة المهندس التونسي
        </div>
        <div style="font-size: 22px; font-weight: 900; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
            حسام القسنطيني (Houssem Kessentini)
        </div>
        <div class="badge-sub">
            ⚡ منصة سيبرانية وتقنية متقدمة | Sfax, Tunisia
        </div>
    </div>
""", unsafe_allow_html=True)

# ========== MAIN TITLE ==========
st.markdown("""
    <div class="main-title">
        <h1>
            <span class="tunisia-flag">🇹🇳</span> 
            Houssem AI Intelligence Hub
            <span class="tunisia-flag">🇹🇳</span>
        </h1>
        <p>
            منظومة الذكاء الاصطناعي السيبرانية والتقنية المتقدمة — 
            <span style="color: #E70000; font-weight: 700;">100% Tunisian</span>
        </p>
        <div class="pattern-divider"></div>
    </div>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ لوحة التحكم</div>', unsafe_allow_html=True)
    
    domain = st.selectbox(
        "🎯 اختر المجال التحليلي:",
        [
            "🔐 الأمن السيبراني والهندسة العكسية",
            "💻 هندسة البرمجيات وتطوير الويب",
            "📈 استراتيجيات التداول والأسواق",
            "📱 التسويق الرقمي ونمو الأعمال",
            "📰 التحليل الاستراتيجي والأخبار التقنية"
        ],
        key="domain_selector"
    )
    
    st.markdown('<hr style="border-color: rgba(231,0,0,0.3);">', unsafe_allow_html=True)
    
    # Stats with Tunisian style
    st.markdown("### 📊 الإحصائيات")
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
    
    st.markdown('<hr style="border-color: rgba(231,0,0,0.3);">', unsafe_allow_html=True)
    
    # Clear Chat
    st.markdown('<div class="clear-button">', unsafe_allow_html=True)
    if st.button("🗑️ مسح المحادثة", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="border-color: rgba(231,0,0,0.3);">', unsafe_allow_html=True)
    
    # System Info
    st.markdown("### 🇹🇳 معلومات المنظومة")
    st.info("""
    ✅ **100% Tunisian Made**  
    ✅ Built for Arab engineers  
    ✅ Cyber security ready  
    ✅ Multi-lingual support  
    ✅ High-speed processing
    """)
    
    st.markdown('<hr style="border-color: rgba(231,0,0,0.3);">', unsafe_allow_html=True)
    
    # Quick Tips
    st.markdown("### 💡 اقتراحات")
    st.caption("🔍 تحليل ثغرات أمنية")
    st.caption("💻 هيكلية مشروع برمجي")
    st.caption("📊 استراتيجيات تداول")
    st.caption("📱 خطط تسويقية")

# ========== CHAT INTERFACE ==========
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"""
                <div class="user-message">
                    {message["content"]}
                    <span class="message-time">أنت • {datetime.now().strftime("%H:%M")}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="assistant-message">
                    {message["content"]}
                    <span class="message-time">Houssem AI • {datetime.now().strftime("%H:%M")}</span>
                </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ========== INPUT AREA ==========
st.markdown('<hr class="tunisian-divider">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:
    user_prompt = st.text_area(
        "💬 أدخل تفاصيل التحدي التقني أو الاستفسار:",
        placeholder="اكتب سؤالك هنا... مثال: حلل ثغرة أمنية في نظام مالي",
        height=80,
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
                    base_identity = "You are Houssem AI, created by Houssem Kessentini, the first Tunisian AI developer. "

                    if "الأمن السيبراني" in domain:
                        system_instruction = base_identity + "You are a Principal Cybersecurity Architect. Provide detailed technical analysis."
                    elif "هندسة البرمجيات" in domain:
                        system_instruction = base_identity + "You are a Lead Software Architect. Provide production-ready code."
                    elif "التداول" in domain:
                        system_instruction = base_identity + "You are a Senior Quantitative Trader. Provide market analysis."
                    elif "التسويق الرقمي" in domain:
                        system_instruction = base_identity + "You are a Growth Hacker. Provide data-driven strategies."
                    else:
                        system_instruction = base_identity + "You are a Global Tech Intelligence Analyst."

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
            st.warning("⚠️ الرجاء كتابة طلبك أولاً.")

# ========== FOOTER ==========
st.markdown("""
    <div class="tunisian-footer">
        <div class="pattern-divider"></div>
        <div class="footer-text">
            <span class="footer-flag">🇹🇳</span>
            Developed with ❤️ in <strong>Sfax, Tunisia</strong> 
            by <strong>Houssem Kessentini</strong> 
            <span class="footer-flag">🇹🇳</span>
        </div>
        <div class="footer-text" style="font-size: 12px; margin-top: 5px; opacity: 0.6;">
            ⚡ Powered by Groq AI | أول ذكاء اصطناعي تونسي متقدم © 2026
        </div>
        <div style="margin-top: 10px; font-size: 20px; letter-spacing: 5px; opacity: 0.3;">
            ★ ★ ★ ★ ★
        </div>
    </div>
""", unsafe_allow_html=True)
