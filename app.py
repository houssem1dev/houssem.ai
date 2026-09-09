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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== MODERN DARK TUNISIAN THEME CSS ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    /* ===== HIDE STREAMLIT TOOLBAR (Share, Star, GitHub, etc.) ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stToolbar {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none;}
    
    /* ===== FORCE PURE DARK MODE ===== */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #16213e, #0f3460);
        font-family: 'Cairo', sans-serif;
        color: #ffffff;
    }
    
    /* Override light mode elements if they appear */
    .css-1d391kg, section[data-testid="stSidebar"] {
        background: rgba(22, 33, 62, 0.9) !important;
        color: #ffffff !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Base text color to white */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Main Container */
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Custom Title */
    .custom-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        color: #fff;
        margin-bottom: 0;
        text-shadow: 0 0 20px rgba(231, 76, 60, 0.5);
    }
    
    .custom-subtitle {
        text-align: center;
        color: #bdc3c7 !important;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Modern Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 900;
        color: #e74c3c !important;
    }
    
    .stat-label {
        color: #ecf0f1 !important;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.5);
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    .stChatMessage.user {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    /* Text Area */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    
    .stTextArea textarea:focus {
        border: 1px solid #e74c3c !important;
    }
    
    /* Chat Input */
    div[data-testid="stChatInput"] {
        background: rgba(22, 33, 62, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    div[data-testid="stChatInput"] input {
        color: #fff !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #95a5a6 !important;
        padding: 20px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# ========== HEADER ==========
st.markdown('<h1 class="custom-title">⚡ Houssem AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subtitle">🇹🇳 أول ذكاء اصطناعي تونسي متقدم — مطور بواسطة حسام كسنطيني</p>', unsafe_allow_html=True)

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
    
    # Stats - Clean Cards
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
    
    # Export & Clear
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
    
    if st.button("🗑️ مسح المحادثة", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()

# ========== CHAT INTERFACE (NATIVE STREAMLIT) ==========
# Welcome Message
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; padding: 40px; color: #95a5a6;">
            <div style="font-size: 50px;">🇹🇳</div>
            <div style="font-size: 1.5rem; font-weight: 700; margin: 10px 0; color: #fff;">مرحباً بك في Houssem AI</div>
            <div>اكتب سؤالك في الأسفل وابدأ التحليل الذكي</div>
        </div>
    """, unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ========== INPUT AREA ==========
st.markdown('<hr>', unsafe_allow_html=True)

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_count += 1
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Response
    with st.chat_message("assistant"):
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
                        {"role": "user", "content": prompt}
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
                            response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"❌ حدث خطأ تقني: {e}")

# ========== FOOTER ==========
st.markdown("""
    <div class="footer-text">
        🇹🇳 Developed with ❤️ in <strong>Sfax, Tunisia</strong> by <strong>Houssem Kessentini</strong> 🇹🇳<br>
        ⚡ Powered by Groq AI | © 2026
    </div>
""", unsafe_allow_html=True)
