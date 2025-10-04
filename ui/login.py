# ui/login.py

import streamlit as st
from auth import verify_user
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_login():
    """
    Render the login screen. On successful login, store user in session and rerun.
    """
    st.title("MowbotFleet Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("🔐 Login"):
        if verify_user(username, password):
            st.session_state["user"] = username
            st.success(f"Welcome, {username}!")
            
            # Show security reminder for default admin
            if username == "admin" and password == "admin":
                st.warning("🔒 Security Reminder: Please change the default admin password!")
            
            # Force rerun
            raise RerunException(RerunData())
        else:
            st.error("Invalid username or password.")
