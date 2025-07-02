import random

import streamlit as st
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from querymancer.agent import ask, create_history
from querymancer.config import Config
from querymancer.models import create_llm
from querymancer.tools import get_available_tools, with_mongo_client

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

@st.cache_data(show_spinner=False)
def get_db_info():
    """Get database information and cache it."""
    try:
        with with_mongo_client() as db:
            collections = db.list_collection_names()
            collection_info = {}
            for collection_name in collections:
                count = db[collection_name].count_documents({})
                collection_info[collection_name] = count
        return collections, collection_info, None
    except Exception as e:
        return [], {}, str(e)

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
    st.write(f"**Database:** {Config.Database.DATABASE_NAME}")
    st.write(f"**Connection:** MongoDB Atlas")
    st.write(f"**Type:** MongoDB")
    
    collections, collection_info, error = get_db_info()
    
    if error:
        st.error(f"Error connecting to database: {error}")
    else:
        st.write(f"**Collections:**")
        for collection_name in collections:
            count = collection_info.get(collection_name, 0)
            st.write(f"- {collection_name} ({count} documents)")
            
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