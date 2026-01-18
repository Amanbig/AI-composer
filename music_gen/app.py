
import streamlit as st
from dotenv import load_dotenv
import os
import sys

# Ensure modules are found (add current dir to path if needed)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modules
from modules.db import init_db
from modules.cron import start_scheduler
from ui.styles import CUSTOM_CSS
from ui.auth_ui import render_login_ui
from ui.app_ui import render_main_app

# Load env
load_dotenv()

# Page Config
st.set_page_config(
    page_title="AI Music Composer",
    page_icon="🎹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize System
init_db()

if 'scheduler_started' not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# Session State
if 'user' not in st.session_state:
    st.session_state.user = None

# Routing
if not st.session_state.user:
    render_login_ui()
else:
    render_main_app(st.session_state.user)
