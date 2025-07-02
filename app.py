import random

import streamlit as st
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from querymancer.agent import ask, create_history
from querymancer.config import Config
from querymancer.models import create_llm
from querymancer.tools import get_available_tools, with_sql_cursor

load_dotenv()

LOADING_MESSAGES = [
    "Processing your request...",
    "Analyzing the database structure...",
    "Formulating the best approach...",
    "Optimizing the query...",
    "Gathering necessary information...",
    "Executing preliminary checks...",
    "Validating the database schema...",
    "Identifying relevant data points...",
    "Analyzing the query's performance...",
    "Generating a detailed response...",
]


@st.cache_resource(show_spinner=False)
def get_model() -> BaseChatModel:
    """Initialize and return the language model."""
    llm = create_llm(Config.MODEL_CONFIG)
    llm = llm.bind_tools(get_available_tools())
    return llm

def load_css(css_file):
    """Load custom CSS from a file."""
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        
st.set_page_config(
    page_title="Querymancer",
    page_icon=":mag_right:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

load_css("assets/style.css")

st.header("ARTIFICIAL INTELLIGENCE DATABASE ASSISTANT")
st.subheader("Your AI Assistant")

with st.sidebar:
    st.markdown("### Database Configuration")
    st.write(f"**File:** {Config.Paths.DATABASE_PATH.relative_to(Config.Paths.APP_HOME)}")
    db_size = Config.Paths.DATABASE_PATH.stat().st_size / (1024 * 1024)  # Size in MB
    st.write(f"**Size:** {db_size:.2f} MB")
    
    with with_sql_cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        st.write(f"**Tables:**")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            st.write(f"- {table} ({count} rows)")
            
if "messages" not in st.session_state:
    st.session_state.messages = create_history()
    
for message in st.session_state.messages:
    if type(message) is SystemMessage:
        continue
    is_user = type(message) is HumanMessage
    avatar = "👤" if is_user else "🤖"
    with st.chat_message("user" if is_user else "assistant", avatar=avatar):
        st.markdown(f"{message.content}")
        
if prompt := st.chat_input("Ask a question about the database..."):
    st.session_state.messages.append(HumanMessage(prompt))
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"{prompt}")
        
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.status(random.choice(LOADING_MESSAGES), state="running")
        
        response = ask(prompt, st.session_state.messages, get_model())
        message_placeholder.markdown(response)
        st.session_state.messages.append(AIMessage(response))