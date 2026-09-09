import streamlit as st
from groq import Groq
import time
from datetime import datetime
import base64

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Page Configuration
st.set_page_config(
    page_title="Houssem AI | أول ذكاء اصطناعي تونسـي", 
    page_icon="⚡", 
    layout="wide"
)

# ========== CUSTOM CSS FOR PREMIUM UI ==========
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: #e6edf3;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat Container */
    .chat-container {
        background: #0d1117;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #30363d;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Message Bubbles */
    .user-message {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 2px 8px rgba(31, 111, 235, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #21262d 0%, #30363d 100%);
        color: #e6edf3;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid #30363d;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Avatar Images */
    .avatar-user {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        float: right;
        margin-left: 10px;
        border: 2px solid #1f6feb;
    }
    
    .avatar-assistant {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        float: left;
        margin-right: 10px;
        border: 2px solid #2ea043;
    }
    
    /* Creator Badge Enhanced */
    .creator-badge {
        background: linear-gradient(135deg, #238636 0%, #2ea043 50%, #3fb950 100%);
        color: white;
        padding: 12px 25px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(35, 134, 54, 0.4);
        border: 1px solid #2ea043;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 4px 20px rgba(35, 134, 54, 0.4); }
        to { box-shadow: 0 4px 30px rgba(35, 134, 54, 0.8); }
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        width: 100%;
        transition: all 0.3s;
        font-size: 16px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #388bfd 0%, #58a6ff 100%);
        box-shadow: 0 0 25px rgba(56, 139, 253, 0.6);
        transform: translateY(-2px);
    }
    
    /* Clear Chat Button */
    .clear-button button {
        background: linear-gradient(135deg, #da3633 0%, #f85149 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .clear-button button:hover {
        background: linear-gradient(135deg, #f85149 0%, #ff7b72 100%);
        box-shadow: 0 0 20px rgba(248, 81, 73, 0.5);
        transform: translateY(-2px);
    }
    
    /* Stats Cards */
    .stat-card {
        background: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin: 10px 0;
        text-align: center;
    }
    
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #58a6ff;
    }
    
    .stat-label {
        color: #8b949e;
        font-size: 14px;
    }
    
    /* Input Area */
    .stTextArea textarea {
        background: #161b22 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2) !important;
    }
    
    /* Domain Selector */
    .stSelectbox div[data-baseweb="select"] {
        background: #161b22 !important;
        border-color: #30363d !important;
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: inline-block;
        padding: 10px 18px;
        background: #21262d;
        border-radius: 18px 18px 18px 4px;
        border: 1px solid #30363d;
        margin: 8px 0;
        float: left;
        clear: both;
    }
    
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 3px;
        background: #58a6ff;
        border-radius: 50%;
        animation: typing 1.4s infinite both;
    }
    
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INITIALIZATION ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# ========== CREATOR BADGE ==========
st.markdown("""
    <div class="creator-badge">
        🚀 منصة مطورة ومبتكرة بواسطة المهندس التونسي: <u>حسام كسنطيني (Houssem Kessentini)</u> — أول ذكاء اصطناعي تونسي متقدم.
        <br>
        <span style="font-size: 12px; opacity: 0.8;">🇹🇳 Built in Sfax, Tunisia | نسخة 2.0</span>
    </div>
""", unsafe_allow_html=True)

# ========== MAIN HEADER ==========
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h1 style="font-size: 42px; background: linear-gradient(135deg, #58a6ff, #2ea043); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚡ Houssem AI Intelligence Hub
            </h1>
            <p style="color: #8b949e; font-size: 18px; -webkit-text-fill-color: #8b949e;">
                منظومة الذكاء الاصطناعي السيبرانية والتقنية المتقدمة
            </p>
        </div>
    """, unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("---")
    
    # Domain Selection
    st.markdown("### ⚙️ لوحة التحكم")
    domain = st.selectbox(
        "اختر المجال التحليلي:",
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
    
    # Clear Chat Button
    st.markdown('<div class="clear-button">', unsafe_allow_html=True)
    if st.button("🗑️ مسح المحادثة", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.conversation_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Info
    st.markdown("### 🇹🇳 معلومات المنظومة")
    st.info("""
    ✅ بنيت محلياً لتلبية احتياجات السوق التونسي  
    ✅ أعلى سرعة وأقصى تفصيل  
    ✅ دعم اللغة العربية والفرنسية والإنجليزية  
    ✅ معمارية أمنية متقدمة
    """)
    
    st.markdown("---")
    
    # Quick Tips
    st.markdown("### 💡 نصائح سريعة")
    st.caption("• اسأل عن تحليل ثغرات أمنية")
    st.caption("• اطلب هيكلية مشروع برمجي")
    st.caption("• استفسر عن استراتيجيات تداول")
    st.caption("• احصل على خطط تسويقية رقمية")

# ========== CHAT INTERFACE ==========
# Chat container
chat_container = st.container()

with chat_container:
    # Display chat messages with avatars
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
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

# ========== INPUT AREA ==========
st.markdown("---")

# Create input row with button
col1, col2 = st.columns([5, 1])

with col1:
    user_prompt = st.text_area(
        "💬 أدخل تفاصيل التحدي التقني أو الاستفسار:",
        placeholder="مثال: تحليل ثغرة أمنية، هيكلية API لنظام مالي، أو خطة تداول...",
        height=80,
        key="user_input"
    )

with col2:
    st.write("")
    st.write("")
    if st.button("🚀 إرسال", key="send_button", use_container_width=True):
        if user_prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            st.session_state.conversation_count += 1
            
            # Process with AI
            with st.spinner("🧠 جاري التحليل العميق..."):
                try:
                    # System prompt
                    base_identity = "You were created by Houssem Kessentini (حسام كسنطيني), the first Tunisian AI developer. "

                    if "الأمن السيبراني" in domain:
                        system_instruction = base_identity + "You are a Principal Cybersecurity Architect. Provide detailed technical analysis in Arabic and English."
                    elif "هندسة البرمجيات" in domain:
                        system_instruction = base_identity + "You are a Lead Software Architect. Provide production-ready code and analysis."
                    elif "التداول" in domain:
                        system_instruction = base_identity + "You are a Senior Quantitative Trader. Provide market analysis and strategies."
                    elif "التسويق الرقمي" in domain:
                        system_instruction = base_identity + "You are a Growth Hacker. Provide data-driven marketing strategies."
                    else:
                        system_instruction = base_identity + "You are a Global Tech Intelligence Analyst."

                    # API Call
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
                    
                    # Collect response
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
                    
                    # Save assistant response
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ حدث خطأ تقني: {e}")
        else:
            st.warning("⚠️ الرجاء كتابة طلبك أولاً.")

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <p style="color: #8b949e; font-size: 14px;">
            Developed with ❤️ in Sfax, Tunisia by <strong style="color: #58a6ff;">Houssem Kessentini</strong> © 2026
        </p>
        <p style="color: #8b949e; font-size: 12px;">
            ⚡ Powered by Groq AI | أول ذكاء اصطناعي تونسي متقدم
        </p>
    </div>
""", unsafe_allow_html=True)

# ========== KEYBOARD SHORTCUT ==========
st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.shiftKey) {
            document.querySelector('[data-testid="stButton"] button').click();
        }
    });
    </script>
""", unsafe_allow_html=True)
