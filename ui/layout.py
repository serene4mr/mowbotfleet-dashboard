# ui/layout.py

import streamlit as st
from .dashboard import render_header, render_row1, render_row2, render_row3, render_debug
from .settings import render_settings
from streamlit.runtime.scriptrunner import RerunException, RerunData

def render_sidebar():
    if st.sidebar.button("🔒 Logout"):
        st.session_state.clear()
        raise RerunException(RerunData())
    return st.sidebar.radio("Navigate", ["Dashboard", "Settings"])

def render_dashboard():
    render_header()
    render_row1()
    render_row2()
    render_row3()
    render_debug()
