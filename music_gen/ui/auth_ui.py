
import streamlit as st
import extra_streamlit_components as stx
from modules.db import get_db
from modules.auth import create_user, authenticate_user
from modules.auth_token import create_access_token
from sqlalchemy.exc import IntegrityError
import time

def render_login_ui(cookie_manager):
    """Renders the login/register page container"""
    
    # Initialize CookieManager (Passed from app.py)
    # cookie_manager = stx.CookieManager() # Removed to avoid dup key
    
    # Center the content using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #60A5FA;">🎹 AI Composer</h1>
            <p style="color: #94A3B8;">Sign in to start creating</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Container with card styling
        with st.container():
            st.markdown('<div class="history-card" style="padding: 2rem;">', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Sign In", width="stretch")
                    
                    if submitted:
                        if not username or not password:
                            st.error("Please enter both username and password")
                        else:
                            db = next(get_db())
                            user = authenticate_user(db, username, password)
                            if user:
                                # Create Token
                                token = create_access_token(data={"sub": user.username})
                                cookie_manager.set("auth_token", token, key="set_login_token")
                                
                                st.session_state.user = {'id': user.id, 'username': user.username}
                                st.success(f"Welcome back, {user.username}!")
                                time.sleep(0.5) # Give time for cookie to set
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                            
            with tab2:
                with st.form("register_form"):
                    new_user = st.text_input("Choose Username")
                    new_pass = st.text_input("Choose Password", type="password")
                    confirm_pass = st.text_input("Confirm Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Create Account", width="stretch")
                    
                    if submitted:
                        if not new_user or not new_pass:
                            st.error("All fields are required")
                        elif new_pass != confirm_pass:
                            st.error("Passwords do not match")
                        else:
                            db = next(get_db())
                            try:
                                user = create_user(db, new_user, new_pass)
                                # Create Token
                                token = create_access_token(data={"sub": user.username})
                                cookie_manager.set("auth_token", token, key="set_reg_token")
                                
                                st.session_state.user = {'id': user.id, 'username': user.username}
                                st.success("Account created! Logging in...")
                                time.sleep(0.5)
                                st.rerun()
                            except IntegrityError:
                                st.error("Username already exists.")
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
