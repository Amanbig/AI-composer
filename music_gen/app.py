
import streamlit as st
from dotenv import load_dotenv
import os
import sys
import sys
# import extra_streamlit_components as stx # Removed

# Ensure modules are found (add current dir to path if needed)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modules
from modules.db import init_db
from modules.db import get_db, User
from modules.cron import start_scheduler
from ui.styles import CUSTOM_CSS
from ui.auth_ui import render_login_ui
from ui.app_ui import render_main_app

# Load env
load_dotenv()

# Page Config
st.set_page_config(
    page_title="AI Music Composer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state.user = None
                # Optional: st.rerun() if strictly needed, but let's see flow

# Load Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize System (db init is now handled by get_db on demand)
if 'scheduler_started' not in st.session_state:
    init_db() # Create tables if not exist
    start_scheduler()
    st.session_state.scheduler_started = True

# Routing
if not st.session_state.user:
    render_login_ui()
else:
    render_main_app(st.session_state.user)
