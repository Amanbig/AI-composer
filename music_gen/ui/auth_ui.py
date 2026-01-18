
import streamlit as st
from modules.db import get_db
from modules.auth import create_user, authenticate_user
from sqlalchemy.exc import IntegrityError

def render_login_ui():
    """Renders the login/register page container"""
    
    st.markdown("## 🔐 Access Music Composer")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    db = next(get_db())
                    user = authenticate_user(db, username, password)
                    if user:
                        st.session_state.user = {'id': user.id, 'username': user.username}
                        st.success(f"Welcome back, {user.username}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account")
            
            if submitted:
                if not new_user or not new_pass:
                    st.error("All fields are required")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match")
                else:
                    db = next(get_db())
                    try:
                        create_user(db, new_user, new_pass)
                        st.success("Account created successfully! Please login.")
                    except IntegrityError:
                        st.error("Username already exists.")
                    except Exception as e:
                        st.error(f"Error: {e}")
