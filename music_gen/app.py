
import streamlit as st
from dotenv import load_dotenv
import os
import sys
import extra_streamlit_components as stx

# Ensure modules are found (add current dir to path if needed)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Modules
from modules.db import init_db
from modules.auth_token import verify_token
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

def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# Check for existing token in cookies if user is not logged in
if st.session_state.user is None:
    token = cookie_manager.get(cookie="auth_token")
    if token:
        payload = verify_token(token)
        if payload:
            # Token valid, fetch user
            db = next(get_db())
            user = db.query(User).filter(User.username == payload['sub']).first()
            if user:
                st.session_state.user = {'id': user.id, 'username': user.username}
                # Optional: st.rerun() if strictly needed, but let's see flow

# Load Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize System (db init is now handled by get_db on demand)
if 'scheduler_started' not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# Routing
if not st.session_state.user:
    render_login_ui(cookie_manager)
else:
    render_main_app(st.session_state.user, cookie_manager)
