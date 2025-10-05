# ui/layout.py

import streamlit as st
from .pages.dashboard import render_header, render_row1, render_row2, render_debug
from .pages.settings import render_settings
from .pages.missions import render_missions
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_sidebar():
    if st.sidebar.button("🔒 Logout"):
        st.session_state.clear()
        raise RerunException(RerunData())
    
    # Navigation - pure Streamlit state management, no manual index
    selected_page = st.sidebar.radio(
        "Navigate", 
        ["Dashboard", "Missions", "Settings"],
        key="page_navigation"
    )
    
    return selected_page

def render_dashboard():
    render_header()
    render_row1()
    render_row2()
    render_debug()

def render_missions_page():
    render_missions()
