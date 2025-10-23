# ui/login.py

import streamlit as st
from auth import verify_user
from streamlit.runtime.scriptrunner import RerunException, RerunData
from i18n_manager import t

def render_login():
    """
    Render the login screen. On successful login, store user in session and rerun.
    """
    st.title(t("login.title"))
    
    # Add helpful information
    st.info(t("login.login_help"))
    
    username = st.text_input(t("login.username"))
    password = st.text_input(t("login.password"), type="password")
    
    # Add forgot password link
    st.caption(t("login.forgot_password"))
    st.caption(t("login.contact_admin"))
    
    if st.button(t("login.login_button"), use_container_width=True):
        if verify_user(username, password):
            st.session_state["user"] = username
            st.success(t("login.welcome_message", username=username))
            
            # Show security reminder for default admin
            if username == "admin" and password == "admin":
                st.warning(t("login.security_reminder"))
            
            # Force rerun
            raise RerunException(RerunData())
        else:
            st.error(t("login.invalid_credentials"))
