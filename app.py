import streamlit as st
from groq import Groq

# Initialize Groq client securely using Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Page Configuration
st.set_page_config(
    page_title="Houssem AI | أول ذكاء اصطناعي تونسـي", 
    page_icon="⚡", 
    layout="wide"
)

# Custom CSS for Sleek UI
st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .stSelectbox label, .stTextArea label {
        color: #58a6ff !important;
        font-weight: 600;
        font-size: 16px;
    }
    .creator-badge {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3);
    }
    .stButton button {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        width: 100%;
        transition: 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #388bfd 0%, #58a6ff 100%);
        box-shadow: 0 0 15px rgba(56, 139, 253, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Creator Banner
st.markdown("""
    <div class="creator-badge">
        🚀 منصة مطورة ومبتكرة بواسطة المهندس التونسي: <u>حسام كسنطيني (Houssem Kessentini)</u> — أول ذكاء اصطناعي تونسي متقدم.
    </div>
""", unsafe_allow_html=True)

st.title("⚡ Houssem AI Intelligence Hub")
st.markdown("منظومة الذكاء الاصطناعي السيبرانية والتقنية المتقدمة — مخصصة للتداول، تطوير الويب، الأمن السيبراني، والتسويق الرقمي.")

# Sidebar
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    domain = st.selectbox(
        "اختر المجال التحليلي:",
        [
            "🔐 الأمن السيبراني والهندسة العكسية",
            "💻 هندسة البرمجيات وتطوير الويب",
            "📈 استراتيجيات التداول والأسواق",
            "📱 التسويق الرقمي ونمو الأعمال",
            "📰 التحليل الاستراتيجي والأخبار التقنية"
        ]
    )
    st.markdown("---")
    st.markdown("### 🇹🇳 معلومات المنظومة")
    st.info("تم بناؤها محلياً لتلبية احتياجات السوق التونسي والمهندسين العرب بأعلى سرعة وأقصى تفصيل.")

# Main input
user_prompt = st.text_area("أدخل تفاصيل التحدي التقني أو الاستفسار:", 
                          placeholder="مثال: تحليل ثغرة أمنية، هيكلية API لنظام مالي، أو خطة تداول...",
                          height=130)

if st.button("🚀 بدء المعالجة والتحليل الفائق"):
    if user_prompt:
        with st.spinner("جاري التشغيل عبر العقد الذكية واستخراج التحليل العميق..."):
            try:
                # System prompt
                base_identity = "You were created, architected, and engineered by the Tunisian developer Houssem Kessentini (حسام كسنطيني). "

                if "الأمن السيبراني" in domain:
                    system_instruction = base_identity + "You are a Principal Cybersecurity Architect and Red Team Lead. Provide detailed technical analysis in Arabic and English."
                elif "هندسة البرمجيات" in domain:
                    system_instruction = base_identity + "You are a Lead Software Architect. Provide production-ready code and structural analysis."
                elif "التداول" in domain:
                    system_instruction = base_identity + "You are a Senior Quantitative Trader. Provide technical analysis and market insights."
                elif "التسويق الرقمي" in domain:
                    system_instruction = base_identity + "You are a Growth Hacker. Provide data-driven marketing strategies."
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
                
                st.subheader("📊 مخرجات التحليل العميق:")
                
                # FIXED: Only show content, not reasoning
                response_container = st.empty()
                full_response = ""
                
                for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        # Only extract content, skip reasoning tokens
                        if hasattr(delta, 'content') and delta.content is not None:
                            full_response += delta.content
                            response_container.markdown(full_response + " ▌")
                
                response_container.markdown(full_response)
                
            except Exception as e:
                st.error(f"حدث خطأ تقني: {e}")
    else:
        st.warning("الرجاء كتابة طلبك أو المشكلة التقنية أولاً.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 14px;'>Developed with passion in Sfax, Tunisia by Houssem Kessentini © 2026</p>", unsafe_allow_html=True)
