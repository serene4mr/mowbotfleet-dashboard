# ui/layout.py

import streamlit as st
from .pages.dashboard import render_header, render_row1, render_row2, render_debug
from .pages.settings import render_settings
from .pages.missions import render_missions
from streamlit.runtime.scriptrunner import RerunException, RerunData
from mqtt_client import get_broker_info

def render_sidebar():
    if st.sidebar.button("🔒 Logout"):
        st.session_state.clear()
        raise RerunException(RerunData())
    
    # Broker connection status in sidebar
    broker_info = get_broker_info()
    if broker_info["status"] == "Connected":
        tls_icon = "🔒" if broker_info["tls"] else "🔓"
        st.sidebar.success(f"🟢 Broker: {broker_info['host']}:{broker_info['port']} {tls_icon}")
        st.sidebar.caption(f"User: {broker_info['username']}")
    else:
        st.sidebar.error("🔴 Broker: Disconnected")
    
    st.sidebar.markdown("---")
    
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
