# ui/layout.py

import streamlit as st
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_sidebar():
    """
    Render the sidebar with Logout button and page navigation.
    Returns the selected page name.
    """
    if st.sidebar.button("🔒 Logout"):
        st.session_state.clear()
        # Force rerun
        raise RerunException(RerunData())
    
    page = st.sidebar.radio(
        "Navigate",
        options=["Dashboard", "Settings"],
        index=0
    )
    return page

def render_dashboard():
    """
    Stub for dashboard page rendering. Implement later.
    """
    st.header("Dashboard")
    st.write("Dashboard content goes here.")

def render_settings():
    """
    Stub for settings page rendering. Implement later.
    """
    st.header("Settings")
    st.write("Settings content goes here.")
